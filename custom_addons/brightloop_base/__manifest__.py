# -*- coding: utf-8 -*-
{
    'name': 'Brightloop Base',
    'version': '19.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Shared Foundation and Security for Brightloop Subscription System',
    'description': """
Brightloop Subscription Management System - Shared Foundation
=============================================================
This module provides the central security structure, user roles, top-level
navigation menus, and shared configuration settings for the Brightloop
Subscription Management platform.
    """,
    'author': 'Brightloop Software',
    'website': 'https://www.brightloopsoftware.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/brightloop_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/brightloop_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
