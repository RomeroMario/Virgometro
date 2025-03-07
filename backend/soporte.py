import random
from fastapi import Depends
from db import get_db
from sqlalchemy.orm import Session
from models import Juego



def genHex(db):  # Inject db session here
    caracteres = '0123456789ABCDEF'
    codigo = ''
    while True:
        codigo = ''.join(random.choice(caracteres) for _ in range(6))
        if not verHex(codigo, db):  # Pass db as argument
            break
    return codigo

# Function to verify if the hex code already exists in the database
def verHex(codigo: str, db: Session):  # Accept db as argument
    codigos = db.query(Juego.codigo).all()
    codigos = [c[0] for c in codigos] 
    if codigo in codigos:
        return True
    
    return False