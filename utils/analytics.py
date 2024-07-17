import sqlite3
from datetime import datetime

class Analytics:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_total_sales(self):
        self.cursor.execute("SELECT SUM(total) FROM sales")
        return self.cursor.fetchone()[0]

    def get_sales_today(self):
        self.cursor.execute("SELECT SUM(total) FROM sales WHERE DATE(created_at) = DATE('now')")
        return self.cursor.fetchone()[0]

    def get_total_orders(self):
        self.cursor.execute("SELECT SUM(quantity) FROM sales")
        return self.cursor.fetchone()[0]
    
    def get_orders_today(self):
        self.cursor.execute("SELECT SUM(quantity) FROM sales WHERE DATE(created_at) = DATE('now')")
        return self.cursor.fetchone()[0]
    
    def get_products_sales_by_date(self, start_data, end_date):
        self.cursor.execute("SELECT * FROM sales WHERE DATE(created_at) BETWEEN ? AND ?", (start_data, end_date))
        rows = self.cursor.fetchall()
        return rows
    
    def get_sales_dates(self):
        self.cursor.execute("SELECT DISTINCT DATE(created_at) FROM sales")
        rows = self.cursor.fetchall()
        return rows
    
    def get_sales_by_date(self, date):
        self.cursor.execute("SELECT SUM(total) FROM sales WHERE DATE(created_at) = ?", (date,))
        rows = self.cursor.fetchone()
        return rows[0]
    
    def get_sales_for_table(self):
        return_data = []
        self.cursor.execute("SELECT s.sale_id, SUM(s.quantity) AS total_quantity, SUM(s.total) AS total_amount, u.firstname || ' ' || u.lastname AS operator_name, s.created_at FROM sales s JOIN users u ON s.operator_id = u.id GROUP BY s.sale_id, s.created_at, operator_name ORDER BY s.created_at DESC")
        rows = self.cursor.fetchall()        
        for row in rows:
            date_object = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
            return_data.append({
                'sale_id': row[0],
                'total_quantity': row[1],
                'total_amount': row[2],
                'operator_name': row[3],
                'created_at': date_object.strftime('%B %d, %Y %I:%M %p')
            })
        return return_data





