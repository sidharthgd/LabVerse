from sentence_transformers import SentenceTransformer
import faiss, pickle

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, k=3):
    index = faiss.read_index("index/faiss.index")
    with open("index/meta.pkl", "rb") as f:
        metadata_list = pickle.load(f)

    query_vec = model.encode([query])
    D, I = index.search(query_vec, k)

    return [metadata_list[i] for i in I[0]]