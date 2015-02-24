WTF_CSRF_ENABLED = False
SECRET_KEY = 'you-will-never-guess'


import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql+oursql://app-root:starwarswat@localhost/nickdb1'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
