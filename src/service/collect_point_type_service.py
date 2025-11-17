from sqlalchemy.orm import Session
from db.core import SessionLocal
from db.models import CollectPointCollectType


class CollectPointCollectTypeService:
    def __init__(self, *, db: Session = None):
        self.db = SessionLocal() if db is None else db

    def create_collect_point_collect_type(self, collect_point_id: int, collect_type_id: int):
        """Cria uma nova relação entre ponto de coleta e tipo de coleta no banco de dados."""
        try:
            new_relation = CollectPointCollectType(
                collect_point_id=collect_point_id, collect_type_id=collect_type_id)
            self.db.add(new_relation)
            self.db.commit()
            self.db.refresh(new_relation)
            return {"status": "success", "message": f"Relação criada com sucesso!", "data": new_relation}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao criar a relação: {e}"}
        finally:
            self.db.close()

    def read_collect_point_collect_types(self):
        try:
            relations = self.db.query(CollectPointCollectType).all()
            return {"status": "success", "data": relations}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def get_collect_point_collect_type(self, collect_point_id: int, collect_type_id: int):
        try:
            relation = self.db.query(CollectPointCollectType).filter(
                CollectPointCollectType.collect_point_id == collect_point_id,
                CollectPointCollectType.collect_type_id == collect_type_id
            ).first()
            if relation:
                return {"status": "success", "data": relation}
            else:
                return {"status": "error", "message": f"Relação não encontrada."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def delete_collect_point_collect_type(self, collect_point_id: int, collect_type_id: int):
        """Deleta uma relação entre ponto de coleta e tipo de coleta do banco de dados."""
        try:
            relation_to_delete = self.db.query(CollectPointCollectType).filter(
                CollectPointCollectType.collect_point_id == collect_point_id,
                CollectPointCollectType.collect_type_id == collect_type_id
            ).first()
            if relation_to_delete:
                self.db.delete(relation_to_delete)
                self.db.commit()
                return {"status": "success", "message": f"Relação deletada com sucesso!"}
            else:
                return {"status": "error", "message": f"Relação não encontrada."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao deletar a relação: {e}"}
        finally:
            self.db.close()

    def get_collect_points_by_collect_type(self, collect_type_id: int):
        """Busca todos os pontos de coleta associados a um determinado tipo de coleta."""
        try:
            relations = self.db.query(CollectPointCollectType).where(
                CollectPointCollectType.collect_type_id == collect_type_id).all()

            collect_points = {}

            for relation in relations:
                point = relation.collect_point
                type = relation.collect_type

                if point.id not in collect_points:
                    collect_points[point.id] = {
                        "id": point.id,
                        "collect_point": point,
                        "collect_types": []
                    }

                collect_points[point.id]["collect_types"].append(type)

            values = list(collect_points.values())

            return {"status": "success", "data": values}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            self.db.close()
