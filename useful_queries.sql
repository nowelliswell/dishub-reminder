-- ============================================================================
-- USEFUL SQL QUERIES FOR REMINDERS DATABASE
-- ============================================================================
-- Database: reminders.db (SQLite)
-- Last Updated: 2025-12-05
-- ============================================================================

-- ============================================================================
-- 1. BASIC QUERIES
-- ============================================================================

-- Lihat semua tabel
SELECT name FROM sqlite_master WHERE type='table';

-- Lihat struktur tabel
PRAGMA table_info(reminders);
PRAGMA table_info(messages);
PRAGMA table_info(chat_templates);

-- Count semua data
SELECT 'reminders' as table_name, COUNT(*) as total FROM reminders
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'chat_templates', COUNT(*) FROM chat_templates;

-- ============================================================================
-- 2. REMINDERS QUERIES
-- ============================================================================

-- Semua reminder (sorted by date)
SELECT * FROM reminders ORDER BY test_date;

-- Reminder hari ini (H)
SELECT * FROM reminders 
WHERE date(test_date) = date('now');

-- Reminder besok (H-1)
SELECT * FROM reminders 
WHERE date(test_date) = date('now', '+1 day');

-- Reminder lusa (H-2)
SELECT * FROM reminders 
WHERE date(test_date) = date('now', '+2 days');

-- Reminder 7 hari ke depan
SELECT * FROM reminders 
WHERE date(test_date) BETWEEN date('now') AND date('now', '+7 days')
ORDER BY test_date;

-- Reminder yang sudah expired
SELECT * FROM reminders 
WHERE date(test_date) < date('now')
ORDER BY test_date DESC;

-- Reminder dengan status
SELECT 
    id,
    name,
    vehicle_number,
    test_date,
    phone,
    CASE 
        WHEN julianday(test_date) - julianday('now') = 0 THEN 'H (today)'
        WHEN julianday(test_date) - julianday('now') = 1 THEN 'H-1'
        WHEN julianday(test_date) - julianday('now') = 2 THEN 'H-2'
        WHEN julianday(test_date) - julianday('now') > 2 THEN 'H-3+'
        ELSE 'Expired'
    END as status,
    CAST(julianday(test_date) - julianday('now') AS INTEGER) as days_until
FROM reminders
ORDER BY test_date;

-- Statistik reminder per status
SELECT 
    CASE 
        WHEN julianday(test_date) - julianday('now') = 0 THEN 'H (today)'
        WHEN julianday(test_date) - julianday('now') = 1 THEN 'H-1'
        WHEN julianday(test_date) - julianday('now') = 2 THEN 'H-2'
        WHEN julianday(test_date) - julianday('now') > 2 THEN 'H-3+'
        ELSE 'Expired'
    END as status,
    COUNT(*) as total
FROM reminders
GROUP BY status
ORDER BY 
    CASE status
        WHEN 'Expired' THEN 1
        WHEN 'H (today)' THEN 2
        WHEN 'H-1' THEN 3
        WHEN 'H-2' THEN 4
        ELSE 5
    END;

-- Cari reminder by name
SELECT * FROM reminders 
WHERE name LIKE '%John%'
ORDER BY test_date;

-- Cari reminder by vehicle number
SELECT * FROM reminders 
WHERE vehicle_number LIKE '%AD 1234%'
ORDER BY test_date;

-- Reminder tanpa nomor telepon
SELECT * FROM reminders 
WHERE phone IS NULL OR phone = ''
ORDER BY test_date;

-- ============================================================================
-- 3. MESSAGES QUERIES
-- ============================================================================

-- Semua pesan keluar
SELECT * FROM messages 
WHERE direction = 'out'
ORDER BY created_at DESC;

-- Pesan hari ini
SELECT * FROM messages 
WHERE date(created_at) = date('now')
ORDER BY created_at DESC;

-- Pesan 7 hari terakhir
SELECT * FROM messages 
WHERE date(created_at) >= date('now', '-7 days')
ORDER BY created_at DESC;

-- Pesan yang berhasil terkirim
SELECT * FROM messages 
WHERE direction = 'out' 
  AND (status LIKE '%sent%' OR status LIKE '%success%' OR status LIKE '%delivered%')
ORDER BY created_at DESC;

-- Pesan yang gagal
SELECT * FROM messages 
WHERE direction = 'out' 
  AND (status LIKE '%failed%' OR status LIKE '%error%' OR status LIKE '%blocked%')
ORDER BY created_at DESC;

-- Statistik pesan per status
SELECT 
    status,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages WHERE direction='out'), 2) as percentage
FROM messages
WHERE direction = 'out'
GROUP BY status
ORDER BY total DESC;

-- Pesan per hari (7 hari terakhir)
SELECT 
    date(created_at) as tanggal,
    COUNT(*) as total_pesan,
    SUM(CASE WHEN status LIKE '%sent%' THEN 1 ELSE 0 END) as berhasil,
    SUM(CASE WHEN status LIKE '%failed%' OR status LIKE '%error%' THEN 1 ELSE 0 END) as gagal
FROM messages
WHERE direction = 'out' 
  AND date(created_at) >= date('now', '-7 days')
GROUP BY date(created_at)
ORDER BY tanggal;

-- Pesan per bulan (12 bulan terakhir)
SELECT 
    strftime('%Y-%m', created_at) as bulan,
    COUNT(*) as total_pesan
FROM messages
WHERE direction = 'out' 
  AND date(created_at) >= date('now', 'start of month', '-12 months')
GROUP BY bulan
ORDER BY bulan;

-- Top 10 nomor yang paling sering dikirim pesan
SELECT 
    phone,
    COUNT(*) as total_pesan,
    MAX(created_at) as terakhir_kirim
FROM messages
WHERE direction = 'out'
GROUP BY phone
ORDER BY total_pesan DESC
LIMIT 10;

-- ============================================================================
-- 4. JOIN QUERIES (Reminders + Messages)
-- ============================================================================

-- Reminder dengan riwayat pesan
SELECT 
    r.id,
    r.name,
    r.vehicle_number,
    r.test_date,
    r.phone,
    COUNT(m.id) as total_pesan_terkirim,
    MAX(m.created_at) as terakhir_kirim
FROM reminders r
LEFT JOIN messages m ON r.phone = m.phone AND m.direction = 'out'
GROUP BY r.id
ORDER BY r.test_date;

-- Reminder yang belum pernah dikirim pesan
SELECT r.*
FROM reminders r
LEFT JOIN messages m ON r.phone = m.phone AND m.direction = 'out'
WHERE m.id IS NULL
  AND date(r.test_date) >= date('now')
ORDER BY r.test_date;

-- Reminder dengan status pengiriman terakhir
SELECT 
    r.id,
    r.name,
    r.vehicle_number,
    r.test_date,
    r.phone,
    m.status as status_terakhir,
    m.created_at as waktu_kirim_terakhir
FROM reminders r
LEFT JOIN (
    SELECT phone, status, created_at,
           ROW_NUMBER() OVER (PARTITION BY phone ORDER BY created_at DESC) as rn
    FROM messages
    WHERE direction = 'out'
) m ON r.phone = m.phone AND m.rn = 1
ORDER BY r.test_date;

-- ============================================================================
-- 5. CHAT TEMPLATES QUERIES
-- ============================================================================

-- Template yang aktif
SELECT * FROM chat_templates 
WHERE is_active = 1
ORDER BY updated_at DESC;

-- Semua template (history)
SELECT 
    id,
    template_name,
    CASE WHEN is_active = 1 THEN '✓ Active' ELSE 'Inactive' END as status,
    created_at,
    updated_at
FROM chat_templates
ORDER BY updated_at DESC;

-- Template terakhir diupdate
SELECT * FROM chat_templates 
ORDER BY updated_at DESC 
LIMIT 1;

-- ============================================================================
-- 6. STATISTICS & ANALYTICS
-- ============================================================================

-- Dashboard statistics (hari ini)
SELECT 
    (SELECT COUNT(*) FROM messages WHERE direction='in' AND date(created_at)=date('now')) as pesan_masuk,
    (SELECT COUNT(*) FROM messages WHERE direction='out' AND date(created_at)=date('now')) as pesan_keluar,
    (SELECT COUNT(*) FROM reminders) as total_reminder,
    (SELECT COUNT(*) FROM reminders WHERE date(test_date) = date('now')) as reminder_hari_ini,
    (SELECT COUNT(*) FROM reminders WHERE date(test_date) = date('now', '+1 day')) as reminder_besok;

-- Success rate pengiriman
SELECT 
    COUNT(*) as total_pesan,
    SUM(CASE WHEN status LIKE '%sent%' OR status LIKE '%success%' THEN 1 ELSE 0 END) as berhasil,
    SUM(CASE WHEN status LIKE '%failed%' OR status LIKE '%error%' THEN 1 ELSE 0 END) as gagal,
    ROUND(
        SUM(CASE WHEN status LIKE '%sent%' OR status LIKE '%success%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as success_rate_persen
FROM messages
WHERE direction = 'out';

-- Reminder per jenis kendaraan
SELECT 
    jenis_kendaraan,
    COUNT(*) as total
FROM reminders
WHERE jenis_kendaraan IS NOT NULL AND jenis_kendaraan != ''
GROUP BY jenis_kendaraan
ORDER BY total DESC;

-- Reminder per bulan (upcoming)
SELECT 
    strftime('%Y-%m', test_date) as bulan,
    COUNT(*) as total_reminder
FROM reminders
WHERE date(test_date) >= date('now')
GROUP BY bulan
ORDER BY bulan;

-- ============================================================================
-- 7. MAINTENANCE QUERIES
-- ============================================================================

-- Check database integrity
PRAGMA integrity_check;

-- Database info
PRAGMA database_list;

-- Table sizes
SELECT 
    name as table_name,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=m.name) as index_count
FROM sqlite_master m
WHERE type='table'
ORDER BY name;

-- Vacuum (optimize database)
-- VACUUM;

-- ============================================================================
-- 8. DATA CLEANUP
-- ============================================================================

-- Hapus pesan lama (lebih dari 90 hari)
-- DELETE FROM messages WHERE date(created_at) < date('now', '-90 days');

-- Hapus reminder yang sudah expired (lebih dari 30 hari)
-- DELETE FROM reminders WHERE date(test_date) < date('now', '-30 days');

-- Hapus template yang tidak aktif (kecuali 5 terakhir)
-- DELETE FROM chat_templates 
-- WHERE is_active = 0 
--   AND id NOT IN (
--       SELECT id FROM chat_templates 
--       WHERE is_active = 0 
--       ORDER BY updated_at DESC 
--       LIMIT 5
--   );

-- Reset auto increment
-- DELETE FROM sqlite_sequence WHERE name='reminders';
-- DELETE FROM sqlite_sequence WHERE name='messages';

-- ============================================================================
-- 9. EXPORT QUERIES
-- ============================================================================

-- Export reminder ke CSV format
SELECT 
    id,
    name,
    vehicle_number,
    no_uji,
    jenis_kendaraan,
    test_date,
    phone,
    created_at
FROM reminders
ORDER BY test_date;

-- Export messages ke CSV format
SELECT 
    id,
    direction,
    phone,
    message,
    status,
    created_at
FROM messages
ORDER BY created_at DESC;

-- ============================================================================
-- 10. TESTING QUERIES
-- ============================================================================

-- Insert test reminder
-- INSERT INTO reminders (name, vehicle_number, no_uji, jenis_kendaraan, test_date, phone, created_at)
-- VALUES ('Test User', 'AD 1234 BC', 'DPR 5060790', 'Truck', date('now', '+1 day'), '6285857768760', datetime('now'));

-- Insert test message
-- INSERT INTO messages (direction, phone, message, status, meta, created_at)
-- VALUES ('out', '6285857768760', 'Test message', 'sent', '{}', datetime('now'));

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Uncomment queries yang diawali dengan -- untuk menjalankannya
-- 2. Backup database sebelum menjalankan DELETE atau UPDATE queries
-- 3. Gunakan LIMIT untuk testing queries yang menghasilkan banyak data
-- 4. date('now') menggunakan UTC, sesuaikan jika perlu timezone
-- ============================================================================
