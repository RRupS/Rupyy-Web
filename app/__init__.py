from flask import Flask

from app.main.views import main
from app.admin.views import admin
from app.api.views import api

import os
import sqlite3
# from flask_wtf.csrf import CSRFProtect

# csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config.update(
        SESSION_COOKIE_SECURE = True,
        SESSION_COOKIE_HTTPONLY = True,
        SESSION_COOKIE_SAMESITE = 'Lax',
        PERMANENT_SESSION_LIFETIME = 1200
    )
    # csrf.init_app(app)
    # csrf.exempt(api)
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(api, url_prefix='/api')
    
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS guilds (guild_id INT, general_xp INT, monthly_xp INT, weekly_xp INT, daily_xp INT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS members (member_id INT, level, xp, max_xp)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS guild_settings (guild_id INT, categories, invite_link, staff_list INT, top10 INT, staff_role_id)""")
    return app