import faiss
import numpy as np
from logger import logger

# Load your FAISS index from disk
index = faiss.read_index("collect_types.faiss")

logger.info("Number of vectors in FAISS:", index.ntotal)
logger.info("Dimension of vectors:", index.d)

# Inspect a few vectors
for i in range(min(5, index.ntotal)):
    vector = index.reconstruct(i)  # get the actual vector as numpy array
    logger.info(f"\nVector {i}:")
    logger.info(vector[:10], "...")  # show only first 10 values for brevity

# Optional: get all vectors
all_vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)])
logger.info("\nAll vectors shape:", all_vectors.shape)
