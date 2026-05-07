"""
Script Migrasi Data dari SQLite ke MySQL
Jalankan: python migrate_to_mysql.py
"""

import sqlite3
from datetime import datetime

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

# ========== KONFIGURASI ==========
SQLITE_DB = 'reminders.db'

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Username MySQL (default XAMPP: root)
    'password': '',           # Password MySQL (default XAMPP: kosong)
    'database': 'reminders'
}

# ========== FUNGSI MIGRASI ==========

def migrate_data():
    print("🔄 Memulai migrasi dari SQLite ke MySQL...\n")
    
    # Koneksi ke SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        print("✅ Terhubung ke SQLite")
    except Exception as e:
        print(f"❌ Gagal koneksi SQLite: {e}")
        return
    
    # Koneksi ke MySQL
    try:
        if MYSQL_LIB == 'mysql.connector':
            mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        else:  # pymysql
            mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        print(f"✅ Terhubung ke MySQL (using {MYSQL_LIB})\n")
    except Exception as e:
        print(f"❌ Gagal koneksi MySQL: {e}")
        print("💡 Pastikan MySQL sudah running dan database 'reminders' sudah dibuat!")
        return
    
    # ========== MIGRASI TABEL REMINDERS ==========
    print("📦 Migrasi tabel 'reminders'...")
    try:
        # Ambil data dari SQLite
        sqlite_cursor.execute("SELECT * FROM reminders")
        reminders = sqlite_cursor.fetchall()
        
        if not reminders:
            print("   ⚠️  Tabel reminders kosong")
        else:
            # Insert ke MySQL
            insert_query = """
                INSERT INTO reminders 
                (id, name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            count = 0
            for row in reminders:
                data = (
                    row['id'],
                    row['name'],
                    row['vehicle_number'],
                    row['no_uji'],
                    row['jenis_kendaraan'],
                    row['test_date'],
                    row['phone'],
                    row['created_at']
                )
                mysql_cursor.execute(insert_query, data)
                count += 1
            
            mysql_conn.commit()
            print(f"   ✅ {count} data reminders berhasil dimigrasikan")
    
    except Exception as e:
        print(f"   ❌ Error migrasi reminders: {e}")
    
    # ========== MIGRASI TABEL MESSAGES ==========
    print("\n📦 Migrasi tabel 'messages'...")
    try:
        # Ambil data dari SQLite
        sqlite_cursor.execute("SELECT * FROM messages")
        messages = sqlite_cursor.fetchall()
        
        if not messages:
            print("   ⚠️  Tabel messages kosong")
        else:
            # Insert ke MySQL
            insert_query = """
                INSERT INTO messages 
                (id, direction, phone, message, status, meta, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            count = 0
            for row in messages:
                data = (
                    row['id'],
                    row['direction'],
                    row['phone'],
                    row['message'],
                    row['status'],
                    row['meta'],
                    row['created_at']
                )
                mysql_cursor.execute(insert_query, data)
                count += 1
            
            mysql_conn.commit()
            print(f"   ✅ {count} data messages berhasil dimigrasikan")
    
    except Exception as e:
        print(f"   ❌ Error migrasi messages: {e}")
    
    # Tutup koneksi
    sqlite_conn.close()
    mysql_conn.close()
    
    print("\n🎉 Migrasi selesai!")
    print("💡 Cek data di phpMyAdmin: http://localhost/phpmyadmin")

# ========== JALANKAN ==========
if __name__ == "__main__":
    migrate_data()
