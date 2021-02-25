import numpy as np
from numpy.random import default_rng
from itertools import islice
rng = default_rng()
default_lambda = 0.3


def init():
    print("init rate_order has been loaded!!!")

def queue_movies(userID,unrated,n_movies=1):
    L = get_lambda(userID)

    infreq_rated_prob = 1/(1+2/L)
    print(len(unrated))
    categories = movie_categories(infreq_rated_prob,n_movies)
    
    def by_popularity(movie):
        return ranked_by_ratings[movie] if movie in ranked_by_ratings else 0
    
    def by_unseen(movie):
        return ranked_by_unseen[movie] if movie in ranked_by_unseen else 0
    
    popular = sorted(unrated,key=by_popularity,reverse=True)
    unseen = sorted(unrated,key=by_unseen)
    
    print(categories)
    p = 1/1e6**L
    
    pop_picked = geom_choice(popular,p,categories['popular'])
    unseen = np.setdiff1d(unseen,pop_picked)
    unseen_picked = geom_choice(unseen,p,categories['infrequently_rated'])
    
    picked = pop_picked + unseen_picked
    rng.shuffle(picked)
    if n_movies == 1:
        return picked[0]
    else:
        return picked

def queue_movies_by_user(user,unrated,_ranked_by_ratings, _rank_by_unseen, n_movies=1):
    L = get_lambda_by_user(user)

    infreq_rated_prob = 1/(1+2/L)
    print(len(unrated))
    categories = movie_categories(infreq_rated_prob,n_movies)
    
    def by_popularity(movie):
        return _ranked_by_ratings[movie] if movie in _ranked_by_ratings else 0
    
    def by_unseen(movie):
        return _rank_by_unseen[movie] if movie in _rank_by_unseen else 0
    
    popular = sorted(unrated,key=by_popularity,reverse=True)
    unseen = sorted(unrated,key=by_unseen)
    
    print(categories)
    p = 1/1e6**L
    
    pop_picked = geom_choice(popular,p,categories['popular'])
    unseen = np.setdiff1d(unseen,pop_picked)
    unseen_picked = geom_choice(unseen,p,categories['infrequently_rated'])
    
    picked = pop_picked + unseen_picked
    rng.shuffle(picked)
    if n_movies == 1:
        return picked[0]
    else:
        return picked

def _queue_movies_by_user(user, unrated, n_movies=1):
    print('unrated {0}'.format(unrated))
    rng.shuffle(unrated)
    
    return list(islice(unrated, n_movies))

def get_lambda(userID):
    u_doc = get_raw_user(userID)
    snap = u_doc.get().to_dict()
    if 'rating_lambda' in snap:
        L = snap['rating_lambda']
        return L
    else:
        u_doc.update({"rating_lambda":default_lambda})
        return default_lambda

def get_lambda_by_user(u_doc):
    snap = u_doc.get().to_dict()
    if 'rating_lambda' in snap:
        L = snap['rating_lambda']
        return L
    else:
        u_doc.update({"rating_lambda":default_lambda})
        return default_lambda

def movie_categories(infreq_prob,n):
    r = rng.random(size=n)
    return {"infrequently_rated":sum(r<=infreq_prob),"popular":sum(r>infreq_prob)}

def geom_choice(items,p,k):
    print('Restantes {0}'.format(items))
    print('1/1e6**L {0}'.format(p))
    print('retornar {0} movies'.format(k))
    if k == 0:
        return []
    n = len(items)
    weights = np.array([(1-p)**(x-1)*p for x in range(1,n+1)])

    picked = rng.choice(n,p=weights/weights.sum(),size=k,replace=False)
    print(f'Chose movies at indexes {picked}')
    return list(np.array(items)[picked])

def get_movie_ratings(u_col):
    global all_ratings
    ratings = [] 
    user_list = [x for x in u_col.stream()]
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

def rank_by_ratings():
    global ranked_by_ratings
    scores = {}
    for movie in all_ratings:
        ratings = all_ratings[movie] #array: [unseen,disliked,ok,liked,loved]
        score = np.dot(ratings,[0,-0.5,0.25,0.5,1])/sum(ratings)
        scores[movie] = score
    ranked_by_ratings = scores

def rank_by_unseen():
    global ranked_by_unseen
    scores = {}
    for movie in all_ratings:
        ratings = all_ratings[movie]
        score = sum(ratings[1:])
        scores[movie] = score
    ranked_by_unseen = scores