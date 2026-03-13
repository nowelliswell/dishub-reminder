"""
Database Structure Viewer - MySQL Style
Menampilkan struktur database lengkap seperti MySQL DESCRIBE/SHOW TABLES
Cocok untuk presentasi skripsi dan dokumentasi
"""
import sqlite3
import os
import sys
from datetime import datetime

# Fix encoding untuk Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

DB_PATH = 'reminders.db'

def print_line(char="-", length=120):
    """Print horizontal line"""
    print(char * length)

def print_double_line():
    """Print double line separator"""
    print("=" * 120)

def print_mysql_header(title):
    """Print header MySQL style"""
    print_double_line()
    print(f"  {title}")
    print_double_line()

def format_mysql_table(headers, rows, col_widths=None):
    """Format data dalam style MySQL table"""
    if not rows:
        return
    
    # Calculate column widths if not provided
    if col_widths is None:
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print top border
    print("+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+")
    
    # Print headers
    header_row = "| " + " | ".join([str(headers[i]).ljust(col_widths[i]) for i in range(len(headers))]) + " |"
    print(header_row)
    
    # Print separator
    print("+" + "+".join(["=" * (w + 2) for w in col_widths]) + "+")
    
    # Print rows
    for row in rows:
        row_str = "| " + " | ".join([str(row[i]).ljust(col_widths[i]) for i in range(len(row))]) + " |"
        print(row_str)
    
    # Print bottom border
    print("+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+")

def get_table_create_statement(cursor, table_name):
    """Get CREATE TABLE statement"""
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    return result[0] if result else None

def analyze_database_mysql_style():
    """Analisis database dengan tampilan MySQL style"""
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ ERROR: Database '{DB_PATH}' tidak ditemukan!")
        print("� Jalankan aplikasi terlebih dahulu: python whatsapp_reminder_app.py\n")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Header
    print("\n")
    print_mysql_header("DATABASE STRUCTURE - MySQL Style View")
    print(f"Database Name    : {DB_PATH}")
    print(f"Database Size    : {os.path.getsize(DB_PATH) / 1024:.2f} KB")
    print(f"Analysis Date    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database Type    : SQLite 3")
    print_double_line()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nTotal Tables: {len(tables)}")
    print()
    
    # SHOW TABLES
    print_mysql_header("SHOW TABLES")
    table_list = [[i+1, table] for i, table in enumerate(tables)]
    format_mysql_table(["No", f"Tables_in_{DB_PATH}"], table_list, [5, 30])
    
    print(f"\n{len(tables)} rows in set\n")
    
    # Analyze each table
    all_primary_keys = {}
    all_foreign_keys = {}
    
    for table_name in tables:
        print("\n")
        print_double_line()
        print(f"TABLE: {table_name}")
        print_double_line()
        
        # DESCRIBE TABLE (MySQL style)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\nDESCRIBE {table_name};\n")
        
        describe_rows = []
        primary_keys = []
        
        for col in columns:
            cid, name, col_type, not_null, default_val, is_pk = col
            
            # Field
            field = name
            
            # Type
            col_type_display = col_type if col_type else "TEXT"
            
            # Null
            null_display = "NO" if not_null else "YES"
            
            # Key
            key_display = "PRI" if is_pk else ""
            if is_pk:
                primary_keys.append(name)
            
            # Default
            default_display = str(default_val) if default_val is not None else "NULL"
            
            # Extra
            extra_display = "auto_increment" if is_pk and col_type == "INTEGER" else ""
            
            describe_rows.append([field, col_type_display, null_display, key_display, default_display, extra_display])
        
        format_mysql_table(
            ["Field", "Type", "Null", "Key", "Default", "Extra"],
            describe_rows,
            [25, 20, 8, 8, 15, 20]
        )
        
        print(f"{len(describe_rows)} rows in set\n")
        
        # Store primary keys
        if primary_keys:
            all_primary_keys[table_name] = primary_keys
        
        # SHOW INDEXES
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"SHOW INDEXES FROM {table_name};\n")
            index_rows = []
            for idx in indexes:
                seq, idx_name, unique, origin, partial = idx
                index_rows.append([
                    table_name,
                    "0" if unique else "1",
                    idx_name,
                    "1",
                    "",
                    "BTREE"
                ])
            
            format_mysql_table(
                ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name", "Index_type"],
                index_rows,
                [20, 12, 25, 15, 20, 12]
            )
            print(f"{len(index_rows)} rows in set\n")
        
        # FOREIGN KEYS
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print(f"SHOW FOREIGN KEYS FROM {table_name};\n")
            fk_rows = []
            fk_list = []
            for fk in foreign_keys:
                fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
                fk_rows.append([
                    from_col,
                    ref_table,
                    to_col,
                    on_update,
                    on_delete
                ])
                fk_list.append({
                    'from_col': from_col,
                    'ref_table': ref_table,
                    'to_col': to_col
                })
            
            format_mysql_table(
                ["Column", "Referenced_Table", "Referenced_Column", "On_Update", "On_Delete"],
                fk_rows,
                [25, 25, 25, 15, 15]
            )
            print(f"{len(fk_rows)} rows in set\n")
            
            all_foreign_keys[table_name] = fk_list
        
        # SHOW CREATE TABLE
        create_stmt = get_table_create_statement(cursor, table_name)
        if create_stmt:
            print(f"SHOW CREATE TABLE {table_name};\n")
            print("+" + "-" * 118 + "+")
            print(f"| {'Table':<20} | {'Create Table':<94} |")
            print("+" + "=" * 118 + "+")
            
            # Format CREATE statement
            create_lines = create_stmt.split('\n')
            for i, line in enumerate(create_lines):
                if i == 0:
                    print(f"| {table_name:<20} | {line:<94} |")
                else:
                    print(f"| {'':<20} | {line:<94} |")
            
            print("+" + "-" * 118 + "+")
            print("1 row in set\n")
        
        # TABLE STATUS
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        print(f"TABLE STATUS FOR {table_name};\n")
        status_rows = [[
            table_name,
            "InnoDB",
            "Dynamic",
            row_count,
            "0",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]]
        
        format_mysql_table(
            ["Name", "Engine", "Row_format", "Rows", "Data_length", "Create_time"],
            status_rows,
            [20, 10, 12, 10, 15, 25]
        )
        print("1 row in set\n")
    
    # DATABASE RELATIONSHIPS
    print("\n")
    print_double_line()
    print("DATABASE RELATIONSHIPS (Entity Relationship)")
    print_double_line()
    
    print("\n+-----------------------------------------------------------------------------------------------------+")
    print("|                                    PRIMARY KEYS SUMMARY                                         |")
    print("+-----------------------------------------------------------------------------------------------------+\n")
    
    if all_primary_keys:
        pk_rows = []
        for table, pks in all_primary_keys.items():
            pk_rows.append([table, ", ".join(pks), "PRIMARY KEY"])
        
        format_mysql_table(
            ["Table Name", "Primary Key Column(s)", "Constraint Type"],
            pk_rows,
            [25, 35, 20]
        )
        print(f"{len(pk_rows)} rows in set\n")
    else:
        print("No primary keys defined.\n")
    
    print("\n+-----------------------------------------------------------------------------------------------------+")
    print("|                                   FOREIGN KEYS SUMMARY                                          |")
    print("+-----------------------------------------------------------------------------------------------------+\n")
    
    if all_foreign_keys:
        fk_rows = []
        for table, fks in all_foreign_keys.items():
            for fk in fks:
                fk_rows.append([
                    table,
                    fk['from_col'],
                    fk['ref_table'],
                    fk['to_col'],
                    f"{table}.{fk['from_col']} → {fk['ref_table']}.{fk['to_col']}"
                ])
        
        format_mysql_table(
            ["Table", "Column", "References Table", "References Column", "Relationship"],
            fk_rows,
            [20, 20, 20, 20, 45]
        )
        print(f"{len(fk_rows)} rows in set\n")
    else:
        print("WARNING: No foreign key constraints defined explicitly.\n")
        print("NOTE: LOGICAL RELATIONSHIPS (Application Level):\n")
        print("   +-----------------------------------------------------------------------------+")
        print("   |  reminders.phone  <->  messages.phone  (Implicit relationship via phone)  |")
        print("   |  chat_templates   ->   Used by application to format messages             |")
        print("   +-----------------------------------------------------------------------------+\n")
        
        print("   Explanation:")
        print("   * reminders: Stores vehicle test reminder data")
        print("   * messages: Logs all sent/received messages (linked via phone number)")
        print("   * chat_templates: Stores WhatsApp message templates (used by app)\n")
    
    # ER DIAGRAM (ASCII)
    print("\n+-----------------------------------------------------------------------------------------------------+")
    print("|                              ENTITY RELATIONSHIP DIAGRAM (ASCII)                                |")
    print("+-----------------------------------------------------------------------------------------------------+\n")
    
    print("   +--------------------------------------+")
    print("   |         REMINDERS (Main)             |")
    print("   +--------------------------------------+")
    print("   | [PK] id                              |")
    print("   |      name                            |")
    print("   |      vehicle_number                  |")
    print("   |      no_uji                          |")
    print("   |      jenis_kendaraan                 |")
    print("   |      test_date                       |")
    print("   |      phone  --------------+          |")
    print("   |      created_at           |          |")
    print("   +---------------------------+----------+")
    print("                               |")
    print("                               | (Logical Relation)")
    print("                               | via phone number")
    print("                               |")
    print("                               V")
    print("   +--------------------------------------+")
    print("   |         MESSAGES (Log)               |")
    print("   +--------------------------------------+")
    print("   | [PK] id                              |")
    print("   |      direction (in/out)              |")
    print("   |      phone                           |")
    print("   |      message                         |")
    print("   |      status                          |")
    print("   |      meta                            |")
    print("   |      created_at                      |")
    print("   +--------------------------------------+")
    print("")
    print("   +--------------------------------------+")
    print("   |      CHAT_TEMPLATES                  |")
    print("   +--------------------------------------+")
    print("   | [PK] id                              |")
    print("   |      template_name                   |")
    print("   |      template_content                |")
    print("   |      is_active                       |")
    print("   |      created_at                      |")
    print("   |      updated_at                      |")
    print("   +--------------------------------------+")
    print("              |")
    print("              | (Used by)")
    print("              V")
    print("      Message Builder Function")
    print("")
    
    # SUMMARY STATISTICS
    print("\n")
    print_double_line()
    print("DATABASE SUMMARY STATISTICS")
    print_double_line()
    print()
    
    total_rows = 0
    summary_rows = []
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_rows += count
        
        # Get table size (approximate)
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        
        summary_rows.append([table, count, "InnoDB", "Active"])
    
    format_mysql_table(
        ["Table Name", "Row Count", "Engine", "Status"],
        summary_rows,
        [25, 15, 15, 15]
    )
    
    print(f"\nTotal Tables      : {len(tables)}")
    print(f"Total Rows        : {total_rows}")
    print(f"Database Size     : {os.path.getsize(DB_PATH) / 1024:.2f} KB")
    print(f"Primary Keys      : {len(all_primary_keys)}")
    print(f"Foreign Keys      : {len(all_foreign_keys)}")
    
    conn.close()
    
    print("\n")
    print_double_line()
    print("✓ Database analysis completed successfully!")
    print_double_line()
    print()

if __name__ == "__main__":
    try:
        analyze_database_mysql_style()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
