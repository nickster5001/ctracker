from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
clients = Table('clients', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fname', String(length=45)),
    Column('lname', String(length=45)),
    Column('dob', Date),
)

deleted_ifa = Table('deleted_ifa', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('description', String(length=450)),
    Column('duedate', Date),
    Column('clients_idclients', Integer),
)

ifa = Table('ifa', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('description', String(length=450)),
    Column('duedate', Date),
    Column('clients_idclients', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['clients'].create()
    post_meta.tables['deleted_ifa'].create()
    post_meta.tables['ifa'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['clients'].drop()
    post_meta.tables['deleted_ifa'].drop()
    post_meta.tables['ifa'].drop()
