import sqlite3
from .products import ProductHandler
from core.utils.functions import UserHandler
import random
import string


class SalesHandler:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.product_handler = ProductHandler()

    def get_stocks(self, product_id):
        self.cursor.execute("SELECT stocks FROM products WHERE id = ?", (product_id,))
        return self.cursor.fetchone()[0]

    def get_sale_by_id(self, sale_id):
        return_data = {
            'data': [],
            'total': 0
        }
        self.cursor.execute("SELECT s.sale_id, p.product_name, s.tendered, s.quantity, s.price, s.total, u.firstname || ' ' || u.lastname AS operator_name, s.created_at FROM sales s JOIN products p ON s.product_id = p.id JOIN users u ON s.operator_id = u.id WHERE s.sale_id = ?", (sale_id,))
        rows = self.cursor.fetchall()
        for row in rows:
            return_data['data'].append({
                'sale_id': row[0],
                'product_name': row[1],
                'tendered': row[2],
                'quantity': row[3],
                'price': row[4],
                'total': row[5],
                'operator_name': row[6],
                'created_at': row[7],
            })
            return_data['total'] += row[5]
        return return_data

    def create_sale(self, sale_id, product_id, quantity, price, tendered, operator_id):
        product_data = self.product_handler.get_product_by_id(product_id)
        if product_data is None:
            return {
                'status': 'error',
                'message': 'Product does not exist',
            }
        if product_data['stocks'] < quantity:
            return {
                'status': 'error',
                'message': 'Insufficient stocks in inventory',
            }
        self.product_handler.decrease_stocks(product_id, quantity)
        self.cursor.execute("INSERT INTO sales (sale_id, product_id, quantity, price, total, operator_id, tendered) VALUES (?, ?, ?, ?, ?, ?, ?)", (sale_id, product_id, quantity, price, price * quantity, operator_id, tendered))
        self.conn.commit()
        return {
            'status': 'success',
            'message': 'Sale added successfully',
        }

    def generate_sale_id(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))