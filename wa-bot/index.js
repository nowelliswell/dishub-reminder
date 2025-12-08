import express from "express";
import fs from "fs-extra";
import bodyParser from "body-parser";
import baileys, { DisconnectReason, useMultiFileAuthState } from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const AUTH_FOLDER = process.env.AUTH_FOLDER || "./auth_info";
const port = process.env.PORT || 3000;

// Enable CORS
app.use(cors());

// Parse JSON request bodies
app.use(express.json());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files from Templates directory
app.use(express.static('../Templates'));

let sock;
let isConnected = false;
let currentQR = null;

// === CONNECT ===
async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);
  const { fetchLatestBaileysVersion, makeWASocket } = baileys;

  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    printQRInTerminal: false,
    auth: state,
    browser: ["Dishub Reminder", "Chrome", "1.0.0"],
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      currentQR = qr;
      console.log("📱 New QR code generated");
    }

    if (connection === "close") {
      console.log("Connection closed. lastDisconnect:", lastDisconnect);
      isConnected = false;
      
      // Handle conflict by stopping reconnection
      if (lastDisconnect?.error?.message?.includes('conflict') || lastDisconnect?.error?.output?.payload?.content?.[0]?.tag === 'conflict') {
        console.log("Session conflict detected. Another WhatsApp session is active. Please log out from other devices or close the official WhatsApp app, then restart this bot.");
        return; // Stop reconnection
      }

      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;

      if (reason === DisconnectReason.loggedOut) {
        console.log("🔓 Logged out, removing auth and reconnecting...");
        await fs.remove(AUTH_FOLDER);
        currentQR = null;
        return connectToWhatsApp();
      }

      // Reconnect for other disconnection reasons
      console.log("🔄 Reconnecting...");
      connectToWhatsApp();
    }

    if (connection === "open") {
      isConnected = true;
      currentQR = null;
      console.log("✅ WhatsApp Connected.");
    }
  });
}

// Start WA
connectToWhatsApp();

// === API: Get QR ===
app.get("/qr", (req, res) => {
  if (currentQR) {
    return res.json({ success: true, qr: currentQR, connected: false });
  }
  if (isConnected) {
    return res.json({ success: false, message: "Already connected to WhatsApp", connected: true });
  }
  return res.json({ success: false, message: "Waiting for QR code...", connected: false });
});

// === API: Send Message ===
app.post("/send", async (req, res) => {
  try {
    console.log("📨 Received request body:", req.body);
    
    const { phone, message } = req.body;
    
    if (!phone || !message) {
      console.log("❌ Missing phone or message in request");
      return res.status(400).json({ error: "Phone and message are required" });
    }
    
    if (!sock || !isConnected) {
      console.log("❌ WhatsApp not connected");
      return res.status(503).json({ error: "WhatsApp not connected" });
    }

    const jid = phone.replace(/[^0-9]/g, "") + "@s.whatsapp.net";
    console.log(`📤 Sending message to ${jid}`);
    
    await sock.sendMessage(jid, { text: message });
    
    console.log(`✅ Message sent successfully to ${phone}`);
    res.json({ success: true, phone: phone, status: "sent" });
  } catch (err) {
    console.log("❌ Error sending message:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// === API: Reset Auth ===
app.delete("/reset-auth", async (req, res) => {
  try {
    console.log("🔄 Resetting auth...");
    
    // Hapus auth folder
    await fs.remove(AUTH_FOLDER);
    console.log("✅ Auth folder removed");
    
    // Reset state
    isConnected = false;
    currentQR = null;
    
    // Logout dari socket jika masih terkoneksi
    if (sock) {
      try {
        await sock.logout();
        console.log("✅ Socket logged out");
      } catch (err) {
        console.log("⚠️ Socket logout error (might be already disconnected):", err.message);
      }
    }
    
    // Reconnect untuk generate QR baru
    setTimeout(() => {
      console.log("🔄 Reconnecting to generate new QR...");
      connectToWhatsApp();
    }, 1000);
    
    res.json({ message: "Auth reset successfully, generating new QR..." });
  } catch (err) {
    console.error("❌ Reset auth error:", err);
    res.status(500).json({ error: err.message });
  }
});

// === Serve Login Page ===
app.get("/login.html", (req, res) => {
  res.sendFile('../Templates/login.html', { root: __dirname });
});

// === API: QR Stream (Server-Sent Events) ===
app.get("/qr-stream", (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Cache-Control',
  });

  // Send initial status
  res.write(`data: ${JSON.stringify({ connected: isConnected, qr: currentQR })}\n\n`);

  // Function to send updates
  const sendUpdate = () => {
    res.write(`data: ${JSON.stringify({ connected: isConnected, qr: currentQR })}\n\n`);
  };

  // Listen for QR updates
  const originalQR = currentQR;
  const checkForUpdates = setInterval(() => {
    if (currentQR !== originalQR || isConnected) {
      sendUpdate();
      if (isConnected) {
        clearInterval(checkForUpdates);
      }
    }
  }, 1000);

  // Clean up on client disconnect
  req.on('close', () => {
    clearInterval(checkForUpdates);
    res.end();
  });
});

// === SERVER ===
app.listen(port, () => console.log("Server running on port", port));
