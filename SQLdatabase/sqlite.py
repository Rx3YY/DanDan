import sqlite3
import os

def create_database():
    try:
        # 获取当前脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'notification.db')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                          (time TEXT PRIMARY KEY, reminded BOOLEAN)''')

        conn.commit()
        print("SQLite database 'notification.db' created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()
