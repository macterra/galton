from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

users = Table('users', meta,
    Column('id', INTEGER, primary_key=True),
    Column('identifier', TEXT),
    Column('name', TEXT),
    Column('email', TEXT),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine 
    users.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    users.drop()    
