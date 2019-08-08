#!python3
from server.auth import Authentication
from flask import Flask, request, jsonify
from flask_cors import CORS
import server.logger as logger
import atexit
import sys
import server.util as util

silent = True if '--silent' in sys.argv else False
verbose = True if '--verbose' in sys.argv else False
provision = True if '--provision' in sys.argv else False
log = logger.create_logger('API', silent=silent, verbose=verbose)

log.info('Instantiating Flask...')
app = Flask('ChoreDevAPI')
CORS(app, resources={r"/register": {"origins": "*"}})
CORS(app, resources={r"/login": {"origins": "*"}})
CORS(app, resources={r"/score/*": {"origins": "*"}})
CORS(app, resources={r"/invite": {"origins": "*"}})
CORS(app, resources={r"/logout": {"origins": "*"}})
CORS(app, resources={r"/user/*": {"origins": "*"}})
CORS(app, resources={r"/chore/*": {"origins": "*"}})
CORS(app, resources={r"/house/*": {"origins": "*"}})

log.info('Creating authentication agent...')
authn_agent = Authentication(silent=silent, verbose=verbose, provision=provision)
log.info('Authentication agent created.')

def exit_handler():
    authn_agent.server.db_wrapper.close()
    log.info('API successfully shut down.')

atexit.register(exit_handler)


# Bind endpoints
@app.route('/register', methods=['POST'])
def register():
    user_data = request.get_json()
    response = jsonify(authn_agent.register(user_data))
    return response

@app.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    response = jsonify(authn_agent.login(user_data))
    return response

@app.route('/logout', methods=['POST'])
def logout():
    user_data = request.get_json()
    return jsonify(authn_agent.logout(user_data))

@app.route('/invite', methods=['POST'])
def invite():
    data = request.get_json()
    return jsonify(authn_agent.invite(data))

@app.route('/chore/<command>', methods=['POST', 'GET'])
def chore(command):
    data = request.get_json()
    if command == 'add':
        # Need house_id, name, description, difficulty, occurs_on, creator, eligible_assignees
        return jsonify(authn_agent.add_chore(data))

    if command == 'delete':
        chore_data = request.get_json() # Need chore_id, house_id
        return jsonify(authn_agent.server.delete_chore(chore_data))

    if command == 'update':
        chore_data = request.get_json() # Need chore_id, house_id, and any updated properties
        return jsonify(authn_agent.server.update_chore(chore_data))

    if command == 'get':
        chore_data = request.get_json() # Need chore_id, house_id
        return jsonify(authn_agent.get_chore(chore_data))

@app.route('/user/<command>', methods=['POST', 'GET'])
def user(command):
    data = request.get_json()
    if command == 'get':
        user_data = request.get_json() # Need username
        return jsonify(authn_agent.server.get_user_profile(user_data))

    if command == 'get_chore_instances':
        return jsonify(authn_agent.server.get_chore_instances(data))

    if command == 'update':
        user_data = request.get_json() # Need username
        return jsonify(authn_agent.server.update_user(user_data))

    if command == 'get_house_profile':
        house_data = request.get_json() # Need house_id
        return jsonify(authn_agent.server.get_house_profile(house_data))

    if command == 'update_house':
        house_data = request.get_json() # Need house_id, new name or description
        return jsonify(authn_agent.server.update_house(house_data))

@app.route('/house/<command>', methods=['POST', 'GET'])
def house(command):
    data = request.get_json()
    if command == 'get_users':
        return jsonify(authn_agent.get_users(data))

    if command == 'complete_chore_instance':
        chore_instance_data = request.get_json()  # Need chore_instance_id
        return jsonify(authn_agent.server.complete_chore_instance(chore_instance_data))

    if command == 'get_chore_instance':
     chore_instance_data = request.get_json()  # Need chore_instance_id
     return jsonify(authn_agent.server.get_chore_instance(chore_instance_data))

    if command == 'get_incomplete_chore_instances_for_house':
    # Want to see incomplete chore_instances for this house
    # in order of increasing deadline
        chore_instance_data = request.get_json()
        return jsonify(authn_agent.server.get_chore_instance_list(chore_instance_data['house_id'],
                                                                completion_filter=False,
                                                                order=True,
                                                                order_direction='ASC',
                                                                datetime_cutoff=util.now()))

    if command == 'get_weekday_abbreviation':
    #    Return string for day of week
        return util.weekday_abbreviation()


@app.route('/score/<command>', methods=['POST', 'GET'])
def score(command):
    data = request.get_json()
    if command == 'get_weekly_chore_instances':
        return jsonify(authn_agent.get_chore_instance_list(data,
                                                            order=True,
                                                            order_direction='DESC',
                                                            datetime_cutoff=util.start_of_week()))

    if command == 'get_monthly_chore_instances':
        return jsonify(authn_agent.get_chore_instance_list(data,
                                                            order=True,
                                                            order_direction='DESC',
                                                            datetime_cutoff=util.start_of_month()))

    if command == 'get_alltime_chore_instances':
        return jsonify(authn_agent.get_chore_instance_list(data,
                                                            order=True,
                                                            order_direction='DESC'))

    if command == 'get_weekly_scores':
        return jsonify(authn_agent.get_all_scores(data, util.start_of_week()))

    if command == 'get_monthly_scores':
        return jsonify(authn_agent.get_all_scores(data, util.start_of_month()))

    if command == 'get_all_time_scores':
        return jsonify(authn_agent.get_all_scores(data, None))


if __name__ == '__main__':
    log.info('Running Flask application...')
    app.run()
