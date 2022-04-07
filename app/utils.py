# --- Imports --- #
import sqlite3
import json
import requests
import os
from dotenv import load_dotenv
# --------------- #

guild_categories = [
    'Oyun',
    'Sosyal',
    'Eğlence',
    'Anime',
    'Meme',
    'Müzik',
    'Roleplay',
    'Minecraft',
    'Moderasyon',
    'Çekiliş'
]

# --- Database Connection --- #
with sqlite3.connect('app/database.sqlite') as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS guilds (guild_id INT, general_xp INT, monthly_xp INT, weekly_xp INT, daily_xp INT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS members (member_id INT, level, xp, max_xp)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS guild_settings (guild_id INT, categories, invite_link, staff_list INT, top10 INT, staff_role_id)""")
# --------------------------- #

load_dotenv()

def create_member(member_id, guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO members (member_id, level, xp, max_xp) VALUES (?, ?, ?, ?)", (member_id, json.dumps({guild_id: 0}), json.dumps({guild_id: 0}), json.dumps({guild_id: 1000})))
        con.commit()

def create_guild(guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO guilds (guild_id, general_xp, monthly_xp, weekly_xp, daily_xp) VALUES ({guild_id}, 0, 0, 0, 0)")
        con.commit()

def add_xp_member(member_id, guild_id, xp):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        guild_id = str(guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        if cur.fetchall() == []: create_member(member_id, guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        data = cur.fetchone()
        level_json = json.loads(data[1])
        xp_json = json.loads(data[2])
        max_xp_json = json.loads(data[3])
        if guild_id not in level_json.keys():
            level_json[guild_id] = 0
            xp_json[guild_id] = xp
            max_xp_json[guild_id] = 1000
            cur.execute("UPDATE members SET level = ?, xp = ?, max_xp = ? WHERE member_id = ?", (json.dumps(level_json), json.dumps(xp_json), json.dumps(max_xp_json), member_id))
            con.commit()
        else:
            if xp+xp_json[guild_id] > max_xp_json[guild_id]:
                xp_json[guild_id] += xp
                level_json[guild_id] += 1
                max_xp_json[guild_id] = int(max_xp_json[guild_id]*2.5)
            else:
                xp_json[guild_id] += xp
            cur.execute("UPDATE members SET level = ?, xp = ?, max_xp = ? WHERE member_id = ?", (json.dumps(level_json), json.dumps(xp_json), json.dumps(max_xp_json), member_id))
            con.commit()

def add_xp_guild(guild_id, xp):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guilds WHERE guild_id = {guild_id}")
        if cur.fetchall() == []: create_guild(guild_id)
        cur.execute(f"SELECT * FROM guilds WHERE guild_id = {guild_id}")
        data = cur.fetchone()
        cur.execute("UPDATE guilds SET general_xp = ?, monthly_xp = ?, weekly_xp = ?, daily_xp = ? WHERE guild_id = ?", (data[1]+xp, data[2]+xp, data[3]+xp, data[4]+xp, guild_id))
        con.commit()

def get_xp_member(member_id, guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        guild_id = str(guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        if cur.fetchall() == []: create_member(member_id, guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        data = cur.fetchone()
        xp_json = json.loads(data[2])
        if guild_id not in xp_json.keys():
            cur.execute("INSERT INTO members (member_id, level, xp, max_xp) VALUES (?, ?, ?, ?)", (member_id, json.dumps({guild_id: 0}), json.dumps({guild_id: 0}), json.dumps({guild_id: 1000})))
            con.commit()
            return 0
        else:
            return xp_json[guild_id]

def get_max_xp_member(member_id, guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        guild_id = str(guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        if cur.fetchall() == []: create_member(member_id, guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        data = cur.fetchone()
        max_xp_json = json.loads(data[3])
        if guild_id not in max_xp_json.keys():
            cur.execute("INSERT INTO members (member_id, level, xp, max_xp) VALUES (?, ?, ?, ?)", (member_id, json.dumps({guild_id: 0}), json.dumps({guild_id: 0}), json.dumps({guild_id: 1000})))
            con.commit()
            return 1000
        else:
            return max_xp_json[guild_id]

def get_level_member(member_id, guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        guild_id = str(guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        if cur.fetchall() == []: create_member(member_id, guild_id)
        cur.execute(f"SELECT * FROM members WHERE member_id = {member_id}")
        data = cur.fetchone()
        level_json = json.loads(data[1])
        if guild_id not in level_json.keys():
            cur.execute("INSERT INTO members (member_id, level, xp, max_xp) VALUES (?, ?, ?, ?)", (member_id, json.dumps({guild_id: 0}), json.dumps({guild_id: 0}), json.dumps({guild_id: 1000})))
            con.commit()
            return 0
        else:
            return level_json[guild_id]

def get_xp_guild(guild_id, time_interval):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guilds WHERE guild_id = {guild_id}")
        if cur.fetchall() == []: create_guild(guild_id)
        if time_interval in ['general', 'monthly', 'weekly', 'daily']:
            cur.execute(f"SELECT {time_interval}_xp FROM guilds WHERE guild_id = {guild_id}")
            return cur.fetchone()[0]

def reset_xp_guilds(time_interval):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guilds")
        guilds = cur.fetchall()
        for guild in guilds:
            cur.execute(f"UPDATE guilds SET {time_interval}_xp = 0 WHERE guild_id = {guild[0]}")
            con.commit()

def get_guilds_sorted(time_interval):
    if time_interval == 'general': index = 1
    if time_interval == 'monthly': index = 2
    if time_interval == 'weekly': index = 3
    if time_interval == 'daily': index = 4
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guilds")
        guilds = cur.fetchall()
        guilds = sorted(guilds, key=lambda x: x[index], reverse=True)
    return guilds

def get_guild_top10(guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        guild_id = str(guild_id)
        cur.execute(f"SELECT * FROM members")
        members = cur.fetchall()
        new_members = []
        for member in members:
            if guild_id in json.loads(member[1]).keys():
                new_members.append(member)
        new_members = sorted(new_members, key=lambda x: json.loads(x[2])[guild_id], reverse=True)
    return new_members

def get_guild_info(guild_id):
    server_info = requests.get(
        url = f'https://discord.com/api/v6/guilds/{guild_id}',
        headers = {
            'Authorization': 'Bot {}'.format(os.getenv('TOKEN'))
        }
    ).json()
    if 'message' in server_info:
        delete_guild(guild_id)
        return None
    return server_info

def get_user_info(user_id):
    user_info = requests.get(
        url = f'https://discord.com/api/v6/users/{user_id}',
        headers = {
            'Authorization': 'Bot {}'.format(os.getenv('TOKEN'))
        }
    ).json()
    return user_info

def get_database():
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM guilds")
        guilds = cur.fetchall()
        cur.execute("SELECT * FROM members")
        members = cur.fetchall()
    data = {
        'guilds': guilds,
        'members': members 
    }
    return data

def get_guild_description(guild_id):
    with open('app/guild_descriptions/{}.txt'.format(guild_id), 'w') as f: f.close()
    with open('app/guild_descriptions/{}.txt'.format(guild_id), 'r') as f:
        return f.read()

def update_guild_description(guild_id, description):
    with open('app/guild_descriptions/{}.txt'.format(guild_id), 'w') as f:
        f.write(description)

def create_guild_settings(guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO guild_settings (guild_id, categories, staff_list, top10, staff_role_id) VALUES ({guild_id}, '0', 0, 0, '0')")
        con.commit()

def get_guild_settings(guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}")
        if cur.fetchall() == []: create_guild_settings(guild_id)
        cur.execute(f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}")
        guild_settings = cur.fetchone()
        data = {
            'categories': guild_settings[1].split(','),
            'invite_link': guild_settings[2],
            'staff_list': guild_settings[3],
            'top10': guild_settings[4],
            'staff_role_id': guild_settings[5]
        }
    return data

def update_guild_settings(categories, invite_link, staff_list, top10, staff_role_id, guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}")
        if cur.fetchall() == []: create_guild_settings(guild_id)
        cur.execute("UPDATE guild_settings SET categories = ?, invite_link = ?, staff_list = ?, top10 = ?, staff_role_id = ? WHERE guild_id = ?", (str(categories), invite_link, staff_list, top10, staff_role_id, guild_id))
        con.commit()

def delete_guild(guild_id):
    with sqlite3.connect('app/database.sqlite') as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM guilds WHERE guild_id = {guild_id}")
        con.commit()