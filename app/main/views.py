from tracemalloc import start
from flask import render_template, redirect, session, request, jsonify, url_for, make_response
from . import main
from app.routes.discord_oauth import DiscordOauth
from app.routes.discord_api import DiscordAPI
import app.utils
from functools import wraps
import json


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in request.cookies:
            return redirect(DiscordOauth.login_url)
        return f(*args, **kwargs)
    return decorated_function


@main.route('/')
def index():
    guilds = app.utils.get_guilds_sorted('general')
    staff_list = DiscordAPI.get_staff_list(952129220748918804, ['952130099363340288', '952130593716600832', '953009896750739506'])
    guild_names, guild_icons = {}, {}
    for index, guild in enumerate(guilds, start=1):
        if index < 11:
            guild_info = app.utils.get_guild_info(guild[0])
            if guild_info:
                guild_names[str(guild[0])] = guild_info['name']
                guild_icons[str(guild[0])] = guild_info['icon']
            else:
                guild_names[str(guild[0])] = 'bilinmeyen sunucu'
                guild_icons[str(guild[0])] = ''
    if 'token' in request.cookies:
        user_object = DiscordOauth.get_user(request.cookies.get('token'))
        return render_template('index.html', guilds=guilds, enumerate=enumerate, guild_names=guild_names, guild_icons=guild_icons, user=user_object, staff_list=staff_list, hex=hex, get_guild_settings=app.utils.get_guild_settings, str=str)
    return render_template('index.html', guilds=guilds, enumerate=enumerate, guild_names=guild_names, guild_icons=guild_icons, oauth_url=DiscordOauth.login_url, staff_list=staff_list, hex=hex, get_guild_settings=app.utils.get_guild_settings, str=str)

@main.route('/server/<id>')
def server(id):
    guild = app.utils.get_guild_info(id)
    guild_xp = {
        'general': app.utils.get_xp_guild(id, 'general'),
        'monthly': app.utils.get_xp_guild(id, 'monthly'),
        'weekly': app.utils.get_xp_guild(id, 'weekly'),
        'daily': app.utils.get_xp_guild(id, 'daily')
    }
    guild_top10 = app.utils.get_guild_top10(id)
    guild_settings = app.utils.get_guild_settings(id)
    guild_description = app.utils.get_guild_description(id)
    user_names, user_avatars, user_discriminators = {}, {}, {}
    for index, user in enumerate(guild_top10, start=1):
        if index < 11:
            user_info = app.utils.get_user_info(user[0])
            user_names[user[0]] = user_info['username']
            user_avatars[user[0]] = user_info['avatar']
            user_discriminators[user[0]] = user_info['discriminator']
    user_info = app.utils.get_user_info(guild['owner_id'])
    user_names[guild['owner_id']] = user_info['username']
    user_avatars[guild['owner_id']] = user_info['avatar']
    user_discriminators[guild['owner_id']] = user_info['discriminator']
    staff_list = DiscordAPI.get_staff_list(id, [guild_settings.get('staff_role_id')])
    if 'token' in request.cookies:
        user_object = DiscordOauth.get_user(request.cookies.get('token'))
        return render_template('server.html', user=user_object, guild=guild, guild_xp=guild_xp, guild_top10=guild_top10, user_names=user_names, user_avatars=user_avatars, user_discriminators=user_discriminators, enumerate=enumerate, json=json, guild_description=guild_description, guild_settings=guild_settings, staff_list=staff_list, hex=hex, list=list)
    return render_template('server.html', oauth_url=DiscordOauth.login_url, guild=guild, guild_xp=guild_xp, guild_top10=guild_top10, user_names=user_names, user_avatars=user_avatars, user_discriminators=user_discriminators, enumerate=enumerate, json=json, guild_description=guild_description, guild_settings=guild_settings, staff_list=staff_list, hex=hex, list=list)

@main.route('/dashboard')
@login_required
def dashboard():
    user_object = DiscordOauth.get_user(request.cookies.get('token'))
    user_guild_object = DiscordOauth.get_user_current_guild(request.cookies.get('token'))
    return render_template('dashboard.html', user=user_object, render_guild=user_guild_object, get_guild_info=app.utils.get_guild_info)

@main.route('/dashboard/manage-server/<id>', methods=['GET', 'POST'])
@login_required
def manage_server(id):
    user_object = DiscordOauth.get_user(request.cookies.get('token'))
    user_guild_object = DiscordOauth.get_user_current_guild(request.cookies.get('token'))
    for i in user_guild_object:
        if str(i['id']) == str(id): is_owner = i['owner']
    if is_owner:
        guild = app.utils.get_guild_info(id)
        if guild.get('message') == 'Missing Access': return redirect('https://discord.com/oauth2/authorize?client_id=952132822460690442&scope=bot&permissions=0&redirect_uri=https://ruppy.herokuapp.com/dashboard')
        guild_settings = app.utils.get_guild_settings(id)
        guild_description = app.utils.get_guild_description(id)
        guild_categories = app.utils.guild_categories
        if request.method == 'POST':
            description = request.form.get('description')
            categories = request.form.getlist('category')
            invite_link = request.form.get('invite_link')
            staff_role_id = request.form.get('staff_role_id')
            if request.form.get('staff_list') == 'on': staff_list = 1
            else: staff_list = 0
            if request.form.get('top10') == 'on': top10 = 1
            else: top10 = 0
            app.utils.update_guild_settings(','.join(categories), invite_link, staff_list, top10, staff_role_id, id)
            app.utils.update_guild_description(id, description)
            return redirect(f'/dashboard/manage-server/{id}')
        return render_template('manage-server.html', user=user_object, guild=guild, guild_settings=guild_settings, guild_description=guild_description, guild_categories=guild_categories, enumerate=enumerate)
    return redirect('/dashboard')

@main.route('/oauth/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    access_token = DiscordOauth.get_access_token(code)
    resp = make_response(redirect('/dashboard'))
    resp.set_cookie('token', access_token)
    return resp

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@main.route('/test')
def test():
    return str(app.utils.test())