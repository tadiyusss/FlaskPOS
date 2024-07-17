import os
import sqlite3
from .category import CategoryHandler 

class ProductHandler:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_product(self, product_name, category_id, stocks, price, filename, visibility):
        if CategoryHandler().get_category_by_id(category_id) is None:
            return {
                'status': 'error',
                'message': 'Category does not exist',
                'input': 'category_id'
            }
        
        if stocks <= 0:
            return {
                'status': 'error',
                'message': 'Stocks must be greater than 0',
                'input': 'stocks'
            }
        
        if price <= 0:
            return {
                'status': 'error',
                'message': 'Price must be greater than 0',
                'input': 'price'
            }

        self.cursor.execute("INSERT INTO products (product_name, category_id, stocks, price, filename, visibility) VALUES (?, ?, ?, ?, ?, ?)", (product_name, category_id, stocks, price, filename, visibility))
        self.conn.commit()
        return {
            'status': 'success',
            'message': 'Product added successfully',
            'input': None
        }
    
    def decrease_stocks(self, product_id, quantity):
        product_data = self.get_product_by_id(product_id)
        if product_data is None:
            return {
                'status': 'error',
                'message': 'Product does not exist'
            }
        if product_data['stocks'] < quantity:
            return {
                'status': 'error',
                'message': 'Insufficient stocks in inventory'
            }
        self.cursor.execute("UPDATE products SET stocks = stocks - ? WHERE id=?", (quantity, product_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': 'Stocks decreased successfully'
        }

    def get_product_by_name(self, product_name):
        self.cursor.execute("SELECT * FROM products WHERE product_name=?", (product_name,))
        return self.cursor.fetchone()

    def get_product_by_id(self, product_id):
        row = self.cursor.execute("SELECT p.id, p.product_name, p.filename, p.stocks, p.category_id, p.price, c.category_name, p.visibility FROM products p JOIN product_category c ON p.category_id = c.id WHERE p.id = ? AND p.is_deleted = 0", (product_id,)).fetchone()
        if row:
            return {
                    'id': row[0],
                    'product_name': row[1],
                    'filename': row[2],
                    'stocks': row[3],
                    'category_id': row[4],
                    'price': row[5],
                    'category_name': row[6],
                    'visibility': row[7]
                }
        else:
            return None

    def get_product_by_category(self, category_id):
        self.cursor.execute("SELECT p.id, p.product_name, p.filename, p.stocks, p.category_id, p.price, c.category_name FROM products p JOIN product_category c ON p.category_id = c.id WHERE p.category_id = ? AND p.is_deleted = 0", (category_id,))
        return_value = [{
            'id': row[0],
            'product_name': row[1],
            'filename': row[2],
            'stocks': row[3],
            'category_name': row[6],
            'price': row[5]
        } for row in self.cursor.fetchall()]
        return return_value

    def get_products(self):
        self.cursor.execute("SELECT p.id, p.product_name, p.filename, p.stocks, p.category_id, p.price, COALESCE(c.category_name, 'N/A') AS category_name FROM products p LEFT JOIN product_category c ON p.category_id = c.id WHERE p.is_deleted = 0;")
        rows = self.cursor.fetchall()
        return_value = [{
            'id': row[0],
            'product_name': row[1],
            'filename': row[2],
            'stocks': row[3],
            'category_name': row[6],
            'price': row[5]
        } for row in rows]
        
        return return_value

    def delete_by_id(self, product_id):
        sql = "UPDATE products SET is_deleted = 1 WHERE id = ?"
        self.cursor.execute(sql, (product_id,))
        self.conn.commit()
        return {
            'status': 'success',
            'message': 'Product deleted successfully'
        }

    def edit_by_id(self, product_id, product_name, category_id, stocks, price, filename, visibility):
        if CategoryHandler().get_category_by_id(category_id) is None:
            return {
                'status': 'error',
                'message': 'Category does not exist'
            }
        
        self.cursor.execute("UPDATE products SET product_name=?, category_id=?, stocks=?, price=?, filename=?, visibility=? WHERE id=?", (product_name, category_id, stocks, price, filename, visibility, product_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': 'Product updated successfully',
            'data': {
                'product_id': product_id,
                'product_name': product_name,
                'category_id': category_id,
                'stocks': stocks,
                'price': price,
                'filename': filename,
                'visibility': visibility
            }
        }