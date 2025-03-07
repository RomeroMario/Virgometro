from pydantic import BaseModel

class JuegoCreate(BaseModel):
    nombre: str
    tipo: int

# Crear una instancia del modelo
nuevo_juego = JuegoCreate(nombre="Adivina el personaje", tipo=1)

# Usar el método dict()
juego_dict = nuevo_juego.dict()

print(juego_dict)  # {'nombre': 'Adivina el personaje', 'tipo': 1}
