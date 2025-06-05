{
    'name': 'Mini store Management',
    'version': '17.0.1.0.0',
    'summary': 'Simple app to manage store',
    'author': 'shadman',
    'depends': ['base','contacts', 'product', 'website', 'sale'],
    'data': [
        
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/product_views.xml',
        'views/category_views.xml',
        'views/customer_views.xml',
        'views/sale_order_views.xml',
        'report/report_invoice.xml',
        'views/invoice_views.xml',
        
    
        'views/web_templates/payment_success.xml',
        'views/web_templates/payment_failed.xml',
        'views/web_templates/templates.xml',
        'data/ir_sequence_data.xml',
    ],
    'tests': [
        'tests/test_sale_order.py',
    ],
    'installable': True,
    'application': True,
    
    'assets': {
    'web.assets_backend': [
        'mini_store/static/src/css/product_image.css',
    ],
},

}
