import express from "express";
import fs from "fs-extra";
import bodyParser from "body-parser";
import qrcode from "qrcode-terminal";
import { makeWASocket, DisconnectReason, useMultiFileAuthState } from "@whiskeysockets/baileys";
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
app.use(express.static(path.join(__dirname, "..", "templates")));

// 🔹 Route default (tampilkan login.html)
app.get("/", (req, res) => {
  try {
    return res.sendFile(path.join(__dirname, "..", "templates", "login.html"));
  } catch (err) {
    console.error("Error serving login.html:", err);
    return res.status(500).json({ error: err.message });
  }
});

// In-memory message store to handle WhatsApp retry requests
const sentMessagesStore = new Map();

function saveSentMessage(key, messageContent) {
  const msgId = key.id;
  sentMessagesStore.set(msgId, messageContent);
  
  // Clean up message from memory after 1 hour to avoid memory leak
  setTimeout(() => {
    sentMessagesStore.delete(msgId);
  }, 3600000); // 1 hour
}

let sock;
let isConnected = false;
let currentQR = null;
let lastConnectionUpdate = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_RECONNECT_DELAY = 5000; // 5 seconds
let encryptionErrorCount = 0; // Track encryption errors
const MAX_ENCRYPTION_ERRORS = 5; // Max errors before force repair
let lastErrorStatus = null;

// Track active clients viewing the login/QR code page
let activeSSEClients = 0;
let lastQRRequestTime = 0;
let reconnectTimeout = null;

function isClientActive() {
  return activeSSEClients > 0 || (Date.now() - lastQRRequestTime < 10000);
}

// === CONNECT TO WHATSAPP ===
async function connectToWhatsApp() {
  try {
    console.log("🔄 Attempting to connect to WhatsApp... (attempt", reconnectAttempts + 1, ")");
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);

    // Add try-catch around makeWASocket to handle init queries errors
    try {
      sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        browser: ["Dishub Reminder", "Chrome", "1.0.0"],
        syncFullHistory: false, // Disable full history sync
        connectTimeoutMs: 60000, // Increase connection timeout to 60 seconds
        defaultQueryTimeoutMs: 60000, // Increase query timeout to 60 seconds
        keepAliveIntervalMs: 30000, // Keep alive every 30 seconds
        retryRequestDelayMs: 2000, // Delay between retries
        maxMsgRetryCount: 5, // Max retry for sending messages
        // ✅ Disable ALL sync features to prevent missing key errors
        shouldSyncHistoryMessage: () => false,
        emitOwnEvents: false, // Don't emit events for own messages
        markOnlineOnConnect: true, // Mark as online when connected
        fireInitQueries: false, // Don't fire initial queries to avoid sync errors
        // ✅ Ignore status broadcast to prevent PreKey errors
        shouldIgnoreJid: (jid) => jid === 'status@broadcast',
        getMessage: async (key) => {
          if (sentMessagesStore.has(key.id)) {
            return sentMessagesStore.get(key.id);
          }
          return {
            conversation: 'Message retry'
          };
        }
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
        
        // ✅ DEBUG: Log semua connection state
        console.log("🔔 Connection update:", { connection, hasQR: !!qr, isConnected });

        // ✅ Handle QR - only set once and log once. Stop connection if no clients are active.
        if (qr && !isConnected) {
          if (!isClientActive()) {
            console.log("⏹️ QR baru di-generate tetapi tidak ada client aktif. Menghentikan socket...");
            try {
              sock.end();
            } catch (err) {
              console.error("Error ending socket:", err);
            }
            sock = null;
            currentQR = null;
            return;
          }
          currentQR = qr;
          console.log("📱 QR baru tersedia (akan dikirim ke frontend).");
        }

        if (connection === "close") {
          isConnected = false;
          currentQR = null; // Clear QR on disconnect
          const boomError = new Boom(lastDisconnect?.error);
          const reason = boomError?.output?.statusCode;
          const shouldReconnect = reason !== DisconnectReason.loggedOut;

          console.log("⚠️ Koneksi terputus:", reason, lastDisconnect?.error?.message);

          if (reason === DisconnectReason.connectionReplaced) {
            console.log("⚠️ ERROR: Sesi ini telah diambil alih oleh perangkat/lokasi lain.");
            lastErrorStatus = "SESSION_REPLACED";
          }

          // Check for logout - automatically reset auth and regenerate QR
          if (reason === DisconnectReason.loggedOut || reason === 401) {
            console.log("🚫 Logout terdeteksi, membersihkan sesi...");
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

            // Restart connection to generate new QR only if client is active
            if (isClientActive()) {
              console.log("🔄 Memulai ulang koneksi untuk QR baru...");
              setTimeout(() => connectToWhatsApp(), 1000); // Small delay before restart
            } else {
              console.log("⏹️ Restart koneksi dibatalkan karena tidak ada client aktif.");
              sock = null;
            }
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
            if (isClientActive()) {
              console.log("🔄 Reconnecting (client aktif terdeteksi)...");
              scheduleReconnect();
            } else {
              console.log("⏹️ Reconnect dibatalkan karena tidak ada client aktif.");
              sock = null;
              currentQR = null;
            }
          } else {
            console.log("🚫 Logged out. Scan ulang diperlukan.");
            reconnectAttempts = 0; // Reset attempts for manual reconnect
          }
        } else if (connection === "open") {
          isConnected = true;
          currentQR = null;
          reconnectAttempts = 0; // Reset on successful connection
          lastErrorStatus = null; // Reset error status
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

        // ✅ FILTER: Ignore status broadcast messages completely
        if (msg.key.remoteJid === 'status@broadcast') {
          return; // Silently ignore status messages - they cause encryption errors but are not needed
        }

        // Reset encryption error count on successful message
        encryptionErrorCount = 0;

        // proses pesan di sini
        console.log('Pesan diterima dari:', msg.key.remoteJid);

      } catch (err) {
        // ✅ FILTER: Suppress errors from status broadcast
        const sender = m.messages[0]?.key?.remoteJid;
        if (sender === 'status@broadcast') {
          return; // Silently ignore status broadcast errors
        }

        // Enhanced error handling for message processing
        if (err.message?.includes('Unknown message type') ||
            err.message?.includes('decode-wa-message')) {
          console.warn('⚠️ Unknown message type encountered - skipping message processing');
          return; // Skip processing this message, don't crash
        }

        // Handle PreKey errors with auto-repair (only for non-status messages)
        if (err.message?.includes('PreKey') || err.name === 'PreKeyError' || 
            err.message?.includes('decrypt') || err.message?.includes('Invalid')) {
          encryptionErrorCount++;
          console.warn(`⚠️ Encryption error detected (${encryptionErrorCount}/${MAX_ENCRYPTION_ERRORS}) - message will be retried`);
          
          // Auto-repair if too many encryption errors
          if (encryptionErrorCount >= MAX_ENCRYPTION_ERRORS) {
            console.error('❌ Too many encryption errors! Force refreshing session...');
            encryptionErrorCount = 0;
            
            // Force reconnect to refresh keys
            if (sock) {
              try {
                await sock.ws.close();
              } catch (e) {}
            }
            
            setTimeout(() => {
              console.log('🔄 Restarting connection to refresh encryption keys...');
              connectToWhatsApp();
            }, 3000);
          }
          return;
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
    if (reconnectTimeout) clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(() => connectToWhatsApp(), 1000); // Small delay before restart
    return;
  }

  reconnectAttempts++;

  if (reconnectTimeout) clearTimeout(reconnectTimeout);
  reconnectTimeout = setTimeout(() => {
    connectToWhatsApp();
  }, BASE_RECONNECT_DELAY);
}

// 🔹 Jalankan koneksi pertama kali HANYA jika ada file session
const credsExist = fs.existsSync(path.join(AUTH_FOLDER, "creds.json"));
if (credsExist) {
  console.log("🔑 Sesi tersimpan ditemukan. Menghubungkan ke WhatsApp...");
  connectToWhatsApp();
} else {
  console.log("🚪 Sesi tidak ditemukan. Tunggu hingga halaman login dibuka untuk memulai.");
}

// === API ===

app.post("/cancel-login", (req, res) => {
  try {
    console.log("⏹️ Pembatalan koneksi dipicu oleh client (Klik Kembali).");
    
    // Clear reconnect timeout
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
      console.log("⏹️ Reconnect timeout dibatalkan.");
    }

    if (!isConnected && sock) {
      console.log("⏹️ Soket WhatsApp dihentikan: dibatalkan oleh client.");
      try {
        sock.end();
      } catch (err) {
        console.error("Error ending socket during cancel:", err);
      }
      sock = null;
      currentQR = null;
      reconnectAttempts = 0;
    }
    return res.json({ success: true, message: "Koneksi berhasil dibatalkan oleh client." });
  } catch (err) {
    console.error("Error canceling login:", err);
    return res.status(500).json({ error: err.message });
  }
});

// Helper function to validate connection before sending
async function validateConnectionBeforeSend(jid) {
  try {
    // Check if socket exists and connected
    if (!sock || !isConnected) {
      throw new Error('Not connected');
    }
    
    // Try to fetch user status as connection test
    await sock.fetchStatus(jid).catch(() => {
      // If fetch fails, it's okay, user might have hidden status
    });
    
    // Small delay to ensure keys are synced
    await new Promise(r => setTimeout(r, 500));
    
    return true;
  } catch (err) {
    console.warn('⚠️ Connection validation failed:', err.message);
    return false;
  }
}

// ✅ Ambil QR untuk frontend
app.get("/qr", (req, res) => {
  try {
    lastQRRequestTime = Date.now();
    // Start socket if it is not running
    if (!sock && !isConnected) {
      console.log("🔌 Client memanggil /qr (polling). Menyalakan socket WhatsApp...");
      connectToWhatsApp();
    }

    if (currentQR) {
      return res.json({ success: true, qr: currentQR });
    } else {
      return res.json({
        success: false,
        isConnected: isConnected,
        message: isConnected
          ? "✅ Sudah terkoneksi ke WhatsApp."
          : "⏳ Menunggu koneksi atau QR baru...",
        connection: lastConnectionUpdate,
        lastErrorStatus: lastErrorStatus,
        activeUser: isConnected && sock?.user ? {
          phone: sock.user.id.split(":")[0].split("@")[0],
          name: sock.user.name || "Perangkat Server"
        } : null
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

    activeSSEClients++;
    // Start socket if it is not running
    if (!sock && !isConnected) {
      console.log("🔌 Ada client terhubung ke QR stream. Menyalakan socket WhatsApp...");
      connectToWhatsApp();
    }

    const sendQR = () => {
      try {
        // ✅ FIX: Jangan kirim QR lagi kalau sudah connected
        if (isConnected) {
          res.write(`data: ${JSON.stringify({ connected: true })}\n\n`);
          return; // Stop sending QR
        }
        
        if (currentQR) {
          res.write(`data: ${JSON.stringify({ qr: currentQR })}\n\n`);
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
    req.on("close", () => {
      clearInterval(interval);
      activeSSEClients--;
      console.log(`🔌 Client terputus dari QR stream. Sisa client: ${activeSSEClients}`);
      
      // Jika tidak ada client lagi dan belum login, hentikan socket
      if (activeSSEClients <= 0 && !isConnected) {
        console.log("⏹️ Tidak ada client aktif (Tab ditutup). Mematikan socket...");
        
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
          console.log("⏹️ Reconnect timeout dibatalkan.");
        }
        
        if (sock) {
          try {
            sock.end();
          } catch (err) {
            console.error("Error ending socket:", err);
          }
          sock = null;
        }
        currentQR = null;
        reconnectAttempts = 0;
      }
    });
  } catch (err) {
    console.error("Error setting up QR stream:", err);
    return res.status(500).json({ error: err.message });
  }
});

// ✅ Reset Auth agar QR baru muncul (mendukung pembatalan login)
app.delete("/reset-auth", async (req, res) => {
  try {
    const isCancel = req.query.cancel === "true";
    
    if (isCancel) {
      console.log("⏹️ Pembatalan koneksi dipicu oleh client (Klik Kembali).");
      
      // Clear reconnect timeout
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
        console.log("⏹️ Reconnect timeout dibatalkan.");
      }

      if (sock) {
        console.log("⏹️ Soket WhatsApp dihentikan: dibatalkan oleh client.");
        try {
          sock.end();
        } catch (err) {
          console.error("Error ending socket during cancel:", err);
        }
        sock = null;
      }
      
      isConnected = false;
      currentQR = null;
      reconnectAttempts = 0;
      
      // Clean auth session
      if (await fs.pathExists(AUTH_FOLDER)) {
        await fs.remove(AUTH_FOLDER);
        console.log("🗑️ Auth info dibersihkan.");
      }
      
      return res.json({ success: true, message: "Koneksi berhasil dibatalkan oleh client." });
    }

    // Normal reset-auth flow (when refresh QR is clicked)
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
    
    // ✅ VALIDATE CONNECTION FIRST
    const isValid = await validateConnectionBeforeSend(jid);
    if (!isValid) {
      return res.status(503).json({ error: "Connection not ready. Please wait a moment and try again." });
    }
    
    // ✅ RETRY LOGIC (3x attempts dengan delay)
    let attempts = 0;
    const maxAttempts = 3;
    let lastError;
    
    while (attempts < maxAttempts) {
      try {
        const sentMsg = await sock.sendMessage(jid, { text: message });
        if (sentMsg && sentMsg.message) {
          saveSentMessage(sentMsg.key, sentMsg.message);
        }
        console.log(`✅ Message sent successfully to ${jid} (attempt ${attempts + 1})`);
        return res.json({ 
          success: true, 
          to: jid, 
          message, 
          attempts: attempts + 1 
        });
      } catch (err) {
        attempts++;
        lastError = err;
        console.log(`⚠️ Attempt ${attempts}/${maxAttempts} failed:`, err.message);
        
        // If encryption error, wait longer before retry
        if (err.message?.includes('encrypt') || err.message?.includes('PreKey') || err.message?.includes('Invalid')) {
          console.log('🔐 Encryption error detected, waiting 5s before retry...');
          if (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // 5 detik untuk encryption error
          }
        } else {
          // Delay sebelum retry (kecuali attempt terakhir)
          if (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 2000)); // 2 detik
          }
        }
      }
    }
    
    // Kalau semua attempts gagal
    throw new Error(`Failed after ${maxAttempts} attempts: ${lastError.message}`);
    
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