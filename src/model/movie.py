import random
import itertools
from firebase import get_movies, get_movie_map, get_genders
import threading as th
import time
import json

class MetaMovies(type):
    movie_lock = th.Lock()
    id_lock = th.Lock()
    genre_lock = th.Lock()
    
    @property
    def movies(self):
        with MetaMovies.movie_lock:
            return self._movies
    
    @movies.setter
    def movies(self,val):
        with MetaMovies.movie_lock:
            self._movies = val
    
    @property
    def id_map(self):
        with MetaMovies.id_lock:
            return self._id_map
    
    @id_map.setter
    def id_map(self,val):
        with MetaMovies.id_lock:
            self._id_map = val
            
    @property
    def genres(self):
        with MetaMovies.genre_lock:
            return self._genres
    
    @genres.setter
    def genres(self,val):
        with MetaMovies.genre_lock:
            self._genres = val

class Movies(object,metaclass=MetaMovies):
    #session vars:
    ## movies_to_rate: last batch of movies sent to user for rating
    ## rating_lambda: User's lambda parameter
    ## unrated_count: Number of movies user has not rated
    # _movies, movies_etag = get_movies(100)
    print('before load movies {0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    _movies, movies_etag = get_movies(10)
    _id_map, id_map_etag = get_movie_map()
    _genres, genres_etag = get_genders()
    # print('Movies model {0}'.format(json.dumps(_movies)))
    print('after load movies {0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))