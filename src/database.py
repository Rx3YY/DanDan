import sqlite3

def init_db():
    conn = sqlite3.connect('recommendation.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp INTEGER,
            schedule INTEGER,
            choice INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 初始化数据库
init_db()
