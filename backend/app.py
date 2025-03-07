from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import *  # Importa tus modelos aquí, por ejemplo, Usuario, Producto, etc.
from schemas import *
from db import get_db, refresh
from soporte import genHex
import os,uvicorn

refresh()
port = int(os.getenv("PORT", 8000))
app = FastAPI()

@app.get("/juegos")
def get_juegos(db: Session = Depends(get_db)):
    juegos = db.query(Juego).all()
    return juegos


@app.post("/newgame")
def create_juego(juego: CrearJuego, db: Session = Depends(get_db)):
    categorias = []
    for cat in juego.categorias:
        categoria = Categoria(nombre=cat.nombre, tipo=cat.tipo)
        db.add(categoria)
        db.commit()
        db.refresh(categoria)  # Esto asegura que se incluyan los campos completos
        categorias.append(categoria)
    
    juegoNuevo = Juego(
        codigo=genHex(db),
        categorias=categorias,
        jugadores=",".join(juego.jugadores)
    )
    db.add(juegoNuevo)
    db.commit()
    db.refresh(juegoNuevo)
    
    return {
        "id": juegoNuevo.id,
        "codigo": juegoNuevo.codigo,
        "jugadores": juegoNuevo.jugadores,
        "categorias": [{"id": c.id, "nombre": c.nombre, "tipo": c.tipo} for c in juegoNuevo.categorias]
    }


@app.put("/juegos/{juego_id}")
def update_juego(juego_id: int, juego: CrearJuego, db: Session = Depends(get_db)):
    db_juego = db.query(Juego).filter(Juego.id == juego_id).first()
    if not db_juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)