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
AUTH_DIR = "wa-bot/auth_info"  # Folder auth yang digunakan Node.js

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
        con.execute('''CREATE TABLE IF NOT EXISTS chat_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT NOT NULL,
            template_content TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )''')
        
        # Insert default template if not exists
        count = con.execute("SELECT COUNT(*) FROM chat_templates").fetchone()[0]
        if count == 0:
            default_template = """🚗 Halo Sdr/i {nama} (sesuai STNK) 

📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {nomor_kendaraan} 
🔢 Nomor Uji : {no_uji} 
🚛 Jenis Kendaraan : {jenis_kendaraan} 
📆 Tanggal Uji Kendaraan: {tanggal_uji}

⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.
✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan. 
🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan
⏰ Harap hadir sesuai jadwal 

🙏 Terima Kasih - Dishub Kota Surakarta"""
            now = datetime.utcnow().isoformat()
            con.execute(
                "INSERT INTO chat_templates (template_name, template_content, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                ("Default Template", default_template, 1, now, now)
            )

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
    elif days_until == 2:
        return "H-2", "info"           # Biru
    elif days_until > 2:
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

def get_active_template():
    """Get active chat template from database"""
    try:
        with get_db_connection() as con:
            row = con.execute("SELECT template_content FROM chat_templates WHERE is_active = 1 ORDER BY updated_at DESC LIMIT 1").fetchone()
            if row:
                return row['template_content']
    except Exception as e:
        print(f"❌ Error getting template: {e}")
    
    # Fallback to default if no template found
    return """🚗 Halo Sdr/i {nama} (sesuai STNK) 

📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {nomor_kendaraan} 
🔢 Nomor Uji : {no_uji} 
🚛 Jenis Kendaraan : {jenis_kendaraan} 
📆 Tanggal Uji Kendaraan: {tanggal_uji}

⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.
✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan. 
🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan
⏰ Harap hadir sesuai jadwal 

🙏 Terima Kasih - Dishub Kota Surakarta"""

def save_template(template_content, template_name="Custom Template"):
    """Save chat template to database"""
    try:
        with get_db_connection() as con:
            now = datetime.utcnow().isoformat()
            # Deactivate all templates
            con.execute("UPDATE chat_templates SET is_active = 0")
            # Insert new active template
            con.execute(
                "INSERT INTO chat_templates (template_name, template_content, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (template_name, template_content, 1, now, now)
            )
            return True
    except Exception as e:
        print(f"❌ Error saving template: {e}")
        return False

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
    """Build message from template with variable replacement"""
    template = get_active_template()
    
    # Replace variables in template
    message = template.replace("{nama}", str(record.get('name', '')))
    message = message.replace("{nomor_kendaraan}", str(record.get('vehicle_number', '')))
    message = message.replace("{no_uji}", str(record.get('no_uji', '')))
    message = message.replace("{jenis_kendaraan}", str(record.get('jenis_kendaraan', '')))
    message = message.replace("{tanggal_uji}", str(record.get('test_date', '')))
    
    return message

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

def send_automatic_reminders():
    """
    Send automatic reminders for H-1 and H-2 at 12:00 WIB noon.
    This function is called by the scheduler and sends messages
    for reminders that are exactly 1 or 2 days before expiration.
    """
    from datetime import datetime, timezone, timedelta

    # Get current time in WIB (UTC+7)
    wib_timezone = timezone(timedelta(hours=7))
    current_time = datetime.now(wib_timezone)

    print(f"🕐 Current time (WIB): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    today = current_time.date()
    reminders = list_reminders()
    sent_count = 0
    failed_count = 0

    print(f"📋 Found {len(reminders)} total reminders in database")

    for reminder in reminders:
        test_date = datetime.strptime(reminder['test_date'], '%Y-%m-%d').date()
        days_until = (test_date - today).days

        # Only send for H-1 (days_until == 1) and H-2 (days_until == 2)
        if days_until in [1, 2]:
            status_label, _ = classify_by_days(days_until)
            message = build_message(reminder, status_label)
            phone = normalize_phone(reminder.get('phone') or "")

            if not phone:
                print(f"⚠️ [{status_label}] No phone number for {reminder['name']}, skipping.")
                continue

            print(f"📤 [{status_label}] Sending to {reminder['name']} ({reminder['vehicle_number']}) at {phone}")
            send_result = send_whatsapp_message(phone, message)

            if send_result.get('status') == 'sent via Node API':
                sent_count += 1
                print(f"✅ [{status_label}] Automatic reminder sent to {reminder['name']} ({reminder['vehicle_number']})")
            else:
                failed_count += 1
                print(f"❌ [{status_label}] Failed to send automatic reminder to {reminder['name']} ({reminder['vehicle_number']})")
                print(f"   Error details: {send_result}")

    print(f"📊 Summary: {sent_count} sent, {failed_count} failed")

    return {
        "status": "completed",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "timestamp": current_time.isoformat()
    }

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

@app.route('/pesankeluar', methods=['GET'])
def pesankeluar():
    return render_template('pesankeluar.html')

@app.route('/edit_chat', methods=['GET'])
def edit_chat():
    return render_template('edit_chat.html')

# ----------------- CHAT TEMPLATE endpoints -----------------
@app.route('/api/template', methods=['GET'])
def get_template():
    """Get active chat template"""
    template = get_active_template()
    return jsonify({"template": template, "status": "ok"})

@app.route('/api/template', methods=['POST'])
def save_template_api():
    """Save chat template"""
    data = request.get_json(force=True)
    template_content = data.get('template')
    template_name = data.get('name', 'Custom Template')
    
    if not template_content:
        return jsonify({"status": "error", "message": "Template content is required"}), 400
    
    success = save_template(template_content, template_name)
    
    if success:
        return jsonify({"status": "ok", "message": "Template saved successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to save template"}), 500

@app.route('/api/template/history', methods=['GET'])
def get_template_history():
    """Get template history"""
    try:
        with get_db_connection() as con:
            rows = con.execute(
                "SELECT id, template_name, is_active, created_at, updated_at FROM chat_templates ORDER BY updated_at DESC LIMIT 10"
            ).fetchall()
            templates = []
            for row in rows:
                templates.append({
                    "id": row['id'],
                    "name": row['template_name'],
                    "is_active": bool(row['is_active']),
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                })
            return jsonify({"templates": templates, "status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

@app.route('/api/sent_messages', methods=['GET', 'DELETE'])
def api_sent_messages():
    if request.method == 'DELETE':
        # Clear all messages
        with get_db_connection() as con:
            con.execute("DELETE FROM messages")
            con.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
        return jsonify({"message": "All messages cleared"})

    # GET: return list of sent messages
    with get_db_connection() as con:
        rows = con.execute("SELECT * FROM messages WHERE direction='out' ORDER BY created_at DESC").fetchall()
        messages = []
        for row in rows:
            r = dict(row)
            messages.append({
                "id": r["id"],
                "phone": r["phone"],
                "message": r["message"],
                "status": r["status"],
                "timestamp": r["created_at"]
            })
        return jsonify(messages)

@app.route('/api/message_stats', methods=['GET'])
def api_message_stats():
    # Return counts for success, pending, failed
    with get_db_connection() as con:
        success = con.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND status LIKE '%sent%' OR status LIKE '%success%' OR status LIKE '%delivered%'").fetchone()[0]
        pending = con.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND status LIKE '%pending%' OR status LIKE '%sending%' OR status LIKE '%queued%'").fetchone()[0]
        failed = con.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND status LIKE '%failed%' OR status LIKE '%error%' OR status LIKE '%blocked%'").fetchone()[0]
    return jsonify({"success": success, "pending": pending, "failed": failed})

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
    """Hapus folder auth agar QR baru bisa muncul. Redirect ke Node.js untuk reset."""
    try:
        # Hit Node.js API untuk reset auth
        node_reset_url = "http://localhost:3000/reset-auth"
        response = requests.delete(node_reset_url, timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                "status": "ok", 
                "message": "Auth berhasil direset. Silakan scan QR baru.",
                "redirect": "/login.html"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Gagal reset auth di Node.js"
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- MAIN -----------------
if __name__ == "__main__":
    import threading
    from scheduler.auto_send import main as scheduler_main

    init_db()
    print('Database initialized (reminders.db).')

    # Start the automatic reminder scheduler in a separate thread
    scheduler_thread = threading.Thread(target=scheduler_main, daemon=True)
    scheduler_thread.start()
    print('🚀 Automatic reminder scheduler started in background.')

    print('Available endpoints:')
    print('  POST /add')
    print('  GET  /list')
    print('  POST /run_now')
    print('  DELETE /clear')
    print('  POST /upload-avatar')
    print('  POST /reset-auth')
    print('  GET /api/stats')
    print('  GET /api/messages_timeseries?period=day|month')

    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask app stopped by user.")
