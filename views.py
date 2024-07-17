from flask import Blueprint, render_template, session, url_for, flash, redirect, abort, request
from werkzeug.utils import secure_filename
from core.utils.functions import UserHandler, ExtensionsHandler, UploadHandler
import json
from core.utils.functions import SiteConfigHandler
from .utils.products import ProductHandler
from .utils.category import CategoryHandler
from .utils.sales import SalesHandler
from .utils.analytics import Analytics
from .utils.string_formatter import Format
from .utils.forms import *
from .api import api

extension_config = json.load(open('extensions/pos/extension_config.json'))
pos = Blueprint(extension_config['blueprint'], __name__, template_folder=extension_config['template_folder'], static_folder=extension_config['static_folder'], static_url_path=extension_config['static_url_path'])
pos.register_blueprint(api)

user_handler = UserHandler()
extension_handler = ExtensionsHandler()
category_handler = CategoryHandler()
upload_handler = UploadHandler()
product_handler = ProductHandler()
site_config = SiteConfigHandler()
sale_handler = SalesHandler()
analytics_handler = Analytics()
format_handler = Format()

@pos.route('/test')
def test():
    return analytics_handler.get_sales_for_table()

@pos.route('/dashboard/pos/view_sale/<sale_id>', methods=['GET'])
@user_handler.login_required('core.login')
def view_sale(sale_id):
    sale_data = sale_handler.get_sale_by_id(sale_id)
    if sale_data is None:
        return abort(404)
    return sale_data

@pos.route('/dashboard/pos/analytics', methods=['GET', 'POST'])
@user_handler.login_required('core.login')
def analytics():

    category_form = CategoryForm()
    product_form = ProductForm()

    category_choices_group = []
    for category in category_handler.get_categories():
        category_choices_group.append((category[0], category[1]))
    product_form.product_category.choices = category_choices_group

    if product_form.validate_on_submit():
        file = product_form.product_image.data
        if file.filename == '':
            flash('No file selected. Please select a image file to upload.', 'product_form_error')
        elif not upload_handler.validate_file_type(file.filename, ['png', 'jpg', 'jpeg', 'gif', 'svg']):
            flash('Invalid file type. Please upload an image file.', 'product_form_error')
        else:
            save_filename = f"{upload_handler.generate_filename()}.{upload_handler.get_file_extension(secure_filename(file.filename))}"
            result = product_handler.create_product(product_form.product_name.data, product_form.product_category.data, product_form.product_stocks.data, product_form.product_price.data, save_filename, product_form.product_visibility.data)
            print(result)
            if result['status'] == 'error':
                flash(result['message'], 'product_form_error')
            elif result['status'] == 'success':
                
                file.save(f'extensions/pos/static/products/{save_filename}')
                flash(result['message'], 'product_form_success')

    if category_form.validate_on_submit():
        category_name = category_form.category_name.data
        if category_handler.check_category_exists(category_name) is None:
            category_handler.create_category(category_name)
            flash('Category added successfully', 'category_success')
        else:
            flash('Category already exists', 'category_error')

    sales_dates = [data[0] for data in analytics_handler.get_sales_dates()]
    sales_dates.sort()
    analytics_data = {
        'total_sales': format_handler.convert_to_readable(analytics_handler.get_total_sales()),
        'sales_today': format_handler.convert_to_readable(analytics_handler.get_sales_today()),
        'total_orders': format_handler.convert_to_readable(analytics_handler.get_total_orders()),
        'orders_today': format_handler.convert_to_readable(analytics_handler.get_orders_today()),
        'sales_chart': {
            'sales_dates': sales_dates,
            'sales_values': [analytics_handler.get_sales_by_date(date) for date in sales_dates]
        },
        'sales_table': analytics_handler.get_sales_for_table()
    }
    return render_template('analytics.html', site_config = site_config.get_site_config(), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs(), analytics_data = analytics_data, product_list = product_handler.get_products(), category_list = category_handler.get_categories(), product_form = product_form, category_form = category_form)

@pos.route('/dashboard/pos/sales')
@user_handler.login_required('core.login')
def sales():
    return render_template('sales.html', site_config = site_config.get_site_config(), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())

@pos.route('/dashboard/pos')
@user_handler.login_required('core.login')
def point_of_sales():
    return render_template('pos.html', category_list = category_handler.get_categories(), product_list = product_handler.get_products(), site_config = site_config.get_site_config(), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())

@pos.route('/dashboard/pos/sales/view/<sale_id>')
@user_handler.login_required('core.login')
def view_sale_id(sale_id):
    sale_data = sale_handler.get_sale_by_id(sale_id)
    if sale_data is None:
        return abort(404)
    
    return render_template('view_sale.html', site_config = site_config.get_site_config(), sale_data = sale_data, sale_id = sale_id)



@pos.route('/dashboard/pos/inventory/edit_product/<product_id>', methods=['GET', 'POST'])
@user_handler.login_required('core.login')
def edit_product(product_id):
    
    product_data = product_handler.get_product_by_id(product_id)
    categories = category_handler.get_categories()
    
    if product_data is None:
        return abort(404)
    
    product_form = EditProductForm(edit = True, product_visibility = product_data['visibility'], product_category = product_data['category_name'])
    category_choices_group = [] 
    for category in categories:
        category_choices_group.append((category[0], category[1]))
    product_form.product_category.choices = category_choices_group
    

    if product_form.validate_on_submit():
        file = product_form.product_image.data
        product_data = product_handler.get_product_by_id(product_id)
        save_filename = product_data['filename']
        if file.filename != '':
            if not upload_handler.validate_file_type(file.filename, ['png', 'jpg', 'jpeg', 'gif', 'svg']):
                flash('Invalid file type. Please upload an image file.', 'editproduct_form_error')
                return redirect(url_for('pos.edit_product', product_id=product_id))
            else:
                save_filename = f"{upload_handler.generate_filename()}.{upload_handler.get_file_extension(product_data['filename'])}"
                file.save(f'extensions/pos/static/products/{save_filename}')
                upload_handler.delete_file(f'extensions/pos/static/products/{product_data["filename"]}')
        result = product_handler.edit_by_id(product_id, product_form.product_name.data, product_form.product_category.data, product_form.product_stocks.data, product_form.product_price.data, save_filename, product_form.product_visibility.data)
        if result['status'] == 'success':
            flash(result['message'], 'editproduct_form_success')
            return redirect(url_for('pos.analytics', product_id=product_id))
        else:
            flash(result['message'], 'editproduct_form_error')
    return render_template('edit_product.html', categories = categories, product_data = product_data, product_form = product_form, site_config = site_config.get_site_config(), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())

@pos.route('/dashboard/pos/inventory/edit_category/<category_id>', methods=['GET', 'POST'])
@user_handler.login_required('core.login')
def edit_category(category_id):
    category_form = CategoryForm()
    if category_handler.get_category_by_id(category_id):
        if category_form.validate_on_submit():
            category_handler.edit_category(category_id, category_form.category_name.data)
            return redirect(url_for('pos.analytics'))
        return render_template('edit_category.html', site_config = site_config.get_site_config(), category_form = category_form, category_data = category_handler.get_category_by_id(category_id), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())
    else:
        return abort(404)


