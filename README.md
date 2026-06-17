# 🚦 Dishub Reminder - Sistem Pengingat Uji Kendaraan

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Sistem manajemen dan pengingat otomatis untuk uji berkala kendaraan bermotor melalui WhatsApp. Dibangun dengan Flask, MySQL/SQLite, dan WhatsApp Bot (Baileys).

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Teknologi](#-teknologi)
- [Prasyarat](#-prasyarat)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Struktur Project](#-struktur-project)
- [Workflow Aplikasi](#-workflow-aplikasi)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Kontribusi](#-kontribusi)

## ✨ Fitur Utama

### 📱 Manajemen Reminder
- ✅ Input data kendaraan dan pemilik
- ✅ Pencatatan nomor uji dan jenis kendaraan
- ✅ Auto-format nomor WhatsApp Indonesia (62xxx)
- ✅ Filter dan pencarian data reminder
- ✅ Edit dan hapus data reminder

### 📊 Dashboard & Monitoring
- ✅ Dashboard statistik real-time
- ✅ Analisis pesan keluar (sent/failed/pending)
- ✅ Grafik pesan per hari dan per bulan
- ✅ Export data ke Excel
- ✅ Export dashboard ke PDF

### 💬 WhatsApp Integration
- ✅ Kirim reminder otomatis via WhatsApp
- ✅ Template pesan yang dapat dikustomisasi
- ✅ QR Code login WhatsApp
- ✅ Auto-reconnect jika koneksi terputus
- ✅ Log semua pesan keluar dengan status

### ⏰ Scheduler Otomatis
- ✅ Kirim reminder otomatis setiap hari jam 12:00 WIB
- ✅ Klasifikasi status: H-today, H-1, H-3+, Expired
- ✅ Tandai kendaraan yang sudah uji

### 🎨 User Interface
- ✅ Modern design dengan Bootstrap 5
- ✅ Responsive mobile-friendly
- ✅ SweetAlert2 notifications
- ✅ DataTables untuk tabel interaktif
- ✅ Chart.js untuk visualisasi data

## 🛠 Teknologi

### Backend
- **Python 3.9+** - Core backend
- **Flask** - Web framework
- **MySQL / SQLite** - Database
- **APScheduler** - Task scheduler
- **python-dotenv** - Environment management

### Frontend
- **Bootstrap 5.3** - UI framework
- **Chart.js** - Data visualization
- **DataTables** - Interactive tables
- **SweetAlert2** - Notifications
- **Bootstrap Icons** - Icon set

### WhatsApp Bot
- **Node.js 18+** - Runtime
- **Baileys** - WhatsApp Web API
- **Express** - API server
- **QRCode Terminal** - QR display

## 📦 Prasyarat

Pastikan sistem Anda memiliki software berikut:

### 1. Python
```bash
# Cek versi Python (minimal 3.9)
python --version
# atau
python3 --version
```

### 2. Node.js dan npm
```bash
# Cek versi Node.js (minimal 18)
node --version

# Cek versi npm
npm --version
```

### 3. MySQL (Opsional)
```bash
# Jika menggunakan MySQL
mysql --version
```

### 4. Git
```bash
git --version
```

## 🚀 Instalasi

### Step 1: Clone Repository

```bash
# Clone repository
git clone https://github.com/nowelliswell/dishub-reminder.git

# Masuk ke folder project
cd dishub-reminder
```

### Step 2: Setup Python Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Untuk Windows:
venv\Scripts\activate
# Untuk Linux/Mac:
source venv/bin/activate

# Install dependencies Python
pip install flask flask-cors python-dotenv requests mysql-connector-python apscheduler werkzeug
```

### Step 3: Setup WhatsApp Bot (Node.js)

```bash
# Masuk ke folder wa-bot
cd wa-bot

# Install dependencies Node.js
npm install

# Kembali ke root folder
cd ..
```

### Step 4: Setup Database

#### Opsi A: Menggunakan MySQL (Recommended untuk Production)

```bash
# Login ke MySQL
mysql -u root -p

# Buat database
CREATE DATABASE dishub_reminder CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

# Keluar dari MySQL
exit;
```

#### Opsi B: Menggunakan SQLite (untuk Development)

SQLite akan otomatis membuat file `reminders.db` saat aplikasi pertama kali dijalankan.

## ⚙️ Konfigurasi

### 1. Environment Variables

Buat file `.env` di root folder project:

```bash
# Copy template .env
cp .env.example .env
# atau buat manual
```

Isi file `.env`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration (MySQL)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=dishub_reminder

# WhatsApp Bot Configuration
NODE_API_URL=http://localhost:3000/send
PORT=3000
AUTH_FOLDER=./auth_info
APP_NAME=WhatsApp API Gateway

# Scheduler Configuration (WIB = UTC+7)
SCHEDULER_HOUR=12
SCHEDULER_MINUTE=0
SCHEDULER_TIMEZONE=Asia/Jakarta
```

### 2. Konfigurasi Database

Edit file sesuai pilihan database Anda:

**Untuk MySQL:**
```bash
# Gunakan file ini
python whatsapp_reminder_app_mysql.py
```

**Untuk SQLite:**
```bash
# Gunakan file ini
python whatsapp_reminder_app.py
```

### 3. Migrasi Database (Jika dari SQLite ke MySQL)

```bash
# Jalankan script migrasi
python migrate_to_mysql.py
```

## 🎯 Menjalankan Aplikasi

### ⚠️ PENTING: Pilih Salah Satu Cara!

**JANGAN jalankan `node index.js` DAN `pm2 start` bersamaan!** Ini akan menyebabkan conflict karena kedua bot rebutan session WhatsApp yang sama.

---

### Cara 1: Manual dengan Node.js (Recommended untuk Development)

**Kelebihan:**
- ✅ Mudah debugging
- ✅ Log real-time di terminal
- ✅ Cepat stop/restart (Ctrl+C)

**Kekurangan:**
- ❌ Harus buka terminal terus
- ❌ Crash = bot mati
- ❌ Tutup terminal = bot mati

**Langkah:**

#### Terminal 1 - WhatsApp Bot (Port 3000)

```bash
cd wa-bot
node index.js
```

Output yang diharapkan:
```
📡 WhatsApp API Gateway aktif di http://localhost:3000
🔗 Akses manual: http://localhost:3000
🔄 Attempting to connect to WhatsApp...
📱 QR baru tersedia (akan dikirim ke frontend).
✅ WhatsApp Connected!
```

#### Terminal 2 - Flask Backend (Port 5000)

```bash
# Pastikan virtual environment aktif
# Untuk MySQL:
python whatsapp_reminder_app_mysql.py

# Untuk SQLite:
python whatsapp_reminder_app.py
```

Output yang diharapkan:
```
✅ Database MySQL initialized.
📊 Database: dishub_reminder
⏰ Scheduler: Active (sends at 12:00 WIB daily)
🌐 Available endpoints:
  POST /add
  GET  /list
  ...
 * Running on http://0.0.0.0:5000
```

---

### Cara 2: Production dengan PM2 (Recommended untuk Production)

**Kelebihan:**
- ✅ Auto-restart kalau crash
- ✅ Jalan di background (bisa tutup terminal)
- ✅ Monitoring CPU/memory
- ✅ Auto-start saat server reboot
- ✅ Scheduled restart (setiap 6 jam untuk refresh session)
- ✅ Log tersimpan otomatis

**Kekurangan:**
- ❌ Setup lebih kompleks
- ❌ Butuh install PM2 global

**Langkah:**

#### Step 1: Install PM2

```bash
npm install -g pm2
```

#### Step 2: Start WhatsApp Bot dengan PM2

```bash
cd wa-bot
pm2 start ecosystem.config.cjs
```

#### Step 3: Cek Status

```bash
pm2 list
```

Output:
```
┌────┬─────────┬─────────┬──────┬────────┬─────────┬──────────┐
│ id │ name    │ mode    │ ↺    │ status │ cpu     │ memory   │
├────┼─────────┼─────────┼──────┼────────┼─────────┼──────────┤
│ 0  │ wa-bot  │ cluster │ 0    │ online │ 2.3%    │ 95.2mb   │
└────┴─────────┴─────────┴──────┴────────┴─────────┴──────────┘
```

#### Step 4: Lihat Logs

```bash
# Real-time logs
pm2 logs wa-bot

# Last 100 lines
pm2 logs wa-bot --lines 100

# Error logs only
pm2 logs wa-bot --err
```

#### Step 5: Save & Setup Auto-Start

```bash
# Save current process list
pm2 save

# Setup auto-start on boot
pm2 startup
# Follow the command shown!
```

#### Step 6: Start Flask App

```bash
cd ..
# Untuk MySQL:
python whatsapp_reminder_app_mysql.py
# Atau pakai PM2 juga untuk Flask:
pm2 start whatsapp_reminder_app_mysql.py --interpreter python3 --name flask-app
```

---

### Cara 3: Menggunakan Screen (Linux Only)

```bash
# Terminal 1 - WhatsApp Bot
screen -S wa-bot
cd wa-bot
node index.js
# Tekan Ctrl+A lalu D untuk detach

# Terminal 2 - Flask
screen -S flask-app
python whatsapp_reminder_app_mysql.py
# Tekan Ctrl+A lalu D untuk detach

# Untuk kembali ke screen
screen -r wa-bot   # atau
screen -r flask-app

# List semua screen
screen -ls
```

---

### 🔥 PM2 Commands Lengkap

```bash
# Start/Stop/Restart
pm2 start ecosystem.config.cjs    # Start bot
pm2 stop wa-bot                   # Stop bot
pm2 restart wa-bot                # Restart bot
pm2 delete wa-bot                 # Remove from PM2
pm2 stop all                      # Stop semua apps
pm2 delete all                    # Remove semua apps

# Monitoring
pm2 list                          # List semua apps
pm2 monit                         # Dashboard real-time
pm2 logs wa-bot                   # Streaming logs
pm2 logs wa-bot --lines 50        # Last 50 lines
pm2 describe wa-bot               # Detail info

# Management
pm2 save                          # Save process list
pm2 resurrect                     # Restore saved apps
pm2 startup                       # Setup auto-start
pm2 unstartup                     # Remove auto-start
pm2 update                        # Update PM2
pm2 flush wa-bot                  # Clear logs

# Logs location
# Windows: C:\Users\<Username>\.pm2\logs\
# Linux: ~/.pm2/logs/
```

---

### 📊 PM2 vs Node.js Manual

| Aspek | `node index.js` | `pm2 start` |
|-------|-----------------|-------------|
| **Fungsi** | Jalanin bot | Jalanin bot |
| **Background** | ❌ Foreground | ✅ Background |
| **Auto-restart** | ❌ Crash = mati | ✅ Auto-restart |
| **Monitoring** | ❌ Tidak ada | ✅ Dashboard (`pm2 monit`) |
| **Logs** | ❌ Terminal only | ✅ Tersimpan di file |
| **Auto-start on boot** | ❌ Manual | ✅ Auto (`pm2 startup`) |
| **Scheduled restart** | ❌ Manual | ✅ Cron (setiap 6 jam) |
| **Memory limit** | ❌ Unlimited | ✅ Auto-restart jika > 500MB |
| **Multi-instance** | ❌ Tidak | ✅ Load balancing |
| **Untuk** | Development | Production |

---

### 🎯 Rekomendasi

**Development/Testing:**
```bash
node index.js
```

**Production:**
```bash
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup
```

**Debugging issue:**
```bash
# Stop PM2 dulu
pm2 stop wa-bot

# Jalankan manual untuk lihat log detail
node index.js
```

**Switching dari Manual ke PM2:**
```bash
# Stop manual (Ctrl+C di terminal)
# Lalu start PM2
pm2 start ecosystem.config.cjs
```

**Switching dari PM2 ke Manual:**
```bash
# Stop PM2
pm2 stop wa-bot
pm2 delete wa-bot

# Start manual
node index.js
```

---

### ⚠️ CATATAN PENTING

**Jangan pernah jalankan keduanya bersamaan!**

```bash
# ❌ SALAH - Akan conflict!
Terminal 1: node index.js
Terminal 2: pm2 start ecosystem.config.cjs

# ✅ BENAR - Pilih salah satu
node index.js ATAU pm2 start ecosystem.config.cjs
```

Kalau kamu jalankan 2 bot bersamaan, akan muncul error:
```
⚠️ Koneksi terputus: 440 Stream Errored (conflict)
```

Solusinya: Stop salah satu, biarkan hanya 1 bot yang jalan.

## 🌐 Akses Aplikasi

Setelah kedua service berjalan, akses:

- **Main App**: http://127.0.0.1:5000/
- **Dashboard**: http://127.0.0.1:5000/dashboard
- **Pesan Keluar**: http://127.0.0.1:5000/pesankeluar
- **Edit Template**: http://127.0.0.1:5000/edit_chat
- **WhatsApp QR**: http://127.0.0.1:3000/

### Login WhatsApp

1. Buka http://127.0.0.1:3000/
2. Scan QR Code dengan aplikasi WhatsApp di HP
3. Tunggu hingga status "Connected"

## 📁 Struktur Project

```
dishub-reminder/
├── 📁 wa-bot/                      # WhatsApp Bot (Node.js)
│   ├── index.js                    # Main bot server
│   ├── package.json                # Node dependencies
│   └── auth_info/                  # WhatsApp session (gitignored)
│
├── 📁 Templates/                   # HTML Templates
│   ├── index.html                  # Main page (form + table)
│   ├── dashboard.html              # Dashboard monitoring
│   ├── pesankeluar.html           # Outgoing messages
│   ├── edit_chat.html             # Template editor
│   ├── db.html                     # Database view
│   ├── api.html                    # API docs
│   └── login.html                  # WhatsApp login
│
├── 📁 static/                      # Static files
│   ├── css/                        # Stylesheets
│   │   ├── design-system.css      # Design tokens
│   │   ├── components.css         # UI components
│   │   └── utilities.css          # Utility classes
│   └── uploads/                    # User uploads (gitignored)
│
├── 📁 scheduler/                   # Background tasks
│   ├── integrated_scheduler.py    # APScheduler setup
│   └── auto_send.py               # Auto-send logic
│
├── whatsapp_reminder_app.py        # Flask app (SQLite)
├── whatsapp_reminder_app_mysql.py  # Flask app (MySQL)
├── migrate_to_mysql.py             # Migration script
├── .env                            # Environment vars (gitignored)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation
```

## 🔄 Workflow Aplikasi

### 1. Input Data Reminder

```mermaid
User Input → Validate → Save to Database → Display in Table
```

1. User mengisi form di halaman utama
2. Data divalidasi (nama, nomor kendaraan, tanggal uji, dll)
3. Nomor WhatsApp diformat otomatis (62xxx)
4. Data disimpan ke database
5. Tabel di-refresh untuk menampilkan data baru

### 2. Kirim Reminder Manual

```mermaid
User Click → Build Message → Call WhatsApp Bot → Log Status → Update UI
```

1. User klik tombol "Kirim" pada salah satu reminder
2. System membuat pesan berdasarkan template aktif
3. Pesan dikirim ke WhatsApp Bot via HTTP POST
4. Bot mengirim pesan via WhatsApp Web
5. Status (sent/failed) dicatat di database
6. UI di-update dengan status terbaru

### 3. Kirim Otomatis (Scheduler)

```mermaid
Cron Job (12:00 WIB) → Check Due Reminders → Send Messages → Log Results
```

1. APScheduler trigger setiap hari jam 12:00 WIB
2. System query semua reminder yang jatuh tempo hari ini
3. Loop setiap reminder:
   - Build message dari template
   - Kirim via WhatsApp Bot
   - Log status ke database
4. Generate report (opsional)

### 4. Dashboard Monitoring

```mermaid
Request Dashboard → Fetch Stats → Render Charts → Display Metrics
```

1. User akses `/dashboard`
2. Backend query statistik:
   - Pesan keluar hari ini
   - User aktif
   - Pesan per hari (30 hari)
   - Pesan per bulan (12 bulan)
3. Frontend render grafik dengan Chart.js
4. Auto-refresh setiap 60 detik

### 5. Edit Template Pesan

```mermaid
Load Template → Edit Content → Save → Apply to Future Messages
```

1. User akses `/edit_chat`
2. Load template aktif dari database
3. User edit template dengan placeholder: `{{name}}`, `{{vehicle_number}}`, dll
4. Save template baru ke database
5. Deactivate template lama
6. Template baru digunakan untuk pesan selanjutnya

## 🔌 API Endpoints

### Reminder Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main page (form + table) |
| POST | `/add` | Add new reminder |
| GET | `/list` | List all reminders |
| PUT | `/edit/<id>` | Edit reminder |
| DELETE | `/delete/<id>` | Delete reminder |
| DELETE | `/clear` | Clear all reminders |
| POST | `/send_one/<id>` | Send single reminder |
| POST | `/run_now` | Send all due reminders |
| PUT | `/mark_tested/<id>` | Mark as tested |

### Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Dashboard page |
| GET | `/pesankeluar` | Outgoing messages page |
| GET | `/api/stats` | Get statistics (in/out/users) |
| GET | `/api/user_count` | Get total users |
| GET | `/api/messages/outgoing` | Get all outgoing messages |
| GET | `/api/messages_timeseries` | Get message timeseries |

### Template Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/edit_chat` | Template editor page |
| GET | `/api/template` | Get active template |
| POST | `/api/template` | Save new template |
| POST | `/api/template/reset` | Reset to default template |
| GET | `/api/template/history` | Get template history |

### WhatsApp Bot

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/qr` | Get QR code JSON |
| GET | `/qr-stream` | QR code SSE stream |
| POST | `/send` | Send WhatsApp message |
| DELETE | `/reset-auth` | Reset WhatsApp session |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-avatar` | Upload user avatar |
| POST | `/reset-auth` | Reset WhatsApp auth |

## 📝 Contoh Request

### Add Reminder

```bash
curl -X POST http://127.0.0.1:5000/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "vehicle_number": "B 1234 CD",
    "no_uji": "SLO 6798/123",
    "jenis_kendaraan": "Truck",
    "test_date": "2026-06-20",
    "phone": "81234567890"
  }'
```

### Send WhatsApp Message

```bash
curl -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "6281234567890",
    "message": "Halo, ini pesan reminder dari Dishub"
  }'
```

### Get Statistics

```bash
curl http://127.0.0.1:5000/api/stats
```

Response:
```json
{
  "in": 5,
  "out": 120,
  "users": 45
}
```

## 🐛 Troubleshooting

### Problem: "Waiting for this message" di WhatsApp

**Penyebab:**
- Session WhatsApp tidak sinkron (PreKey error)
- Multi-device conflict (ada device lain yang login bersamaan)
- Network latency saat handshake encryption

**Solusi Permanen:**

1. **Upgrade Baileys ke versi terbaru:**
```bash
cd wa-bot
npm install @whiskeysockets/baileys@latest
```

2. **Implementasi Retry Logic (Sudah diterapkan):**
- Bot akan auto-retry 3x dengan delay 2 detik
- Encryption error akan retry dengan delay 5 detik
- Pre-send validation untuk memastikan koneksi siap

3. **Rate Limiting (Sudah diterapkan):**
- Delay 3 detik antar pesan untuk avoid spam
- Timeout dinaikkan ke 60 detik

4. **Auto-Repair Session (Sudah diterapkan):**
- Bot akan auto-refresh encryption keys setelah 5 error berturut-turut
- Force reconnect untuk refresh session

5. **Reset Auth jika masih gagal:**
```bash
# Stop bot
pm2 stop wa-bot
# atau Ctrl+C jika manual

# Hapus session lama
cd wa-bot
rm -rf auth_info  # Linux/Mac
# atau
rmdir /s /q auth_info  # Windows

# Start ulang
node index.js
# Scan QR dari Linked Devices di HP (BUKAN WhatsApp Web biasa!)
```

### Problem: Conflict Error (440 Stream Errored)

**Penyebab:**
Ada 2+ koneksi WhatsApp aktif bersamaan menggunakan session yang sama.

**Diagnosis:**
```bash
# Windows - Cek berapa bot yang jalan
tasklist | findstr node.exe

# Linux/Mac
ps aux | grep node
```

**Solusi:**

1. **Pastikan hanya 1 bot yang jalan:**
```bash
# Stop semua process
pm2 stop all
pm2 delete all

# Kill manual process (Windows)
taskkill /F /PID <PID_NUMBER>

# Kill manual process (Linux/Mac)
kill -9 <PID_NUMBER>

# Cek bersih
tasklist | findstr node.exe  # Windows
ps aux | grep node           # Linux/Mac
# Harusnya kosong!
```

2. **Logout semua Linked Devices:**
- Buka WhatsApp di HP
- Menu → **Linked Devices**
- **Logout SEMUA device** yang ada
- Tunggu 30 detik

3. **Start 1 bot saja:**
```bash
# Pilih salah satu:

# Option A: Manual (untuk development/debugging)
cd wa-bot
node index.js

# Option B: PM2 (untuk production)
pm2 start ecosystem.config.cjs
```

4. **Scan QR dengan benar:**
- Buka http://localhost:3000
- Scan dari **Linked Devices** di HP (BUKAN WhatsApp Web!)
- Scan **1x saja**, jangan berkali-kali

**Aturan Ketat:**
- ❌ JANGAN jalankan `node index.js` DAN `pm2 start` bersamaan
- ❌ JANGAN buka multiple tabs localhost:3000
- ❌ JANGAN scan QR berkali-kali
- ❌ JANGAN buka WhatsApp Web di browser lain saat bot jalan
- ✅ Pilih 1 cara saja: manual ATAU PM2

### Problem: WhatsApp Bot tidak connect

**Solusi:**
1. Pastikan Node.js version >= 18
2. Hapus folder `wa-bot/auth_info`
3. Restart bot: `node index.js`
4. Scan QR code baru

### Problem: Database connection error (MySQL)

**Solusi:**
```bash
# Cek MySQL service
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql

# Cek credentials di .env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
```

### Problem: Port already in use

**Solusi:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Problem: Module not found

**Solusi:**
```bash
# Reinstall Python dependencies
pip install -r requirements.txt

# Reinstall Node dependencies
cd wa-bot
npm install
```

### Problem: Timeout error saat init queries

**Solusi:**
- Sudah ditangani dengan auto-retry dan increased timeout
- Bot akan otomatis reconnect dengan exponential backoff
- Jika gagal 5x, akan auto-reset auth dan generate QR baru

### Problem: Template tidak terupdate

**Solusi:**
1. Akses `/edit_chat`
2. Klik "Reset ke Template Default"
3. Atau hapus template dari database:
```sql
DELETE FROM chat_templates WHERE is_active = 1;
```

### Problem: QR Code Spam di Log

**Penyebab:**
Event QR triggered multiple kali sebelum scan.

**Solusi:**
Sudah di-fix dengan debounce logic. QR hanya akan muncul 1x di log. Abaikan saja atau tunggu sampai scan QR.

### Problem: PM2 tidak ditemukan

**Solusi:**
```bash
# Install PM2 global
npm install -g pm2

# Verifikasi instalasi
pm2 --version
```

## 🔒 Security Best Practices

1. **Jangan commit file sensitif:**
   - `.env` file
   - `wa-bot/auth_info/`
   - `*.db` files
   - User uploads

2. **Gunakan environment variables:**
   - Database credentials
   - API keys
   - Secret keys

3. **Update dependencies secara berkala:**
```bash
pip list --outdated
npm outdated
```

4. **Gunakan HTTPS untuk production:**
   - Setup SSL certificate
   - Use reverse proxy (Nginx)

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 License

Project ini menggunakan MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 👥 Tim Pengembang

- **Developer** - [Nowell](https://github.com/nowelliswell)

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Baileys](https://github.com/WhiskeySockets/Baileys) - WhatsApp Web API
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Chart.js](https://www.chartjs.org/) - Data visualization
- [SweetAlert2](https://sweetalert2.github.io/) - Beautiful alerts

---

**🚀 Happy Coding!** Jika ada pertanyaan, silakan buat [issue](https://github.com/nowelliswell/dishub-reminder/issues) di repository ini.
