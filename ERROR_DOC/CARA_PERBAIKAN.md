# 🔧 Panduan Perbaikan WhatsApp Reminder Bot

## 📋 Ringkasan Masalah

Anda mengalami 2 masalah utama:

1. **Error API**: `"Cannot destructure property 'phone' of 'req.body' as it is undefined"`
2. **Scheduler tidak mengirim**: Pesan otomatis H-1/H-2 jam 12 siang tidak terkirim

## ✅ Perbaikan yang Sudah Dilakukan

### 1. File `wa-bot/index.js` (Node.js WhatsApp Bot)

**Masalah**: Node.js tidak bisa membaca JSON dari request body

**Perbaikan**:
```javascript
// DITAMBAHKAN middleware ini:
app.use(cors());                                    // ← Baru
app.use(express.json());                            // ← Baru
app.use(bodyParser.json());                         // ← Baru
app.use(bodyParser.urlencoded({ extended: true })); // ← Baru
```

**Hasil**: Sekarang Node.js bisa menerima dan membaca `phone` dan `message` dari Python

### 2. File `whatsapp_reminder_app.py` (Flask Backend)

**Masalah**: Fungsi `send_automatic_reminders()` terlalu ketat mengecek waktu

**Perbaikan**:
- Dihapus pengecekan `if current_time.hour != 12 or current_time.minute != 0`
- Ditambahkan logging detail untuk debugging
- Ditambahkan summary report

**Hasil**: Scheduler bisa berjalan dengan baik dan mengirim pesan

### 3. File `requirement.txt`

**Ditambahkan**:
- `apscheduler` (untuk scheduler)
- `werkzeug` (untuk Flask utilities)

## 🚀 Langkah-Langkah Menjalankan Ulang

### Opsi 1: Menggunakan Script Otomatis (MUDAH)

1. **Double-click** file `restart_services.bat`
2. Tunggu kedua window terbuka (Node.js dan Flask)
3. Cek log di masing-masing window

### Opsi 2: Manual (Jika ingin lebih kontrol)

#### A. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirement.txt

# Install Node.js dependencies
cd wa-bot
npm install
cd ..
```

#### B. Start Node.js WhatsApp Bot

```bash
cd wa-bot
node index.js
```

**Tunggu sampai muncul**:
- `Server running on port 3000`
- `WhatsApp Connected.` (atau scan QR code dulu)

#### C. Start Flask App (di terminal baru)

```bash
python whatsapp_reminder_app.py
```

**Tunggu sampai muncul**:
- `Database initialized (reminders.db).`
- `🚀 Automatic reminder scheduler started in background.`
- `Running on http://0.0.0.0:5000`

## 🧪 Testing

### Test 1: Cek Services Berjalan

```bash
python test_api.py
```

Script ini akan:
- ✅ Cek apakah Flask dan Node.js berjalan
- ✅ Test Node.js API langsung
- ✅ Test Flask send_one endpoint
- ✅ Test fungsi automatic reminders

### Test 2: Manual Send (via Browser/Postman)

**Test kirim 1 reminder**:
```
POST http://localhost:5000/send_one/1
```

**Test Node.js langsung**:
```
POST http://localhost:3000/send
Content-Type: application/json

{
  "phone": "6285857768760",
  "message": "Test message"
}
```

### Test 3: Cek Log

**Log Node.js** (harus muncul):
```
📨 Received request body: { phone: '628xxx', message: '...' }
📤 Sending message to 628xxx@s.whatsapp.net
✅ Message sent successfully to 628xxx
```

**Log Flask** (harus muncul):
```
📤 Sending to Node API http://localhost:3000/send payload={...}
📥 Response: 200 {"success":true,"phone":"628xxx","status":"sent"}
```

## ⏰ Cara Kerja Scheduler

### Jadwal Otomatis
- **Waktu**: Setiap hari jam **12:00 WIB**
- **Target**: Reminder dengan status **H-1** (besok) dan **H-2** (lusa)
- **Proses**:
  1. Scheduler bangun jam 12:00 WIB
  2. Ambil semua reminder dari database
  3. Filter yang H-1 dan H-2 saja
  4. Kirim pesan ke masing-masing nomor
  5. Log hasil ke database

### Log yang Akan Muncul (Jam 12:00 WIB)

```
🕐 [2025-12-04T12:00:00.026761+07:00] Starting automatic reminder job...
🕐 Current time (WIB): 2025-12-04 12:00:00
📋 Found 5 total reminders in database
📤 [H-1] Sending to Noelino Grevansha Arsandy (AD 12345 BC) at 6285857768760
📤 Sending to Node API http://localhost:3000/send payload={...}
📥 Response: 200 {"success":true,"phone":"6285857768760","status":"sent"}
✅ [H-1] Automatic reminder sent to Noelino Grevansha Arsandy (AD 12345 BC)
📊 Summary: 1 sent, 0 failed
✅ Job completed: {'status': 'completed', 'sent_count': 1, 'failed_count': 0, ...}
```

## 🐛 Troubleshooting

### ❌ Masih Error "Cannot destructure property 'phone'"

**Penyebab**: Node.js belum di-restart setelah perubahan

**Solusi**:
1. Tutup terminal Node.js (Ctrl+C)
2. Jalankan ulang: `cd wa-bot && node index.js`
3. Pastikan muncul "Server running on port 3000"

### ❌ Scheduler Tidak Jalan

**Cek 1**: Apakah Flask sudah jalan?
```bash
# Harus muncul:
🚀 Automatic reminder scheduler started in background.
```

**Cek 2**: Apakah ada reminder H-1 atau H-2?
- Buka http://localhost:5000/list
- Pastikan ada reminder dengan test_date besok atau lusa

**Cek 3**: Tunggu sampai jam 12:00 WIB
- Scheduler hanya jalan jam 12 siang
- Atau gunakan test manual: `curl -X POST http://localhost:5000/run_now`

### ❌ WhatsApp Tidak Tersambung

**Solusi**:
1. Buka http://localhost:3000/login.html
2. Scan QR code dengan WhatsApp di HP
3. Tunggu sampai muncul "WhatsApp Connected" di console Node.js

**Catatan**: Pastikan tidak ada WhatsApp Web lain yang aktif!

### ❌ Pesan Tidak Terkirim (Status 503)

**Penyebab**: WhatsApp belum connect

**Solusi**:
1. Cek console Node.js, harus ada "WhatsApp Connected"
2. Jika belum, scan QR code lagi
3. Restart Node.js jika perlu

## 🧪 Test Scheduler Sekarang (Tanpa Tunggu Jam 12)

Jika ingin test scheduler **sekarang** tanpa menunggu jam 12:00:

### Cara 1: Gunakan Endpoint Manual

```bash
curl -X POST http://localhost:5000/run_now
```

Atau buka di browser:
```
http://localhost:5000/run_now
```

### Cara 2: Ubah Jadwal Scheduler (Sementara)

Edit file `scheduler/auto_send.py`:

```python
# SEBELUM (jam 12:00 saja):
trigger = CronTrigger(hour=12, minute=0, timezone=wib_timezone)

# SESUDAH (setiap menit - untuk testing):
trigger = CronTrigger(minute='*', timezone=wib_timezone)
```

Restart Flask, dan scheduler akan jalan setiap menit.

**INGAT**: Kembalikan ke `hour=12, minute=0` setelah testing!

## 📊 Monitoring

### Cek Pesan Terkirim

**Via Browser**:
```
http://localhost:5000/pesankeluar
```

**Via API**:
```bash
curl http://localhost:5000/api/sent_messages
```

### Cek Statistik

```bash
curl http://localhost:5000/api/stats
```

Response:
```json
{
  "in": 0,
  "out": 5,
  "users": 10
}
```

## 📝 Checklist Setelah Perbaikan

- [ ] Node.js berjalan di port 3000
- [ ] Flask berjalan di port 5000
- [ ] WhatsApp sudah tersambung (scan QR)
- [ ] Test manual send berhasil (`/send_one/1`)
- [ ] Test script berhasil (`python test_api.py`)
- [ ] Scheduler sudah jalan (cek log "scheduler started")
- [ ] Tunggu jam 12:00 WIB atau test dengan `/run_now`

## 🎯 Kesimpulan

Masalah utama adalah **Node.js tidak bisa membaca JSON** karena tidak ada middleware body parser. Setelah ditambahkan:

✅ API bisa menerima request dari Python
✅ Scheduler bisa mengirim pesan otomatis
✅ Logging lebih jelas untuk debugging

**Selamat mencoba!** 🎉

Jika masih ada masalah, cek log di console Node.js dan Flask untuk detail error.
