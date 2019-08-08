import server.constants as constants
import server.util as util
import server.logger as logger
from datetime import datetime, timedelta, date
import schedule
import time
import threading

class User(object):

	def __init__(self, house, data, session_token, timestamp):
		self.load(house, data, session_token, timestamp);

	def load(self, house, data, session_token, timestamp):
		self.id = data[0];
		self.house_id = data[1];
		self.username = data[2];
		self.email = data[3];
		self.nickname = data[4];
		self.invite_token = data[5];
		self.session_token = session_token
		self.timestamp = timestamp
		self.house = house

	def set_timestamp(self, date):
		self.timestamp = date

	def get_timestamp(self):
		return self.timestamp


class House(object):

	def __init__(self, data, db_wrapper):
		self.db_wrapper = db_wrapper
		self.log = logger.create_logger('House', silent=False, verbose=False)
		self.online_users = {}
		if data is not None:
			self.load(data)

	def load(self, data):
		self.id = data[0]
		self.name = data[1]
		self.description = data[2]
		self.online_users = {}
		self.users = self._get_users()
		self.chore_instances = self._get_chore_instances()

	def _get_chore_instances(self, user_filter=None, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None):
		chore_instance_records = self.db_wrapper.get_chore_instances(self.id, user_filter=user_filter,
																	completion_filter=completion_filter,
																	order=order,
																	order_direction=order_direction,
																	number_returned=number_returned,
																	datetime_cutoff=datetime_cutoff)
		self.chore_instances = []
		if chore_instance_records is not None:
			for record in chore_instance_records:
				self.chore_instances.append(ChoreInstance(self.db_wrapper, record))

	def remove_user_by_token(self, token):
		if token in self.online_users:
			del self.online_users[token]
			return True
		else:
			return False

	def update(self, house_data):
		if 'description' in house_data:
			self.description = house_data['description']
		if 'name' in house_data:
			if not house_data['name']:
				self.log.exception('Tried to make the name of the house blank!')
				return False
			else:
				self.name = house_data['name']
				return self.db_wrapper.update_house(house_data)

	def add_user(self, user):
		self.online_users[user.session_token] = user

	def get_online_users(self):
		return self.online_users

	def generate_invite_token(self):
		return ''.join(random.choices(string.ascii_lowercase + string.digits, k=INVITE_TOKEN_LENGTH))

	def create(self, name):
		self.name = name
		new_house_id = self.db_wrapper.insert_house(self.name)['name']
		if (house.id is not None):
			self.id = new_house_id
			return True
		else:
			return False

	def _get_users(self):
		result = []
		raw_users = self.db_wrapper.get_users_by_house(self.id)
		for ruser in raw_users:
			result.append({'id': ruser[0], 'username': ruser[2]})
		return result

	def add_chore(self, uid, chore_data):
		occurs_on = ';'.join(x for x in chore_data['occurs_on'])
		assignee_str = ';'.join(str(user['id']) for user in chore_data['eligible_assignees'])
		try:
			complete_chore_data = {
				'house_id':             self.id,
				'creator_id':           uid,
				'name':                 chore_data['name'],
				'eligible_assignees':   assignee_str,
				'difficulty':           chore_data['difficulty'],
				'occurs_on':            occurs_on,
				'description':          chore_data['description'],
				'default_pts': 					chore_data['default_pts']
			}
			chore_id = self.db_wrapper.insert_chore(complete_chore_data)
			return True
		except:
			self.log.exception('Something went wrong in adding chore.')
			return False

	def delete_chore(self, chore_id):
		try:
			self.db_wrapper.delete_chore({'id': chore_id})
			return True
		except:
			self.log.exception('Something went wrong in deleting chore.')
			return False

	def get_chore_list(self):
		return self.db_wrapper.get_chore_list(self.id)

	def update_chore(self, chore_data):
		if 'id' not in chore_data:
			self.log.exception('Tried to update a chore without an id!')

		if 'name' in chore_data:
			if not chore_data['name']:
				self.log.exception('Tried to enter a blank name for a chore!')
				return False

		if 'occurs_on' in chore_data:
			if (len(chore_data['occurs_on']) != 7) or (False in [digit in ['0', '1'] for digit in list(chore_data['occurs_on'])]):
				self.log.exception('Tried to enter improper occurs_on for a chore!')
				return False

		try:
			self.db_wrapper.update_chore(chore_data)
			return True
		except:
			self.log.exception('Something went wrong in updating the chore')
			return False

	def get_chore(self, chore_id):
		return self.db_wrapper.get_chore_by_id(chore_id)

	def get_chore_instance_list(self, user_filter=None, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None):
		self._get_chore_instance_list(user_filter=user_filter,
										completion_filter=completion_filter,
										order=order,
										order_direction=order_direction,
										number_returned=number_returned,
										datetime_cutoff=datetime_cutoff)
		return self.chore_instances

	def add_chore_instance(self, chore_instance):
		if self.chore_instances is None:
			self.chore_instances = [chore_instance]
		else:
			self.chore_instances.append(chore_instance)

	def delete_weekly_chore_instances(self):
		print('Deleting weekly chore instances')
		current_time = datetime.now()
		if self.chore_instances is not None:
			for chore_instance in self.chore_instances:
				if (chore_instance.get_deadline() < current_time):
					self.chore_instances.remove(chore_instance)


class ChoreInstance(object):
	def __init__(self, db_wrapper, data):
		self.db_wrapper = db_wrapper
		self.data = data

		if self.data is not None: # Chore instance has already been created
			self.load()

	def load_parent_chore(self):
		chore_data = self.db_wrapper.get_chore_by_id(self.chore_id)
		self.house_id = chore_data[1]
		self.creator_id = chore_data[2]
		self.eligible_assignees = chore_data[3]
		self.difficulty = chore_data[4]
		self.occurs_on = chore_data[5]
		self.description = chore_data[6]
		self.name = chore_data[7]
		self.default_pts = chore_data[8]

	def load(self): # data is the entire record for this chore instance
		# Chore instance properties
		self.chore_instance_id = self.data[0]
		self.chore_id = self.data[1]
		print('Chore id is: {}'.format(self.chore_id))
		self.assigned_user = self.data[2]
		self.completed_by = self.data[3]
		self.instance_default_pts = self.data[4]
		self.awarded_pts = self.data[5] 
		self.deadline = self.data[5]
		self.is_completed = self.data[7]

		self.load_parent_chore()

	def create(self, chore_id, assigned_user, deadline, default_pts):
		# Only for new chore instances. Adds to database
		self.chore_id = chore_id

		self.load_parent_chore()
		self.assigned_user = assigned_user
		self.completed_by = None
		self.awarded_pts = 0
		self.instance_default_pts = default_pts
		self.deadline = deadline
		self.is_completed = False

		chore_data = {
			'chore_id': self.chore_id,
			'assigned_user': self.assigned_user,
			'completed_by': self.completed_by,
			'awarded_pts': self.awarded_pts,
			'default_pts': self.instance_default_pts,
			'deadline': self.deadline,
			'is_completed': self.is_completed,
		}

		self.chore_instance_id = self.db_wrapper.insert_chore_instance(chore_data)

	def delete(self):
		self.db_wrapper.delete_chore_instance({'id': self.chore_instance_id})

	def get_deadline(self):
		return self.deadline
		# chore_instance = self.db_wrapper.get_chore_instance_by_id(self.chore_instance_id)
		# return chore_instance[5]

	def complete(self):
		self.is_completed = True
		self.completed_by = self.assigned_user

		if datetime.now() < self.get_deadline():
			self.awarded_pts = self.instance_default_pts
		else:
			self.awarded_pts = 0

		self.db_wrapper.update_chore_instance({'id': self.chore_instance_id,
												'completed_by': self.completed_by,
												'awarded_pts': self.awarded_pts,
												'is_completed': self.is_completed})

class ChoreScheduler(object):
# Need to think about how to handle the first week (before the first Sunday)
# Could create a new job that runs just rotate_house, and then delete the job
# Changes to online houses will not get back out. Maybe need to reload in authn or something
# ChoreScheduler is also created before houses get added, so this doesn't make sense
	def __init__(self, server, silent=False, verbose=False):
		self.server = server
		self.log = logger.create_logger('ChoreScheduler', silent=silent, verbose=verbose)

		if constants.TEST:
			# Pretend it's Sunday, and create a current_time variable that can be
			# artificially incremented by 1 day every TEST_DAY_LENGTH_SECONDS
			self.current_time = util.start_of_week()
			schedule.every(constants.TEST_DAY_LENGTH_SECONDS).seconds.do(self.manage_incomplete_chore_instances)
			schedule.run_continuously(constants.TEST_SCHEDULER_INTERVAL_SECONDS)
		else:
			schedule.every().sunday.at("00:00").do(self.rotate_all_houses)
			schedule.every().day.at("00:00").do(self.manage_incomplete_chore_instances)
			schedule.run_continuously(constants.SCHEDULER_INTERVAL_SECONDS)


	def manage_incomplete_chore_instances(self):
		# Should deal with all the chore instances that were not completed in time and (not) assign points accordingly
		# Should probably be run at the end of every day
		if constants.TEST:
			self.current_time = self.current_time + timedelta(days = 1)
			print('New day! It is day #{}'.format(self.current_time.weekday()))
		all_house_ids = self.server.get_all_house_ids()
		for house_id in all_house_ids:
			house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)

			chore_instances = house.get_chore_instance_list()
			if chore_instances is not None:
				for i in range(len(chore_instances)):
					if house.chore_instances[i].is_completed is False:
						house.chore_instances[i].complete(None)

		if constants.TEST:
			if self.current_time.weekday() == constants.SUNDAY:
				self.rotate_all_houses()

	def rotate_all_houses(self):
		# This is called once per week. Rotates chore schedules for all houses
		# Loops through all houses and calls rotate_house for each
		print('Rotating all houses')
		all_house_ids = self.server.get_all_house_ids()
		for house_id in all_house_ids:
			print('house_id {}'.format(house_id))
			self.rotate_house(house_id)

	def rotate_house(self, house_id):
		# This rotates the chore schedule for a single house
		print('Now working on house {}'.format(house_id))
		house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)

		chore_records = house.get_chore_list()

		if self.server.db_wrapper.house_has_no_chore_instances(house_id):
			print('chore_instances table is empty')
			assigned_chores = self.initialize_rotation_schedule(chore_records)
			for assignee in assigned_chores:
				for chore in assigned_chores[assignee]:
					self.create_weekly_chore_instances(house, chore[0], assignee, chore[1], chore[2])

		else:
			print('chore_instances table is not empty')
			for i in range(len(chore_records)):
				eligible_assignees = chore_records[i][3]
				chore_id = chore_records[i][0]
				occurs_on = chore_records[i][5]
				default_pts = chore_records[i][8]

				eligible_assignees_list = eligible_assignees.split(';')
				current_assignee = self.get_current_assignee(chore_id)

				current_index = eligible_assignees_list.index(str(current_assignee))
				print('Currently assigned to assignee #{} at index {}'.format(current_assignee, current_index))
				new_assignee = eligible_assignees_list[(current_index + 1) % len(eligible_assignees_list)]
				print('Doing calculation {} % {} = {}, making new_assignee={}'.format(current_index+1, len(eligible_assignees_list), (current_index+1)%len(eligible_assignees_list), new_assignee))

				self.create_weekly_chore_instances(house, chore_id, int(new_assignee), occurs_on, default_pts) # Should update house object and db

			house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)
			house.delete_weekly_chore_instances()

	def initialize_rotation_schedule(self, chore_records):
		print('Initializing chore rotation schedule')
		assigned_chores = {}  # key = assignee, value = list of assigned chores (chore_id, occurs_on, and default_pts)

		for i in range(len(chore_records)):
			eligible_assignees = chore_records[i][3]
			chore_id = chore_records[i][0]
			occurs_on = chore_records[i][5]
			default_pts = chore_records[i][8]

			eligible_assignees_list = eligible_assignees.split(';')

			assigned = False
			for assignee in eligible_assignees_list:
				if (assignee not in assigned_chores):
					assigned_chores[assignee] = [(chore_id, occurs_on, default_pts)]
					assigned = True
					print('Chore {} assigned'.format(chore_id))
					break

			if assigned:
				continue

			chores_assigned_to_each_person = 0
			number_of_loops = 0
			assignee_number = 0
			while(True):
				if number_of_loops % len(eligible_assignees_list) == 0:
					chores_assigned_to_each_person = chores_assigned_to_each_person + 1

				if (len(assigned_chores[eligible_assignees_list[assignee_number]]) > chores_assigned_to_each_person):
					number_of_loops = number_of_loops + 1
					assignee_number = (assignee_number + 1) % len(eligible_assignees_list)
					continue
				else:
					assigned_chores[eligible_assignees_list[assignee_number]].append((chore_id, occurs_on, default_pts))
					break

		return assigned_chores

	def get_current_assignee(self, chore_id):
		print('getting most recent assignee for chore {}'.format(chore_id))
		chore_instance_record = self.server.db_wrapper.get_most_recent_chore_instance(chore_id)
		return chore_instance_record[2]

	def calculate_chore_instance_pts(self, total_pts, number_of_instances):
		if number_of_instances is not 0:
			pts_per_instance = number_of_instances * [total_pts // number_of_instances]
			for i in range(total_pts % number_of_instances):
				pts_per_instance[i] = pts_per_instance[i] + 1
		else:
			pts_per_instance = []

		return pts_per_instance

	def occurs_on_to_deadlines(self, occurs_on):
		deadlines = []
		if constants.TEST:
			current_date = self.current_time
		else:
			# This does not work, because chore instances that get skipped this
			# week will screw up scheduling next week because they're uninitialized
			current_date = datetime.now()

		weekday = (current_date.weekday() + 1) % constants.DAYS_IN_WEEK

		for i in range(weekday, constants.DAYS_IN_WEEK):
			if occurs_on[i] == '1':
				deadline_date = current_date + timedelta(days = (i - weekday))
				deadline = datetime(deadline_date.year, deadline_date.month, deadline_date.day, constants.MAX_HOUR, constants.MAX_MINUTE, constants.MAX_SECOND, constants.MAX_MICROSECOND)
				deadlines.append(deadline)
		return deadlines

	def create_weekly_chore_instances(self, house, chore_id, assignee, occurs_on, default_pts):
		print('Now creating weekly chore instances for chore {}'.format(chore_id))
		deadlines = self.occurs_on_to_deadlines(occurs_on)
		pts_per_instance = self.calculate_chore_instance_pts(default_pts, len(deadlines))

		for i in range(len(deadlines)):
			chore_instance = ChoreInstance(self.server.db_wrapper, None)
			chore_instance.create(chore_id, assignee, deadlines[i], pts_per_instance[i])
			house.add_chore_instance(chore_instance)
		return house
