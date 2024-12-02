import sqlite3
from datetime import datetime

# Tạo hoặc kết nối tới cơ sở dữ liệu
conn = sqlite3.connect("file_translation.db")
cursor = conn.cursor()

# Tạo bảng lưu thông tin file
cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    translated_filename TEXT NOT NULL,
    user_id TEXT,
    src_lang TEXT,
    trg_lang TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    translated_at TIMESTAMP,
    file_path TEXT NOT NULL
)
''')

conn.commit()
conn.close()

def save_file_to_db(original_filename, translated_filename, src_lang, trg_lang, file_path, output_path, user_id=None):
    conn = sqlite3.connect("file_translation.db")
    cursor = conn.cursor()

    translated_at = datetime.now()  # Thời gian file được dịch xong
    cursor.execute('''
        INSERT INTO files (original_filename, translated_filename, user_id, src_lang, trg_lang, translated_at, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (original_filename, translated_filename, user_id, src_lang, trg_lang, translated_at, file_path))

    conn.commit()
    conn.close()

def get_all_files():
    conn = sqlite3.connect("file_translation.db")
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM files')
    files = cursor.fetchall()

    conn.close()
    return files

def get_files_by_user(user_id):
    conn = sqlite3.connect("file_translation.db")
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM files WHERE user_id = ?', (user_id,))
    files = cursor.fetchall()

    conn.close()
    return files
