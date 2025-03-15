from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import *
from schemas import *
from db import get_db, refresh
from soporte import genHex
import os,uvicorn
from collections import defaultdict

print("Iniciando")
refresh()
port = int(os.getenv("PORT", 8000))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)

active_connections = {}

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
        db.refresh(categoria)
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

juegos_espera = {}
jugadores_conectados = {}
conexiones_ws = {}
puntajes_recibidos = {}

@app.websocket("/ws/{codigo}/{nombre}")
async def websocket_endpoint(websocket: WebSocket, codigo: str,nombre: str,db: Session = Depends(get_db)):
    
    await websocket.accept()
    try:
        player_name = nombre
        if codigo not in jugadores_conectados:
            jugadores_conectados[codigo] = set()
            conexiones_ws[codigo] = set()
        jugadores_conectados[codigo].add(player_name)
        conexiones_ws[codigo].add(websocket)

        juego = db.query(Juego).filter(Juego.codigo == codigo).first()
        if not juego:
            print("No se encontro el juego con el codigo", codigo)
            await websocket.close()
            return

        jugadores = juego.jugadores.split(',')
        categorias = juego.categorias

        if categorias and jugadores:
            print("Trata")
            await enviar_siguiente_ronda(websocket, codigo, juego, jugadores, categorias, 0, 0)

        
        while True:
            data = await websocket.receive_json()
            nuevo_puntaje = Puntaje(
                id_juego=juego.id,
                categoria_id=data['categoria_id'],
                jugadorCalificado=data['playerCalificado'],
                nombreCalificador=player_name,
                puntaje=data['voto']
            )
            db.add(nuevo_puntaje)
            db.commit()
        
            if codigo not in puntajes_recibidos:
                puntajes_recibidos[codigo] = {}
            clave = (data['playerCalificado'], data['categoria_id'])
            if clave not in puntajes_recibidos[codigo]:
                puntajes_recibidos[codigo][clave] = set()
            puntajes_recibidos[codigo][clave].add(player_name)
        
            # Verificar si todos los calificadores ya votaron para este jugador y categoría
            if verificar_todos_votaron(codigo, jugadores_conectados[codigo], puntajes_recibidos[codigo], data['playerCalificado'], data['categoria_id']):
                categoria_index = next((i for i, cat in enumerate(categorias) if cat.id == data['categoria_id']), 0)
                jugador_index = jugadores.index(data['playerCalificado'])
        
                if categoria_index + 1 < len(categorias):
                    await enviar_siguiente_ronda(websocket, codigo, juego, jugadores, categorias, jugador_index, categoria_index + 1)
                elif jugador_index + 1 < len(jugadores):
                    await enviar_siguiente_ronda(websocket, codigo, juego, jugadores, categorias, jugador_index + 1, 0)
                else:
                    # Trigger cuando TODAS las votaciones han finalizado
                    await send_finish(codigo,db)
                    
                    websocket.send_json({
                        "status": "finalizado",
                        "mensaje": "Todas las votaciones han concluido."
                    })
                    print(f"Juego {codigo} finalizado. Se enviaron los resultados.")
                    break  # Salir del bucle, ya no hay más votaciones

    except WebSocketDisconnect:
        jugadores_conectados[codigo].remove(player_name)
        if not jugadores_conectados[codigo]:
            del jugadores_conectados[codigo]
            del conexiones_ws[codigo]
    finally:
        await websocket.close()
async def send_finish(codigo,db):
    
    promedios,totales = calcular_promedios(codigo,db)
    mensaje = {
        "status": "finalizado",
        "mensaje": "Todas las votaciones han concluido.",
        "promedios": promedios,
        "totales": totales
        
    }
    for ws in conexiones_ws[codigo]:
        await ws.send_json(mensaje)

def calcular_promedios(codigo: str, db: Session):
    # Obtener el juego por código
    juego = db.query(Juego).filter(Juego.codigo == codigo).first()
    if not juego:
        return {}, []

    # Obtener todos los puntajes del juego
    puntajes = db.query(Puntaje).filter(Puntaje.id_juego == juego.id).all()

    # Calcular promedios por jugador y categoría
    promedios = defaultdict(lambda: defaultdict(list))
    for puntaje in puntajes:
        categoria_nombre = db.query(Categoria).filter(Categoria.id == puntaje.categoria_id).first().nombre
        promedios[puntaje.jugadorCalificado][categoria_nombre].append(puntaje.puntaje)

    # Convertir listas de puntajes a promedios
    promedios_finales = defaultdict(dict)
    for jugador in promedios:
        for categoria in promedios[jugador]:
            promedio = sum(promedios[jugador][categoria]) / len(promedios[jugador][categoria])
            promedios_finales[jugador][categoria] = promedio

    # Calcular la suma total de los promedios de cada jugador
    totales = {jugador: sum(promedios_finales[jugador].values()) for jugador in promedios_finales}

    return promedios_finales, totales

async def enviar_siguiente_ronda(websocket, codigo, juego, jugadores, categorias, jugador_index, categoria_index):
    jugador = jugadores[jugador_index]
    categoria = categorias[categoria_index]
    mensaje = {
        "jugador": jugador,
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "tipo": categoria.tipo
        }}
    for ws in conexiones_ws[codigo]:
        await ws.send_json(mensaje)
    
    print("Enviando siguiente ronda")

def verificar_todos_votaron(codigo, jugadores_conectados, puntajes, jugador, categoria_id):
    clave = (jugador, categoria_id)
    if clave in puntajes:
        return jugadores_conectados == puntajes[clave]
    return False


if __name__ == "__main__":
     uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)