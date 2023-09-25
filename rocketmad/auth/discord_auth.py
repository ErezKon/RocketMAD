#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
import time
import uuid

from base64 import b64encode
from datetime import datetime
from flask import request, session, url_for

from .oauth2 import OAuth2Base
from ..utils import get_args

log = logging.getLogger(__name__)
args = get_args()

#usrName = ''

class DiscordAuth(OAuth2Base):

    def __init__(self):
        self.guild_id = '734716032270336110'
        self.rl_premium_role = '1155481931736174642'
        self.premium_role = '755468514180988952'
        self.advanced_role = '734762107328790588'
        self.basic_role = '755467984721674363'
        self.member_role = '734761924981555230'

        self.redirect_uri = args.server_uri + '/auth/discord'
        self.client_id = args.discord_client_id
        self.client_secret = args.discord_client_secret
        self.api_base_url = 'https://discord.com/api/v6'
        self.access_token_url = 'https://discord.com/api/oauth2/token'
        self.revoke_token_url = ('https://discord.com/api/oauth2/token/'
                                 'revoke')
        self.authorize_url = 'https://discord.com/api/oauth2/authorize'
        self.scope = 'identify guilds'

        self.fetch_role_guilds = []
        self.required_roles = []
        self.blacklisted_roles = []
        self.access_configs = []

        #self.username = ''

        roles = args.discord_required_roles + args.discord_blacklisted_roles
        for role in roles:
            if ':' in role:
                guild_id = role.split(':')[0]
            else:
                # No guild specified, use first required guild.
                guild_id = args.discord_required_guilds[0]
            if guild_id not in self.fetch_role_guilds:
                self.fetch_role_guilds.append(guild_id)

        for role in args.discord_required_roles:
            if ':' in role:
                guild_id = role.split(':')[0]
                role_id = role.split(':')[1]
            else:
                # No guild specified, use first required guild.
                guild_id = args.discord_required_guilds[0]
                role_id = role
            self.required_roles.append((guild_id, role_id))

        for role in args.discord_blacklisted_roles:
            if ':' in role:
                guild_id = role.split(':')[0]
                role_id = role.split(':')[1]
            else:
                # No guild specified, use first required guild.
                guild_id = args.discord_required_guilds[0]
                role_id = role
            self.blacklisted_roles.append((guild_id, role_id))

        for elem in args.discord_access_configs:
            count = 0
            for c in elem:
                if c == ':':
                    count += 1
            if count == 1:
                guild_id = elem.split(':')[0]
                role_id = None
                config_name = elem.split(':')[1]
            elif count == 2:
                guild_id = elem.split(':')[0]
                role_id = elem.split(':')[1]
                config_name = elem.split(':')[2]
                if guild_id not in self.fetch_role_guilds:
                    self.fetch_role_guilds.append(guild_id)
            self.access_configs.append((guild_id, role_id, config_name))

    def get_authorization_url(self):
        #log.info(f'redirect url is: {self.redirect_uri}')
        session['state'] = str(uuid.uuid4())
        auth_url = ('{}?response_type=code&client_id={}&scope={}&state={}&'
                    'redirect_uri={}&prompt=consent'.format(
                        self.authorize_url, self.client_id,
                        self.scope.replace(' ', '%20'), session['state'],
                        self.redirect_uri))
        #log.info(f'auth url is: {auth_url}')
        return auth_url

    def authorize(self):
        if 'state' not in session:
            log.warning('Invalid Discord authorization attempt: '
                        'no state in session.')
            return False

        state = request.args.get('state')
        if state != session['state']:
            log.warning('Invalid Discord authorization attempt: '
                        'incorrect state.')
            del session['state']
            return False
        del session['state']

        error = request.args.get('error')
        if error is not None:
            if error == 'access_denied':
                log.debug('Discord authorization attempt denied, the resource '
                          'owner denied the request.')
            else:
                error_description = request.args.get('error_description', '')
                log.warning('Discord authorization attempt error: %s',
                            error_description)
            return False

        code = request.args.get('code')
        #log.info(f' code: {code}')

        if code is None:
            log.warning('Invalid Discord authorization attempt: '
                        'access code missing.')
            return False
        try:
            token = self._exchange_code(code)
        except requests.exceptions.HTTPError as e:
            log.warning('Exception while retrieving Discord access token: %s',
                        e)
            return False

        try:
            self._add_user(token)
        except requests.exceptions.HTTPError as e:
            log.warning('Exception while adding Discord user: %s', e)
            return False
        session['auth_type'] = 'discord'
        log.info('Discord user %s succesfully logged in.',
                  session['username'])

        #self.username = session['username']
        #global usrName
        #usrName = session['username']

        return True

    def end_session(self):
        try:
            self._revoke_token(session['token']['access_token'])
        except requests.exceptions.HTTPError as e:
            log.warning('Exception while revoking Discord access token: %s', e)

        log.debug('Discord user %s succesfully logged out.',
                  session['username'])
        session.clear()

    def get_access_data(self):
        if session.get('access_data_updated_at', 0) + 900 < time.time():
            try:
                self._update_access_data()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [400, 401]:
                    log.debug('Exception while retrieving Discord data: %s', e)

                    token = session['token']
                    if token['expires_at'] < time.time():
                        try:
                            token = self._refresh_token(token['refresh_token'])
                            session['token'] = {
                                'access_token': token['access_token'],
                                'refresh_token': token['refresh_token'],
                                'expires_at': (time.time()
                                               + token['expires_in'] - 5)
                            }

                            return self.get_access_data()
                        except requests.exceptions.HTTPError as ex:
                            log.warning('Exception while refreshing Discord '
                                        'token: %s', ex)

                    # Token has (probably) been revoked by user.
                    return False, url_for('login_page'), None

                if e.response.status_code == 429:
                    log.debug('Discord rate limit exceeded: %s', e)
                else:
                    log.warning('Exception while retrieving Discord data: %s',
                                e)

                if 'has_permission' not in session:
                    # Access data is still missing, retry.
                    if e.response.status_code == 429:
                        # We are rate limited, wait a bit.
                        t = int(e.response.headers['x-ratelimit-reset-after'])
                        time.sleep(t)

                    return self.get_access_data()

        has_permission = session['has_permission']
        redirect_uri = (args.discord_no_permission_redirect
                        if not has_permission else None)
        access_config_name = session['access_config_name']

        return has_permission, redirect_uri, access_config_name

    def _get_user_auth(self, roles):
        #log.info('in the user auth')

        is_premium = False
        is_advanced = False
        is_basic = False
        is_member = False

        for role in roles:
            #log.info(f'comparing {role} to {self.premium_role}')
            if role == self.premium_role or role == self.rl_premium_role:
                #log.info(role + ' logged in as premium')
                is_premium = True
            #log.info(f'comparing {role} to {self.advanced_role}')
            if role == self.advanced_role:
                #log.info('found advanced')
                is_advanced = True
            #log.info(f'comparing {role} to {self.basic_role}')
            if role == self.basic_role:
                #log.info('found basic')
                is_basic = True
            if role == self.member_role:
                is_member = True

        if is_premium:
            #log.info('is premium')
            session['is_premium'] = True
            session['is_advanced'] = True
            session['is_basic'] = True
            session['is_member'] = True
            session['auth_role'] = 3
            return
        elif is_advanced:
            #log.info('is advanced')
            session['is_premium'] = False
            session['is_advanced'] = True
            session['is_basic'] = True
            session['is_member'] = True
            session['auth_role'] = 2
        elif is_basic:
            #log.info('is basic')
            session['is_premium'] = False
            session['is_advanced'] = False
            session['is_basic'] = True
            session['is_member'] = True
            session['auth_role'] = 1
        elif is_member:
            #log.info('is member')
            session['is_premium'] = False
            session['is_advanced'] = False
            session['is_basic'] = False
            session['is_member'] = True
            session['auth_role'] = 0
        else:
            #log.info('is none')
            session['is_premium'] = False
            session['is_advanced'] = False
            session['is_basic'] = False
            session['is_member'] = False

    def _update_access_data(self):
        authorizedRole = False
        session['authorizedRole'] = False
        if session['id'] in args.discord_blacklisted_users:
            session['has_permission'] = False
            session['access_config_name'] = None
            return

        user_guilds = self._get_guilds()
        user_roles = {}
        for guild_id in self.fetch_role_guilds:
            if guild_id in user_guilds:
                roles = self._get_roles(guild_id, session['id'])
                user_roles[guild_id] = roles

        # Whitelisted users/admins bypass other whitelists/blacklists.
        if (session['id'] in args.discord_whitelisted_users
                or session['id'] in args.discord_admins):
            session['has_permission'] = True
            config_name = self._get_access_config_name(user_guilds, user_roles)
            session['access_config_name'] = config_name
            session['access_data_updated_at'] = time.time()
            return

        # Check required guilds.
        in_required_guild = any(guild_id in user_guilds
                                for guild_id in args.discord_required_guilds)
        if args.discord_required_guilds and not in_required_guild:
            session['has_permission'] = False
            session['access_config_name'] = None
            return

        # Check blacklisted guilds.
        for guild_id in args.discord_blacklisted_guilds:
            if guild_id in user_guilds:
                session['has_permission'] = False
                session['access_config_name'] = None
                return

        roles = user_roles[self.guild_id]
        #log.info(f'roles: {roles}')
        self._get_user_auth(roles)

        # Check required roles.
        has_required_role = any(role[0] in user_guilds
                                and role[1] in user_roles[role[0]]
                                for role in self.required_roles)
        if self.required_roles and not has_required_role:
            session['has_permission'] = False
            session['access_config_name'] = None
            return

        # Check blacklisted roles:
        for role in self.blacklisted_roles:
            guild_id = role[0]
            role_id = role[1]
            if guild_id in user_guilds and role_id in user_roles[guild_id]:
                session['has_permission'] = False
                session['access_config_name'] = None
                return

        session['has_permission'] = True
        config_name = self._get_access_config_name(user_guilds, user_roles)
        session['access_config_name'] = config_name
        session['access_data_updated_at'] = time.time()

    def _get_access_config_name(self, guilds, roles):
        access_config_name = None
        for elem in self.access_configs:
            guild_id = elem[0]
            role_id = elem[1]
            config_name = elem[2]

            if role_id is not None:
                if guild_id in guilds and role_id in roles[guild_id]:
                    access_config_name = config_name
                    break
            else:
                if guild_id in guilds:
                    access_config_name = config_name
                    break

        return access_config_name

    def _add_user(self, token):
        headers = {
            'Authorization': 'Bearer ' + token['access_token']
        }
        r = requests.get(self.api_base_url + '/users/@me', headers=headers)
        r.raise_for_status()
        user = r.json()

        session['id'] = user['id']
        session['username'] = user['username']
        #self.username = user['username']
        #global usrName
        #usrName = user['username']
        session['token'] = {
            'access_token': token['access_token'],
            'refresh_token': token['refresh_token'],
            'expires_at': time.time() + token['expires_in'] - 5
        }

    def _exchange_code(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(self.access_token_url, data=data, headers=headers)
        r.raise_for_status()
        return r.json()

    def _refresh_token(self, refresh_token):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(self.access_token_url, data=data, headers=headers)
        r.raise_for_status()
        return r.json()

    def _revoke_token(self, access_token):
        data = self.client_id + ':' + self.client_secret
        bytes = b64encode(data.encode("utf-8"))
        encoded_creds = str(bytes, "utf-8")
        headers = {
            'Authorization': 'Basic ' + encoded_creds,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = 'token=' + access_token
        r = requests.post(self.revoke_token_url, data=data, headers=headers)
        r.raise_for_status()

    def _get_guilds(self):
        headers = {
            'Authorization': 'Bearer ' + session['token']['access_token']
        }
        r = requests.get(self.api_base_url + '/users/@me/guilds',
                         headers=headers)
        r.raise_for_status()
        guilds = r.json()
        guilds_dict = {}
        for guild in guilds:
            guilds_dict[guild['id']] = guild
        return guilds_dict

    def _get_roles(self, guild_id, user_id):
        headers = {
            'Authorization': 'Bot ' + args.discord_bot_token
        }
        r = requests.get(
            self.api_base_url + '/guilds/' + guild_id + '/members/' + user_id,
            headers=headers
        )
        r.raise_for_status()
        return r.json()['roles']
