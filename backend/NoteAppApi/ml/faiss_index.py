import faiss
import numpy as np
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

INDEX_PATH = os.path.join(BASE_DIR, "faiss", "notes.index")
IDS_PATH = os.path.join(BASE_DIR, "faiss", "note_ids.npy")


def create_index():
    dimension = 384
    index = faiss.IndexFlatL2(dimension)
    return index


def add_embedding(index, embedding):
    embedding = np.array(embedding).astype("float32").reshape(1, -1)
    index.add(embedding)
    
def save_index(index):
    faiss.write_index(index, INDEX_PATH)
    
    
def load_index():
    return faiss.read_index(INDEX_PATH)

def save_note_ids(note_ids):
    np.save(IDS_PATH, np.array(note_ids, dtype=np.int64))
    
def load_note_ids():
    if os.path.exists(IDS_PATH):
        return np.load(IDS_PATH).tolist()
    return []

def get_or_create_index():
    if os.path.exists(INDEX_PATH):
        return load_index()

    return create_index()