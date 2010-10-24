from sqlalchemy import *
from migrate import *

from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR
            
meta = MetaData()

projects = Table('projects', meta,
    Column('id', INTEGER, primary_key=True),
    Column('description', TEXT),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    col = Column('estimate', TEXT, default='median')
    col.create(projects, populate_default=True)
    assert col is projects.c.estimate
    
    col = Column('units', TEXT, default='days')
    col.create(projects, populate_default=True)
    assert col is projects.c.units

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    projects.c.estimate.drop()
    projects.c.units.drop()
