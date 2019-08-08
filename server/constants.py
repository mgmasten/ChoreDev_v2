import os

APP_NAME = 'ChoreDev'
DATABASE_URL = os.environ['DATABASE_URL']
SERVER_ROOT  = os.path.dirname(os.path.realpath(__file__))
LOG_FMT = '%(asctime)s [%(levelname)s] - %(name)s: %(message)s'
LOG_PATH = '%(root)s/logs/' % {'root': SERVER_ROOT}
LOG_FILE = '%(log_path)s/dump.log' % {'log_path': LOG_PATH}
MINUTES_TO_LOGOUT = 30
INVITE_TOKEN_LENGTH = 5
DEFAULT_PTS = {'easy': 10, 'medium': 20, 'hard': 30}
#DIFFICULTY_TO_INT = {'easy': 1, 'medium': 2, 'hard': 3}
SECONDS_PER_MINUTE = 60
SCHEDULER_INTERVAL_SECONDS = 5 * 60
DAYS_IN_WEEK = 7
SUNDAY = 6
MAX_HOUR = 23
MAX_MINUTE = 59
MAX_SECOND = 59
MAX_MICROSECOND = 999999
SMTP_SERVER = 'smtp.gmail.com'
SMTP_SENDER = 'Chore Scores Mailer'
SMTP_USERNAME = 'chorescores.invites@gmail.com'
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
SMTP_TYPE = 'html'
INVITE_EMAIL_CONTENT = """\
<h1>You've been invited to try <i>ChoreScores</i>!</h1><br>

Use the following <b>invite token</b> when you register: %(invite_token)s<br>
"""

CHORE_SCHEDULER_ON = False
TEST = True
TEST_SCHEDULER_INTERVAL_SECONDS = 2
TEST_DAY_LENGTH_SECONDS = 5
