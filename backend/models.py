from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="operator")

    paradas = relationship("Parada", back_populates="user")

class Parada(Base):
    """Tabla de registro de paradas de máquina."""

    __tablename__ = 'paradas'

    id = Column(Integer, primary_key=True, index=True)
    seccion = Column(String, index=True)
    motivo = Column(String)
    timestamp_inicio = Column(DateTime, default=datetime.utcnow)
    timestamp_fin = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("User", back_populates="paradas")
