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
    dbname='postgres'
)
cur = conn.cursor()
cur.execute("SELECT pid, datname, state, query_start, query FROM pg_stat_activity WHERE datname='brightloop_dev'")
rows = cur.fetchall()
print(f"Active connections on brightloop_dev: {len(rows)}")
for r in rows:
    print(r[0], r[1], r[2], r[3], str(r[4])[:100])
conn.close()
