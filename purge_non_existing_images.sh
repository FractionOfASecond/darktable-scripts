#!/bin/sh

DRYRUN=yes

if [ "$1" = "-p" ]; then
    DRYRUN=no
fi

DBFILE=~/.config/darktable/library.db
TMPFILE=`mktemp -t tmp.XXXXXXXXXX`
TMPQUERY=`mktemp -t tmp.XXXXXXXXXX`
QUERY="select A.id,B.folder,A.filename from images as A join film_rolls as B on A.film_id = B.id"
sqlite3 $DBFILE "$QUERY" > $TMPFILE
echo "Image count: $TOTALLINES, processing..."
echo "BEGIN;\n" >> $TMPQUERY

echo "Removing the following non existent file(s):"

cat $TMPFILE | while read result
do
  ID=$(echo "$result" | cut -f1 -d"|")
  FD=$(echo "$result" | cut -f2 -d"|")
  FL=$(echo "$result" | cut -f3 -d"|")
  if ! [ -f "$FD/$FL" ];
  then
    echo "  $FD/$FL with ID = $ID"

    if [ $DRYRUN = no ]; then
        for table in images meta_data; do
            echo "DELETE FROM $table WHERE id=$ID;\n" >> $TMPQUERY
        done

        for table in color_labels history mask selected_images tagged_images; do
            echo "DELETE FROM $table WHERE imgid=$ID;\n" >> $TMPQUERY
        done
    fi
  fi
done
rm $TMPFILE


if [ $DRYRUN = no ]; then
    # delete now-empty filmrolls
    echo "DELETE FROM film_rolls WHERE (SELECT COUNT(A.id) FROM images AS A WHERE A.film_id=film_rolls.id)=0;\n" >> $TMPQUERY
else
    echo
    echo Remove following now-empty filmrolls:
    echo "SELECT folder FROM film_rolls WHERE (SELECT COUNT(A.id) FROM images AS A WHERE A.film_id=film_rolls.id)=0;\n" >> $TMPQUERY
fi

echo "END;" >> $TMPQUERY
sqlite3 "$DBFILE" < $TMPQUERY
rm $TMPFILE

if [ $DRYRUN = yes ]; then
    echo
    echo to really remove non existing images from the database call:
    echo $0 -p
fi
