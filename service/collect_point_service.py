from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import CollectPoint

class CollectPointService:
    def __init__(self, db: Session = None):
        self.db = SessionLocal() if db is None else db

    def create_collect_point(self, description: str, cep: str, street: str, number: str, city: str, state: str, contact_name: str, phone: str, email: str):
        """Cria um novo ponto de coleta no banco de dados."""
        try:
            new_collect_point = CollectPoint(description=description, cep=cep, street=street, number=number, city=city, state=state, contact_name=contact_name, phone=phone, email=email)
            self.db.add(new_collect_point)
            self.db.commit()
            self.db.refresh(new_collect_point)
        
            return {"status": "success", "message": f"Ponto de coleta '{description}' cadastrado com sucesso!", "data": new_collect_point}
        
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao cadastrar o ponto de coleta: {e}"}
        
        finally:
            self.db.close()

    def read_collect_points(self):
        try:
            collect_points = self.db.query(CollectPoint).order_by(CollectPoint.id).all()
        
            return {"status": "success", "data": collect_points}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        finally:
            self.db.close()

    def get_collect_point(self, collect_point_id: int):
        try:
            collect_point = self.db.query(CollectPoint).filter(CollectPoint.id == collect_point_id).first()

            if collect_point:
                return {"status": "success", "data": collect_point}
            
            else:
                return {"status": "error", "message": f"Ponto de coleta com ID {collect_point_id} não encontrado."}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            self.db.close()

    def update_collect_point(self, collect_point_id: int, description: str, cep: str, street: str, number: str, city: str, state: str, contact_name: str, phone: str, email: str):
        """Atualiza um ponto de coleta existente no banco de dados."""
        try:
            collect_point = self.db.query(CollectPoint).filter(CollectPoint.id == collect_point_id).first()
            if collect_point:
                collect_point.description = description
                collect_point.cep = cep
                collect_point.street = street
                collect_point.number = number
                collect_point.city = city
                collect_point.state = state
                collect_point.contact_name = contact_name
                collect_point.phone = phone
                collect_point.email = email

                self.db.commit()
                self.db.refresh(collect_point)
                
                return {"status": "success", "message": f"Ponto de coleta '{description}' atualizado com sucesso!", "data": collect_point}
            
            else:
                return {"status": "error", "message": f"Ponto de coleta com ID {collect_point_id} não encontrado."}
        
        except Exception as e:
            self.db.rollback()
        
            return {"status": "error", "message": f"Ocorreu um erro ao atualizar o ponto de coleta: {e}"}
        
        finally:
            self.db.close()

    def delete_collect_point(self, collect_point_id: int):
        """Deleta um ponto de coleta do banco de dados."""
        try:
            collect_point_to_delete = self.db.query(CollectPoint).filter(CollectPoint.id == collect_point_id).first()
            if collect_point_to_delete:
                self.db.delete(collect_point_to_delete)
                self.db.commit()
                return {"status": "success", "message": f"Ponto de coleta ID {collect_point_id} deletado com sucesso!"}
            else:
                return {"status": "error", "message": f"Ponto de coleta com ID {collect_point_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao deletar o ponto de coleta: {e}"}
        finally:
            self.db.close()