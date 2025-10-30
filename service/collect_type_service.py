
import numpy as np
from db.database import SessionLocal
from db.models import CollectTypes
from sqlalchemy.orm import Session
from logger import logger
from service.vectorstore_service import (
    warm_up_model,
    get_embedding,
    save_faiss_index,
    load_faiss_index
)


# --- Dispara o carregamento assíncrono assim que o app inicia ---
warm_up_model()


class CollectTypeService:
    def __init__(self, db: Session = None):
        """O __init__ permanece o mesmo."""
        self.db = SessionLocal() if db is None else db

    def _add_embedding_to_faiss(self, collect_type_id: int, description: str):
        """Cria embedding e adiciona no FAISS usando IndexIDMap."""
        index = load_faiss_index()
        embedding = get_embedding(description)

        id_to_add = np.array([collect_type_id], dtype=np.int64)

        index.add_with_ids(embedding, id_to_add)

        save_faiss_index(index)

    def _update_embedding_in_faiss(self, collect_type_id: int, description: str):
        """Atualiza o embedding no IndexIDMap."""
        index = load_faiss_index()
        embedding = get_embedding(description)

        id_to_remove = np.array([collect_type_id], dtype=np.int64)
        index.remove_ids(id_to_remove)

        id_to_add = np.array([collect_type_id], dtype=np.int64)
        index.add_with_ids(embedding, id_to_add)

        save_faiss_index(index)

    def _delete_embedding_from_faiss(self, collect_type_id: int):
        """Remove embedding quando um item é deletado."""
        index = load_faiss_index()

        id_to_remove = np.array([collect_type_id], dtype=np.int64)

        num_removed = index.remove_ids(id_to_remove)

        if num_removed > 0:
            save_faiss_index(index)

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
            collect_types = self.db.query(
                CollectTypes).order_by(CollectTypes.id).all()
            return {"status": "success", "data": collect_types}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def get_collect_type(self, collect_type_id: int):
        try:
            collect_type = self.db.query(CollectTypes).filter(
                CollectTypes.id == collect_type_id).first()
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
            collect_type_to_update = self.db.query(CollectTypes).filter(
                CollectTypes.id == collect_type_id).first()
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
            collect_type_to_delete = self.db.query(CollectTypes).filter(
                CollectTypes.id == collect_type_id).first()
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
