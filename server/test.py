import unittest
from server.database import QueryParser
import server.auth as auth
from datetime import datetime, timedelta
import server.util as util
import server.server as server


class TestQueryParser(unittest.TestCase):

    def test_create_table(self):
        parser = QueryParser(silent=True)
        name = 'Chores'
        data = {'name': name, 'column_list': parser.query['schemas']['users']}
        compare = parser.query['commands']['create_table'] % data
        self.assertEqual(parser.parse_create_table(name, 'users'), compare)

class TestAuthentication(unittest.TestCase):

    def register(self):
        
        pass

    def test_login_logout(self):
        authn = auth.Authentication(silent=True)
        token = authn.login({'username':'asdf', 'password':'asdf'})['session_token']
        self.assertIn(token, authn.authorized_users)
        self.assertTrue(authn._token_exists(token))
        authn._logout(token)
        self.assertNotIn(token, authn.authorized_users)
        self.assertFalse(authn._token_exists(token))

    def test_fake_token(self):
        authn = auth.Authentication(silent=True)
        token = authn.login({'username':'asdf', 'password':'asdf'})['session_token']
        self.assertTrue(authn._token_exists(token))
        self.assertFalse(authn._token_exists(util.generate_uuid()))

    def test_expiration(self):
        authn = auth.Authentication(silent=True)
        token = authn.login({'username':'asdf', 'password':'asdf'})['session_token']
        self.assertFalse(authn._is_expired(token))
        authn.authorized_users[token].set_timestamp(datetime.datetime.now() - datetime.timedelta(minutes=30))
        self.assertTrue(authn._is_expired(token))

class TestServer(unittest.TestCase):
    def test_add_chore(self):
        authn = auth.Authentication(silent=True)

        # Need house_id, name, description, difficulty, occurs_on, creator, eligible_assignees
        #chore_data = {'house_id': 1, 'name': 'Floors', 'description': 'Mop all floors', 'difficulty': 2, 'occurs_on': '0100000', 'creator_id': 1, 'eligible_assignees':'1;2'}
        #chore_data = {'house_id': 1, 'name': 'Trash', 'description': 'Take out the trash!', 'difficulty': 1, 'occurs_on': '0000010', 'creator_id': 1, 'eligible_assignees':'1;2'}
        #chore_data = {'house_id': 2, 'name': 'Bathroom', 'description': 'Clean downstairs bathroom', 'difficulty': 3, 'occurs_on': '0000001', 'creator_id': 3, 'eligible_assignees':'3;4;5'}
        #chore_data = {'house_id': 2, 'name': 'Bathroom', 'description': 'Clean downstairs bathroom', 'difficulty': 3, 'occurs_on': '0000001', 'creator_id': 3, 'eligible_assignees':'3;4'}
        chore_data = {'house_id': 1, 'name': 'Bathrooms', 'description': 'Clean them!', 'difficulty': 3, 'occurs_on': '1000100', 'creator_id': 1, 'eligible_assignees':'1;2'}
        print(authn.server.add_chore(chore_data))

    def test_update_chore(self):
        authn = auth.Authentication(silent=True)

        # Need chore_id, house_id, and any updated properties
        chore_data = {'house_id': 1, 'id': 1, 'eligible_assignees': '1', 'difficulty': 3, 'occurs_on': '1010101', 'description': 'Put every dish away', 'name': 'The Dishes'}
        print(authn.server.update_chore(chore_data))

    def test_delete_chore(self):
        authn = auth.Authentication(silent=True)
        print(authn.server.delete_chore({'house_id': 1, 'id': 7}))
        #print(authn.server.delete_chore({'house_id': 2, 'id': 4}))

    def test_get_chore(self):
        authn = auth.Authentication(silent=True)
        print(authn.server.get_chore({'house_id': 1, 'id': 2}))


    def test_get_user_profile(self):
        authn = auth.Authentication(silent=True)
        print(authn.server.get_user_profile({'house_id': 1, 'username': 'asdf'}))

    def test_update_user_nickname(self):
        authn = auth.Authentication(silent=True)
        token = authn.login({'username':'asdf', 'password':'asdf'})['session_token']

        user_data = {'username': 'asdf', 'nickname': 'AwesomeSauce'}
        print(authn.server.update_user(user_data))
        authn._logout(token)

    def test_update_user_password(self):
        authn = auth.Authentication(silent=True)

        user_data = {'username': 'asdf', 'password': 'asdf'}
        print(authn.server.update_user(user_data))

    def test_get_house_profile(self):
        authn = auth.Authentication(silent=True)
        print(authn.server.get_house_profile({'id': 1}))

    def test_get_all_house_ids(self):
        authn = auth.Authentication(silent=False)
        print(authn.server.get_all_house_ids())

    def test_update_house_name(self):
        authn = auth.Authentication(silent=False)
        print(authn.server.update_house({'id': 1, 'name': 'Awesome House'}))

    def test_update_house_description(self):
        authn = auth.Authentication(silent=False)
        print(authn.server.update_house({'id': 1, 'description': 'The awesomest house!'}))

    def test_complete_chore_instance(self):
        authn = auth.Authentication(silent=False)
        print(authn.server.complete_chore_instance({'id': 270}))

    def test_get_chore_instance(self):
        authn = auth.Authentication(silent=False)
        print(authn.server.complete_chore_instance({'id': 269}))

    def test_get_chore_instance_list(self):
        authn = auth.Authentication(silent=False)
        #list = authn.server.get_chore_instance_list(1, user_filter=None, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(2, user_filter=None, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(1, user_filter=1, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(2, user_filter=3, completion_filter=None, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(1, user_filter=1, completion_filter=True, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(1, completion_filter=False, order=False, order_direction=None, number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(1, completion_filter=None, order=True, order_direction='DESC', number_returned=None, datetime_cutoff=None)
        #list = authn.server.get_chore_instance_list(1, completion_filter=False, order=False, order_direction=None, number_returned=None, datetime_cutoff=datetime.now() + timedelta(days=5))
        list = authn.server.get_chore_instance_list(1, user_filter=1, completion_filter=False, order=True, order_direction='DESC', number_returned=5, datetime_cutoff=datetime.now() + timedelta(days=4))

        for instance in list:
            print(instance)

    def test_get_all_scores(self):
        authn = auth.Authentication(silent=False)
        scores_dictionary = authn.server.get_all_scores(1, 1, util.start_of_week())
        print(scores_dictionary)


class TestChoreScheduler(unittest.TestCase):
    def test_chore_rotation(self):
        auhtn = auth.Authentication(silent=False)

if __name__ == '__main__':
    unittest.main()
