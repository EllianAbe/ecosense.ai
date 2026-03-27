import streamlit as st
from sentence_transformers import SentenceTransformer
from huggingface_hub import login as hf_login
from utils.logger import logger
import threading
import os
import faiss
import numpy as np
# --- FAISS setup ---
FAISS_INDEX_PATH = "data/collect_types.faiss"
DISTANCE_THRESHOLD = float(os.getenv('DISTANCE_THRESHOLD', '1.3'))
MODEL = 'google/embeddinggemma-300m'


@st.cache_resource
def get_embedder():
    '''Carrega e retorna o modelo de embedding com caching.'''

    logger.info("🔑 Conectando ao Hugging Face...")

    HF_TOKEN = st.secrets['HUGGINGFACE_TOKEN']
    hf_login(HF_TOKEN)

    logger.info(
        f"📦 Carregando modelo '{MODEL}' (isso pode demorar na primeira vez)...")
    model = SentenceTransformer(MODEL)
    logger.info("✅ Modelo carregado e cacheado.")

    return model


class VectorStoreService:
    def __init__(self):
        self.warm_up_model()
        self.index = self.load_faiss_index()
        self._index_lock = threading.Lock()

    # --- Lazy model setup with caching and async warm-up ---

    def warm_up_model(self):
        """Pré-carrega o modelo em background sem travar o Streamlit."""
        def _load():
            try:
                logger.info("🕓 Iniciando carregamento assíncrono do modelo...")
                self.embedder = get_embedder()
                logger.info(
                    "🔥 Modelo pronto para uso (carregado em background).")
            except Exception as e:
                logger.info(f"⚠️ Falha ao carregar modelo em background: {e}")

        threading.Thread(target=_load, daemon=True).start()

    def get_embed_dim(self):
        """Obtém a dimensão do embedding (sem carregar o modelo antes da hora)."""
        return self.embedder.get_sentence_embedding_dimension()

    def get_embedding(self, text: str):
        return self.embedder.encode([text], convert_to_numpy=True, normalize_embeddings=True)

    def load_faiss_index(self):
        """Carrega o índice FAISS (IndexIDMap) do disco."""
        if os.path.exists(FAISS_INDEX_PATH):
            logger.info(
                f"Carregando índice FAISS existente de {FAISS_INDEX_PATH}")
            index = faiss.read_index(FAISS_INDEX_PATH)
        else:
            logger.info(
                "Nenhum índice FAISS encontrado. Criando um novo IndexIDMap.")
            embed_dim = self.get_embed_dim()

            index_flat = faiss.IndexFlatL2(embed_dim)
            index = faiss.IndexIDMap(index_flat)

        return index

    def save_faiss_index(self, index):
        """Persiste o índice FAISS no disco."""
        logger.info(f"Salvando índice FAISS em {FAISS_INDEX_PATH}")
        faiss.write_index(index, FAISS_INDEX_PATH)

    def search_faiss_index(self, query_text: str, *, k: int = 3, distance_threshold: float = DISTANCE_THRESHOLD):
        try:
            logger.info(f"🔍 Iniciando busca semântica por: '{query_text}'")

            index = self.load_faiss_index()
            if index.ntotal == 0:
                logger.warning(
                    "⚠️ O índice FAISS está vazio. Nenhuma busca pode ser realizada.")
                return [], []

            query_embedding = self.get_embedding(query_text)
            k_search = min(k, index.ntotal)

            distances, ids = index.search(query_embedding, k_search)

            original_ids = ids[0]
            original_distances = distances[0]

            found_db_ids = []
            found_distances = []

            for i, dist in enumerate(original_distances):
                db_id = int(original_ids[i])

                if db_id != -1 and dist <= distance_threshold:
                    found_db_ids.append(db_id)
                    found_distances.append(dist)

                elif db_id == -1:
                    pass

                else:
                    logger.info(
                        f"ℹ️ Resultado ID {db_id} com distância {dist:.4f} (maior que {distance_threshold}) descartado. Parando filtro.")
                    break

            logger.info(f"✅ Busca concluída. IDs encontrados: {found_db_ids}")
            return found_db_ids, found_distances

        except Exception as e:
            logger.error(f"❌ Erro durante a busca no FAISS: {e}")
            return [], []

    def add_embedding(self, id: int, text: str):
        embedding = self.get_embedding(text)
        ids = np.array([id], dtype=np.int64)
        with self._index_lock:
            self.index.add_with_ids(embedding, ids)
            self.save_faiss_index(self.index)

    def update_embedding(self, id: int, text: str):
        embedding = self.get_embedding(text)
        ids = np.array([id], dtype=np.int64)
        with self._index_lock:
            try:
                self.index.remove_ids(ids)
            except Exception:
                pass
            self.index.add_with_ids(embedding, ids)
            self.save_faiss_index(self.index)

    def remove_embedding(self, id: int):
        ids = np.array([id], dtype=np.int64)
        with self._index_lock:
            num_removed = self.index.remove_ids(ids)
            if num_removed > 0:
                self.save_faiss_index(self.index)
