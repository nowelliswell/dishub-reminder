import express from "express";
import fs from "fs-extra";
import bodyParser from "body-parser";
import qrcode from "qrcode-terminal";
import makeWASocket, {
    useMultiFileAuthState,
    DisconnectReason
} from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import open from "open";
import dotenv from "dotenv"; // ✅ Tambahan

// Load .env
dotenv.config();

const app = express();
const AUTH_FOLDER = process.env.AUTH_FOLDER || "auth_info";
const port = process.env.PORT || 3000;
const appName = process.env.APP_NAME || "WhatsApp API Gateway";

// ✅ Fix __dirname untuk ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Middleware
app.use(bodyParser.json());
app.use(cors());

// ✅ Route default langsung buka login.html
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "..", "Templates", "login.html"));
});

// ✅ Sajikan file static (HTML, CSS, JS) dari folder Templates
app.use(express.static(path.join(__dirname, "..", "Templates")));

// ✅ Endpoint untuk cek status koneksi
app.get("/status", (req, res) => {
    res.json({ connected: isConnected });
});

app.listen(port, () => {
    console.log(`📡 ${appName} aktif di http://localhost:${port}`);
    open(`http://localhost:${port}`);
});

let sock;
let isConnected = false;
let currentQR = null; // simpan QR sementara

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);

    sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            currentQR = qr; // simpan QR
            console.log("📱 QR tersedia, scan di frontend...");
            qrcode.generate(qr, { small: true });
        }

        if (connection === "close") {
            isConnected = false;
            let shouldReconnect = true;

            if (lastDisconnect?.error) {
                const err = lastDisconnect.error;
                if (err instanceof Boom) {
                    shouldReconnect =
                        err.output?.statusCode !== DisconnectReason.loggedOut;
                } else if (err.output && err.output.statusCode !== undefined) {
                    shouldReconnect =
                        err.output.statusCode !== DisconnectReason.loggedOut;
                }
            }
            console.log("⚠️ Koneksi terputus:", lastDisconnect?.error);
            if (shouldReconnect) connectToWhatsApp();
        } else if (connection === "open") {
            isConnected = true;
            currentQR = null; // reset QR karena sudah login
            console.log("✅ WhatsApp Connected!");
        }
    });
}

connectToWhatsApp();

// === API untuk ambil QR ===
app.get("/qr", (req, res) => {
    if (currentQR) {
        res.json({ success: true, qr: currentQR });
    } else {
        res.json({
            success: false,
            qr: null,
            message: isConnected
                ? "Sudah terkoneksi ke WhatsApp."
                : "Tidak ada QR. Tunggu koneksi."
        });
    }
});

// === Reset auth tetap sama ===
app.delete("/reset-auth", async (req, res) => {
    try {
        if (sock) {
            try {
                await sock.logout();
                if (sock.ws) sock.ws.close();
            } catch (e) {
                console.log("⚠️ Error saat logout:", e.message);
            }
            sock = null;
            isConnected = false;
        }

        if (await fs.pathExists(AUTH_FOLDER)) {
            await fs.remove(AUTH_FOLDER);
            console.log("🗑️ Auth info dihapus.");
        }

        connectToWhatsApp();
        res.json({
            success: true,
            message: "Auth info berhasil direset. Scan QR baru di frontend."
        });
    } catch (err) {
        console.error("❌ Reset gagal:", err);
        res.status(500).json({ success: false, message: "Gagal reset auth info." });
    }
});

// === Kirim pesan ===
app.post("/send", async (req, res) => {
    try {
        const { phone, message } = req.body;
        if (!phone || !message) {
            return res.status(400).json({ error: "Field 'phone' dan 'message' wajib diisi" });
        }

        if (!isConnected || !sock) {
            return res.status(503).json({ error: "WhatsApp belum terkoneksi. Scan QR dulu." });
        }

        const jid = formatPhoneNumber(phone);
        await sock.sendMessage(jid, { text: message });

        res.json({ success: true, to: jid, message });
    } catch (err) {
        console.error("❌ Gagal kirim WA:", err);
        res.status(500).json({ error: err.toString() });
    }
});

// === Format nomor ===
function formatPhoneNumber(number) {
    if (!number) throw new Error("Nomor tidak boleh kosong");
    number = number.toString().replace(/[^0-9+]/g, "");
    if (number.startsWith("+")) number = number.slice(1);
    if (number.startsWith("0")) number = "62" + number.slice(1);
    if (!number.startsWith("62")) {
        throw new Error("Nomor WhatsApp harus diawali 62, +62, atau 0");
    }
    return number + "@s.whatsapp.net";
}
