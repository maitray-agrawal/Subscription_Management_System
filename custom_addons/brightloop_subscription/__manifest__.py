# -*- coding: utf-8 -*-
{
    'name': 'Brightloop Subscription Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Core Subscription Lifecycle, Plans, Variants, and Quotation Management',
    'description': """
Brightloop Subscription Management System - Core Subscriptions
==============================================================
Manages subscription products, product variants with price surcharges,
flexible recurrence plans (daily, weekly, monthly, yearly), quotation
templates, and contract lifecycle state machine (Draft -> Quotation -> Confirmed -> Active -> Closed).
    """,
    'author': 'Brightloop Software',
    'website': 'https://www.brightloopsoftware.com',
    'depends': [
        'base',
        'mail',
        'portal',
        'product',
        'account',
        'brightloop_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/subscription_security.xml',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/product_views.xml',
        'views/subscription_plan_views.xml',
        'views/quotation_template_views.xml',
        'views/subscription_views.xml',
        'views/subscription_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
