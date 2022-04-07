import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DiscordAPI:
    token = os.getenv('TOKEN')
    api_endpoint = 'https://discord.com/api/v6'

    # Get all guild members
    @staticmethod
    def get_all_users(guild_id):
        user_list = requests.get(
            url = f'{DiscordAPI.api_endpoint}/guilds/{guild_id}/members',
            headers = {'Authorization': 'Bot %s' % DiscordAPI.token},
            params = {'limit': 1000}
        ).json()

        return user_list

    # Get all guild roles
    @staticmethod
    def get_all_roles(guild_id):
        role_list = requests.get(
            url = f'{DiscordAPI.api_endpoint}/guilds/{guild_id}/roles',
            headers = {'Authorization': 'Bot %s' % DiscordAPI.token}
        ).json()

        return role_list

    # Get guild role
    @staticmethod
    def get_role(rid, guild_id):
        role = requests.patch(
            url = f'{DiscordAPI.api_endpoint}/guilds/{guild_id}/roles/{rid}',
            headers = {
                'Authorization': 'Bot %s' % DiscordAPI.token,
                'Content-Type': 'application/json'
            },
            json = {}
        ).json()

        return role

    # Get guild staffs
    @staticmethod
    def get_staff_list(guild_id, staff_roles):
        staff_list = []
        all_roles = DiscordAPI.get_all_roles(guild_id)
        for user in DiscordAPI.get_all_users(guild_id):
            for staff_role_id in staff_roles: 
                if staff_role_id in user['roles']:
                    staff_list.append(user)
        for index, staff in enumerate(staff_list):
            position = 0
            staff_list[index]['highest_role'] = 'Discord Staff'
            staff_list[index]['highest_role_position'] = 0
            staff_list[index]['highest_role_color'] = 0
            for staff_role in staff['roles']:
                for role in all_roles:
                    if staff_role == role['id']:
                        if role['position'] > position:
                            if role['hoist'] == True:
                                position = role['position']
                                staff_list[index]['highest_role'] = role['name']
                                staff_list[index]['highest_role_position'] = role['position']
                                staff_list[index]['highest_role_color'] = role['color']
        staff_list = sorted(staff_list, key=lambda x: x['highest_role_position'], reverse=True)

        return staff_list