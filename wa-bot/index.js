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
  res.sendFile(path.join(__dirname, "..", "Templates", "login.html"));
});

let sock;
let isConnected = false;
let currentQR = null;
let lastConnectionUpdate = null;

// === CONNECT TO WHATSAPP ===
async function connectToWhatsApp() {
  try {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);
    const { makeWASocket } = baileys;

  sock = makeWASocket({
    auth: state,
    printQRInTerminal: false,
    browser: ["Dishub Reminder", "Chrome", "1.0.0"],
});

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect, qr } = update;
      lastConnectionUpdate = update;

      if (qr) {
  currentQR = qr;
  console.log("📱 QR baru tersedia (akan dikirim ke frontend).");
}

      if (connection === "close") {
        isConnected = false;
        const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
        const shouldReconnect = reason !== DisconnectReason.loggedOut;

        console.log("⚠️ Koneksi terputus:", reason, lastDisconnect?.error?.message);
        if (shouldReconnect) {
          console.log("🔄 Reconnecting...");
          connectToWhatsApp();
        } else {
          console.log("🚫 Logged out. Scan ulang diperlukan.");
        }
      } else if (connection === "open") {
        isConnected = true;
        currentQR = null;
        console.log("✅ WhatsApp Connected!");
      }
    });
  } catch (err) {
    console.error("❌ Gagal koneksi ke WhatsApp:", err);
    setTimeout(connectToWhatsApp, 5000);
  }
}

// 🔹 Jalankan koneksi pertama kali
connectToWhatsApp();

// === API ===

// ✅ Ambil QR untuk frontend
app.get("/qr", (req, res) => {
  if (currentQR) {
    res.json({ success: true, qr: currentQR });
  } else {
    res.json({
      success: false,
      message: isConnected
        ? "✅ Sudah terkoneksi ke WhatsApp."
        : "⏳ Menunggu koneksi atau QR baru...",
      connection: lastConnectionUpdate,
    });
  }
});

// ✅ Streaming QR ke frontend (tanpa refresh)
app.get("/qr-stream", async (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const sendQR = () => {
    if (currentQR) {
      res.write(`data: ${JSON.stringify({ qr: currentQR })}\n\n`);
    } else if (isConnected) {
      res.write(`data: ${JSON.stringify({ connected: true })}\n\n`);
    }
  };

  // kirim QR pertama kali (jika sudah ada)
  sendQR();

  // interval untuk push update QR baru
  const interval = setInterval(sendQR, 3000);

  // bersihkan koneksi jika user tutup halaman
  req.on("close", () => clearInterval(interval));
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
