from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from service.movie import __get_movies_by_user, get_movie_ratings, _get_movies_by_user
from model.item import Item
import time

app = FastAPI()
print('start app {0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))


@app.on_event("startup")
async def startup_event():
    print('app started {0}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    get_movie_ratings()
    
@app.get("/")
def read_root():
    return {"Hello": "Fast Api!!!"}

@app.get("/movies/{user_uid}")
def get_movies_by_user(user_uid: str, n_movies: Optional[str] = None, vendor: Optional[str] = None, qa: Optional[str] = None):
    return __get_movies_by_user(user_uid, n_movies, vendor, qa)

@app.get("/movies2/{user_uid}")
def get_movies_by_user2(user_uid: str):
    return _get_movies_by_user(user_uid)

 