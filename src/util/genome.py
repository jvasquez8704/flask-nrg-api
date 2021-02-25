import math
import threading as th
from db import query, cols
from firebase import fs

genes = fs.collection('genes')
sql_semaphore = th.BoundedSemaphore(10)
fs_semaphore = th.BoundedSemaphore(1000)

def add_genes(ids):
    if len(ids) > 10:
        for i in range(0,len(ids),10):
            add_genes(ids[i:min(len(ids),i+10)])
            print("Group %d/%d completed"%(i/10+1,math.ceil(len(ids)/10)))
        return
        
    gene_barrier = th.Barrier(len(ids)+1)
    for id in ids:
        gene_op = th.Thread(target=add_gene,args=(id,gene_barrier))
        gene_op.start()
    gene_barrier.wait()
    print("Bulk add complete")

def get_gene_ids():
    q = query("""select "gene number" from coded_movie_taxonomy""")
    q = [x[0] for x in q]
    return q

def get_coded_genes():
    return cols("select * from mct_stable")[6:]

def add_gene(id,barrier=None):
    
    if type(id) == int:
        id = str(id)
        
    with sql_semaphore:
    
        taxonomy = query(f"""select * from coded_movie_taxonomy where "gene number"='{id}'""")
    
    if len(taxonomy) == 0:
        print(f'Gene {id} unavailable')
        barrier.wait()
        return -1
    
    taxonomy = taxonomy[0]
    
    gene_doc = genes.document(id)
    gene_doc.set({'category':taxonomy[0],'name':taxonomy[2]})
    
    
    with sql_semaphore:
    #Note: remember genes use different scales
        gene = query(f"""select max(movies),"imdb number",avg(cast("{id}" as float)) from mct_stable where "{id}">'0' group by "imdb number" """)
    

    movie_coll = gene_doc.collection('movies')
    
    movie_barrier = th.Barrier(len(gene)+1)
    
    def add_movie(name,id,score):
        with fs_semaphore:
            movie_coll.document(id).set({'name':name,'score':score})
        movie_barrier.wait()
    
    #Bulk adds should be done in parallel
    for movie in gene:
        op = th.Thread(target=add_movie,args=movie)
        op.start()
        #print("Added movie: "+movie[0])
    movie_barrier.wait()
    print(f"Gene {id} added")
    if barrier:
        barrier.wait()    