from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from db.database import Base
import enum


class UserPosition(str, enum.Enum):
    ADMINISTRADOR = "admin"
    USUARIO_COMUM = "common"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    position = Column(SQLAlchemyEnum(UserPosition))


class CollectTypes(Base):
    __tablename__ = 'collect_type'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)


class CollectPoint(Base):
    __tablename__ = 'collect_point'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    cep = Column(String)
    street = Column(String)
    number = Column(String)
    city = Column(String)
    state = Column(String)
    contact_name = Column(String)
    phone = Column(String)
    email = Column(String)


class CollectPointCollectType(Base):
    __tablename__ = 'collect_point_collect_type'

    collect_point_id = Column(Integer, ForeignKey(
        'collect_point.id'), primary_key=True)
    collect_type_id = Column(Integer, ForeignKey(
        'collect_type.id'), primary_key=True)
    collect_point = relationship(
        "CollectPoint", backref="collect_point_collect_types")
    collect_type = relationship(
        "CollectTypes", backref="collect_point_collect_types")
