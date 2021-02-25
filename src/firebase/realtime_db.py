from .config import fb, db
from util.constants import USER_SCHEME
from util.model import Model

movie_id_map_ref = fb.child('movie-ids')
movies_ref = fb.child('Movies')
genres_ref = fb.child('Genres')
users_ref = fb.child('Users')

movie_id_map = movie_id_map_ref.get()
katch_movies = {x:y for x,y in movie_id_map.items() if 'katch' in y}

 

def get_movies(n: int = None):
    if n:
        return (movies_ref.order_by_key().limit_to_first(n).get(), 'ffffffffffftttttt-0122')
    return movies_ref.get(etag=True)
    

# def get_n_movies(n):
#     return movies_ref.limit_to_first(n).get(etag=True)

def get_genders():
    return genres_ref.get(etag=True)

def get_movie_map(n: int = None):
    #mapping with imdb 
    # if n:
    #     return movie_id_map_ref.limit_to_first(n).get(etag=True)
    return movie_id_map_ref.get(etag=True)




#Vendor 
def get_katch_movies():
    return [y['katch'] for y in katch_movies.values()]

def get_vendor_movies(vendor):
    vendor_movies = [y['katch'] for y in katch_movies.values() if vendor in y]
    return vendor_movies


def convert_user_id(user_id,from_vendor,to_vendor,quiet=False):
    to_id = None
    if from_vendor == "katch":
        for uid,user in users_ref.order_by_key().equal_to(user_id).get().items():
            if to_vendor=="utelly":
                try:
                    to_id = user['utellyID']
                except:
                    pass
    elif from_vendor == "utelly":
        for uid in users_ref.order_by_child('utellyID').equal_to(user_id).get():
            if to_vendor=="katch":
                to_id = uid
    if not quiet and not to_id:
        raise IDConversionUnavailable()
    
    return to_id

def convert_movie_id(movie_id,from_vendor,to_vendor,quiet=False):
    if from_vendor=="katch":
        Model.localize_check()
        imdb_id = Model.to_imdb(movie_id)
    elif from_vendor=="utelly":
        snap = movie_id_map_ref.order_by_child("utelly").equal_to(movie_id).get()
        for key in snap:
            imdb_id = key
    
    
    movie_id_obj = movie_id_map[imdb_id]
    if to_vendor=="utelly":
        try:
            return movie_id_obj['utelly']
        except KeyError:
            if quiet:
                return None
            else:
                raise IDConversionUnavailable()
    elif to_vendor=="katch":
        return movie_id_obj['katch']


class IDConversionUnavailable(Exception):
    pass

    

