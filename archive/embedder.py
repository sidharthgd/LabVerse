from sentence_transformers import SentenceTransformer
import faiss
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_metadata(metadata_list):
    texts = []
    for m in metadata_list:
        # Get a preview of sample data
        sample_text = "; ".join(
            [", ".join(f"{k}: {v}" for k, v in row.items()) for row in m["sample"]]
        )
        desc = f"{m['file']} with columns {', '.join(m['columns'])}. Sample rows: {sample_text}"
        texts.append(desc)

    embeddings = model.encode(texts, show_progress_bar=True)
    
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(embeddings)

    with open("index/meta.pkl", "wb") as f:
        pickle.dump(metadata_list, f)
    faiss.write_index(index, "index/faiss.index")