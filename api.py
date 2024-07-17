from flask import Blueprint, request, redirect, abort, url_for, session
from core.utils.functions import UserHandler, ExtensionsHandler, UploadHandler
import json
from .utils.products import ProductHandler
from .utils.category import CategoryHandler
from .utils.sales import SalesHandler
from .utils.analytics import Analytics
from .utils.string_formatter import Format
from core.utils.functions import SiteConfigHandler

api = Blueprint('pos_api', __name__)
user_handler = UserHandler()
extension_handler = ExtensionsHandler()
category_handler = CategoryHandler()
upload_handler = UploadHandler()
product_handler = ProductHandler()
site_config = SiteConfigHandler()
sale_handler = SalesHandler()
analytics_handler = Analytics()
format_handler = Format()


@api.route('/api/pos/remove_category/<category_id>')
@user_handler.login_required('core.login')
def remove_category(category_id):
    if category_handler.get_category_by_id(category_id) is not None:
        category_handler.remove_category(category_id)
        return redirect(url_for('pos.analytics'))
    else:
        return abort(404)
    
@api.route('/api/pos/remove_product/<product_id>')
@user_handler.login_required('core.login')
def remove_product(product_id):
    if product_handler.get_product_by_id(product_id) is not None:
        product_handler.delete_by_id(product_id)
        return redirect(url_for('pos.analytics'))
    else:
        return abort(404)

@api.route('/api/pos/get_product/category_id/<category_id>')
@user_handler.login_required('core.login')
def get_product_by_category(category_id):
    if category_id == 'all':
        return {
            'status': 'success',
            'data': product_handler.get_products()
        }
    return {
        'status': 'success',
        'data': product_handler.get_product_by_category(category_id)
    }

@api.route('/api/pos/get_product/product_id/<product_id>')
@user_handler.login_required('core.login')
def get_product_by_id(product_id):
    result = product_handler.get_product_by_id(product_id)
    if result:
        return {
            'status': 'success',
            'data': product_handler.get_product_by_id(product_id)
        }
    else:
        return {
            'status': 'error',
            'message': 'Product not found'
        }

@api.route('/api/pos/checkout', methods = ['POST'])
@user_handler.login_required('core.login')
def checkout():
    
    for field in ['cart', 'tendered']:
        if field not in request.form:
            return {
                'status': 'error',
                'message': 'Invalid field'
            }
        if request.form[field] == '':
            return {
                'status': 'error',
                'message': 'Please fill up all fields'
            }
        
    sale_id = sale_handler.generate_sale_id(12)
    cart = json.loads(request.form['cart'])
    operator_id = user_handler.get_by_login_id(session.get('login_id'), safe=True)[0]
    tendered = request.form['tendered']
    for product_id in cart:
        if sale_handler.get_stocks(product_id) < cart[product_id]['quantity']:
            return {
                'status': 'error',
                'message': f'Unable to checkout. Insufficient stocks for {product_handler.get_product_by_id(product_id)["product_name"]}',
                'id': product_id
            }
        
    for product_id in cart:
        result = sale_handler.create_sale(sale_id, product_id, cart[product_id]['quantity'], cart[product_id]['price'], tendered, operator_id)
        if result['status'] == 'error':
            result['id'] = product_id
            return result
    return {
        'status': 'success',
        'message': 'Checkout successful',
        'sale_id': sale_id
    }