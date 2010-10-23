from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

projects = Table('projects', meta,
    Column('id', INTEGER, primary_key=True),
    Column('name', TEXT),
    Column('description', TEXT),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    projects.c.name.drop()

def downgrade(migrate_engine):
    col = Column('name', TEXT, default='project name')
    col.create(projects, populate_default=True)
    assert col is projects.c.name
