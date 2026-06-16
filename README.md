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

### Cara 1: Manual (Development)

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

### Cara 2: Production dengan PM2

```bash
# Install PM2 globally
npm install -g pm2

# Start WhatsApp Bot
cd wa-bot
pm2 start index.js --name "wa-bot"

# Start Flask App
cd ..
pm2 start --name "flask-app" --interpreter python3 -- whatsapp_reminder_app_mysql.py

# Lihat status
pm2 status

# Lihat logs
pm2 logs

# Save configuration
pm2 save
pm2 startup
```

### Cara 3: Menggunakan Screen (Linux)

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
