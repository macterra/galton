from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

users = Table('users', meta,
    Column('username', TEXT),
    Column('password', TEXT),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine 
    users.drop()    

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    users.create()
