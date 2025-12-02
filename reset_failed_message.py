import sqlite3

DB_PATH = 'reminders.db'

# SCRIPT UNTUK MENGHAPUS SEMUA PESAN GAGAL DIKIRIM
def reset_failed_messages():
    """Delete all failed messages from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get count before deletion
        c.execute("SELECT COUNT(*) FROM messages WHERE direction='out' AND (LOWER(status) LIKE '%failed%' OR LOWER(status) LIKE '%error%' OR LOWER(status) LIKE '%gagal%')")
        failed_count_before = c.fetchone()[0]

        # Delete failed messages
        c.execute("DELETE FROM messages WHERE direction='out' AND (LOWER(status) LIKE '%failed%' OR LOWER(status) LIKE '%error%' OR LOWER(status) LIKE '%gagal%')")

        # Reset autoincrement if needed (optional)
        # c.execute("DELETE FROM sqlite_sequence WHERE name='messages'")

        conn.commit()

        # Get count after deletion
        c.execute("SELECT COUNT(*) FROM messages WHERE direction='out'")
        total_after = c.fetchone()[0]

        print(f"Deleted {failed_count_before} failed messages.")
        print(f"Total outgoing messages remaining: {total_after}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_failed_messages()
