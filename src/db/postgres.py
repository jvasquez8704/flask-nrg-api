import sqlalchemy

#db = sqlalchemy.create_engine("postgres+pg8000://georgekavel:kleberson@35.188.155.18:5432/genome")
db = sqlalchemy.create_engine("postgres+pg8000://georgekavel:kleberson@/genome?unix_sock=/cloudsql/curationtool-beb47:us-central1:metadata-db/.s.PGSQL.5432") 

def query(q):
   with db.connect() as conn:
       res = conn.execute(q)
       return res.fetchall()
   
def cols(q):
    with db.connect() as conn:
        res = conn.execute(q)
        return res.keys()