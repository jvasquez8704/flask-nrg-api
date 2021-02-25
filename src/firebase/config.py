import firebase_admin
from firebase_admin import credentials, db, firestore
from util.constants import DB_URL_KEY
from system.config import Configuration 

cred = credentials.Certificate(Configuration.GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    DB_URL_KEY : Configuration.KATCH_FIREBASE_DB_URL
})

fs = firestore.client() 
fb = db.reference()