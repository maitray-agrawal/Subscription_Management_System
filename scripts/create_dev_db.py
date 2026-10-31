# -*- coding: utf-8 -*-
import configparser
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    config = configparser.ConfigParser()
    config.read(r'G:\NixelSoft\Odoo 19.0.20260522\server\odoo.conf')
    conn = psycopg2.connect(
        host=config.get('options', 'db_host', fallback='localhost'),
        port=config.get('options', 'db_port', fallback='5432'),
        user=config.get('options', 'db_user', fallback='odoo'),
        password=config.get('options', 'db_password', fallback='odoo'),
        dbname='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='brightloop_dev'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE brightloop_dev WITH OWNER odoo TEMPLATE template0 ENCODING 'UTF8'")
        print("Created database brightloop_dev successfully!")
    else:
        print("Database brightloop_dev already exists.")
    conn.close()

if __name__ == '__main__':
    create_database()
