from model import Model
from application import App

ref = App.katch_data
movie_id_map_ref = ref.child('movie-ids')
movie_id_map = movie_id_map_ref.get()
katch_movies = {x:y for x,y in movie_id_map.items() if 'katch' in y}
users_ref = ref.child('Users')



