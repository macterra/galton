from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

tasks = Table('tasks', meta,
    Column('project', INTEGER),
    Column('description', TEXT),
    Column('estimate', FLOAT),
    Column('risk', TEXT),
    Column('variance', FLOAT),
    Column('count', INTEGER),
    Column('include', BOOLEAN),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    tasks.c.variance.drop()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    col = Column('variance', FLOAT)
    col.create(tasks)
    assert col is tasks.c.variance