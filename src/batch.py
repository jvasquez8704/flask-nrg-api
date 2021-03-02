from db.mysql import query
import json
#from firebase import _get_movie_map

#moviemap =_get_movie_map()
#print(query("Select * from movies"))
def load_csv():
    with open('katch-nrg-6b8c7-movie-ids-export.json') as json_file:
        data = json.loads(json.dumps(json.load(json_file)))
    
    return data

jsontemp = load_csv()
for x in jsontemp:
   if x["film"]:
       print("film: {0}".format(x))
#    if x["utelly"]:
#        print("utelly: {0}".format(x["utelly"]))
#    if x["katch"]:
#        print("katch: {0}".format(x["katch"]))