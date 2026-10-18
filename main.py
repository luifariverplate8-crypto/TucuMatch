from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3
import os

app = FastAPI(title="TucuMatch API")

# Permitir peticiones desde cualquier origen (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Base de Datos SQLite
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
            verificado INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            matched_user_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Ruta raíz: sirve directamente la interfaz visual (index.html)
@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "TucuMatch Backend Online - Archivo index.html no encontrado"}

# Obtener perfiles para descubrir
@app.get("/api/profiles")
def get_profiles():
    # Perfiles de prueba iniciales para Tucumán
    profiles = [
        {
            "id": 1,
            "nombre": "Lucía",
            "edad": 24,
            "barrio": "Yerba Buena",
            "bio": "Amante del cerro San Javier y el sanguchazo de milanesa con todo 🥪",
            "verificado": True,
            "fotos": ["https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500"]
        },
        {
            "id": 2,
            "nombre": "Gonzalo",
            "edad": 27,
            "barrio": "Barrio Norte",
            "bio": "Café en la plaza San Martín los domingos y mates en el parque 🌿",
            "verificado": True,
            "fotos": ["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500"]
        },
        {
            "id": 3,
            "nombre": "Sofía",
            "edad": 22,
            "barrio": "Barrio Sur",
            "bio": "Estudiante de UNT. ¿Sanguche de milanesa en primera cita es buen plan o red flag?",
            "verificado": False,
            "fotos": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500"]
        }
    ]
    return profiles

# Endpoint para verificación por Selfie
@app.post("/api/verify")
async def verify_user(selfie: UploadFile = File(...)):
    # Simulación de verificación instantánea
    return {
        "status": "success",
        "message": "¡Selfie recibida y perfil verificado exitosamente!",
        "verified": True
    }

# Endpoint para dar Like / Match
@app.post("/api/like/{profile_id}")
def like_profile(profile_id: int):
    # Simulación de Match automático para pruebas
    is_match = profile_id in [1, 2]
    return {
        "status": "success",
        "match": is_match,
        "message": "¡Es un Match Tucumano! 🎉" if is_match else "Like enviado"
    }
