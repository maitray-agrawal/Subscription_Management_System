# -*- coding: utf-8 -*-
import configparser
import psycopg2

config = configparser.ConfigParser()
config.read(r'G:\NixelSoft\Odoo 19.0.20260522\server\odoo.conf')
conn = psycopg2.connect(
    host=config.get('options', 'db_host', fallback='localhost'),
    port=config.get('options', 'db_port', fallback='5432'),
    user=config.get('options', 'db_user', fallback='odoo'),
    password=config.get('options', 'db_password', fallback='odoo'),
    dbname='brightloop_dev'
)
cur = conn.cursor()
cur.execute("SELECT name, state FROM ir_module_module WHERE name LIKE '%brightloop%'")
rows = cur.fetchall()
print("Brightloop modules in db:", rows)
conn.close()
