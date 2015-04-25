#!/bin/bash

cat gtfs_tables.sqlite \
  <(python import_gtfs_to_sql.py ../data/google_transit nocopy)  \
| sqlite3 ../data/gtfs.db
