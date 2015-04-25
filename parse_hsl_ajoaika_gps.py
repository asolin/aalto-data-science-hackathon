#!/usr/env python3

import pandas as pd
import zipfile
import os
import numpy as np

import sqlalchemy

def parse_data():

    datadir = 'data/dev.hsl.fi/ajoaika_gps/'
    #datadir = '/home/jluttine/Workspace/aalto-data-science-hackathon/data/dev.hsl.fi/ajoaika_gps/'
    zipped_files = sorted(os.listdir(datadir))
    #zipped_files = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),
    #                                       datadir))
    saved_files = []

    print(zipped_files)

    db = sqlalchemy.create_engine('sqlite:///data.sqlite')


    data = None

    while len(zipped_files) > 0:
    #for zipped_file in zipped_files:

        zipped_file = list(zipped_files)[0]
        
        print("Parsing file", zipped_file, "...")
        fz = zipfile.ZipFile(os.path.join(datadir, zipped_file))
        f = fz.open(fz.filelist[0])
        x = pd.read_csv(f)
                        ## dtype={"palveluntuottaja": np.int64,
                        ##        "linja": np.int64,
                        ##        "tarkenne": str,
                        ##        "reitti": str,
                        ##        "lahtoaika_time": "datetime64",
                        ##        #"tuloaika_time": "timedelta64[ns]"
                        ##        },
                        ## parse_dates=[
                        ##     "tapahtumapaiva",
                        ##     "liikpaiva",
                        ##     "tuloaika_time",
                        ##     "lahtoaika_time",
                        ##     "ohitusaika_time",
                        ##     "joreohitusaika_time",
                        ##     "aluetuloaika_time",
                        ##     "aluelahtoaika_time",
                        ## ])
        ## x = x[[
        ##           "palveluntuottaja",
        ##           "linja",
        ##           #"tarkenne",
        ##           #"suunta",
        ##           "laikajore",
        ##           #"tapahtumapaiva",
        ##           "ptyyppi",
        ##           "ptyyppiliik",
        ##           #"liikpaiva",
        ##           "kpaiva",
        ##           "joukkollaji",
        ##           "ajtyyppi",
        ##           "bussityyppi",
        ##           #"virhekoodi",
        ##           "lahtopysakki",
        ##           "tulopysakki",
        ##           "pysakkijarj",
        ##           "pysakkityyppi",
        ##           "tuloaika",
        ##           "lahtoaika",
        ##           "ohitusaika",
        ##           "joreohitusaika",
        ##           #"tuloaika_time",
        ##           #"lahtoaika_time",
        ##           #"ohitusaika_time",
        ##           #"joreohitusaika_time",
        ##           "ohitusaika_ero",
        ##           "ajoaika",
        ##           "pysakkiaika",
        ##           "pysakkialueella_oloaika",
        ##           "pysahdyskpl",
        ##           "kumul_pysakkiaika",
        ##           "kumul_pysakkialueella_oloaika",
        ##           "ta_viikko",
        ##           "ta_kuukausi",
        ##           "ta_vuosi",
        ##           "virhe_pysakki",
        ##           "virhe_gps",
        ##           "virhe_askellus",
        ##           "virhe_ohitusaika",
        ##           "virhe_lahto",
        ##           "kumul_matkaaika",
        ##           "aluetuloaika",
        ##           "aluelahtoaika",
        ##           #"aluetuloaika_time",
        ##           #"aluelahtoaika_time",
        ##           "vuosiviikko",
        ##        ]]
        ## if data is None:
        ##     data = x
        ## else:
        ##     data = pd.concat([data, x], ignore_index=True)

        x.to_sql('ajoaika_gps', db, if_exists='append')

        saved_files.append(zipped_file)

        zipped_files = sorted(list(set(os.listdir(datadir)).difference(saved_files)))

        print(zipped_files)

    #data.to_hdf('data.hdf', 'ajoaika_gps')

    ## return data



if __name__ == "__main__":
    parse_data()
