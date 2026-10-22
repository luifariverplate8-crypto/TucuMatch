from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI(title="TucuMatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProfileCreate(BaseModel):
    nombre: str
    edad: int
    barrio: str
    bio: str
    pregunta: Optional[str] = "¿Sanguche de milanesa en primera cita?"
    respuesta: Optional[str] = "¡Buen plan de una!"
    fotos: List[str]

def init_db():
    conn = sqlite3.connect("tucumatch.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            barrio TEXT NOT NULL,
            bio TEXT,
            pregunta TEXT,
            respuesta TEXT,
            verificado INTEGER DEFAULT 1,
            fotos TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "TucuMatch Backend Online"}

@app.get("/api/profiles")
def get_profiles():
    conn = sqlite3.connect("tucumatch.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, edad, barrio, bio, pregunta, respuesta, verificado, fotos FROM users ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        # Perfiles oficiales de lanzamiento para Tucumán
        return [
            {
                "id": 1,
                "nombre": "Lucía",
                "edad": 24,
                "barrio": "Yerba Buena",
                "bio": "Fan del cerro San Javier, mates en el parque y el sanguchazo con todo 🥪",
                "pregunta": "¿Sanguche de milanesa en primera cita?",
                "respuesta": "¡Totalmente, re buen plan!",
                "verificado": True,
                "fotos": ["https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500", "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=500"]
            },
            {
                "id": 2,
                "nombre": "Gonzalo",
                "edad": 27,
                "barrio": "San Miguel de Tucumán - Barrio Norte",
                "bio": "Café en Barrio Norte los domingos y salidas a la Aconquija ☕",
                "pregunta": "¿Empanada tucumana con limón?",
                "respuesta": "Sí o sí, sin discusión 🍋",
                "verificado": True,
                "fotos": ["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500"]
            },
            {
                "id": 3,
                "nombre": "Valentina",
                "edad": 22,
                "barrio": "Tafí del Valle",
                "bio": "Amante de los valles, las caminatas y el queso tafisto 🌄",
                "pregunta": "¿Mejor lugar para merendar?",
                "respuesta": "Mirador de Tafí del Valle",
                "verificado": True,
                "fotos": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500"]
            },
            {
                "id": 4,
                "nombre": "Mateo",
                "edad": 25,
                "barrio": "Concepción",
                "bio": "Estudiante de agronomía, apasionado de las motos y el fútbol ⚽",
                "pregunta": "¿Sanguche de milanesa en primera cita?",
                "respuesta": "Obvio, en la sanguchería del barrio",
                "verificado": True,
                "fotos": ["https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=500"]
            }
        ]

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "nombre": r[1],
            "edad": r[2],
            "barrio": r[3],
            "bio": r[4],
            "pregunta": r[5],
            "respuesta": r[6],
            "verificado": bool(r[7]),
            "fotos": r[8].split("|||")
        })
    return result

@app.post("/api/profiles")
def create_profile(profile: ProfileCreate):
    conn = sqlite3.connect("tucumatch.db")
    cursor = conn.cursor()
    fotos_str = "|||".join(profile.fotos)
    cursor.execute("""
        INSERT INTO users (nombre, edad, barrio, bio, pregunta, respuesta, verificado, fotos)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (profile.nombre, profile.edad, profile.barrio, profile.bio, profile.pregunta, profile.respuesta, fotos_str))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "id": new_id}
