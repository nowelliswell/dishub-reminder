# backend.py
import os
import sqlite3
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import shutil
from werkzeug.utils import secure_filename

load_dotenv()

DB_PATH = 'reminders.db'
NODE_API = os.getenv("NODE_API_URL", "http://localhost:3000/send")  # Node API endpoint

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 🔑 Lokasi auth session WA (sesuaikan dengan Node.js)
AUTH_FILE = "auth_info.json"   # kalau Node.js simpan JSON auth
AUTH_DIR = "session"           # kalau Node.js pakai folder session

UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------------- DATABASE -----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            no_uji TEXT,
            jenis_kendaraan TEXT,
            test_date TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL
        )''')
        con.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction TEXT NOT NULL, -- 'in' or 'out'
            phone TEXT,
            message TEXT,
            status TEXT,
            meta TEXT,
            created_at TEXT NOT NULL
        )''')

# ----------------- HELPERS -----------------
def add_reminder(name, nik, vehicle_number, test_date, phone=None):
    # pastikan test_date selalu format YYYY-MM-DD
    try:
        test_date = datetime.strptime(test_date.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception:
        raise ValueError("❌ Format test_date harus YYYY-MM-DD")

    # Ambil no_uji dan jenis_kendaraan dari kwargs jika ada
    no_uji = None
    jenis_kendaraan = None
    if isinstance(phone, dict):
        no_uji = phone.get('no_uji')
        jenis_kendaraan = phone.get('jenis_kendaraan')
        phone = phone.get('phone')

    with get_db_connection() as con:
        con.execute(
            'INSERT INTO reminders (name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, datetime.utcnow().isoformat())
        )

def list_reminders():
    with get_db_connection() as con:
        rows = con.execute('SELECT * FROM reminders ORDER BY test_date').fetchall()
        results = []
        today = date.today()
        for row in rows:
            r = dict(row)
            raw_date = str(r['test_date']).split()[0]
            try:
                test_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            except:
                continue
            days_until = (test_date - today).days
            status_label, color = classify_by_days(days_until)
            r['status'] = status_label
            r['color'] = color
            r['days_until'] = days_until  # penting untuk frontend filter
            r['test_date'] = test_date.strftime("%Y-%m-%d")  # normalisasi
            results.append(r)
        return results

def classify_by_days(days_until):
    if days_until == 0:
        return "H (today)", "danger"  # Merah
    elif days_until == 1:
        return "H-1", "warning"        # Kuning
    elif days_until >= 2:
        return "H-3 or more", "success" # Hijau
    else:
        return "Expired", "secondary"  # Abu-abu

def normalize_phone(phone: str) -> str:
    """Pastikan nomor WA selalu format internasional (62xxx tanpa + for Node maybe)"""
    if not phone:
        return ""
    phone = phone.strip().replace(" ", "").replace("-", "")
    # Sesuaikan format sesuai Node API yang kamu gunakan. Di sini kita return tanpa +
    if phone.startswith("+62"):
        return phone[1:]
    elif phone.startswith("62"):
        return phone
    elif phone.startswith("0"):
        return "62" + phone[1:]
    elif phone.startswith("8"):
        return "62" + phone
    return phone

def log_message(direction, phone, message_text, status="unknown", meta=None):
    try:
        with get_db_connection() as con:
            con.execute(
                "INSERT INTO messages (direction, phone, message, status, meta, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (direction, phone, message_text, status, (meta or ""), datetime.utcnow().isoformat())
            )
    except Exception as e:
        print("❌ Gagal log message:", e)

def build_message(record, status_label):
    return (
        f"🚗 Halo Sdr/i {record['name']} (sesuai STNK) \n\n"
        f"📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {record['vehicle_number']} \n"
        f"🔢 Nomor Uji : {record['no_uji']} \n"
        f"🚛 Jenis Kendaraan : {record['jenis_kendaraan']} \n"
        f"📆 Tanggal Uji Kendaraan: {record['test_date']}\n\n"
        f"⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.\n"
        f"✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan. \n"
        f"🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan\n"
        f"⏰ Harap hadir sesuai jadwal \n\n"
        f"🙏 Terima Kasih - Dishub Kota Surakarta\n"
    )

def send_whatsapp_message(phone, message_text):
    """Kirim ke Node API. Return dict berisi status dan info. Juga log ke DB messages."""
    phone_norm = normalize_phone(phone)
    try:
        payload = {"phone": phone_norm, "message": message_text}
        print(f"📤 Sending to Node API {NODE_API} payload={payload}")
        r = requests.post(NODE_API, json=payload, timeout=10)
        print("📥 Response:", r.status_code, r.text)
        try:
            resp_json = r.json()
        except Exception:
            resp_json = {"raw_text": r.text}
        if r.status_code == 200:
            result = {"status": "sent via Node API", "response": resp_json}
            log_message("out", phone_norm, message_text, status="sent", meta=str(resp_json))
            return result
        else:
            log_message("out", phone_norm, message_text, status="failed", meta=str(resp_json))
            return {"status": "failed", "error": resp_json}
    except Exception as e:
        print("❌ Exception:", str(e))
        log_message("out", phone_norm, message_text, status="error", meta=str(e))
        return {"status": "error", "error": str(e)}

def run_now_check(as_of_date=None):
    today = date.today() if as_of_date is None else datetime.strptime(as_of_date, '%Y-%m-%d').date()
    results = list_reminders()
    actions = []
    for r in results:
        test_date = datetime.strptime(r['test_date'], '%Y-%m-%d').date()
        days_until = (test_date - today).days
        status_label, color = classify_by_days(days_until)
        if days_until >= 0:
            msg = build_message(r, status_label)
            phone = normalize_phone(r.get('phone') or "")
            send_result = send_whatsapp_message(phone, msg)
            actions.append({
                'id': r['id'],
                'name': r['name'],
                'vehicle_number': r['vehicle_number'],
                'test_date': r['test_date'],
                'days_until': days_until,
                'status': status_label,
                'color': color,
                'send_result': send_result
            })
            print(f"[{status_label}] Reminder sent to {r['name']} ({r['vehicle_number']}) → {send_result.get('status')}")
    return actions

# ----------------- ROUTES -----------------

@app.route("/", methods=["GET"])
def api_home():
    if request.args.get("format") == "json" or request.accept_mimetypes.best == 'application/json':
        return jsonify({
            "message": "WhatsApp Reminder API is running!",
            "available_endpoints": {
                "POST /add": "Add new reminder",
                "GET /list": "Get list of reminders",
                "POST /run_now": "Run reminders manually",
                "DELETE /clear": "Clear all reminders and reset IDs",
                "POST /upload-avatar": "Upload user avatar",
                "GET /api/stats": "Stats (in/out/users)",
                "GET /api/messages_timeseries": "messages timeseries (period=day|month)"
            }
        })
    return render_template("api.html")

@app.route("/add", methods=["POST"])
def http_add():
    data = request.get_json(force=True)
    required = ['name', 'vehicle_number', 'test_date', 'no_uji', 'jenis_kendaraan']
    for k in required:
        if k not in data:
            return jsonify({'error': f'missing field {k}'}), 400
    try:
        datetime.strptime(data['test_date'], '%Y-%m-%d')
    except Exception:
        return jsonify({'error': 'test_date must be YYYY-MM-DD'}), 400
    phone = data.get('phone') or ""
    no_uji = data.get('no_uji')
    jenis_kendaraan = data.get('jenis_kendaraan')
    add_reminder(data['name'], None, data['vehicle_number'], data['test_date'], {
        'phone': phone,
        'no_uji': no_uji,
        'jenis_kendaraan': jenis_kendaraan
    })
    return jsonify({'status': 'ok'})

@app.route("/delete/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted", "id": reminder_id})

@app.route("/send_one/<int:reminder_id>", methods=["POST"])
def send_one(reminder_id):
    with get_db_connection() as con:
        row = con.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
        if not row:
            return jsonify({"error": "Reminder tidak ditemukan"}), 404

        reminder = dict(row)
        message = build_message(reminder, "manual")
        phone = normalize_phone(reminder.get('phone') or "")
        send_result = send_whatsapp_message(phone, message)

        return jsonify({
            "id": reminder_id,
            "status": send_result.get('status'),
            "detail": send_result
        })

@app.route('/clear', methods=['DELETE'])
def clear_reminders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Hapus semua data
    c.execute("DELETE FROM reminders")
    # Reset autoincrement (SQLite pakai sqlite_sequence)
    c.execute("DELETE FROM sqlite_sequence WHERE name='reminders'")
    conn.commit()
    conn.close()
    return jsonify({"message": "Semua data terhapus dan ID direset ke 1"})

@app.route('/list', methods=['GET'])
def list_reminders_route():
    reminders = list_reminders()
    if request.args.get("format") == "json":
        return jsonify(reminders)
    return render_template("db.html", reminders=reminders)

@app.route("/edit/<int:reminder_id>", methods=["PUT"])
def edit_reminder(reminder_id):
    data = request.get_json(force=True)
    try:
        with get_db_connection() as con:
            con.execute("""
                UPDATE reminders 
                SET name=?, vehicle_number=?, no_uji=?, jenis_kendaraan=?, test_date=?, phone=? 
                WHERE id=?
            """, (
                data.get("name"),
                data.get("vehicle_number"),
                data.get("no_uji"),
                data.get("jenis_kendaraan"),
                data.get("test_date"),
                data.get("phone"),
                reminder_id
            ))
        return jsonify({"status": "updated", "id": reminder_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run_now', methods=['POST'])
def http_run_now():
    data = request.get_json(silent=True) or {}
    actions = run_now_check(as_of_date=data.get('as_of'))
    return jsonify(actions)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

# ----------------- STAT endpoints -----------------
@app.route('/api/stats', methods=['GET'])
def api_stats():
    # in = pesan masuk hari ini, out = pesan keluar hari ini, users = jumlah rows reminders
    today = datetime.utcnow().date().isoformat()
    with get_db_connection() as con:
        in_count = con.execute("SELECT COUNT(*) FROM messages WHERE direction='in' AND date(created_at)=?", (today,)).fetchone()[0]
        out_count = con.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND date(created_at)=?", (today,)).fetchone()[0]
        users = con.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]
    return jsonify({"in": in_count, "out": out_count, "users": users})

@app.route('/api/user_count', methods=['GET'])
def api_user_count():
    with get_db_connection() as con:
        users = con.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]
    return jsonify({"users": users})

@app.route('/api/messages_timeseries', methods=['GET'])
def api_messages_timeseries():
    """
    Query params:
      period=day|month (default day)
      days=30 (for period=day)
      months=12 (for period=month)
    Returns JSON:
      { labels: [...], data: [...] }
    """
    period = request.args.get('period', 'day')
    if period == 'month':
        months = int(request.args.get('months', 12))
        with get_db_connection() as con:
            # last N months including this one
            rows = con.execute("""
                SELECT strftime('%Y-%m', created_at) as period, COUNT(*) as cnt
                FROM messages
                WHERE direction='out' AND date(created_at) >= date('now','start of month', ?)
                GROUP BY period
                ORDER BY period
            """, (f"-{months-1} months",)).fetchall()
        labels = []
        data = []
        # build ordered list of last months
        from datetime import datetime
        now = datetime.utcnow()
        months_list = []
        for i in range(months-1, -1, -1):
            m = (now.replace(day=1) - __import__('datetime').timedelta(days=0)).month  # dummy to satisfy style
        # simpler build using relativedelta isn't available; use loop:
        months_list = []
        for i in range(months-1, -1, -1):
            dt = datetime(now.year, now.month, 1)
            # subtract i months:
            y = dt.year
            m = dt.month - i
            while m <= 0:
                m += 12
                y -= 1
            months_list.append(f"{y:04d}-{m:02d}")
        rowdict = {r['period']: r['cnt'] for r in rows}
        for m in months_list:
            labels.append(m)
            data.append(rowdict.get(m, 0))
        return jsonify({"labels": labels, "data": data})

    else:
        days = int(request.args.get('days', 30))
        with get_db_connection() as con:
            rows = con.execute("""
                SELECT date(created_at) as day, COUNT(*) as cnt
                FROM messages
                WHERE direction='out' AND date(created_at) >= date('now', ?)
                GROUP BY day
                ORDER BY day
            """, (f"-{days-1} days",)).fetchall()
        labels = []
        data = []
        # build list of last days (YYYY-MM-DD)
        from datetime import timedelta, datetime
        today = datetime.utcnow().date()
        days_list = [(today - timedelta(days=i)).isoformat() for i in range(days-1, -1, -1)]
        rowdict = {r['day']: r['cnt'] for r in rows}
        for d in days_list:
            labels.append(d)
            data.append(rowdict.get(d, 0))
        return jsonify({"labels": labels, "data": data})

# ----------------- UPLOAD AVATAR -----------------
@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    # Simpan sebagai avatar.png (overwrite)
    filename = secure_filename("avatar.png")
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    return jsonify({"status": "ok", "path": f"/static/uploads/{filename}"}), 200

# ----------------- RESET AUTH WA -----------------
@app.route("/reset-auth", methods=["POST"])
def reset_auth():
    """Hapus file atau folder auth agar QR baru bisa muncul."""
    try:
        removed = []
        if os.path.exists(AUTH_FILE):
            os.remove(AUTH_FILE)
            removed.append(AUTH_FILE)

        if os.path.exists(AUTH_DIR):
            shutil.rmtree(AUTH_DIR)
            removed.append(AUTH_DIR)

        if not removed:
            return jsonify({"status": "ok", "message": "Tidak ada auth file untuk dihapus."})

        return jsonify({"status": "ok", "message": f"Auth info dihapus: {', '.join(removed)}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ----------------- MAIN -----------------
if __name__ == "__main__":
    init_db()
    print('Database initialized (reminders.db).')
    print('Available endpoints:')
    print('  POST /add')
    print('  GET  /list')
    print('  POST /run_now')
    print('  DELETE /clear')
    print('  POST /upload-avatar')
    print('  POST /reset-auth')
    print('  GET /api/stats')
    print('  GET /api/messages_timeseries?period=day|month')
    app.run(host="0.0.0.0", port=5000, debug=True)
