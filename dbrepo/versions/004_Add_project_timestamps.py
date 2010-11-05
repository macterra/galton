from sqlalchemy import *
from sqlalchemy.sql.functions import now
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
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    col = Column('created', TIMESTAMP, default=now())
    col.create(projects, populate_default=True)
    assert col is projects.c.created
    col = Column('updated', TIMESTAMP, default=now())
    col.create(projects, populate_default=True)
    assert col is projects.c.updated

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    projects.c.created.drop()
    projects.c.updated.drop()
