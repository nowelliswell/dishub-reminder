import express from "express";
import fs from "fs-extra";
import bodyParser from "body-parser";
import qrcode from "qrcode-terminal";
import baileys, { DisconnectReason, useMultiFileAuthState } from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";

// 🔹 Load .env lebih awal
dotenv.config();

// 🔹 Setup dasar
const app = express();
const AUTH_FOLDER = process.env.AUTH_FOLDER || "./auth_info";
const port = process.env.PORT || 3000;
const appName = process.env.APP_NAME || "WhatsApp API Gateway";

// 🔹 Fix __dirname di ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 🔹 Middleware
app.use(bodyParser.json());
app.use(cors());
app.use(express.static(path.join(__dirname, "..", "Templates")));

// 🔹 Route default (tampilkan login.html)
app.get("/", (req, res) => {
  try {
    return res.sendFile(path.join(__dirname, "..", "Templates", "login.html"));
  } catch (err) {
    console.error("Error serving login.html:", err);
    return res.status(500).json({ error: err.message });
  }
});

let sock;
let isConnected = false;
let currentQR = null;
let lastConnectionUpdate = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_RECONNECT_DELAY = 5000; // 5 seconds

// === CONNECT TO WHATSAPP ===
async function connectToWhatsApp() {
  try {
    console.log("🔄 Attempting to connect to WhatsApp... (attempt", reconnectAttempts + 1, ")");
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);
    const { makeWASocket } = baileys;

    // Add try-catch around makeWASocket to handle init queries errors
    try {
      sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        browser: ["Dishub Reminder", "Chrome", "1.0.0"],
        syncFullHistory: false,
        connectTimeoutMs: 60000, // Increase connection timeout to 60 seconds
        defaultQueryTimeoutMs: 60000, // Increase query timeout to 60 seconds
        keepAliveIntervalMs: 30000, // Keep alive every 30 seconds
      });
    } catch (socketError) {
      console.error("❌ Error creating WhatsApp socket (init queries failed):", socketError.message);
      if (socketError.message.includes("init queries") || socketError.output?.statusCode === 400) {
        console.log("🔄 Init queries error detected. Retrying with backoff...");
        return scheduleReconnect();
      }
      throw socketError;
    }

    sock.ev.on("creds.update", async () => {
      try {
        await saveCreds();
      } catch (err) {
        console.error("Error saving creds:", err);
      }
    });

    sock.ev.on("connection.update", async (update) => {
      try {
        const { connection, lastDisconnect, qr } = update;
        lastConnectionUpdate = update;

        if (qr) {
          currentQR = qr;
          console.log("📱 QR baru tersedia (akan dikirim ke frontend).");
        }

        if (connection === "close") {
          isConnected = false;
          const boomError = new Boom(lastDisconnect?.error);
          const reason = boomError?.output?.statusCode;
          const shouldReconnect = reason !== DisconnectReason.loggedOut;

          console.log("⚠️ Koneksi terputus:", reason, lastDisconnect?.error?.message);

          // Check for logout - automatically reset auth and regenerate QR
          if (reason === DisconnectReason.loggedOut || reason === 401) {
            console.log("🚫 Logout terdeteksi, regenerasi QR otomatis...");
            // Reset connection state
            reconnectAttempts = 0;
            currentQR = null;

            // Delete old auth session
            try {
              if (await fs.pathExists(AUTH_FOLDER)) {
                await fs.remove(AUTH_FOLDER);
                console.log("🗑️ Auth info lama dihapus.");
              }
            } catch (err) {
              console.error("Error deleting auth folder:", err);
            }

            // Restart connection to generate new QR
            console.log("🔄 Memulai ulang koneksi untuk QR baru...");
            setTimeout(() => connectToWhatsApp(), 1000); // Small delay before restart
            return;
          }

          // Check for init queries error specifically
          if (lastDisconnect?.error?.message?.includes("init queries") ||
              boomError?.output?.payload?.message?.includes("init queries") ||
              reason === 400) {
            console.log("🔄 Init queries error detected in connection update. Retrying...");
            return scheduleReconnect();
          }

          if (shouldReconnect) {
            console.log("🔄 Reconnecting...");
            scheduleReconnect();
          } else {
            console.log("🚫 Logged out. Scan ulang diperlukan.");
            reconnectAttempts = 0; // Reset attempts for manual reconnect
          }
        } else if (connection === "open") {
          isConnected = true;
          currentQR = null;
          reconnectAttempts = 0; // Reset on successful connection
          console.log("✅ WhatsApp Connected!");
        }
      } catch (err) {
        console.error("Unexpected error in connection update:", err);
      }
    });

    sock.ev.on('messages.upsert', async (m) => {
      try {
        const msg = m.messages[0];
        if (!msg.message) return;

        // proses pesan di sini
        console.log('Pesan diterima dari:', msg.key.remoteJid);

      } catch (err) {
        // Enhanced error handling for message processing
        if (err.message?.includes('Unknown message type') ||
            err.message?.includes('decode-wa-message')) {
          console.warn('⚠️ Unknown message type encountered - skipping message processing');
          return; // Skip processing this message, don't crash
        }

        console.error('❌ Error saat proses pesan:', err.message);
        // Don't rethrow - let the bot continue running
      }
    });
  } catch (err) {
    console.error("❌ Gagal koneksi ke WhatsApp:", err.message);
    scheduleReconnect();
  }
}

// Helper function for exponential backoff retry
async function scheduleReconnect() {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.error("❌ Max reconnect attempts reached. Auto-resetting auth and starting fresh...");

    // Auto-reset auth and restart
    reconnectAttempts = 0;
    currentQR = null;

    try {
      // Delete old auth session
      if (await fs.pathExists(AUTH_FOLDER)) {
        await fs.remove(AUTH_FOLDER);
        console.log("🗑️ Auth info dihapus otomatis.");
      }
    } catch (err) {
      console.error("Error deleting auth folder:", err);
    }

    // Restart connection immediately
    console.log("🔄 Memulai ulang koneksi otomatis...");
    setTimeout(() => connectToWhatsApp(), 1000); // Small delay before restart
    return;
  }

  reconnectAttempts++;

  setTimeout(() => {
    connectToWhatsApp();
  }, BASE_RECONNECT_DELAY);
}

// 🔹 Jalankan koneksi pertama kali
connectToWhatsApp();

// === API ===

// ✅ Ambil QR untuk frontend
app.get("/qr", (req, res) => {
  try {
    if (currentQR) {
      return res.json({ success: true, qr: currentQR });
    } else {
      return res.json({
        success: false,
        message: isConnected
          ? "✅ Sudah terkoneksi ke WhatsApp."
          : "⏳ Menunggu koneksi atau QR baru...",
        connection: lastConnectionUpdate,
      });
    }
  } catch (err) {
    console.error("Error fetching QR:", err);
    return res.status(500).json({ error: err.message });
  }
});

// ✅ Streaming QR ke frontend (tanpa refresh)
app.get("/qr-stream", async (req, res) => {
  try {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const sendQR = () => {
      try {
        if (currentQR) {
          res.write(`data: ${JSON.stringify({ qr: currentQR })}\n\n`);
        } else if (isConnected) {
          res.write(`data: ${JSON.stringify({ connected: true })}\n\n`);
        }
      } catch (err) {
        console.error("Error sending QR data:", err);
      }
    };

    // kirim QR pertama kali (jika sudah ada)
    sendQR();

    // interval untuk push update QR baru
    const interval = setInterval(sendQR, 3000);

    // bersihkan koneksi jika user tutup halaman
    req.on("close", () => clearInterval(interval));
  } catch (err) {
    console.error("Error setting up QR stream:", err);
    return res.status(500).json({ error: err.message });
  }
});

// ✅ Reset Auth agar QR baru muncul
app.delete("/reset-auth", async (req, res) => {
  try {
    if (sock) {
      await sock.logout().catch(() => {});
      sock = null;
      isConnected = false;
      currentQR = null;
    }

    if (await fs.pathExists(AUTH_FOLDER)) {
      await fs.remove(AUTH_FOLDER);
      console.log("🗑️ Auth info dihapus.");
    }

    // Reconnect untuk generate QR baru
    connectToWhatsApp();

    res.json({ success: true, message: "Auth info direset, tunggu QR baru muncul di frontend." });
  } catch (err) {
    console.error("❌ Reset gagal:", err);
    res.status(500).json({ success: false, message: "Gagal reset auth info." });
  }
});

// ✅ Kirim pesan
app.post("/send", async (req, res) => {
  try {
    const { phone, message } = req.body;
    if (!phone || !message)
      return res.status(400).json({ error: "Field 'phone' dan 'message' wajib diisi" });

    if (!isConnected || !sock)
      return res.status(503).json({ error: "WhatsApp belum terkoneksi. Scan QR dulu." });

    const jid = formatPhoneNumber(phone);
    await sock.sendMessage(jid, { text: message });

    res.json({ success: true, to: jid, message });
  } catch (err) {
    console.error("❌ Gagal kirim WA:", err);
    res.status(500).json({ error: err.toString() });
  }
});

// === Helper ===
function formatPhoneNumber(number) {
  number = number.toString().replace(/[^0-9+]/g, "");
  if (number.startsWith("+")) number = number.slice(1);
  if (number.startsWith("0")) number = "62" + number.slice(1);
  if (!number.startsWith("62"))
    throw new Error("Nomor WhatsApp harus diawali 62, +62, atau 0");
  return number + "@s.whatsapp.net";
}

// === Jalankan Server ===
app.listen(port, () => {
  console.log(`📡 ${appName} aktif di http://localhost:${port}`);
  console.log(`🔗 Akses manual: http://localhost:${port}`);
});