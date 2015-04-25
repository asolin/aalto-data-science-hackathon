# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.sql import func, and_
import re
import sys
import random
import time
import cPickle as pickle
import json

#db = sa.create_engine('sqlite:///../copy_data.sqlite', echo=False)
db = sa.create_engine('sqlite:///../data.db', echo=False)
metadata = sa.MetaData(db)
trips = sa.Table('ajoaika_gps', metadata, autoload=True)

with open('../stop_coords.pckl', 'r') as f:
    stop_coords = pickle.load(f)

conditions = []
conditions.append(trips.c.pysakkiaika >= 0)
conditions.append(trips.c.virhe_pysakki == 0)
conditions.append(trips.c.virhe_gps == 0)
conditions.append(trips.c.virhe_askellus == 0)
conditions.append(trips.c.virhe_ohitusaika == 0)
conditions.append(trips.c.virhe_lahto == 0)
conditions.append(trips.c.lahtopysakki != 0)

def run(cols, conds=and_(*conditions), groupcols=None, n_limit=None):
    s = sa.select(cols).where(conds)
    if groupcols is not None:
        s = s.group_by(groupcols)
    if n_limit is not None:
        s = s.limit(n_limit)
    res = s.execute().fetchall()
    for r in res:
        print r
    return res

def get_avg():
    cols = [func.avg(trips.c.pysakkiaika)]
    conds = and_(*conditions)
    run(cols, conds)

def get_stop_times():
    cols = [trips.c.tulopysakki, func.sum(trips.c.pysakkiaika).label('stop_sum')]
    conds = and_(*conditions)
    groupcols = trips.c.tulopysakki
    ts = run(cols, conds, groupcols, n_limit=None)
    x = []
    for row in ts:
        sid = row[0]
        if str(sid) not in stop_coords:
            print "Missing stop id:", sid
            continue
        x.append({"id":sid, "coords":stop_coords[str(sid)], "value":[row[1]]})
    with open('cum_stop_times.json', 'w') as outfile:
        json.dump({"stops": x}, outfile)

if __name__ == "__main__":
    get_avg()
