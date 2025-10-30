
import streamlit as st
from sentence_transformers import SentenceTransformer
from huggingface_hub import login as hf_login
from logger import logger
import threading
import os
import os
import faiss
import numpy as np

# --- FAISS setup ---
FAISS_INDEX_PATH = "collect_types.faiss"
FAISS_ID_MAP_PATH = "collect_type_ids.npy"


@st.cache_resource
def get_embedder():
    """Carrega e cacheia o modelo de embedding."""
    HF_TOKEN = os.environ.get(
        "HUGGINGFACE_TOKEN") or "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"
    logger.info("🔑 Conectando ao Hugging Face...")
    hf_login(HF_TOKEN)
    logger.info(
        "📦 Carregando modelo 'google/embeddinggemma-300m' (isso pode demorar na primeira vez)...")
    model = SentenceTransformer("google/embeddinggemma-300m")
    logger.info("✅ Modelo carregado e cacheado.")
    return model


# --- Lazy model setup with caching and async warm-up ---
def warm_up_model():
    """Pré-carrega o modelo em background sem travar o Streamlit."""
    def _load():
        try:
            logger.info("🕓 Iniciando carregamento assíncrono do modelo...")
            _ = get_embedder()
            logger.info("🔥 Modelo pronto para uso (carregado em background).")
        except Exception as e:
            logger.info(f"⚠️ Falha ao carregar modelo em background: {e}")

    threading.Thread(target=_load, daemon=True).start()


def get_embed_dim():
    """Obtém a dimensão do embedding (sem carregar o modelo antes da hora)."""
    embedder = get_embedder()
    return embedder.get_sentence_embedding_dimension()


def get_embedding(text: str):
    embedder = get_embedder()
    return embedder.encode([text], convert_to_numpy=True)


def load_faiss_index():
    """Carrega o índice e mapa de IDs do FAISS (se houver)."""
    embed_dim = get_embed_dim()
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_ID_MAP_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        id_map = np.load(FAISS_ID_MAP_PATH)
    else:
        index = faiss.IndexFlatL2(embed_dim)
        id_map = np.array([], dtype=np.int32)
    return index, id_map


def save_faiss_index(index, id_map):
    """Persiste índice e mapa de ID do FAISS no disco."""
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(FAISS_ID_MAP_PATH, id_map)
