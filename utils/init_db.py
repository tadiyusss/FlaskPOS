import sqlite3
from core.utils.logging import Logging

log = Logging()

def create_database():
    with open('extensions/pos/utils/database.sql', 'r') as f:
        sql = f.read()
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.executescript(sql)
        conn.commit()
        conn.close()
        log.log("POS database initialized successfully", "success")

create_database()