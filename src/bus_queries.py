# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.sql import func, and_
import re
import sys
import random
import time
import cPickle as pickle
import json
import numpy as np

#db = sa.create_engine('sqlite:///../copy_data.sqlite', echo=False)
db = sa.create_engine('sqlite:///../data.db', echo=False)
metadata = sa.MetaData(db)
trips = sa.Table('ajoaika_gps', metadata, autoload=True)

with open('../stop_coords2.pckl', 'r') as f:
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
        s = s.group_by(*groupcols)
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

def save_json(ts, filename):
    x = []
    for row in ts:
        sid = row[0]
        if str(sid) not in stop_coords:
            print "Missing stop id:", sid
            continue
        x.append({"id":sid, "coords":stop_coords[str(sid)], "value":[row[1]]})
    with open(filename, 'w') as outfile:
        json.dump({"stops": x}, outfile)

def get_stop_times():
    cols = [trips.c.tulopysakki, func.sum(trips.c.pysakkiaika).label('stop_sum')]
    conds = and_(*conditions)
    groupcols = trips.c.tulopysakki
    ts = run(cols, conds, groupcols, n_limit=None)
    save_json(ts, "../site/cum_stop_times.json")

def get_stop_time_matrix():
    weekhour = func.strftime('%w', trips.c.tapahtumapaiva) * 24 + func.cast(func.substr(trips.c.tuloaika_time,1,2), sa.Integer)
    cols = [trips.c.tulopysakki,
            weekhour,
            func.sum(trips.c.pysakkiaika).label('stop_sum')]
    conds = and_(*conditions)
    groupcols = [trips.c.tulopysakki, weekhour]
    ts = run(cols, conds, groupcols, n_limit=None)
    # Write to a csv file
    stops = list(set([val[0] for val in ts]))
    stop_map = {v: idx for (idx, v) in enumerate(stops)}
    mat = np.zeros((168, len(stops)))
    for (stop, wh, val) in ts:
        mat[wh, stop_map[stop]] = val
    with open('../site/stop_time_matrix.csv', 'w') as f:
        f.write(",".join(map(str, stops)) + '\n')
        for i in range(mat.shape[0]):
            f.write(",".join(map(str, mat[i,:])) + '\n')

def get_stop_delays():
    cols = [trips.c.tulopysakki, func.avg(trips.c.ohitusaika_ero).label('delay_avg')]
    conds = and_(*conditions)
    groupcols = trips.c.tulopysakki
    ts = run(cols, conds, groupcols, n_limit=None)
    save_json(ts, "../site/avg_stop_delays.json")

def get_stop_locations():
    ts = []
    for sid in stop_coords.iterkeys():
        ts.append((sid,1))
    save_json(ts, "../site/stop_1.json")

if __name__ == "__main__":
    get_avg()
