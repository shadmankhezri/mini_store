{
    'name': 'Mini store Management',
    'version': '17.0.1.0.0',
    'summary': 'Simple app to manage store',
    'author': 'shadman',
    'depends': ['base','contacts', 'product', 'website'],
    'data': [
        
        'security/ir.model.access.csv',
    
        'views/menu.xml',
        'views/product_views.xml',
        'views/category_views.xml',
        'views/customer_views.xml',
        'views/sale_order_views.xml',
        'views/invoice_views.xml',
        'views/web_templates/payment_success.xml',
        'views/web_templates/payment_failed.xml',
        'views/web_templates/templates.xml',
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
    'application': True,
    
    'assets': {
    'web.assets_backend': [
        'mini_store/static/src/css/product_image.css',
    ],
},

}
