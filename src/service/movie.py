from firebase import get_raw_user, get_user, get_katch_movies, get_vendor_movies, rank_by_ratings, rank_by_unseen, get_movie_ratings, convert_movie_id, convert_user_id
from model import Movies
from util import queue_movies_by_user, _queue_movies_by_user

import numpy as np
import vendor as vnd
import threading as th
import time
import json


def __get_movies_by_user(user_uid, n_movies, vendor, qa):
    ret_movies = ''
    #organice pagination 
    num_mov = int(n_movies or 10)
    if num_mov < 3:
        num_mov = 3
    elif num_mov > 100:
        num_mov = 100
     
    if vendor:
        t = time.time()
        user_uid = convert_user_id(user_uid,vendor,"katch")
        print('if vendor time mark =======> {0}'.format(time.time()-t))
        
    #process data => todo: fetch movies periodically - when new movies become available (data changes) 
    # user = firestore.collection('users').document(user_uid)
    user = get_raw_user(user_uid)
    user_data = user.get(['session_movies','rated_movies']).to_dict()
    print('User Data {0}'.format(user_data))
    session_movies = user_data['session_movies'] if 'session_movies' in user_data else []
    rated = []
     
    if 'rated_movies' in user_data and user_data['rated_movies']:
        rated = list(user_data['rated_movies'].keys())

    #intersetion group
    session_movies = np.setdiff1d(session_movies,rated).tolist()

    if vendor:
        all_movies = get_vendor_movies(vendor)
    else:
        all_movies = get_katch_movies()
    
    all_movies = {x:Movies.movies[x] for x in all_movies if x in Movies.movies}
    
    if qa != "true":
        all_movies = [x for x,y in all_movies.items() if 'PosterURL' in y and 'impawards' not in y['PosterURL'].lower()]
    exclude = session_movies + rated
    
    #intersetion group
    unrated = np.setdiff1d(all_movies,exclude).tolist()

     
    ret_movies = queue_movies_by_user(user,unrated,rank_by_ratings(), rank_by_unseen(), num_mov)
    th.Thread(target=lambda : user.update({"session_movies":session_movies+ret_movies})).start()           
        
   
    if vendor == "utelly":
        ret_movies = [convert_movie_id(x,"katch","utelly",quiet=True) for x in ret_movies]
    else: 
        ret_movies = [Movies.movies[x] for x in ret_movies]
        for movie in ret_movies:
            if 'PosterURL' not in movie or 'impawards' in movie['PosterURL'].lower():
                movie['PosterURL'] = 'https://storage.googleapis.com/katch_posters/missing_poster.jpg'
  
    return {"movies": ret_movies}


def _get_movies_by_user(user_uid):
    ret_movies = ''
    #organice pagination 
    num_mov = 2
        
    user = get_raw_user(user_uid)

    user_data = user.get(['session_movies','rated_movies']).to_dict()
    session_movies = user_data['session_movies'] if 'session_movies' in user_data else []
    
    rated = []     
    if 'rated_movies' in user_data and user_data['rated_movies']:
        rated = list(user_data['rated_movies'].keys())
    

    all_movies = get_katch_movies()
    #parse to movie map 
    all_movies = {x:Movies.movies[x] for x in all_movies if x in Movies.movies}
    
   
    all_movies = [x for x,y in all_movies.items() if 'PosterURL' in y and 'impawards' not in y['PosterURL'].lower()]
    
    #intersetion group
    unrated = np.setdiff1d(all_movies,rated).tolist()
    # print('unrated {0}'.format(unrated))
    print('User Data {0}'.format(user_data))
    print('todas {0}'.format(all_movies))
    print('rated {0}'.format(rated))
     
    ret_movies = _queue_movies_by_user(user, unrated, num_mov)
    # th.Thread(target=lambda : user.update({"session_movies":session_movies + ret_movies})).start()
    th.Thread(target=lambda : user.update({"session_movies": ret_movies })).start()
   

    ret_movies = [Movies.movies[x] for x in ret_movies]
    for movie in ret_movies:
        if 'PosterURL' not in movie or 'impawards' in movie['PosterURL'].lower():
            movie['PosterURL'] = 'https://storage.googleapis.com/katch_posters/missing_poster.jpg'
  
    return {"movies": ret_movies}