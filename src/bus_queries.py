# -*- coding: utf-8 -*-

# Copyright (c) 2015 Eric Malmi
# GPL v3

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

def save_multi_json(ts, filename):
    values = {}
    for row in ts:
        sid = row[0]
        hour = row[1]
        val = row[2]
        if str(sid) not in stop_coords:
            print "Missing stop id:", sid
            continue
        if sid not in values:
            values[sid] = [0] * 24
        values[sid][hour-1] = val
    x = []
    for sid, vals in values.iteritems():
        x.append({"id":sid, "coords":stop_coords[str(sid)], "value":vals})
    with open(filename, 'w') as outfile:
        json.dump({"stops": x}, outfile)

def save_route_json(ts, filename):
    x = []
    for row in ts:
        sid = row[0:2]
        #if str(sid) not in stop_coords:
        #    print "Missing stop id:", sid
        #    continue
        x.append({"id":sid, "value":[row[2]]})
    with open(filename, 'w') as outfile:
        json.dump({"routes": x}, outfile)

def get_stop_times():
    cols = [trips.c.tulopysakki, func.sum(trips.c.pysakkiaika).label('stop_sum')]
    conds = and_(*conditions)
    groupcols = [trips.c.tulopysakki]
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
    groupcols = [trips.c.tulopysakki]
    ts = run(cols, conds, groupcols, n_limit=None)
    save_json(ts, "../site/avg_stop_delays.json")

def get_stop_locations():
    ts = []
    for sid in stop_coords.iterkeys():
        ts.append((sid,1))
    save_json(ts, "../site/stop_1.json")

def get_route_delays():
    cols = [trips.c.tulopysakki, trips.c.lahtopysakki, func.avg(trips.c.ohitusaika_ero).label('delay_avg')]
    conds = and_(*conditions)
    groupcols = [trips.c.tulopysakki, trips.c.lahtopysakki]
    ts = run(cols, conds, groupcols, n_limit=None)
    save_route_json(ts, "../site/avg_route_dest_delay.json")

def get_route_dest_delay_matrix():
    weekhour = func.strftime('%w', trips.c.tapahtumapaiva) * 24 + func.cast(func.substr(trips.c.tuloaika_time,1,2), sa.Integer)
    cols = [trips.c.tulopysakki,
            trips.c.lahtopysakki,
            weekhour,
            func.sum(trips.c.pysakkiaika).label('stop_sum')]
    conds = and_(*conditions)
    groupcols = [trips.c.tulopysakki, trips.c.lahtopysakki, weekhour]
    ts = run(cols, conds, groupcols, n_limit=None)
    # Write to a csv file
    stops = list(set([(val[0], val[1]) for val in ts]))
    stop_map = {v: idx for (idx, v) in enumerate(stops)}
    mat = np.zeros((168, len(stops)))
    for val in ts:
        stop = (val[0], val[1])
        wh = val[2]
        value = val[3]
        mat[wh, stop_map[stop]] = value
    with open('../site/route_dest_delay_matrix.csv', 'w') as f:
        route_strs = ["%d-%d" % (val[0], val[1]) for val in stops]
        f.write(",".join(route_strs) + '\n')
        for i in range(mat.shape[0]):
            f.write(",".join(map(str, mat[i,:])) + '\n')

def analyze_day(day = "2014-08-22"):
    hour = func.cast(func.substr(trips.c.joreohitusaika_time,1,2), sa.Integer)
    cols = [trips.c.tulopysakki, hour, func.avg(trips.c.ohitusaika_ero).label('delay_avg')]
    new_conds = conditions
    new_conds.append(trips.c.tapahtumapaiva==day)
    conds = and_(*new_conds)
    groupcols = [trips.c.tulopysakki, hour]
    ts = run(cols, conds, groupcols, n_limit=None)
    save_multi_json(ts, "../site/hourly_stop_delays_%s.json" % day)
    

def get_delay_histogram():
    #bucket = func.round(trips.c.ohitusaika_ero/10)*10
    bucket = trips.c.ohitusaika_ero
    cols = [bucket, func.count()]
    new_conds = conditions
    #new_conds.append(n >= -2000)
    #new_conds.append(n <= 2000)
    conds = and_(*new_conds)
    groupcols = [bucket]
    ts = run(cols, conds, groupcols, n_limit=None)
    # Write to a csv file
    with open("../data/wait_histogram1.csv","w") as f:
        for val in ts:
            f.write("%d,%d\n" % (val[0], val[1]))

def plot_histogram():
    x = np.loadtxt("../data/wait_histogram1.csv", delimiter=',')
    #x = x[np.logical_and(x[:,0]>=-2000, x[:,0]<=2000),:]
    import matplotlib.pyplot as plt
    y = np.cumsum(x[:,1])
    y = y / y[-1]
    plt.plot(x[:,0]/60.0, y, '-', linewidth=2)
    plt.rcParams.update({'font.size': 14})
    xmax = 5
    plt.xlim(-5,xmax)
    plt.xticks(np.arange(-5,xmax+0.1,1))
    plt.yticks(np.arange(0,1.01,0.1))
    plt.xlabel('Arrival to stop (min)')
    plt.ylabel('Bus missing probability')
    plt.grid()
    plt.show()

if __name__ == "__main__":
    get_avg()
