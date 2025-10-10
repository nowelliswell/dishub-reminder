import sqlite3
from tabulate import tabulate

# Koneksi ke database
conn = sqlite3.connect("reminders.db")
cursor = conn.cursor()

# Ambil semua tabel di database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("❌ Tidak ada tabel dalam database.")
else:
    print("📋 Daftar tabel dan isinya:\n")

    # Loop semua tabel
    for table in tables:
        table_name = table[0]
        print(f"🟦 Tabel: {table_name}")

        # Ambil semua data dan nama kolom
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]

        if rows:
            # Tampilkan dalam format tabel
            print(tabulate(rows, headers=col_names, tablefmt="grid"))
        else:
            print("(Tabel kosong)")

        print("-" * 80)

conn.close()
