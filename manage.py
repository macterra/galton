#!/usr/bin/env python
from migrate.versioning.shell import main
main(url='sqlite:///test.db', debug='False', repository='dbrepo')
