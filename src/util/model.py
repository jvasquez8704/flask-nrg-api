# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random
import os
import os.path
# from google.cloud.exceptions import NotModified, NotFound
# from google.cloud import logging

import threading as th

# import search

local = th.local()

class Model:
    
    generation = 0
    logger = None
    firestore = None
    
    

    reload_condition = th.Condition()
    _reloading = False
    
    def download_model():
        from util import download_folder,download_file
        
        try:
            generation =  download_file('model/timestamp.txt',newerThan=Model.generation)
        except NotModified:
            return -2
        except NotFound:
            return -1
        download_folder('model')
        download_folder('data')
        return generation

    def reload(force=False):
        from application import App
        from movies import Movies
        
        if not Model.firestore:
            Model.firestore = App.db_firestore
            
        if not Model.logger:
            if App.mode == "DEBUG":
                Model.logger = logging.Client().logger("Model_local")
            else:
                Model.logger = logging.Client().logger("Model")

        
        if not os.path.exists("model/"):
            Model.logger.log_text("Model directory does not exist. Creating now.",severity="WARNING")
            os.mkdir("model")
            os.mkdir("data")
            
            
        #import time
        #t = time.time()
        generation = Model.download_model()
        #print(time.time() - t)
        
        if generation >= 0:
            Model.logger.log_text("New model was available. Downloaded from Cloud Storage.",severity="WARNING")
        elif generation == -1:
            Model.logger.log_text("Models not found on Cloud Storage!",severity="CRITICAL")
            exit();
        elif generation == -2:
            Model.logger.log_text("Model is already up to date.",severity="INFO")
            if not force:
                return
                
        
        
       
        

        users_data = Model.firestore.collection(u'users')
        tmdb = Model.firestore.collection(u'tmdb')
        genes = Model.firestore.collection(u'genes')
        
        with Model.reload_condition:
            Model._reloading = True   
            Model.generation = generation
            #Model.all_users = dict([(x.id,x.to_dict()) for x in users_data.stream()])
            Model.all_tmdb = dict([(x.id,x.to_dict()) for x in tmdb.stream()])
            Model.all_genes = dict([(x.id,x.to_dict()) for x in genes.stream()])
            Model.all_movies = Movies.movies
            
            Model.row = np.load('model/row.npy')
            Model.col = np.load('model/col.npy')
            Model.user = np.array(np.load('model/user.npy',allow_pickle=True),dtype=np.int)
            Model.item = np.array(np.load('model/item.npy',allow_pickle=True),dtype=np.int)
            Model.svd_comp = np.load('model/svd.npy')
            #print(col)
            #print(row)
            
            #print(user)
            #print(item)
            
            
            Model.user_map = pd.read_csv("data/users.tsv",sep="\t",header=None)
            Model.movie_map = pd.read_csv("data/movies.tsv",sep="\t",header=None,encoding='windows-1252') 
            Model._reloading = False
            Model.reload_condition.notify_all()
        
        
        #print(user_map)
        
        #print(movie_map)
      
    
    def _is_done_reloading():
        return not Model._reloading
    
    def _localize():
        l = local
        #l.all_users = Model.all_users
        l.all_tmdb = Model.all_tmdb
        l.all_genes = Model.all_genes
        l.all_movies = Model.all_movies
        l.row = Model.row
        l.col = Model.col
        l.user = Model.user
        l.item = Model.item
        l.svd_comp = Model.svd_comp
        l.user_map = Model.user_map
        l.movie_map = Model.movie_map
        l.generation = Model.generation
        l.initialized = True
    
    def _mapuser(userID,transform_mode="dislike_negative"):
        for x in Model.firestore.collection(u'users').where(u'uid',u'==',userID).stream():
            user = x.to_dict()
        total_movies = len(local.movie_map)
        user_row = np.zeros(total_movies)
        for key in user['rated_movies']:
            idx = Model.movie_index(key)
            if idx > -1:
                user_row[idx] = Model._transform_rating(user['rated_movies'][key],transform_mode)
        return user_row
    
    def _transform_rating(rating,mode="dislike_negative"):
        if mode=="dislike_negative":
            if rating==2:
                return -1
            if rating==1:
                return 0
            else:
                return rating-2
        elif mode=="unseen_zero":
            return rating - 1
            
    
    def _get_user_row(userID,mode="svd",transform_mode="dislike_negative"):
        if mode == "wals":
            user_idx = Model.user_index(userID)
            if user_idx == -1:
                return np.zeros(len(local.row[0]))
            return local.row[user_idx]
        elif mode == "svd":
            return Model._mapuser(userID,transform_mode)
    
    def predict(userID,mode="default",transform_mode=None):
        if mode=="default":
            return Model.predict(userID,Model._detect_mode(userID),"dislike_negative")
        pred_rating = Model._predict(Model._get_user_row(userID,mode,transform_mode),mode)
        return pred_rating
    
    def predict_party(userIDs,mode="default",transform_mode=None):
        if mode == "default":
            return Model.predict_party(userIDs,Model._detect_mode(userIDs),"dislike_negative")
        rows = np.array([Model._get_user_row(x,mode,transform_mode) for x in userIDs])    
        cmb_user = rows.sum(axis=0)
        pred_rating = Model._predict(cmb_user,mode)
        return pred_rating
        
    
    def _predict(user_row,mode="svd"):    
        if mode == "wals":
            return np.dot(user_row,local.col.T)
        elif mode == "svd":
            if user_row.shape[0] > local.svd_comp.shape[1]:
                user_row = user_row[:len(Model.local.svd_comp)]
            return np.dot(np.dot(user_row,local.svd_comp.T),local.svd_comp)
        
    def choose_movies(take_top,k,pred):
       # if k > take_top:
       #     k = take_top
        print("Recs selected from top %d movies"%take_top)
        order = np.argsort(pred)
        ranked_movies = local.movie_map[0][order]
        rec_idx = random.sample(range(-take_top,0),k)
        print(pred[order][rec_idx])
        picked = ranked_movies.to_numpy()[rec_idx]
        return picked, Model.get_movie_names(picked), pred[order][rec_idx]
    
    def _detect_mode(userID):
        if type(userID) != str:
            #only return wals if ALL users are in the system
            return "wals" if all([Model._detect_mode(u)=="wals" for u in userID]) else "svd"
        
        if Model.user_index(userID) == -1:
            return "svd"
        else:
            return "wals"
    
    
    def localize_check():
        try:      
            if local.initialized and Model.generation > local.generation and Model._is_done_reloading():
                with Model.reload_condition:
                    Model.reload_condition.wait_for(Model._is_done_reloading)
                    Model._localize()
        except AttributeError:
            with Model.reload_condition:
                Model.reload_condition.wait_for(Model._is_done_reloading)
                Model._localize()     
    
    def get_recs(userID,k=3,mode="default",transform_mode=None,genre=None,gene=None,query=None): 
        Model.localize_check()    
        
        
        if mode == "default":
            mode = Model._detect_mode(userID)
            transform_mode="unseen_zero"
        
        if type(userID) != str:
            return Model._get_recs_party(userID,k,mode,transform_mode,genre,gene)
        
        pred = Model.predict(userID,mode,transform_mode)
        if len(pred) == 0:
            return np.zeros(0)
        
        rated = Model.get_rated_movies(userID,transform_mode)
        pred[rated] = -np.inf #if already seen, don't recommend
        
        recs_rated = Model.get_rated_recs(userID)
        disliked_recs = [Model.movie_index(movie) for movie in recs_rated if recs_rated[movie] < 0]
        pred[disliked_recs] = -np.inf
        
        if genre != None or gene != None:
            if genre != None:
                genre_movie_list = Model.by_genre(genre)
                movie_list = genre_movie_list
            if gene != None:
                gene_movie_list = Model.by_gene(gene)
                movie_list = gene_movie_list
            if genre != None and gene != None:
                movie_list = np.intersect1d(gene_movie_list,genre_movie_list).tolist()
                print(Model.get_movie_names(movie_list))
                
            indicator = np.zeros(len(pred))-np.inf 
            list_movies = 0
            for movie in movie_list:
                idx = Model.movie_index(movie)
                if idx > -1: #many movies in firebase not in rec model
                    list_movies += 1
                    indicator[idx] = 0
            pred = pred + indicator
            return {"rec":Model.choose_movies(min(25,list_movies),k,pred),"mode":mode}
        
        if query:
            Model.localize_check()
            movies = search.search_by_title(local.all_movies,query)
            indicator = np.zeros(len(pred))-np.inf 
            list_movies = 0
            for movie in movies:
                idx = Model.movie_index(movie)
                if idx > -1: #many movies in firebase not in rec model
                    list_movies += 1
                    indicator[idx] = 0
            pred = pred + indicator
            return {"rec":Model.choose_movies(max(min(25,list_movies),k),k,pred),"mode":mode}
        
        return {"rec":Model.choose_movies(100,k,pred),"mode":mode}
    
    def _get_top_movies(userID,k=10,mode="svd",transform_mode="dislike_negative"):
        pred = Model.predict(userID,mode,transform_mode)
        pred[Model.get_rated_movies(userID,transform_mode)] = 0
        idx = np.argsort(pred)
        print(pred[idx[-k:]])
        return Model.get_movie_names(idx[-k:].tolist())
        
    
    def _get_recs_party(userIDs,k,mode,transform_mode,genre,gene):
        pred = Model.predict_party(userIDs,mode,transform_mode)
        if len(pred) == 0:
            return np.zeros(0)
    
        rated = []
        for x in userIDs:
            rated += Model.get_rated_movies(x,transform_mode).tolist()
        pred[rated] = -np.inf
        print("Unseen movies: %s"%(len(pred)-len(rated)))
        
        if genre != None:
            movie_list = Model.by_genre(genre)
            indicator = np.zeros(len(pred))-np.inf
            genre_movies = 0
            for movie in movie_list:
                idx = Model.movie_index(movie)
                if idx > -1: #many movies in firebase not in rec model
                    genre_movies += 1
                    indicator[idx] = 0
            pred = pred + indicator           
            return {"rec":Model.choose_movies(min(15,genre_movies),k,pred),"mode":mode}
        
        return {"rec":Model.choose_movies(50,k,pred),"mode":mode}
    
    def _rmse(true,pred):
        count = 0
        err = 0
        for i in range(len(true)):
            if true[i] == 0:
                continue
            count += 1
            err += (true[i]-pred[i])**2
        err /= count
        return err**0.5
    
    
    def get_rmse(userID,mode="default",transform_mode="dislike_negative"):
        pred = Model.predict(userID,mode,transform_mode)
        true = Model._mapuser(userID,transform_mode)
        return Model._rmse(true,pred)
            
    def get_rated_movies(userID,transform_mode="dislike_negative"):
        #returns movies that have been given a rating (other than unseen)
        #only works for transform modes where unseen=>0
        return np.nonzero(Model._mapuser(userID))[0]
    
    def get_rated_recs(userID):
        recs = {}
        for rec in Model.firestore.collection('users').document(userID).collection('recs').stream():
            try:
                recs[rec.id] = rec.get('RecommendationRating')
            except:
                recs[rec.id] = 0
        return recs
    
    def user_index(userID):
        try:
            return local.user_map[0].to_list().index(userID)
        except ValueError:
            return -1
        
    def movie_index(movieID):
        try:
            return local.movie_map[0].to_list().index(movieID)
        except ValueError:
            return -1
    
    def get_movie_names(movieIDs):
        if type(movieIDs) == str:
            return local.all_movies[movieIDs]['Title']
        elif type(movieIDs) == int:
            return local.all_movies[local.movie_map[0][movieIDs]]['Title']
        else:
            if type(movieIDs)==np.ndarray:
                movieIDs = movieIDs.tolist()
            names = []
            for id in movieIDs:
                names.append(Model.get_movie_names(id) if id != None else None)
            return names
    
    def from_imdb(imdb_id):
        ids = [x for x in local.all_movies if local.all_movies[x]['IMDb hash']==imdb_id]
        if len(ids) == 0:
            return None
        return ids[0]
    
    def to_imdb(movie_id):
        if type(movie_id) == list or type(movie_id)==np.ndarray: 
            return [Model.to_imdb(x) for x in movie_id]
        return local.all_movies[movie_id]['IMDb hash']
    
    def by_genre(genre):
        #Note: This takes ~0.3sec for a larger genre
        l = [Model.from_imdb(local.all_tmdb[x]['imdb_id']) for x in local.all_tmdb if 'genres' in local.all_tmdb[x] and genre.lower() in [y['name'].lower() for y in local.all_tmdb[x]['genres']]]
        return [x for x in l if x != None]
        
    def by_gene(gene_id,min_score=3):
        if type(gene_id) == int:
            gene_id = str(gene_id)
        s = Model.firestore.collection('genes').document(gene_id).collection('movies').where('score','>=',min_score).stream()
        l = [Model.from_imdb(x.id) for x in s]
        return [x for x in l if x != None]
    
    def get_gene_info(gene_id):
        return Model.firestore.collection('genes').document(str(gene_id)).get().to_dict()
    