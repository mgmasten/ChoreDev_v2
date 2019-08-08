from server.house import House
from server.chore_instance import ChoreInstance
import server.constants as constants
import server.util as util
import server.logger as logger

import schedule
import time
import threading
from datetime import datetime, timedelta, date

class ChoreScheduler(object):
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

	def increment_day_for_testing(self):
		self.current_time = self.current_time + timedelta(days = 1)

	def rotate_chores_for_testing(self):
		if self.current_time.weekday() == constants.SUNDAY:
			self.rotate_all_houses()

	def manage_incomplete_chore_instances(self):
		# Manages chore instances that were due at the end of this day but were
		# not completed.
		# For testing, also artificially increments the datetime by one day
		# and calls rotate_all_houses if the artificial day is Sunday
		if constants.TEST:
			self.increment_day_for_testing()

		all_house_ids = self.server.get_all_house_ids()
		for house_id in all_house_ids:
			house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)

			if house.chore_instances is not None:
				for instance in house.chore_instances:
					if instance.is_completed is False:
						instance.complete()

		if constants.TEST:
			self.rotate_chores_for_testing()

	def rotate_all_houses(self):
		# This is called once per week. Rotates chore schedules for all houses
		# Loops through all houses and calls rotate_house for each
		all_house_ids = self.server.get_all_house_ids()
		for house_id in all_house_ids:
			self.rotate_house(house_id)

	def rotate_house(self, house_id):
		'''Rotates chores for a single house. The chore rotation algorithm depends on a
		fair initial distribution of chores (in terms of number per person--see
		initialize_rotation schedule). Then, the chore is just rotated to the next
		eligible assignee in the list of eligible assignees.'''

		house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)

		chore_records = house.get_chore_list()

		if self.house_has_new_chores(house_id):
			assigned_chores = self.initialize_rotation_schedule(chore_records)
			for assignee in assigned_chores:
				for chore in assigned_chores[assignee]:
					self.create_weekly_chore_instances(house, chore[0], assignee, chore[1], chore[2])

		else:
			for i in range(len(chore_records)):
				eligible_assignees = chore_records[i][3]
				chore_id = chore_records[i][0]
				occurs_on = chore_records[i][5]
				default_pts = chore_records[i][8]

				eligible_assignees_list = eligible_assignees.split(';')
				current_assignee = self.get_current_assignee(chore_id)

				current_index = eligible_assignees_list.index(str(current_assignee))
				new_assignee = eligible_assignees_list[(current_index + 1) % len(eligible_assignees_list)]

				self.create_weekly_chore_instances(house, chore_id, int(new_assignee), occurs_on, default_pts)

			house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)
			house.delete_weekly_chore_instances()

	def house_has_new_chores(self, house_id):
		'''Checks whether rotation schedule needs to be re-initialized by checking whether
		the house has chores that have no stored chore instances.'''
		house = House(self.server.db_wrapper.get_house_by_id(house_id), self.server.db_wrapper)
		chore_list_records = house.get_chore_list

		for record in chore_list_records:
			chore_id = record[0]
			if self.server.db_wrapper.get_most_recent_chore_instance(chore_id) is None: # Chore is new
				return True

		return False



	def initialize_rotation_schedule(self, chore_records):
		'''Initializes rotation schedule for a house. Happens on first Sunday, and then
		any Sunday after a new chore has been added in a previous week.
		Loops through the list of chores in order. For each chore, assigns to the next user
		in the list of eligible assignees who does not already have an "extra" chore.
		Having an extra chore is defined as having more chores than the number of chores
		assigned to everyone else in that group of eligible assignees.'''

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
			current_date = datetime.now()

		weekday = (current_date.weekday() + 1) % constants.DAYS_IN_WEEK

		for i in range(weekday, constants.DAYS_IN_WEEK):
			if occurs_on[i] == '1':
				deadline_date = current_date + timedelta(days = (i - weekday))
				deadline = datetime(deadline_date.year, deadline_date.month, deadline_date.day, constants.MAX_HOUR, constants.MAX_MINUTE, constants.MAX_SECOND, constants.MAX_MICROSECOND)
				deadlines.append(deadline)
		return deadlines

	def create_weekly_chore_instances(self, house, chore_id, assignee, occurs_on, default_pts):
		deadlines = self.occurs_on_to_deadlines(occurs_on)
		pts_per_instance = self.calculate_chore_instance_pts(default_pts, len(deadlines))

		for i in range(len(deadlines)):
			chore_instance = ChoreInstance(self.server.db_wrapper, None)
			chore_instance.create(chore_id, assignee, deadlines[i], pts_per_instance[i])
			house.add_chore_instance(chore_instance)
		return house
