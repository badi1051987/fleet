

{
    'name': 'Fleet System Enh',
    'version': '16.0.1.1.1',
    'description': """Fleet System Enh""",
    'summary': """Fleet System Enh""",
    'author': 'AB',
    'depends': ['base','fleet','account','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_view.xml',
        'wizard/vendor_bill.xml',
        'wizard/invoice_wizard_views.xml',
    ],
    'images': ['static/description/image.png'],
    'author': 'AB',
    'maintainer': 'AB',
    'website': 'https://AB.co/',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    "price": 3,
    "currency": 'USD'
}
