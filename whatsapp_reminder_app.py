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
            # no_uji dan jenis_kendaraan sudah otomatis ada di r
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
        f"⏰ Harap hadir sesuai jadwal \n"
        f"🙏 Terima Kasih - Dishub Kota Surakarta\n"
    )

def send_whatsapp_message(phone, message_text):
    """Kirim ke Node API. Return dict berisi status dan info."""
    try:
        payload = {"phone": phone, "message": message_text}
        print(f"📤 Sending to Node API {NODE_API} payload={payload}")
        r = requests.post(NODE_API, json=payload, timeout=10)
        print("📥 Response:", r.status_code, r.text)
        # coba parse json kalau bisa
        try:
            resp_json = r.json()
        except Exception:
            resp_json = {"raw_text": r.text}
        if r.status_code == 200:
            return {"status": "sent via Node API", "response": resp_json}
        else:
            return {"status": "failed", "error": resp_json}
    except Exception as e:
        print("❌ Exception:", str(e))
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
            print(f"[{status_label}] Reminder sent to {r['name']} ({r['vehicle_number']}) → {send_result['status']}")
    return actions

# ----------------- ROUTES -----------------

@app.route("/", methods=["GET"])
def api_home():
    """Jika client minta JSON (atau param ?format=json) kembalikan JSON.
       Jika diakses lewat browser biasa render template api.html (landing page)."""
    if request.args.get("format") == "json" or request.accept_mimetypes.best == 'application/json':
        return jsonify({
            "message": "WhatsApp Reminder API is running!",
            "available_endpoints": {
                "POST /add": "Add new reminder",
                "GET /list": "Get list of reminders",
                "POST /run_now": "Run reminders manually",
                "DELETE /clear": "Clear all reminders and reset IDs",
                "POST /upload-avatar": "Upload user avatar"
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

        message = (
            f"🚗 Halo Sdr/i {reminder['name']} (sesuai STNK) \n\n"
            f"📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {reminder['vehicle_number']} \n"
            f"🔢 Nomor Uji : {reminder['no_uji']} \n"
            f"🚛 Jenis Kendaraan : {reminder['jenis_kendaraan']} \n"
            f"📆 Tanggal Uji Kendaraan: {reminder['test_date']}\n\n"
            f"⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.\n"
            f"✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan. \n"
            f"🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan\n"
            f"⏰ Harap hadir sesuai jadwal \n"
            f"🙏 Terima Kasih - Dishub Kota Surakarta\n"
        )

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
    app.run(host="0.0.0.0", port=5000, debug=True)
