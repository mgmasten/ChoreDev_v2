from server.server import Server
import server.constants as constants
import server.logger as logger
from datetime import datetime, timedelta
import server.util as util

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

from server.classes import User, House, ChoreScheduler

class Mailer(object):
    def __init__(self, silent=False, verbose=False):
        self.log = logger.create_logger('Mailer', silent=silent, verbose=verbose)

    def connect(self):
        self.log.debug('Connecting to SMTP account...')
        self.conn = SMTP(constants.SMTP_SERVER)
        self.conn.set_debuglevel(False)
        self.conn.login(constants.SMTP_USERNAME, constants.SMTP_PASSWORD)
        self.log.debug('Logged in!')

    def quit(self):
        self.log.debug('Quitting SMTP...')
        self.conn.quit()
        self.log.debug('Quit!')

    def send_invite_email(self, email, invite_token):
        '''email, invite_token, url'''
        self.log.debug('Sending an invite email!')
        msg = MIMEText(constants.INVITE_EMAIL_CONTENT % {'invite_token':invite_token}, constants.SMTP_TYPE)
        msg['Subject'] = "You've been invited to ChoreScores!"
        msg['From'] = constants.SMTP_SENDER

        try:
            self.connect()
            self.conn.sendmail(constants.SMTP_USERNAME, email, msg.as_string())
            self.log.debug('Email sent!')
            self.quit()
            return True
        except:
            self.log.exception('Something went wrong sending the email...')
            self.quit()
            return False

class Authentication(object):
    def __init__(self, silent=False, verbose=False, provision=False):
        self.log = logger.create_logger('Authentication', silent=silent, verbose=verbose)
        self.log.info('Creating Server...')
        self.server = Server(silent=silent, verbose=verbose, provision=provision)
        self.log.info('Server created.')
        self.log.info('Creating Mailer...')
        self.mailer = Mailer(silent=silent, verbose=verbose)
        self.log.info('Mailer created.')
        self.authorized_users = {}
        self.active_houses = {}

        if constants.CHORE_SCHEDULER_ON is True:
            self.log.info('Creating ChoreScheduler...')
            self.chore_scheduler = ChoreScheduler(self.server, silent=silent, verbose=verbose)
            self.log.info('ChoreScheduler created.')

    # -- Private -- #
    def _login(self, user_tuple):
        session_token = str(util.generate_uuid()) # Generate random session token
        house_id = user_tuple[1]
        if house_id in self.active_houses:
            house = self.active_houses[house_id]
        else:
            house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)
            self.active_houses[house_id] = house
        for token in house.get_online_users():
            user = house.get_online_users()[token]
            if user.id == user_tuple[0]:
                self.log.exception('Duplicate login detected...')
                house.remove_user_by_token(token)
                del self.authorized_users[token]
                break

        user = User(house, user_tuple, session_token, datetime.now())
        house.add_user(user)
        # needs to check for duplicate logins
        self.authorized_users[session_token] = user
        self.log.info('Current online: ')
        self.log.info(self.authorized_users)

        return session_token

    def _token_exists(self, token):
        return (token in self.authorized_users)

    def _update_user(self, token):
        if self._token_exists(token):
            self.authorized_users[token].set_timestamp(datetime.now())

    def _is_expired(self, token):
        current_time = datetime.now()
        if self._token_exists(token):
            previous_time = self.authorized_users[token].get_timestamp()
            time_difference_in_minutes = (current_time - previous_time) / timedelta(minutes=1)
            return (time_difference_in_minutes >= constants.MINUTES_TO_LOGOUT)
        else:
            return True

    def _logout(self, token):
        if self._token_exists(token):
            user = self.authorized_users[token]
            user.house.remove_user_by_token(token)
            if len(user.house.get_online_users()) == 0:
                del self.active_houses[user.house.id]
            del self.authorized_users[token]
            return True
        else:
            return False

    def _get_house_id_by_token(self, token):
        if token not in self.authorized_users:
            return None
        return self.authorized_users[token].house_id

    # -- Public -- #

    def token_valid(self, token):
        return self._token_exists(token) # and not self._is_expired(token)

    def logout(self, data):
        if 'session_token' not in data:
            self.log.exception('No session token specified!')
            return {'code': -1}
        if self._logout(data['session_token']): return {'code': 1}
        else: return {'code': 0}

    def login(self, data):
        if 'username' not in data and 'password' not in data:
            self.log.exception('Tried to log in with no data!')
            return {'code': -1}
        user = self.server.db_wrapper.get_user_by_username(data['username'])
        if user is None:
            self.log.exception('Could not find user!')
            return {'code': -2}
        if user[6] == util.md5(data['password']):
            session_token = self._login(user)
            return {'code': 1, 'session_token': session_token}
        else:
            return {'code': 0}

    def register(self, data):
        # Data validation here
        print(data['username'])
        print(data['password'])
        if 'username' not in data or 'password' not in data:
            self.log.exception('Tried to register user with no username or no password!')
            return {'code': -1}
        data['password'] = util.md5(data['password'])
        if 'house_name' not in data and 'invite_token' not in data:
            self.log.exception('Tried to register user with no house!')
            return {'code': -2}
        elif 'invite_token' not in data:
            house_data = {}
            house_data['name'] = data['house_name']
            del data['house_name']
            if 'house_description' in data:
                house_data['description'] = data['house_description']
                del data['house_description']
            house_id = self.server.db_wrapper.insert_house(house_data)
            if house_id is None:
                self.log.exception('Something went wrong creating a house and user!')
                return {'code': -3}
            data['house_id'] = house_id
            self.server.db_wrapper.insert_user(data)
        else:
            # just modify the user
            self.server.db_wrapper.update_user_by_invite(data)
        return {'code': 1}

    def invite(self, data):
        if 'session_token' not in data:
            self.log.exception('Tried to perform invite with no session token!')
            return {'code': -1}
        if 'email' not in data:
            self.log.exception('Tried to invite someone without email!')
            return {'code': -2}
        if not self.token_valid(data['session_token']):
            self.log.exception('Tried to invite with an invalid token: %s!' % data['session_token'])
            return {'code': -3}
        invite_token = str(util.generate_uuid())[:7]
        if not self.server.db_wrapper.insert_user({
            'invite_token': invite_token,
            'house_id': self._get_house_id_by_token(data['session_token'])}):
            self.log.exception('Could not invite user!')
            return {'code': -4}
        self.mailer.send_invite_email(data['email'], invite_token)
        return {'code': 1}

    def get_active_houses(self):
        return self.active_houses

    def get_chore(self, data):
        return self.server.get_chore(data)

    def get_chore_instances(self, data):
        if 'session_token' not in data:
            self.log.exception('Tried to get user chores with no session token!')
            return {'code': -1}
        house_id = self._get_house_id_by_token(data['session_token'])
        if house_id is None:
            self.log.exception('Tried to perform get chores from invalid session token!')
            return {'code': -2}
        try:
            user = self.authorized_users[data['session_token']]
        except:
            self.log.exception('Could not find authorized user from session token!')
            return {'code': -3}
        result = []
        for chore in user.house.chore_instances:
            result.append({
                'name': chore.name,
                'description': chore.description,
                'assigned_user': chore.assigned_user,
                'deadline': chore.deadline,
                'is_completed': chore.is_completed,
                'default_pts': chore.default_pts,
                'difficulty': chore.difficulty,
                'eligible_assignees': chore.eligible_assignees
            })
        return {'code': 1, 'chore_instances': result}


    def add_chore(self, data):
        if 'session_token' not in data:
            self.log.exception('Tried to perform add chore with no session token!')
            return {'code': -1}
        house_id = self._get_house_id_by_token(data['session_token'])
        if house_id is None:
            self.log.exception('Tried to add a chore from invalid session token!')
            return {'code': -2}
        try:
            user = self.authorized_users[data['session_token']]
        except:
            self.log.exception('Could not find authorized user from session token!')
            return {'code': -3}

        return self.server.add_chore(user.id, self.active_houses[house_id], data)

    def get_users(self, data):
        if 'session_token' not in data:
            self.log.exception('Tried to perform get users with no session token!')
            return {'code': -1}
        house_id = self._get_house_id_by_token(data['session_token'])
        if house_id is None:
            self.log.exception('Tried to get users from invalid session token!')
            return {'code': -2}
        return {'code': 1, 'users': self.active_houses[house_id].users}

    def get_all_scores(self, data, date_cutoff):
        if 'session_token' not in data:
            self.log.exception('Tried to fetch scores without session token!')
            return {'code': -1}
        house_id = self._get_house_id_by_token(data['session_token'])
        if house_id is None:
            self.log.exception('Tried to fetch scores from invalid session token!')
            return {'code': -2}
        try:
            user = self.authorized_users[data['session_token']]
            house = self.active_houses[house_id]
        except:
            self.log.exception('Could not find authorized user/house from session token!')
            return {'code': -3}
        return self.server.get_all_scores(house, user.id, date_cutoff)

    def get_chore_instance_list(self, data, order, order_direction, date_cutoff=None):
        if 'session_token' not in data:
            self.log.exception('Tried to fetch chore instance history without session token!')
            return {'code': -1}
        house_id = self._get_house_id_by_token(data['session_token'])
        if house_id is None:
            self.log.exception('Tried to fetch scores from invalid session token!')
            return {'code': -2}
        return self.server.get_chore_instance_list(house_id, order=order, order_direction=order_direction, datetime_cutoff=date_cutoff)
