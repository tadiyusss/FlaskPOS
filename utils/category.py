import sqlite3


class CategoryHandler:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def edit_category(self, category_id, category_name):
        self.cursor.execute("UPDATE product_category SET category_name=? WHERE id=?", (category_name, category_id))
        self.conn.commit()

    def check_category_exists(self, category_name):
        self.cursor.execute("SELECT * FROM product_category WHERE category_name=? AND is_deleted = 0", (category_name,))
        return self.cursor.fetchone()

    def create_category(self, category_name):
        self.cursor.execute("INSERT INTO product_category (category_name) VALUES (?)", (category_name,))
        self.conn.commit()

    def get_categories(self):
        self.cursor.execute("SELECT * FROM product_category WHERE is_deleted = 0")
        return self.cursor.fetchall()

    def get_category_by_id(self, category_id):
        self.cursor.execute("SELECT * FROM product_category WHERE id=? AND is_deleted = 0", (category_id,))
        return self.cursor.fetchone()
    
    def remove_category(self, category_id):
        self.cursor.execute("UPDATE product_category SET is_deleted = 1 WHERE id = ?", (category_id,))
        self.conn.commit()