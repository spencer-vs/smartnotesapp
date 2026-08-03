from .embedding import generate_embedding
from .faiss_index import (
    get_or_create_index,
    add_embedding,
    save_index,
    load_note_ids,
    save_note_ids,
)


def build_search_text(note):
    title = note.title or " "
    content = note.content or " "
    
    return f"{title}\n\n{content}"

def index_note(note):
    text = build_search_text(note)
    embedding = generate_embedding(text)
    index = get_or_create_index()
    add_embedding(index, embedding)
    note_ids = load_note_ids()
    note_ids.append(note.id)
    save_note_ids(note_ids)
    save_index(index)
    