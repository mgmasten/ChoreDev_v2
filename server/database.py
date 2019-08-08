import json
import server.constants as constants
import server.logger as logger
import psycopg2


class QueryParser(object):

    def __init__(self, silent=False, verbose=False):
        self.log = logger.create_logger('QueryParser', silent=silent, verbose=verbose)
        self.log.debug('Loading queries from JSON...')
        self.load()

    def parse_create_table(self, name, column_list):
        '''Creates and returns a CREATE TABLE query'''
        data = { 'name' : name, 'column_list': self.query['schemas'][column_list] }
        self.log.debug('Generated query to create table %(name)s with column list: %(column_list)s' % data)
        return self.query['commands']['create_table'] % data

    def parse_select(self, table, column_list, conditions='', order=False, ordering_column='id', order_direction='ASC', limit=None):
        '''Creates and returns a SELECT query'''
        query = self.query['commands']['select'] % {
            'column_list': column_list,
            'table': table,
            'conditions': conditions
        }
        if order:
            query = query[:-1]
            query += 'ORDER BY ' + ordering_column + ' ' + order_direction + ' ;'

        if limit is not None:
            query = query[:-1]
            query += 'LIMIT ' + str(limit) + ' ;'

        return query

    def parse_insert(self, table, column_list, values, return_id=False):
        '''Creates and returns an INSERT PostgreSQL query'''
        query = self.query['commands']['insert'] % {
            'table': table,
            'column_list': column_list,
            'values': values
        }
        if return_id:
            query = query[:-1]
            query += ' RETURNING id;'

        return query

    def parse_delete(self, table, conditions=''):
        '''Creates and returns a DELETE query'''
        return self.query['commands']['delete'] % {
            'table':table,
            'conditions': conditions
        }


    def parse_update(self, table, column_list, values, conditions=''):
        '''Creates and returns an UPDATE query'''
        if ',' in column_list:  #updates more than one column
            update_command = 'update'
        else: # updates only one column
            update_command = 'update_one'
        return self.query['commands'][update_command] % {
            'table': table,
            'column_list': column_list,
            'values': values,
            'conditions': conditions
        }

    def format(self, value):
        '''Returns a value formatted for a SQL query'''
        if isinstance(value, str):
            return "'%s'" % value
        else:
            return value

    def unzip_to_str(self, data):
        '''Takes a dictionary and unzips it into two comma separated strings'''
        keys = ', '.join(map(str, data.keys()))
        values = ', '.join(map(self.format, map(str, data.values())))
        return (keys, values)

    def load(self):
        '''Reloads the queries from JSON'''
        tmp = open(constants.SERVER_ROOT + '/query.json', 'r')
        self.query = json.load(tmp)
        tmp.close()

    def parse_count(self, table, conditions=''):
        '''Creates and returns a query to test if a table is empty'''
        return self.query['commands']['count'] % {
            'table': table,
            'conditions': conditions
        }

class DbWrapper(object):

    def __init__(self, silent=False, verbose=False, provision=False):

        self.log = logger.create_logger('Database Wrapper', silent=silent, verbose=verbose)
        self.log.info('Creating database connection...')
        self.conn = psycopg2.connect(constants.DATABASE_URL, sslmode='require')
        self.log.info('Database connection created.')

        self.log.info('Creating query parser...')
        self.parser = QueryParser(silent=silent, verbose=verbose)
        self.log.info('Query parser created.')

        self.cursor = self.conn.cursor()

        self.create_tables()

    def _execute(self, query):
        '''Executes and commits a query'''
        self.log.debug('Executing query: \n\n%s\n' % query)
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        '''Rolls back the cursor and closes SQL connection'''
        self.cursor.close()
        self.conn.close()

    def user_exists(self, username):
        '''Returns true if a user is in the users table'''
        query = self.parser.parse_select('users', 'id', "WHERE username = '%s'" % username)
        try:
            self._execute(query)
            user = self.cursor.fetchone()
            return True
        except:
            self.cursor.rollback()
            return False

    def create_tables(self):
        '''Provisions the application tables in PostgreSQL'''
        self.log.debug('Provisioning ChoreDev tables...')
        for schema in self.parser.query['schemas']:
            query = self.parser.parse_create_table(schema, schema)
            self._execute(query)
            self.log.debug('Created %s table.' % schema)
        self.log.debug('Created ChoreDev tables.')

    def get_user_by_username(self, username):
        '''Returns a user by username, returns None if not found'''
        self.log.debug('Fetching data for user...')
        query = self.parser.parse_select('users', '*', "WHERE username = '%s'" % username)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None

    def get_house_by_id(self, id):
        '''Returns a house by the house id, returns None if not found'''
        self.log.debug('Fetching house by id %s...' % id)
        query = self.parser.parse_select('houses', '*', "WHERE id='%s'" % id)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None

    def get_all_houses(self):
        '''Returns all houses in the database'''
        self.log.debug('Fetching all houses...')
        query = self.parser.parse_select('houses', '*', '', True, 'id', 'ASC')
        try:
            self._execute(query)
            data = self.cursor.fetchall()
            return data
        except:
            self.conn.rollback()
            return None

    def update_user_by_invite(self, data):
        '''Updates a user in database'''
        try:
            self.log.debug('Updating a user in the database...')
            invite_token = data['invite_token']
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_update('users', column_list, values, "WHERE invite_token = '%s'" % invite_token)
            self._execute(query)
            self.log.debug('User updated.')
            return True
        except:
            self.log.exception('Something went wrong updating the user!')
            self.conn.rollback()
            return False

    def update_user_by_username(self, data):
        '''Updates a user in database by username'''
        try:
            self.log.debug('Updating a user in the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_update('users', column_list, values, "WHERE username = '%s'" % data['username'])
            self._execute(query)
            self.log.debug('User updated.')
            return True
        except:
            self.log.exception('Something went wrong updating the user!')
            self.conn.rollback()
            return False

    def insert_user(self, data):
        '''Inserts a user to database'''
        try:
            self.log.debug('Adding a user to the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_insert('users', column_list, values)
            self._execute(query)
            self.log.debug('User added.')
            return True
        except:
            self.log.exception('Something went wrong adding a user!')
            self.conn.rollback()
            return False

    def insert_house(self, data):
        '''Inserts a house to database'''
        if 'name' not in data:
            self.log.exception('Tried to add a house with no name!')
            return None
        try:
            self.log.debug('Adding house %s to the database...' % data['name'])
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_insert('houses', column_list, values, return_id=True)
            self._execute(query)
            self.log.debug('House added.')
            new_house_id = self.cursor.fetchone()[0]
            return new_house_id
        except:
            self.log.exception('Something went wrong adding house %s!' % data['name'])
            self.conn.rollback()
            return None

    def update_house(self, data):
        '''Updates a house name or description in database given id'''
        if ('id' not in data):
            self.log.exception('Tried to change house without id!')
            return False
        try:
            self.log.debug('Updating a house in the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_update('houses', column_list, values, "WHERE id = '%s'" % data['id'])
            self._execute(query)
            self.log.debug('House updated.')
            return True
        except:
            self.log.exception('Something went wrong updating the house!')
            return False

    def get_house_from_id(self, house_id):
        '''Returns a house by house_id, returns None if not found'''
        self.log.debug('Fetching data for house...')
        query = self.parser.parse_select('houses', '*', "WHERE id = '%s'" % house_id)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None

    def insert_chore(self, data):
        '''Inserts a chore to database. Returns id'''
        if None in (data['name'], data['creator_id'], data['house_id'], data['difficulty'], data['default_pts']) or not data['name']:
            self.log.exception('Tried to add a chore with missing information!')
            return None

        try:
            self.log.debug('Adding chore %s to the database...' % data['name'])
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_insert('chores', column_list, values, return_id=True)
            self._execute(query)
            self.log.debug('Chore added.')
            new_chore_id = self.cursor.fetchone()[0]
            return new_chore_id
        except:
            self.log.exception('Something went wrong adding chore %s!' % data['name'])
            self.conn.rollback()
            return None

    def update_chore(self, data):
        '''Updates a chore in the database'''
        if ('id' not in data):
            self.log.exception('Tried to update an unspecified chore!')
            return False
        try:
            self.log.debug('Updating a chore in the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_update('chores', column_list, values, "WHERE id = '%s'" % data['id'])
            self._execute(query)
            self.log.debug('Chore updated.')
            return True
        except:
            self.log.exception('Something went wrong updating the chore!')
            return False

    def get_chore_by_id(self, chore_id):
        '''Returns a chore given id, returns None if not found'''
        self.log.debug('Fetching data for chore...')
        query = self.parser.parse_select('chores', '*', "WHERE id = '%s'" % chore_id)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None

    def get_chore_list(self, house_id):
        '''Returns the chore list for house with id, sorted by ascending id'''
        self.log.debug('Fetching chore list...')
        query = self.parser.parse_select('chores', '*', "WHERE house_id = '%s'" % house_id, True, 'id', 'ASC')
        try:
            self._execute(query)
            data = self.cursor.fetchall()
            return data
        except:
            self.conn.rollback()
            return None

    def delete_chore(self, data):
        '''Deletes a chore from the database'''
        try:
            self.log.debug('Deleting a chore in the database...')
            query = self.parser.parse_delete('chores', "WHERE id = '%s'" % data['id'])
            self._execute(query)
            self.log.debug('Chore deleted.')
            return True
        except:
            self.log.exception('Something went wrong deleting the chore!')
            return False

    def insert_chore_instance(self, data):
        '''Inserts a chore to database. Returns chore_instance_id'''
        if None in (data['chore_id'], data['assigned_user'], data['default_pts'], data['awarded_pts'], data['deadline'], data['is_completed']):
            self.log.exception('Tried to add a chore instance with missing information!')
            return None

        try:
            self.log.debug('Adding chore instance to the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_insert('chore_instances', column_list, values, return_id=True)
            self._execute(query)
            self.log.debug('Chore instance added.')
            new_chore_instance_id = self.cursor.fetchone()[0]
            return new_chore_instance_id
        except:
            self.log.exception('Something went wrong adding chore instance!')
            self.conn.rollback()
            return None

    def update_chore_instance(self, data):
        '''Updates a chore instance in the database'''
        if ('id' not in data):
            self.log.exception('Tried to update an unspecified chore instance!')
            return False
        try:
            self.log.debug('Updating a chore instance in the database...')
            (column_list, values) = self.parser.unzip_to_str(data)
            query = self.parser.parse_update('chore_instances', column_list, values, "WHERE id = '%s'" % data['id'])
            self._execute(query)
            self.log.debug('Chore instance updated.')
            return True
        except:
            self.log.exception('Something went wrong updating the chore instance!')
            return False

    def delete_chore_instance(self, data):
        '''Deletes a chore from the database'''
        try:
            self.log.debug('Deleting a chore in the database...')
            query = self.parser.parse_delete('chore', "WHERE id = '%s'" % data['id'])
            self._execute(query)
            self.log.debug('Chore deleted.')
            return True
        except:
            self.log.exception('Something went wrong deleting the chore!')
            return False

    def get_chore_instance_by_id(self, chore_instance_id):
        '''Returns a chore instance given id, returns None if not found'''
        self.log.debug('Fetching data for chore instance...')
        query = self.parser.parse_select('chore_instances', '*', "WHERE id = '%s'" % chore_instance_id, False)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None

    def get_chore_instances(self, house_id, user_filter=None, completion_filter=None, order=False, order_direction=None,  number_returned=None, datetime_cutoff=None):
        '''Returns the chore instances for house with id house_id'''
        self.log.debug('Fetching housemate list...')
        conditions = "WHERE chore_id IN (SELECT id FROM chores WHERE house_id = '%s')" % house_id
        if user_filter is not None:
            conditions = conditions + " AND assigned_user = '%s'" % user_filter
        if completion_filter is not None:
                conditions = conditions + " AND is_completed = '%s'" % completion_filter
        if datetime_cutoff is not None:
                conditions = conditions + " AND deadline >= '%s'" % datetime_cutoff
        query = self.parser.parse_select('chore_instances', '*', conditions,
                                        order=order, ordering_column='deadline',
                                        order_direction=order_direction, limit=number_returned)
        try:
            self._execute(query)
            data = self.cursor.fetchall()
            return data
        except:
            self.conn.rollback()
            return None

    def get_users_by_house(self, house_id):
        '''Returns the housemate list for house with id house_id'''
        self.log.debug('Fetching housemate list...')
        query = self.parser.parse_select('users', '*', "WHERE house_id = '%s'" % house_id)
        try:
            self._execute(query)
            data = self.cursor.fetchall()
            return data
        except:
            self.conn.rollback()
            return None

    def table_is_empty(self, table):
        '''Returns true if the given table is empty, false if not'''
        self.log.debug('Checking whether table is empty...')
        query = self.parser.parse_count(table)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            if data[0] == 0:
                return True
            else:
                return False
        except:
            self.conn.rollback()
            self.log.exception('Something went wrong counting the rows of this table')
            return None

    def house_has_no_chore_instances(self, house_id):
        '''Returns true if this house has no chore instances, false if not'''
        self.log.debug('Checking whether house has chore instances...')
        query = self.parser.parse_count('chore_instances', "WHERE chore_id IN (SELECT id FROM chores WHERE house_id = '%s')" % house_id)
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            if data[0] == 0:
                return True
            else:
                return False
        except:
            self.conn.rollback()
            self.log.exception('Something went wrong counting the rows of this table')
            return None

    def get_most_recent_chore_instance(self, chore_id):
        '''Gets most recent chore_instance for a chore with chore_id'''
        self.log.debug('Fetching most recent chore instance...')
        query = self.parser.parse_select('chore_instances', '*', "WHERE chore_id = '%s'" % chore_id, order=True, ordering_column='deadline', order_direction='DESC')
        try:
            self._execute(query)
            data = self.cursor.fetchone()
            return data
        except:
            self.conn.rollback()
            return None
