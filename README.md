# dishub-reminder
🚦 WhatsApp Reminder System - Dishub

Sistem pengingat uji kendaraan dengan Flask + SQLite + Bootstrap.
Dilengkapi form input, tabel reminder, kirim otomatis via WhatsApp, dan manajemen dashboard dengan SweetAlert.

📂 Struktur Project
project-folder/
│── app.py              # Main Flask backend
│── templates/          # HTML (dashboard, login, dll.)
│── static/             # CSS, JS, icons
│── database.db         # SQLite database
│── README.md           # Dokumentasi

⚙️ Requirements

Python 3.9+

Node.js (jika pakai Baileys/WA bot)

pipenv / venv

Python packages:

pip install flask flask-cors

▶️ Cara Menjalankan

Clone repo:

git clone https://github.com/username/repo.git
cd repo


Jalankan backend Flask:

python app.py


App akan jalan di: http://127.0.0.1:5000/

(Opsional) Jalankan WA bot (Node.js):

node index.js


Endpoint reset-auth: http://localhost:3000/reset-auth

✨ Fitur

Tambah & simpan reminder

Auto-format nomor WhatsApp

Kirim 1 reminder / semua reminder

Reset login WhatsApp

UI modern (Bootstrap + SweetAlert2)
