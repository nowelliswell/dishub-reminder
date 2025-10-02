import sqlite3

conn = sqlite3.connect("reminders.db")
cursor = conn.cursor()

# tampilkan semua tabel
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabel yang ada:", tables)

# kalau sudah tahu tabelnya, cek 5 data teratas
if tables:
    table_name = tables[0][0]  # ambil tabel pertama
    print(f"\nCek isi tabel {table_name}:")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    print(cursor.fetchall())

conn.close()
