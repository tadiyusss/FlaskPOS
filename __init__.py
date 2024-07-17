from core.utils.logging import Logging
from core.utils.functions import ExtensionsHandler
from .utils.init_db import create_database
import json
import os

def install():
    logging = Logging()
    extension_handler = ExtensionsHandler()
    extension_config = json.load(open('extensions/pos/extension_config.json'))
    if extension_handler.get_extension_config(extension_config['blueprint']) is None or extension_handler.get_extension_config(extension_config['blueprint'])[3] != extension_config['version'] or extension_config['debug']:
        logging.log('Initializing pos extension.', 'info')
        extension_handler.delete_extension_database(extension_config['blueprint'])
        extension_config = json.load(open('extensions/pos/extension_config.json'))
        values = (extension_config['enabled'], extension_config['name'], extension_config['version'], extension_config['description'], extension_config['url_prefix'], extension_config['blueprint'], extension_config['template_folder'], extension_config['static_folder'], extension_config['static_url_path'])
        extension_handler.add_config_to_database(values)

        for tab in extension_config['navigation_tab']:
            extension_handler.add_tab_to_database(extension_config['blueprint'], tab['name'], tab['url_for'])

        logging.log('Extension pos initialized.', 'success')
    else:
        logging.log('Extension pos already initialized.', 'info')
    if os.path.isdir('extensions/pos/static/products') == False:
        os.makedirs('extensions/pos/static/products')
        
install()