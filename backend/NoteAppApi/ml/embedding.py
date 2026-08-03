from sentence_transformers import SentenceTransformer

# Load the model once when the application starts
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text):
    """
    Generate a semantic embedding for the given text.
    """
    return model.encode(text)