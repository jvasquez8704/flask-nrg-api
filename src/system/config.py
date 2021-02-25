import os
from util.constants import DEV_MODE
class Configuration:
  #[App Secrets]
  APP_SECRET_KEY='katch-app-504'
  APP_JWT_SECRET_SEED='s4P3r-s3cr3t_K@tCh-d3V_K3y'
 
  #[Credentials]
  GOOGLE_APPLICATION_CREDENTIALS = '../watch-party-test.json'
  CREDENTIALS_FIREBASE_SDK_PATH = '../watch-party-test.json'
  FIREBASE_WEB_API_KEY='AIzaSyBJM-U6ZGMF2iItNbXbDrds043_LM4htd0'
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

  #[Firebase]
  KATCH_FIREBASE_DB_URL='https://watch-party-test-71b4e.firebaseio.com/'
  KATCH_FIREBASE_SIGNIN_URL='https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword'
  KATCH_FIREBASE_SIGNUP_URL='https://identitytoolkit.googleapis.com/v1/accounts:signUp'

  #[Utelly]
  KATCH_UTELLY_URL = 'https://dev-api.utelly.com/phoenix/9/user'
  HEADER_X_APP_KEY='9404481bdc5f765cba251e74a71ce15b'
  CURRENT_ENV = os.getenv('CURRENT_ENV', DEV_MODE)