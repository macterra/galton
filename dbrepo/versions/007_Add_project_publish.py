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
    Column('userid', INTEGER),
    Column('publish', BOOLEAN),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine   
    
    userid = Column('userid', INTEGER, default=0)
    userid.create(projects, populate_default=True)
    assert userid is projects.c.userid
    
    publish = Column('publish', BOOLEAN, default=False)
    publish.create(projects, populate_default=True)
    assert publish is projects.c.publish

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    projects.c.userid.drop()
    projects.c.publish.drop()
