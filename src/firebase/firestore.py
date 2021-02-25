from .config import fs
from util.constants import DB_URL_KEY, FS_USER_SCHEME
import numpy as np
import time

def get_user(user_uid):
    ref = fs.collection(FS_USER_SCHEME).document(user_uid)
    user = ref.get()
    return user.to_dict()

def get_raw_user(user_uid):
    ref = fs.collection(FS_USER_SCHEME).document(user_uid) 
    # return ref.get()
    return ref

def get_users():
    ref = fs.collection(FS_USER_SCHEME)
    # return ref.stream()
    return ref

def get_movie_ratings():
    global all_ratings
    u_col = get_users()
    ratings = [] 
    # user_list = [x for x in u_col.stream()]
    user_list = [x for x in u_col.limit(5).stream()]
    for user in user_list:
        data = user.to_dict()
        if 'rated_movies' in data:
            ratings.append(data['rated_movies'])
    all_ratings = {}
    for user in ratings:
        for movie in user:
            if type(user[movie]) != int:
                continue
            if movie not in all_ratings:
                all_ratings[movie] = [0,0,0,0,0]
            all_ratings[movie][user[movie] - 1] += 1
    print('ratings loaded {0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))

def rank_by_ratings():
    global ranked_by_ratings
    scores = {}
    for movie in all_ratings:
        ratings = all_ratings[movie] #array: [unseen,disliked,ok,liked,loved]
        score = np.dot(ratings,[0,-0.5,0.25,0.5,1])/sum(ratings)
        scores[movie] = score
    ranked_by_ratings = scores
    return scores

def rank_by_unseen():
    global ranked_by_unseen
    scores = {}
    for movie in all_ratings:
        ratings = all_ratings[movie]
        score = sum(ratings[1:])
        scores[movie] = score
    ranked_by_unseen = scores
    return scores


