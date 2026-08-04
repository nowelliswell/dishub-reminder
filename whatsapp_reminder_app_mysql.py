# backend.py - MySQL Version
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from datetime import datetime, date
import re
from scheduler.integrated_scheduler import init_scheduler
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import shutil
from werkzeug.utils import secure_filename

# Try import MySQL library
try:
    import mysql.connector
    MYSQL_LIB = 'mysql.connector'
except ImportError:
    try:
        import pymysql
        MYSQL_LIB = 'pymysql'
    except ImportError:
        print("❌ Error: Tidak ada library MySQL terinstall!")
        print("💡 Install salah satu:")
        print("   pip install mysql-connector-python")
        print("   atau")
        print("   pip install pymysql")
        exit(1)

load_dotenv(override=True)

# ========== MYSQL CONFIG ==========
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'dishub_reminder'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

NODE_API = os.getenv("NODE_API_URL", "http://localhost:3000/send")

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

AUTH_FILE = "auth_info.json"
AUTH_DIR = "session"

UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------------- DATABASE -----------------
def get_db_connection():
    """Koneksi ke MySQL"""
    if MYSQL_LIB == 'mysql.connector':
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:  # pymysql
        return pymysql.connect(**MYSQL_CONFIG)

def init_db():
    """Inisialisasi database dan tabel (jika belum ada)"""
    # Buat database jika belum ada
    db_name = MYSQL_CONFIG.get('database', 'dishub_reminder')
    config_without_db = MYSQL_CONFIG.copy()
    config_without_db.pop('database', None)
    
    try:
        if MYSQL_LIB == 'mysql.connector':
            conn = mysql.connector.connect(**config_without_db)
        else:
            conn = pymysql.connect(**config_without_db)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cursor.close()
        conn.close()
        print(f"✅ Database '{db_name}' siap/terbuat.")
    except Exception as e:
        print(f"⚠️ Warning: Gagal membuat database '{db_name}' secara otomatis: {e}")
        print("💡 Mencoba melanjutkan koneksi langsung...")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        vehicle_number VARCHAR(100) NOT NULL,
        no_uji VARCHAR(100),
        jenis_kendaraan VARCHAR(100),
        test_date DATE NOT NULL,
        phone VARCHAR(20),
        is_tested TINYINT(1) DEFAULT 0,
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
    
    # Add is_tested column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE reminders ADD COLUMN is_tested TINYINT(1) DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # Column already exists
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        direction VARCHAR(10) NOT NULL,
        phone VARCHAR(20),
        message TEXT,
        status VARCHAR(50),
        meta TEXT,
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_templates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        template_name VARCHAR(255) NOT NULL,
        template_content TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        is_active TINYINT(1) DEFAULT 0,
        created_by VARCHAR(100) DEFAULT 'admin'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
    
    conn.commit()
    cursor.close()
    conn.close()

# ----------------- HELPERS -----------------
def add_reminder(name, nik, vehicle_number, test_date, phone=None):
    try:
        test_date = datetime.strptime(test_date.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception:
        raise ValueError("❌ Format test_date harus YYYY-MM-DD")

    no_uji = None
    jenis_kendaraan = None
    if isinstance(phone, dict):
        no_uji = phone.get('no_uji')
        jenis_kendaraan = phone.get('jenis_kendaraan')
        phone = phone.get('phone')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Cek apakah nomor kendaraan ini sudah ada di database
    cursor.execute("SELECT id FROM reminders WHERE vehicle_number = %s", (vehicle_number,))
    existing = cursor.fetchone()
    
    if existing:
        # 2. Jika ada, UPDATE data tersebut dan RESET status centang (is_tested = 0)
        cursor.execute("""
            UPDATE reminders 
            SET name=%s, no_uji=%s, jenis_kendaraan=%s, test_date=%s, phone=%s, is_tested=0 
            WHERE id=%s
        """, (name, no_uji, jenis_kendaraan, test_date, phone, existing[0]))
        print(f"🔄 Data kendaraan {vehicle_number} diperbarui (is_tested direset ke 0)")
    else:
        # 3. Jika belum ada, buat record baru
        cursor.execute(
            'INSERT INTO reminders (name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, created_at, is_tested) VALUES (%s, %s, %s, %s, %s, %s, %s, 0)',
            (name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, datetime.utcnow())
        )
        print(f"📥 Data kendaraan {vehicle_number} ditambahkan baru")
        
    conn.commit()
    cursor.close()
    conn.close()

def list_reminders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM reminders ORDER BY test_date')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    today = date.today()
    for row in rows:
        r = dict(row)
        raw_date = str(r['test_date'])
        try:
            test_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except:
            continue
        
        days_until = (test_date - today).days
        
        # Check if already tested
        if r.get('is_tested') == 1:
            status_label = "Sudah Uji"
            color = "info"
        elif days_until < 0:
            # Tanggal sudah lewat dan belum uji -> Expired
            status_label = "Expired"
            color = "secondary"
        else:
            # Belum expired, classify by days
            status_label, color = classify_by_days(days_until)
        
        r['status'] = status_label
        r['color'] = color
        r['days_until'] = days_until
        r['test_date'] = test_date.strftime("%Y-%m-%d")
        results.append(r)
    return results

def classify_by_days(days_until):
    if days_until == 0:
        return "H (today)", "danger"
    elif days_until == 1:
        return "H-1", "warning"
    elif days_until >= 2:
        return "H-3 or more", "success"
    else:
        return "Expired", "secondary"

def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    # Hapus spasi, strip, tanda kurung, dsb
    phone = re.sub(r'[\s\-\(\)\.]', '', str(phone).strip())
    if not phone:
        return ""
    if phone.startswith("+628"):
        phone = phone[1:]
    elif phone.startswith("08"):
        phone = "62" + phone[1:]
    elif phone.startswith("8"):
        phone = "62" + phone
    elif phone.startswith("628"):
        pass
    else:
        return ""
    
    # Validasi panjang: 628 diikuti 8-11 digit (total 11-14 digit angka)
    if re.match(r'^628[0-9]{8,11}$', phone):
        return phone
    return ""

def log_message(direction, phone, message_text, status="unknown", meta=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (direction, phone, message, status, meta, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (direction, phone, message_text, status, (meta or ""), datetime.utcnow())
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Gagal log message:", e)

def build_message(record, status_label):
    """Build message from database template"""
    # Ensure all values are strings and handle None first
    name = str(record.get('name') or '')
    vehicle_number = str(record.get('vehicle_number') or '')
    no_uji = str(record.get('no_uji') or '')
    jenis_kendaraan = str(record.get('jenis_kendaraan') or '')
    test_date = str(record.get('test_date') or '')
    
    print(f"🔍 DEBUG - Record data:")
    print(f"  name: '{name}'")
    print(f"  vehicle_number: '{vehicle_number}'")
    print(f"  no_uji: '{no_uji}'")
    print(f"  jenis_kendaraan: '{jenis_kendaraan}'")
    print(f"  test_date: '{test_date}'")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT template_content FROM chat_templates WHERE is_active = 1 LIMIT 1")
    template_row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if template_row:
        template = template_row['template_content']
        print(f"📄 DEBUG - Template from database:")
        print(f"  {repr(template[:200])}...")
    else:
        # Fallback to default template with proper \n newlines
        template = "🚗 Halo Sdr/i {{name}} (sesuai STNK)\n\n📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {{vehicle_number}}\n🔢 Nomor Uji : {{no_uji}}\n🚛 Jenis Kendaraan : {{jenis_kendaraan}}\n📆 Tanggal Uji Kendaraan: {{test_date}}\n\n⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.\n✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan.\n🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan\n⏰ Harap hadir sesuai jadwal\n\n🙏 Terima Kasih - Dishub Kota Surakarta"
        print("⚠️ DEBUG - Using fallback template")
    
    # Replace variables - support both {{var}} and {var} formats
    message = template
    
    # Replace {{variable}} format
    message = message.replace('{{name}}', name)
    message = message.replace('{{vehicle_number}}', vehicle_number)
    message = message.replace('{{no_uji}}', no_uji)
    message = message.replace('{{jenis_kendaraan}}', jenis_kendaraan)
    message = message.replace('{{test_date}}', test_date)
    
    # Also replace {variable} format (if template uses single braces)
    message = message.replace('{name}', name)
    message = message.replace('{vehicle_number}', vehicle_number)
    message = message.replace('{no_uji}', no_uji)
    message = message.replace('{jenis_kendaraan}', jenis_kendaraan)
    message = message.replace('{test_date}', test_date)
    
    print(f"✅ DEBUG - Final message:")
    print(f"  {repr(message[:200])}...")
    
    return message

def send_whatsapp_message(phone, message_text):
    phone_norm = normalize_phone(phone)
    if not phone_norm:
        print(f"⚠️ Nomor telepon kosong atau tidak valid: {phone}")
        return {"status": "skipped", "reason": "invalid_or_empty_phone"}
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
        # JIKA SUDAH UJI, JANGAN KIRIM REMINDER APAPUN!
        if r.get('is_tested') == 1:
            continue
            
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
            "message": "WhatsApp Reminder API is running! (MySQL Version)",
            "database": "MySQL",
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
    phone = (data.get('phone') or "").strip()
    if phone:
        norm_phone = normalize_phone(phone)
        if not norm_phone:
            return jsonify({'error': 'Format nomor WhatsApp tidak valid. Gunakan format 081234567890 atau 81234567890 (9-13 digit)'}), 400
        phone = norm_phone
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id=%s", (reminder_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "deleted", "id": reminder_id})

@app.route("/send_one/<int:reminder_id>", methods=["POST"])
def send_one(reminder_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reminders WHERE id = %s", (reminder_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        return jsonify({"error": "Reminder tidak ditemukan"}), 404

    reminder = dict(row)
    
    # Convert test_date to string format if it's a date object
    if 'test_date' in reminder and reminder['test_date']:
        if isinstance(reminder['test_date'], date):
            reminder['test_date'] = reminder['test_date'].strftime('%Y-%m-%d')
        else:
            reminder['test_date'] = str(reminder['test_date'])
    
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders")
    cursor.execute("ALTER TABLE reminders AUTO_INCREMENT = 1")
    conn.commit()
    cursor.close()
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
    phone = (data.get("phone") or "").strip()
    if phone:
        norm_phone = normalize_phone(phone)
        if not norm_phone:
            return jsonify({'error': 'Format nomor WhatsApp tidak valid. Gunakan format 081234567890 atau 81234567890 (9-13 digit)'}), 400
        phone = norm_phone
    else:
        phone = ""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mengubah data dan mereset is_tested kembali ke 0
        cursor.execute("""
            UPDATE reminders 
            SET name=%s, vehicle_number=%s, no_uji=%s, jenis_kendaraan=%s, test_date=%s, phone=%s, is_tested=0 
            WHERE id=%s
        """, (
            data.get("name"),
            data.get("vehicle_number"),
            data.get("no_uji"),
            data.get("jenis_kendaraan"),
            data.get("test_date"),
            phone,
            reminder_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "updated", "id": reminder_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/mark_tested/<int:reminder_id>", methods=["PUT"])
def mark_tested(reminder_id):
    """Mark vehicle as tested"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET is_tested = 1 WHERE id = %s", (reminder_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "marked as tested", "id": reminder_id})
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

@app.route('/api/stats', methods=['GET'])
def api_stats():
    today = datetime.utcnow().date().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE direction='in' AND DATE(created_at)=%s", (today,))
    in_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND DATE(created_at)=%s", (today,))
    out_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reminders")
    users = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"in": in_count, "out": out_count, "users": users})

@app.route('/api/user_count', methods=['GET'])
def api_user_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reminders")
    users = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"users": users})

@app.route('/api/messages_timeseries', methods=['GET'])
def api_messages_timeseries():
    period = request.args.get('period', 'day')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if period == 'month':
        months = int(request.args.get('months', 12))
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%%Y-%%m') as period, COUNT(*) as cnt
            FROM messages
            WHERE direction='out' AND created_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
            GROUP BY period
            ORDER BY period
        """, (months,))
        rows = cursor.fetchall()
        
        from datetime import datetime
        now = datetime.utcnow()
        months_list = []
        for i in range(months-1, -1, -1):
            y = now.year
            m = now.month - i
            while m <= 0:
                m += 12
                y -= 1
            months_list.append(f"{y:04d}-{m:02d}")
        
        rowdict = {r['period']: r['cnt'] for r in rows}
        labels = months_list
        data = [rowdict.get(m, 0) for m in months_list]
    else:
        days = int(request.args.get('days', 30))
        cursor.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as cnt
            FROM messages
            WHERE direction='out' AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY day
            ORDER BY day
        """, (days,))
        rows = cursor.fetchall()
        
        from datetime import timedelta, datetime
        today = datetime.utcnow().date()
        days_list = [(today - timedelta(days=i)).isoformat() for i in range(days-1, -1, -1)]
        rowdict = {str(r['day']): r['cnt'] for r in rows}
        labels = days_list
        data = [rowdict.get(d, 0) for d in days_list]
    
    cursor.close()
    conn.close()
    return jsonify({"labels": labels, "data": data})

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename("avatar.png")
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    return jsonify({"status": "ok", "path": f"/static/uploads/{filename}"}), 200

@app.route("/reset-auth", methods=["POST"])
def reset_auth():
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
    
# ----------------- CHAT TEMPLATE ROUTES -----------------
@app.route('/edit_chat', methods=['GET'])
def edit_chat_page():
    return render_template('edit_chat.html')

@app.route('/api/template', methods=['GET'])
def get_template():
    """Get active template"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chat_templates WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1")
    template = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if template:
        return jsonify({'status': 'ok', 'template': template['template_content']})
    else:
        return jsonify({"status": "error", "message": "No active template found"}), 404

@app.route('/api/template', methods=['POST'])
def save_template():
    """Save new template and set as active"""
    data = request.get_json(force=True)
    
    if 'template' not in data:
        return jsonify({'status': 'error', 'message': 'template required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deactivate all templates
    cursor.execute("UPDATE chat_templates SET is_active = 0")
    
    # Insert new template
    cursor.execute("""
        INSERT INTO chat_templates (template_name, template_content, created_at, is_active, created_by)
        VALUES (%s, %s, %s, 1, %s)
    """, (
        data.get('name', 'Custom Template'),
        data['template'],
        datetime.utcnow(),
        data.get('created_by', 'admin')
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'ok', 'message': 'Template saved and activated'}), 200


@app.route('/api/template/history', methods=['GET'])
def get_template_history():
    """Get template history (last 10)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chat_templates ORDER BY created_at DESC LIMIT 10")
    templates = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(templates)

@app.route('/api/template/reset', methods=['POST'])
def reset_template():
    """Reset template to default"""
    default_template = "🚗 Halo Sdr/i {{name}} (sesuai STNK)\n\n📅 Masa berlaku UJI KIR anda dengan Nomor Kendaraan: {{vehicle_number}}\n🔢 Nomor Uji : {{no_uji}}\n🚛 Jenis Kendaraan : {{jenis_kendaraan}}\n📆 Tanggal Uji Kendaraan: {{test_date}}\n\n⚠️ Mohon untuk segera melakukkan uji berkala kendaraan anda di Pengujian Kendaraan Bermotor di Dishub Kota Surakarta.\n✅ Pastikan kendaraan anda sudah siap diuji dan layak jalan.\n🔧 Pemilik wajib menjaga dan memelihara kendaraan agar selalu dalam kondisi baik dan layak jalan\n⏰ Harap hadir sesuai jadwal\n\n🙏 Terima Kasih - Dishub Kota Surakarta"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deactivate all templates
    cursor.execute("UPDATE chat_templates SET is_active = 0")
    
    # Insert default template
    cursor.execute("""
        INSERT INTO chat_templates (template_name, template_content, created_at, is_active, created_by)
        VALUES (%s, %s, %s, 1, %s)
    """, (
        'Default Template (Reset)',
        default_template,
        datetime.utcnow(),
        'system'
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'ok', 'message': 'Template reset to default'}), 200

# ----------------- PESAN KELUAR ROUTES -----------------
@app.route('/pesankeluar', methods=['GET'])
def pesankeluar_page():
    """Analisis Pesan Keluar page"""
    return render_template('pesankeluar.html')

@app.route('/api/messages/outgoing', methods=['GET'])
def api_messages_outgoing():
    """Get all outgoing messages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, phone, message, status, meta, created_at 
            FROM messages 
            WHERE direction = 'out' 
            ORDER BY created_at DESC
        """)
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert datetime to string for JSON serialization
        for msg in messages:
            if msg.get('created_at'):
                msg['created_at'] = msg['created_at'].isoformat()
        
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    
    # Initialize scheduler
    scheduler = init_scheduler()
    
    print('✅ Database MySQL initialized.')
    print('📊 Database:', MYSQL_CONFIG['database'])
    print('⏰ Scheduler: Active (sends at 12:00 WIB daily)')
    print('🌐 Available endpoints:')
    print('  POST /add')
    print('  GET  /list')
    print('  POST /run_now')
    print('  DELETE /clear')
    print('  POST /upload-avatar')
    print('  POST /reset-auth')
    print('  GET /api/stats')
    print('  GET /api/template')
    print('  POST /api/template')
    print('  POST /api/template/reset')
    print('  GET /api/template/history')
    print('  GET /pesankeluar')
    print('  GET /api/messages/outgoing')
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\n🛑 Scheduler stopped.")