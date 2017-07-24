#!/usr/bin/python3
import subprocess
import tempfile
import argparse
import os

parser = argparse.ArgumentParser(description='Remove non existing images from Darktable database')
parser.add_argument("-p", required=False, action="store_true", help="Actually remove image references instead of dry run")
parser.add_argument("-v", '--verbose', required=False, action="store_true", help="Verbose mode. Print every reference that will be removed")
args = parser.parse_args()

DB = os.path.expanduser("~")+"/.config/darktable/library.db"
QUERY = 'SELECT a.id, b.folder, a.filename FROM images AS a JOIN film_rolls AS b ON a.film_id=b.id'

output = subprocess.check_output(['sqlite3', DB, QUERY]).splitlines()
print("Image count:", len(output))
cont = 0

with tempfile.NamedTemporaryFile(mode='w') as tmpfile:
    tmpfile.write("BEGIN;\n")
    for line in output:
        id, file_path, file_name = line.decode().split("|")
        if not os.path.isfile("{}/{}".format(file_path, file_name)):
            if args.verbose:
                print("will remove non existing: {}/{} with ID:{}".format(file_path, file_name, id))
            if args.p:
                queries = u"DELETE FROM images WHERE id={};\n".format(id)
                queries += "DELETE FROM meta_data WHERE id={};\n".format(id)
                queries += "DELETE FROM color_labels WHERE imgid={};\n".format(id)
                queries += "DELETE FROM history WHERE imgid={};\n".format(id)
                queries += "DELETE FROM mask WHERE imgid={};\n".format(id)
                queries += "DELETE FROM selected_images WHERE imgid={};\n".format(id)
                queries += "DELETE FROM tagged_images WHERE imgid={};\n".format(id)
                tmpfile.write(queries)
            cont += 1

    if args.p:
        tmpfile.write("DELETE FROM film_rolls WHERE (SELECT COUNT(a.id) FROM images AS a WHERE a.film_id=film_rolls.id)=0;\n")
        tmpfile.write("END;")
        tmpfile.flush()
        subprocess.check_output("sqlite3 {} < {}".format(DB, tmpfile.name), shell=True)
        message = "{} references has been removed".format(cont)
    else:
        message = "{} references could be removed".format(cont)
    print(message)
