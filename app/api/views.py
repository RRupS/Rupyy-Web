from flask import render_template, request, jsonify
from . import api
import app.utils

import os
from dotenv import load_dotenv

load_dotenv()

@api.route('/get-member', methods=['GET'])
def get_member():
    member_id = request.args.get('member_id')
    guild_id = request.args.get('guild_id')
    data = {
        'member-id': member_id,
        'guild-id': guild_id,
        'level': app.utils.get_level_member(int(member_id), guild_id),
        'xp': app.utils.get_xp_member(member_id, guild_id),
        'max-xp': app.utils.get_max_xp_member(member_id, guild_id)
    }
    return jsonify(data)

@api.route('/get-guild', methods=['GET'])
def get_server():
    guild_id = request.args.get('guild_id')
    data = {
        'guild-id': guild_id,
        'general-xp': app.utils.get_xp_guild(guild_id, 'general'),
        'monthly-xp': app.utils.get_xp_guild(guild_id, 'monthly'),
        'weekly-xp': app.utils.get_xp_guild(guild_id, 'weekly'),
        'daily-xp': app.utils.get_xp_guild(guild_id, 'daily')
    }
    return jsonify(data)

@api.route('/add-xp-member', methods=['PATCH'])
def add_xp_member():
    if request.method == 'PATCH':
        if request.headers.get('Authorization') == 'Bot %s' % os.getenv('TOKEN'):
            json = request.get_json()
            if 'member_id' in json.keys() and 'guild_id' in json.keys() and 'xp' in json.keys():
                member_id = json['member_id']
                guild_id = json['guild_id']
                xp = json['xp']
                app.utils.add_xp_member(member_id, guild_id, xp)
                data = {
                    'code': '200',
                    'message': 'OK'
                }
                return jsonify(data), 200
            else:
                data = {
                    'code': '400',
                    'message': 'Bad Request'
                }
                return jsonify(data), 400
        else:
            data = {
                'code': '401',
                'message': 'Unauthorized'
            }
            return jsonify(data), 401
    else:
        data = {
            'code': '405',
            'message': 'Method Not Allowed'
        }
        return jsonify(data), 405

@api.route('/add-xp-guild', methods=['PATCH'])
def add_xp_guild():
    if request.method == 'PATCH':
        if request.headers.get('Authorization') == 'Bot %s' % os.getenv('TOKEN'):
            json = request.get_json()
            if 'guild_id' in json.keys() and 'xp' in json.keys():
                guild_id = json['guild_id']
                xp = json['xp']
                app.utils.add_xp_guild(guild_id, xp)
                data = {
                    'code': '200',
                    'message': 'OK'
                }
                return jsonify(data), 200
            else:
                data = {
                    'code': '400',
                    'message': 'Bad Request'
                }
                return jsonify(data), 400
        else:
            data = {
                'code': '401',
                'message': 'Unauthorized'
            }
            return jsonify(data), 401
    else:
        data = {
            'code': '405',
            'message': 'Method Not Allowed'
        }
        return jsonify(data), 405

@api.route('/reset-xp-guilds', methods=['PATCH'])
def reset_xp_guilds():
    if request.method == 'PATCH':
        if request.headers.get('Authorization') == 'Bot %s' % os.getenv('TOKEN'):
            json = request.get_json()
            if 'time_interval' in json.keys():
                app.utils.reset_xp_guilds(json['time_interval'])
                data = {
                    'code': '200',
                    'message': 'OK'
                }
                return jsonify(data), 200
            else:
                data = {
                    'code': '400',
                    'message': 'Bad Request'
                }
                return jsonify(data), 400
        else:
            data = {
                'code': '401',
                'message': 'Unauthorized'
            }
            return jsonify(data), 401
    else:
        data = {
            'code': '405',
            'message': 'Method Not Allowed'
        }
        return jsonify(data), 405