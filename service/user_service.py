import streamlit as st
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User, UserPosition


class UserService:
    def __init__(self, db: Session = None):
        self.db = SessionLocal() if db is None else db

    def create_user(self, username: str, position: str):
        """Cria um novo usuário no banco de dados."""
        try:
            new_user = User(username=username,
                            position=UserPosition(position))
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return {"status": "success", "message": f"Usuário '{username}' cadastrado com sucesso!", "data": new_user}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao cadastrar o usuário: {e}"}
        finally:
            self.db.close()

    def read_users(self):
        try:
            users = self.db.query(User).order_by(User.id).all()
            return {"status": "success", "data": users}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def get_user(self, user_id: int = None, username=None):
        try:
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
            elif username:
                user = self.db.query(User).filter(
                    User.username == username).first()

            if user:
                return {"status": "success", "data": user}
            else:
                return {"status": "error", "message": f"Usuário com ID {user_id} não encontrado."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.db.close()

    def update_user(self, user_id: int, description: str, position: str):
        """Atualiza um usuário existente no banco de dados."""
        try:
            user_to_update = self.db.query(
                User).filter(User.id == user_id).first()
            if user_to_update:
                user_to_update.username = description
                user_to_update.position = UserPosition(position)
                self.db.commit()
                self.db.refresh(user_to_update)
                return {"status": "success", "message": f"Usuário '{description}' atualizado com sucesso!", "data": user_to_update}
            else:
                return {"status": "error", "message": f"Usuário com ID {user_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao atualizar o usuário: {e}"}
        finally:
            self.db.close()

    def delete_user(self, user_id: int):
        """Deleta um usuário do banco de dados."""
        try:
            user_to_delete = self.db.query(
                User).filter(User.id == user_id).first()
            if user_to_delete:
                self.db.delete(user_to_delete)
                self.db.commit()
                return {"status": "success", "message": f"Usuário ID {user_id} deletado com sucesso!"}
            else:
                return {"status": "error", "message": f"Usuário com ID {user_id} não encontrado."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": f"Ocorreu um erro ao deletar o usuário: {e}"}
        finally:
            self.db.close()

    def is_table_empty(self):
        """Verifica se a tabela de usuários está vazia."""
        try:
            user_count = self.db.query(User).count()
            return user_count == 0
        except Exception as e:
            print(f"Erro ao verificar se a tabela está vazia: {e}")
            return True  # Assume vazia em caso de erro para evitar falhas
        finally:
            self.db.close()
