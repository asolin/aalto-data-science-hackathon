#!/bin/bash

DB="../data.db"
DATADIR="../data/dev.hsl.fi/ajoaika_gps"

mkdir -p .tmp
rm -f .tmp/*

# Create database
cat create_ajoaika_gps.sqlite | sqlite3 $DB

for ZIPFILE in $(ls -r $DATADIR/*.zip | sort)
do
    # Unzip to temporary directory
    unzip $ZIPFILE -d .tmp

    # Import CSV to sqlite
    CSVFILE=$(ls -r .tmp/*.csv)
    echo $CSVFILE
    CMD=".mode csv\n.import $CSVFILE ajoaika_gps"
    echo -e $CMD | sqlite3 $DB

    # Remove temporary file
    rm $CSVFILE
done

# Delete header row data
sqlite3 $DB "DELETE FROM ajoaika_gps WHERE palveluntuottaja = 'palveluntuottaja';"

rm -rf .tmp

