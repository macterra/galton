from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

projects = Table('projects', meta,
    Column('id', INTEGER, primary_key=True),
    Column('description', TEXT),
    Column('estimate', TEXT),
    Column('units', TEXT),
    Column('created', TIMESTAMP),
    Column('updated', TIMESTAMP),
    Column('owner', TEXT),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    col = Column('owner', TEXT)
    col.create(projects)
    assert col is projects.c.owner

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    projects.c.owner.drop()
