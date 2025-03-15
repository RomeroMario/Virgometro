from pydantic import BaseModel
from typing import List, Optional

class CrearCategoria(BaseModel):
    nombre: str
    tipo: int
    
class CrearJuego(BaseModel):
    categorias: List[CrearCategoria]
    jugadores: List[str]
    

class ActualizarJuego(BaseModel):
    jugadorActual: str
    catActual: int
    


