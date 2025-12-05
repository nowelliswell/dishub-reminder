# 🚦 WhatsApp Reminder System - Dishub Kota Surakarta

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey.svg)

**Sistem Pengingat Otomatis Uji Kendaraan Bermotor**

Aplikasi web untuk mengelola dan mengirim pengingat otomatis uji KIR kendaraan melalui WhatsApp dengan penjadwalan H-1 dan H-2.

[Fitur](#-fitur) • [Instalasi](#-instalasi) • [Penggunaan](#-penggunaan) • [API](#-api-endpoints) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📋 Daftar Isi

- [Tentang Project](#-tentang-project)
- [Fitur](#-fitur)
- [Teknologi](#-teknologi)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Penggunaan](#-penggunaan)
- [API Endpoints](#-api-endpoints)
- [Scheduler](#-scheduler)
- [Struktur Project](#-struktur-project)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Kontribusi](#-kontribusi)
- [Lisensi](#-lisensi)

---

## 🎯 Tentang Project

WhatsApp Reminder System adalah aplikasi web yang dirancang untuk **Dinas Perhubungan Kota Surakarta** untuk mengelola dan mengirim pengingat otomatis kepada pemilik kendaraan tentang jadwal uji berkala kendaraan (Uji KIR).

### Masalah yang Diselesaikan

- ✅ Mengurangi keterlambatan uji kendaraan
- ✅ Otomasi pengiriman reminder via WhatsApp
- ✅ Manajemen data kendaraan dan pemilik
- ✅ Monitoring pesan terkirim
- ✅ Dashboard statistik real-time

### Cara Kerja

1. **Input Data**: Admin memasukkan data kendaraan dan jadwal uji
2. **Penjadwalan**: Sistem otomatis mendeteksi H-1 dan H-2
3. **Pengiriman**: Setiap hari jam 12:00 WIB, sistem mengirim reminder otomatis
4. **Monitoring**: Admin dapat melihat status pengiriman dan statistik

---

## ✨ Fitur

### 🎨 Dashboard & UI

- **Dashboard Modern**: Interface Bootstrap dengan SweetAlert2
- **Manajemen Reminder**: CRUD lengkap (Create, Read, Update, Delete)
- **Filter & Search**: Cari berdasarkan nama, nomor kendaraan, status
- **Statistik Real-time**: Grafik pesan masuk/keluar, jumlah user
- **Responsive Design**: Mobile-friendly interface

### 📱 WhatsApp Integration

- **Auto-send H-1/H-2**: Pengiriman otomatis 1-2 hari sebelum jadwal
- **Manual Send**: Kirim reminder individual kapan saja
- **Bulk Send**: Kirim ke semua reminder sekaligus
- **QR Code Login**: Mudah connect WhatsApp Web
- **Session Management**: Auto-reconnect jika terputus

### ⏰ Scheduler

- **Cron-based**: Menggunakan APScheduler
- **Timezone Support**: WIB (UTC+7)
- **Configurable**: Mudah ubah jadwal pengiriman
- **Logging**: Detail log setiap pengiriman

### 📊 Monitoring & Reporting

- **Message History**: Riwayat semua pesan terkirim
- **Status Tracking**: Success, Failed, Pending
- **Time Series**: Grafik pengiriman per hari/bulan
- **Export Data**: Download data dalam format JSON

### ✏️ Template Chat Editor (NEW!)

- **Visual Editor**: Edit template pesan WhatsApp dengan mudah
- **Live Preview**: Preview real-time dengan data contoh
- **Dynamic Variables**: 5 variabel otomatis ({nama}, {nomor_kendaraan}, {no_uji}, {jenis_kendaraan}, {tanggal_uji})
- **Database Storage**: Template tersimpan di database, tidak hilang
- **Template History**: Lihat dan rollback ke template sebelumnya
- **Test Send**: Test kirim pesan sebelum digunakan
- **One-Click Insert**: Klik variabel untuk insert ke template

---

## 🛠 Teknologi

### Backend

- **Python 3.9+**: Core backend language
- **Flask**: Web framework
- **SQLite**: Database
- **APScheduler**: Task scheduling
- **Requests**: HTTP client

### WhatsApp Bot

- **Node.js 18+**: Runtime environment
- **Express**: Web server
- **Baileys**: WhatsApp Web API
- **@whiskeysockets/baileys**: WhatsApp library

### Frontend

- **HTML5/CSS3**: Markup & styling
- **Bootstrap 5**: UI framework
- **JavaScript**: Client-side logic
- **SweetAlert2**: Beautiful alerts
- **Chart.js**: Data visualization

---

## 📦 Instalasi

### Prerequisites

Pastikan sudah terinstall:

- Python 3.9 atau lebih tinggi
- Node.js 18 atau lebih tinggi
- npm atau yarn
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/dishub-reminder.git
cd dishub-reminder
```

### 2. Install Python Dependencies

```bash
# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirement.txt
```

### 3. Install Node.js Dependencies

```bash
cd wa-bot
npm install
cd ..
```

### 4. Setup Database

Database akan otomatis dibuat saat pertama kali menjalankan aplikasi.

```bash
python whatsapp_reminder_app.py
```

---

## ⚙️ Konfigurasi

### Environment Variables

Buat file `.env` di root directory:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Node.js Configuration
NODE_API_URL=http://localhost:3000/send
PORT=3000
AUTH_FOLDER=./auth_info

# Database
DB_PATH=reminders.db
```

### Konfigurasi Scheduler

Edit `scheduler/auto_send.py` untuk mengubah jadwal:

```python
# Default: Setiap hari jam 12:00 WIB
trigger = CronTrigger(hour=12, minute=0, timezone=wib_timezone)

# Contoh: Setiap jam
trigger = CronTrigger(hour='*', minute=0, timezone=wib_timezone)

# Contoh: Setiap 30 menit
trigger = CronTrigger(minute='*/30', timezone=wib_timezone)
```

---

## 🚀 Penggunaan

### Quick Start (Otomatis)

**Windows**:
```bash
restart_services.bat
```

Script ini akan:
1. Stop semua proses yang berjalan
2. Start Node.js WhatsApp Bot
3. Start Flask Application

### Manual Start

#### 1. Start WhatsApp Bot

```bash
cd wa-bot
node index.js
```

**Output yang diharapkan**:
```
Server running on port 3000
WhatsApp Connected.
```

#### 2. Start Flask Application

Di terminal baru:

```bash
python whatsapp_reminder_app.py
```

**Output yang diharapkan**:
```
Database initialized (reminders.db).
🚀 Automatic reminder scheduler started in background.
 * Running on http://0.0.0.0:5000
```

#### 3. Connect WhatsApp

1. Buka browser: `http://localhost:3000/login.html`
2. Scan QR code dengan WhatsApp di HP
3. Tunggu hingga muncul "WhatsApp Connected" di console

### Akses Aplikasi

- **Home/Input**: http://localhost:5000/
- **Dashboard Monitoring**: http://localhost:5000/dashboard
- **Database List**: http://localhost:5000/list
- **Edit Chat Template**: http://localhost:5000/edit_chat ✨ **NEW!**
- **Pesan Keluar**: http://localhost:5000/pesankeluar
- **WhatsApp Login**: http://localhost:3000/login.html

---

## 📡 API Endpoints

### Reminder Management

#### GET /list
Mendapatkan daftar semua reminder

```bash
curl http://localhost:5000/list?format=json
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "vehicle_number": "AD 1234 BC",
    "no_uji": "DPR 5060790",
    "jenis_kendaraan": "Truck",
    "test_date": "2025-12-05",
    "phone": "6285857768760",
    "status": "H-1",
    "color": "warning",
    "days_until": 1
  }
]
```

#### POST /add
Menambah reminder baru

```bash
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "vehicle_number": "AD 1234 BC",
    "no_uji": "DPR 5060790",
    "jenis_kendaraan": "Truck",
    "test_date": "2025-12-05",
    "phone": "085857768760"
  }'
```

#### PUT /edit/:id
Update reminder

```bash
curl -X PUT http://localhost:5000/edit/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe Updated",
    "vehicle_number": "AD 1234 BC",
    "test_date": "2025-12-06",
    "phone": "085857768760"
  }'
```

#### DELETE /delete/:id
Hapus reminder

```bash
curl -X DELETE http://localhost:5000/delete/1
```

### Message Operations

#### POST /send_one/:id
Kirim reminder ke satu nomor

```bash
curl -X POST http://localhost:5000/send_one/1
```

#### POST /run_now
Kirim semua reminder H-1 dan H-2 sekarang

```bash
curl -X POST http://localhost:5000/run_now
```

#### GET /api/sent_messages
Lihat riwayat pesan terkirim

```bash
curl http://localhost:5000/api/sent_messages
```

### Statistics

#### GET /api/stats
Statistik hari ini

```bash
curl http://localhost:5000/api/stats
```

**Response**:
```json
{
  "in": 0,
  "out": 15,
  "users": 50
}
```

#### GET /api/messages_timeseries
Data time series untuk grafik

```bash
# Per hari (30 hari terakhir)
curl http://localhost:5000/api/messages_timeseries?period=day&days=30

# Per bulan (12 bulan terakhir)
curl http://localhost:5000/api/messages_timeseries?period=month&months=12
```

### WhatsApp Bot API

#### POST /send
Kirim pesan WhatsApp

```bash
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "6285857768760",
    "message": "Test message"
  }'
```

#### GET /qr
Dapatkan QR code untuk login

```bash
curl http://localhost:3000/qr
```

#### DELETE /reset-auth
Reset session WhatsApp

```bash
curl -X DELETE http://localhost:3000/reset-auth
```

### Chat Template API ✨ NEW!

#### GET /api/template
Ambil template chat aktif

```bash
curl http://localhost:5000/api/template
```

**Response:**
```json
{
  "template": "🚗 Halo Sdr/i {nama}...",
  "status": "ok"
}
```

#### POST /api/template
Simpan template chat baru

```bash
curl -X POST http://localhost:5000/api/template \
  -H "Content-Type: application/json" \
  -d '{
    "template": "Template baru dengan {variabel}",
    "name": "Custom Template"
  }'
```

**Response:**
```json
{
  "status": "ok",
  "message": "Template saved successfully"
}
```

#### GET /api/template/history
Lihat riwayat template (10 terakhir)

```bash
curl http://localhost:5000/api/template/history
```

**Response:**
```json
{
  "templates": [
    {
      "id": 2,
      "name": "Custom Template",
      "is_active": true,
      "created_at": "2025-12-05T10:30:00",
      "updated_at": "2025-12-05T10:30:00"
    }
  ],
  "status": "ok"
}
```

---

## ⏰ Scheduler

### Cara Kerja

Scheduler menggunakan **APScheduler** dengan timezone WIB (UTC+7):

1. **Trigger**: Setiap hari jam 12:00 WIB
2. **Proses**:
   - Ambil semua reminder dari database
   - Filter reminder dengan status H-1 (besok) dan H-2 (lusa)
   - Build pesan sesuai template
   - Kirim via WhatsApp Bot API
   - Log hasil ke database

### Template Pesan ✨ (Dapat Diedit!)

Template pesan sekarang dapat diedit melalui halaman **Edit Chat Template** (`/edit_chat`).

**Variabel yang Tersedia:**
- `{nama}` - Nama pemilik kendaraan (sesuai STNK)
- `{nomor_kendaraan}` - Nomor plat kendaraan
- `{no_uji}` - Nomor uji kendaraan
- `{jenis_kendaraan}` - Jenis kendaraan (Truck, Pickup, dll)
- `{tanggal_uji}` - Tanggal jadwal uji kendaraan

**Template Default:**
```
🚗 Halo Sdr/i {nama} (sesuai STNK)

📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {nomor_kendaraan}
🔢 Nomor Uji : {no_uji}
🚛 Jenis Kendaraan : {jenis_kendaraan}
📆 Tanggal Uji Kendaraan: {tanggal_uji}

⚠️ Mohon untuk segera melakukan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.
✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan.
🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan
⏰ Harap hadir sesuai jadwal

🙏 Terima Kasih - Dishub Kota Surakarta
```

**Cara Edit Template:**
1. Buka halaman `/edit_chat`
2. Edit template di editor
3. Klik variabel untuk insert otomatis
4. Preview real-time di sebelah kanan
5. Klik "Simpan Template"
6. Template baru langsung aktif untuk semua pengiriman

### Monitoring Scheduler

Log scheduler akan muncul di console Flask:

```
🕐 [2025-12-04T12:00:00+07:00] Starting automatic reminder job...
🕐 Current time (WIB): 2025-12-04 12:00:00
📋 Found 50 total reminders in database
📤 [H-1] Sending to John Doe (AD 1234 BC) at 6285857768760
✅ [H-1] Automatic reminder sent to John Doe (AD 1234 BC)
📤 [H-2] Sending to Jane Smith (AD 5678 EF) at 6281234567890
✅ [H-2] Automatic reminder sent to Jane Smith (AD 5678 EF)
📊 Summary: 2 sent, 0 failed
✅ Job completed: {'status': 'completed', 'sent_count': 2, 'failed_count': 0}
```

---

## 📁 Struktur Project

```
dishub-reminder/
├── whatsapp_reminder_app.py    # Main Flask application
├── requirement.txt             # Python dependencies
├── reminders.db               # SQLite database
├── check_db.py                # Database viewer utility
├── test_api.py                # API testing script
├── restart_services.bat       # Windows service restart script
│
├── scheduler/
│   └── auto_send.py           # Automatic reminder scheduler
│
├── wa-bot/                    # WhatsApp Bot (Node.js)
│   ├── index.js               # Main bot server
│   ├── package.json           # Node.js dependencies
│   └── auth_info/             # WhatsApp session data
│
├── static/                    # Static files
│   ├── common.css             # Global styles
│   └── uploads/               # Uploaded files (avatars, logos)
│
├── templates/                 # HTML templates
│   ├── index.html             # Home/Input page
│   ├── dashboard.html         # Main dashboard
│   ├── db.html                # Reminder list view
│   ├── edit_chat.html         # Chat template editor ✨ NEW!
│   ├── pesankeluar.html       # Sent messages view
│   ├── login.html             # WhatsApp login page
│   └── api.html               # API documentation page
│
└── docs/                      # Documentation
    ├── README.md              # This file
    ├── QUICK_START.md         # Quick start guide
    ├── CARA_PERBAIKAN.md      # Troubleshooting guide (ID)
    ├── DEBUG_CHECKLIST.md     # Debug checklist
    └── SUMMARY_PERBAIKAN.md   # Technical summary
```

---

## 🗄️ Database Schema

### Tables

#### 1. **reminders**
Menyimpan data pengingat kendaraan
```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    vehicle_number TEXT NOT NULL,
    no_uji TEXT,
    jenis_kendaraan TEXT,
    test_date TEXT NOT NULL,
    phone TEXT,
    created_at TEXT NOT NULL
);
```

#### 2. **messages**
Log pesan yang terkirim
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL,  -- 'in' or 'out'
    phone TEXT,
    message TEXT,
    status TEXT,
    meta TEXT,
    created_at TEXT NOT NULL
);
```

#### 3. **chat_templates** ✨ NEW!
Menyimpan template pesan WhatsApp
```sql
CREATE TABLE chat_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL,
    template_content TEXT NOT NULL,
    is_active INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**Note:** Database akan otomatis dibuat saat pertama kali menjalankan aplikasi. Default template akan otomatis diinsert.

---

## 🧪 Testing

### Automated Testing

Jalankan test suite lengkap:

```bash
python test_api.py
```

Test suite akan mengecek:
- ✅ Node.js API connectivity
- ✅ Flask API endpoints
- ✅ WhatsApp message sending
- ✅ Automatic reminder function
- ✅ Database operations

### Manual Testing

#### Test 1: Node.js API

```bash
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"phone":"6285857768760","message":"Test"}'
```

**Expected**: `{"success":true,"phone":"6285857768760","status":"sent"}`

#### Test 2: Flask Send One

```bash
curl -X POST http://localhost:5000/send_one/1
```

**Expected**: Status 200 dengan detail pengiriman

#### Test 3: Automatic Reminders

```bash
curl -X POST http://localhost:5000/run_now
```

**Expected**: Array of sent reminders

### Database Testing

Lihat isi database:

```bash
python check_db.py
```

Output akan menampilkan semua tabel dan isinya dalam format tabel.

---

## 🐛 Troubleshooting

### Masalah Umum

#### 1. Error: "Cannot destructure property 'phone'"

**Penyebab**: Node.js tidak bisa parse JSON body

**Solusi**:
```bash
# Pastikan wa-bot/index.js sudah ada middleware:
app.use(express.json());
app.use(bodyParser.json());

# Restart Node.js
cd wa-bot
node index.js
```

#### 2. WhatsApp Not Connected (503)

**Penyebab**: WhatsApp belum login

**Solusi**:
1. Buka http://localhost:3000/login.html
2. Scan QR code
3. Tunggu "WhatsApp Connected" di console

#### 3. Scheduler Tidak Kirim Pesan

**Penyebab**: Tidak ada reminder H-1 atau H-2

**Cek**:
```bash
curl http://localhost:5000/list?format=json
```

Pastikan ada reminder dengan `days_until: 1` atau `days_until: 2`

**Test Manual**:
```bash
curl -X POST http://localhost:5000/run_now
```

#### 4. Port Already in Use

**Solusi**:
```bash
# Windows - Kill process di port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Windows - Kill process di port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Debug Mode

Enable debug logging:

```python
# whatsapp_reminder_app.py
app.run(host="0.0.0.0", port=5000, debug=True)
```

### Logs

**Flask Console**: Lihat request/response dan scheduler logs

**Node.js Console**: Lihat WhatsApp connection dan message sending logs

**Database**: Query messages table untuk error details
```bash
sqlite3 reminders.db "SELECT * FROM messages WHERE status='failed' ORDER BY created_at DESC LIMIT 10;"
```

### Dokumentasi Lengkap

Lihat file-file berikut untuk troubleshooting detail:

- `QUICK_START.md` - Panduan cepat
- `CARA_PERBAIKAN.md` - Panduan perbaikan lengkap (Bahasa Indonesia)
- `DEBUG_CHECKLIST.md` - Checklist debugging
- `SUMMARY_PERBAIKAN.md` - Summary teknis

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Berikut cara berkontribusi:

1. Fork repository ini
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

### Development Guidelines

- Gunakan Python PEP 8 style guide
- Tambahkan docstring untuk fungsi baru
- Update README jika menambah fitur
- Test sebelum commit

---

## 📄 Lisensi

Project ini dilisensikan under MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

## 👥 Tim

**Dinas Perhubungan Kota Surakarta**

- Developer: [Your Name]
- Contact: [Your Email]
- Website: [Dishub Website]

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Baileys](https://github.com/WhiskeySockets/Baileys) - WhatsApp Web API
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [SweetAlert2](https://sweetalert2.github.io/) - Beautiful alerts

---

## 📞 Support

Jika mengalami masalah atau punya pertanyaan:

1. Cek [Troubleshooting](#-troubleshooting) section
2. Lihat [DEBUG_CHECKLIST.md](DEBUG_CHECKLIST.md)
3. Buka issue di GitHub
4. Contact: [your-email@example.com]

---

<div align="center">

**Made with ❤️ for Dishub Kota Surakarta**

⭐ Star project ini jika bermanfaat!

</div>
