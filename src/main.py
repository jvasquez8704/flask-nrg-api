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
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item0(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.put("/items/")
def update_item(item: Item):
    # return {"item_name": item.name, "item_id": item.item_id}
    return item


@app.get("/user/{user_uid}")
def get_user(user_uid: str = None):
    ret = json.loads(json.dumps(get_user(user_uid)))
    return {"user":ret }


@app.get("/movies/{user_uid}")
def get_movies_by_user(user_uid: str, n_movies: Optional[str] = None, vendor: Optional[str] = None, qa: Optional[str] = None):
    return __get_movies_by_user(user_uid, n_movies, vendor, qa)

@app.get("/movies2/{user_uid}")
def get_movies_by_user2(user_uid: str):
    return _get_movies_by_user(user_uid)

 