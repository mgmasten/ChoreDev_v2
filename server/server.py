from server.database import DbWrapper
import server.logger as logger
import server.util as util
import server.constants as constants
from server.classes import ChoreScheduler, House, ChoreInstance

class Server(object):

    def __init__(self, silent=False, verbose=False, provision=False):
        self.log = logger.create_logger('Server', silent=silent, verbose=verbose)

        self.log.info('Creating database wrapper...')
        self.db_wrapper = DbWrapper(silent=silent, verbose=verbose, provision=provision)
        self.log.info('Database wrapper created.')

    def truth_value_to_code(self, truth_value):
        if truth_value is True:
            return {'code': 1}
        else:
            return {'code': 0}

    def add_chore(self, uid, house, chore_data):
        chore_data['default_pts'] = constants.DEFAULT_PTS[chore_data['difficulty']]
        return self.truth_value_to_code(house.add_chore(uid, chore_data))
        # Chore instances are not updated until next week

    def delete_chore(self, chore_data):
        # Need chore_id, house_id
        house = House(self.db_wrapper.get_house_by_id(chore_data['house_id']), self.db_wrapper)
        return self.truth_value_to_code(house.delete_chore(chore_data['id']))
        # Chore instances are not updated until next week

    def update_chore(self, chore_data):
        # Need chore_id, house_id, and any updated properties
        house = House(self.db_wrapper.get_house_by_id(chore_data['house_id']), self.db_wrapper)
        return self.truth_value_to_code(house.update_chore(chore_data))
        # Chore instances are not updated until next week--this creates problems because
        # if you need to load a chore instance, the parent will be gone
        # So either chore_instances need to be deleted too, or need to not delete
        # parent until next week

    def get_chore(self, chore_data):
        # Need chore_id, house_id
        house = House(self.db_wrapper.get_house_by_id(chore_data['house_id']), self.db_wrapper)
        chore_array = house.get_chore(chore_data['id'])
        return {'id': chore_array[0],
                'house_id': chore_array[1],
                'creator_id': chore_array[2],
                'eligible_assignees': chore_array[3],
                'difficulty': chore_array[4],
                'occurs_on': chore_array[5],
                'description': chore_array[6],
                'name': chore_array[7],
                'default_pts': chore_array[8]}

    def get_user_profile(self, user_data):
        # Need house_id, username
        house = House(self.db_wrapper.get_house_by_id(user_data['house_id']), self.db_wrapper)
        user_array = self.db_wrapper.get_user_by_username(user_data['username'])
        return {'id': user_array[0],
                'house_id': user_array[1],
                'username': user_array[2],
                'email': user_array[3],
                'nickname': user_array[4],
                'invite_token': user_array[5]}
                # Does not send password back
                # Should it send the length or that many *'s?

    def update_user(self, user_data):
        # Need username
        # Can update nickname, password, (avatar)

        # This should never be called when the user isn't online
        #house = House(self.db_wrapper.get_house_by_id(user_data['house_id']), self.db_wrapper)
        #user = house.get_online_users()[user_data['session_token']]

        if 'password' in user_data:
            user_data['password'] = util.md5(user_data['password'])

        user_data['username'] = user_data['username']
        self.db_wrapper.update_user_by_username(user_data)

        #user.load(house, self.db_wrapper.get_user_by_username(user.username), user_data['session_token'], user.get_timestamp())
        #house.add_user(user)

    def get_house_profile(self, house_data):
        # Need house_id
        house = House(self.db_wrapper.get_house_by_id(house_data['id']), self.db_wrapper)

        housemates = house.get_housemate_list()
        nicknames = '' # string here? Or would a list be okay?
        # Returns username if user has no nickname
        for housemate in housemates:
            if housemate[4] is None:
                nicknames += str(housemate[2]) + ';'
            else:
                nicknames += str(housemate[4]) + ';'

        chores = house.get_chore_list()
        chore_names = '' # string here? Or would a list be okay?
        for chore in chores:
            chore_names += str(chore[7]) + ';'

        return {'name': house.name,
                'housemate_nicknames': nicknames,
                'chore_names': chore_names
                }

    def get_all_house_ids(self):
        return [record[0] for record in self.db_wrapper.get_all_houses()]

    def update_house(self, house_data):
        # Only name and description can be updated. Chore list can be updated, but only by
        # clicking on an individual chore and deleting it
        house = House(self.db_wrapper.get_house_by_id(house_data['id']), self.db_wrapper)
        house.update(house_data)

    def complete_chore_instance(self, chore_instance_data):
        # Needs chore_instance_id
        print('complete chore instance')
        print(self.db_wrapper.get_chore_instance_by_id(chore_instance_data['id']))
        chore_instance = ChoreInstance(self.db_wrapper, self.db_wrapper.get_chore_instance_by_id(chore_instance_data['id']))
        chore_instance.complete()

    def get_chore_instance(self, chore_instance_data):
        chore_instance = self.db_wrapper.get_chore_instance_by_id(chore_instance_data['id'])
        # Passes everything back. Note that the display pretty much only needs day of week due, number of points, and which
        # instance this is out of total number of instances. Rest of info comes from parent chore. Not sure where the logic should go
        return {'id': chore_instance[0],
                'chore_id': chore_instance[1],
                'assigned_user': chore_instance[2],
                'completed_by': chore_instance[3],
                'awarded_pts': chore_instance[4],
                'deadline': chore_instance[5],
                'is_completed': chore_instance[6],
                'default_pts': chore_instance[7]
        }

    def get_chore_instance_list(self, house_id, user_filter=None, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None):
        #filters is a dictionary that can have entries user_id and 'completion'
        #want this so we can easily supply the different views
        #needs more thought in terms of what gets returned and how it works with the house methods
        chore_instance_records = self.db_wrapper.get_chore_instances(house_id,
                                                                    user_filter=user_filter,
                                                                    completion_filter=completion_filter,
                                                                    order=order,
                                                                    order_direction=order_direction,
                                                                    number_returned=number_returned,
                                                                    datetime_cutoff=datetime_cutoff
                                                                    )
        chore_instances = []
        for record in chore_instance_records:
            chore_instances.append({'id': record[0],
                                    'chore_id': record[1],
                                    'assigned_user': record[2],
                                    'completed_by': record[3],
                                    'awarded_pts': record[4],
                                    'deadline': record[5],
                                    'is_completed': record[6],
                                    'description': record[7]})
        return {'code': 1, 'chore_instances': chore_instances}

    def get_all_scores(self, house, user_id, datetime_cutoff):

        scores = {}
        for housemate in house.users:
            try:
                chore_instances = self.db_wrapper.get_chore_instances(house.id,
                                                                        user_filter = housemate['id'],
                                                                        completion_filter = True,
                                                                        datetime_cutoff = datetime_cutoff)
                print('Chore instances: {}'.format(chore_instances))
                if chore_instances is None:
                    score = 0
                else:
                    score = sum(instance[4] for instance in chore_instances)
                print('{} has {} points'.format(housemate['username'], score))
                scores[housemate['username']] = score
            except:
                self.log.exception('Something went wrong getting scores!')
                return {'code': -1}
                
        return {'code': 1, 'scores': scores}
