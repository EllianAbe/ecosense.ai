import os
import faiss
import numpy as np
import threading
import streamlit as st
from time import sleep
from sentence_transformers import SentenceTransformer
from huggingface_hub import login as hf_login
from db.database import SessionLocal
from db.models import CollectTypes
from sqlalchemy.orm import Session


# --- Lazy model setup with caching and async warm-up ---

@st.cache_resource
def get_embedder():
    """Carrega e cacheia o modelo de embedding."""
    HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN") or "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"
    print("🔑 Conectando ao Hugging Face...")
    hf_login(HF_TOKEN)
    print("📦 Carregando modelo 'google/embeddinggemma-300m' (isso pode demorar na primeira vez)...")
    model = SentenceTransformer("google/embeddinggemma-300m")
    print("✅ Modelo carregado e cacheado.")
    return model


def warm_up_model():
    """Pré-carrega o modelo em background sem travar o Streamlit."""
    def _load():
        try:
            print("🕓 Iniciando carregamento assíncrono do modelo...")
            _ = get_embedder()
            print("🔥 Modelo pronto para uso (carregado em background).")
        except Exception as e:
            print(f"⚠️ Falha ao carregar modelo em background: {e}")

    threading.Thread(target=_load, daemon=True).start()


# --- Dispara o carregamento assíncrono assim que o app inicia ---
warm_up_model()


def get_embed_dim():
    """Obtém a dimensão do embedding (sem carregar o modelo antes da hora)."""
    embedder = get_embedder()
    return embedder.get_sentence_embedding_dimension()


# --- FAISS setup ---
FAISS_INDEX_PATH = "collect_types.faiss"
FAISS_ID_MAP_PATH = "collect_type_ids.npy"


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


class CollectTypeService:
    def __init__(self, db: Session = None):
        self.db = SessionLocal() if db is None else db

    def _get_embedding(self, text: str):
        embedder = get_embedder()
        return embedder.encode([text], convert_to_numpy=True)

    def _add_embedding_to_faiss(self, collect_type_id: int, description: str):
        """Cria embedding e adiciona no FAISS."""
        index, id_map = load_faiss_index()
        embedding = self._get_embedding(description)
        index.add(embedding)
        id_map = np.append(id_map, collect_type_id)
        save_faiss_index(index, id_map)

    def _update_embedding_in_faiss(self, collect_type_id: int, description: str):
        """Atualiza o embedding."""
        index, id_map = load_faiss_index()
        embedding = self._get_embedding(description)

        if collect_type_id in id_map:
            pos = np.where(id_map == collect_type_id)[0][0]
            index.remove_ids(np.array([pos], dtype=np.int64))
            index.add(embedding)
        else:
            index.add(embedding)
            id_map = np.append(id_map, collect_type_id)

        save_faiss_index(index, id_map)

    def _delete_embedding_from_faiss(self, collect_type_id: int):
        """Remove embedding quando um item é deletado."""
        index, id_map = load_faiss_index()
        if collect_type_id in id_map:
            pos = np.where(id_map == collect_type_id)[0][0]
            index.remove_ids(np.array([pos], dtype=np.int64))
            id_map = np.delete(id_map, pos)
            save_faiss_index(index, id_map)

    def create_collect_type(self, description: str):
        """Cria um novo tipo de coleta no banco de dados e adiciona o embedding."""
        try:
            new_collect_type = CollectTypes(description=description)
            self.db.add(new_collect_type)
            self.db.commit()
            self.db.refresh(new_collect_type)

            # Adiciona o embedding
            self._add_embedding_to_faiss(new_collect_type.id, description)

            return {
                "status": "success",
                "message": f"Tipo de coleta '{description}' cadastrado com sucesso!",
                "data": new_collect_type
            }
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao cadastrar o tipo de coleta: {e}"}
        finally:
            self.db.close()

    def read_collect_types(self):
        try:
            collect_types = self.db.query(CollectTypes).order_by(CollectTypes.id).all()
            return {"status": "success", "data": collect_types}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def get_collect_type(self, collect_type_id: int):
        try:
            collect_type = self.db.query(CollectTypes).filter(CollectTypes.id == collect_type_id).first()
            if collect_type:
                return {"status": "success", "data": collect_type}
            else:
                return {"status": "error", "message": f"Tipo de coleta com ID {collect_type_id} não encontrado."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def update_collect_type(self, collect_type_id: int, description: str):
        """Atualiza um tipo de coleta existente no banco de dados e o embedding."""
        try:
            collect_type_to_update = self.db.query(CollectTypes).filter(CollectTypes.id == collect_type_id).first()
            if collect_type_to_update:
                collect_type_to_update.description = description
                self.db.commit()
                self.db.refresh(collect_type_to_update)

                # Atualiza o embedding
                self._update_embedding_in_faiss(collect_type_id, description)

                return {
                    "status": "success",
                    "message": f"Tipo de coleta '{description}' atualizado com sucesso!",
                    "data": collect_type_to_update
                }
            else:
                return {"status": "error", "message": f"Tipo de coleta com ID {collect_type_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao atualizar o tipo de coleta: {e}"}
        finally:
            self.db.close()

    def delete_collect_type(self, collect_type_id: int):
        """Deleta um tipo de coleta do banco de dados e o embedding."""
        try:
            collect_type_to_delete = self.db.query(CollectTypes).filter(CollectTypes.id == collect_type_id).first()
            if collect_type_to_delete:
                self.db.delete(collect_type_to_delete)
                self.db.commit()

                # Deletar embedding
                self._delete_embedding_from_faiss(collect_type_id)

                return {"status": "success", "message": f"Tipo de coleta ID {collect_type_id} deletado com sucesso!"}
            else:
                return {"status": "error", "message": f"Tipo de coleta com ID {collect_type_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao deletar o tipo de coleta: {e}"}
        finally:
            self.db.close()
