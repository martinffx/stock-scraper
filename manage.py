#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(repository='migrations', url='postgres://stocks:password@db:5432/stocks', debug='False')
