import faiss
import numpy as np 

def create_index(chunks):
    embeddings=np.array([chunk['embedding'] for chunk in chunks],dtype='float32')
    dimension=embeddings.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def search(index,query_embedd,chunk,top_k:int=3):
    query=np.array([query_embedd],dtype="float32")
    distances,indices=index.search(query,top_k)
    result=[]
    for distance , idx in zip(distances[0],indices[0]):
        result.append({
            "chunk":chunk[idx],
            "distance":distance
        })

    return result
