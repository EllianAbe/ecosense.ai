import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from huggingface_hub import login as hf_login

from db.database import SessionLocal
from db.models import CollectTypes
from sqlalchemy.orm import Session

# --- Embedding setup ---
#TODO: Substituir o token
HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN") or "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"

print("Acessando Hugging Face...")
hf_login(HF_TOKEN)

print("Carregando embedding model google/embeddinggemma-300m (aguarde)...")
embedder = SentenceTransformer("google/embeddinggemma-300m")
EMBED_DIM = embedder.get_sentence_embedding_dimension()

# --- FAISS setup ---
FAISS_INDEX_PATH = "collect_types.faiss"
FAISS_ID_MAP_PATH = "collect_type_ids.npy"

def load_faiss_index():
    """Carrega o índice e mapa de IDs do FAISS (se houver)"""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_ID_MAP_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        id_map = np.load(FAISS_ID_MAP_PATH)
    else:
        index = faiss.IndexFlatL2(EMBED_DIM)
        id_map = np.array([], dtype=np.int32)
    return index, id_map

def save_faiss_index(index, id_map):
    """Persiste índice e mapa de ID do FAISS no disco."""
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(FAISS_ID_MAP_PATH, id_map)


class CollectTypeService:
    def __init__(self, db: Session = None):
        self.db = SessionLocal() if db is None else db

    def _add_embedding_to_faiss(self, collect_type_id: int, description: str):
        """Cria embedding e adiciona no FAISS"""
        index, id_map = load_faiss_index()
        embedding = embedder.encode([description], convert_to_numpy=True)
        index.add(embedding)
        id_map = np.append(id_map, collect_type_id)
        save_faiss_index(index, id_map)

    def _update_embedding_in_faiss(self, collect_type_id: int, description: str):
        """Atualizar o embedding."""
        index, id_map = load_faiss_index()
        if collect_type_id in id_map:
            pos = np.where(id_map == collect_type_id)[0][0]
            embedding = embedder.encode([description], convert_to_numpy=True)
            index.reconstruct(pos)  # placeholder to ensure FAISS aware of modification
            index.remove_ids(np.array([pos], dtype=np.int64))
            index.add(embedding)
        else:
            # If missing (maybe FAISS index was reset), add it
            embedding = embedder.encode([description], convert_to_numpy=True)
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

            # Add embedding
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

                # Update embedding
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

                # Delete embedding
                self._delete_embedding_from_faiss(collect_type_id)

                return {"status": "success", "message": f"Tipo de coleta ID {collect_type_id} deletado com sucesso!"}
            else:
                return {"status": "error", "message": f"Tipo de coleta com ID {collect_type_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao deletar o tipo de coleta: {e}"}
        finally:
            self.db.close()
