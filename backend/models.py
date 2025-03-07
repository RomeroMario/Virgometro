import random, string
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Juego(Base):
    __tablename__ = 'juegos'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    jugadores = Column(String)
    cat_actual = Column(Integer)
    jug_actual = Column(String)
    categorias = relationship("Categoria", back_populates="juego")

class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, index=True)
    
    nombre = Column(String)
    tipo = Column(Integer)
    juego_id = Column(Integer, ForeignKey('juegos.id'))
    juego = relationship("Juego", back_populates="categorias")

class Puntaje(Base):
    __tablename__ = 'puntajes'

    id = Column(Integer, primary_key=True, index=True)
    id_juego= Column(Integer, ForeignKey('juegos.id'))
    nombreJugador = Column(String) 
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    puntaje = Column(Integer)

    categoria = relationship("Categoria", back_populates="puntajes")

Categoria.puntajes = relationship("Puntaje", back_populates="categoria")
