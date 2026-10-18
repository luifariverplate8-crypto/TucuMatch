import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="TucuMatch API")

# Habilitar CORS para permitir peticiones desde cualquier origen (Vercel, localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "citas.db"

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de usuarios principal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            zone TEXT NOT NULL,
            bio TEXT,
            icebreaker TEXT,
            ideal_date TEXT,
            milanesa_stance TEXT DEFAULT 'Buen Plan 🥪🔥',
            photo_url TEXT,
            is_verified INTEGER DEFAULT 1,
            interests TEXT DEFAULT '[]',
            answers TEXT DEFAULT '{}'
        )
    """)
    
    # Tabla para fotos de la galería
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            photo_url TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Insertar usuarios semilla si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ("41234567", "Lara Albarracín", 23, "Yerba Buena", "Amante de las caminatas por San Javier, la cumbia y el trekking.", "¿A qué lugar me invitás en la primera cita?", "Caminata y mates por el Cerro San Javier ⛰️", "Buen Plan 🥪🔥", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500", 1, '["Trekking","Cumbia","Viajes","Mascotas"]', '{"night":"Series","drink":"Mates","music":"Cumbia"}'),
            ("42076543", "Facundo Juárez", 26, "Barrio Norte", "Estudiante de ingeniería, fan del café en Barrio Norte y el mate amargo.", "¿Lugar preferido para unos mates?", "Café amargo en Barrio Norte ☕", "Red Flag 🚩", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", 1, '["Café","Música","Gimnasio","Tecnología"]', '{"night":"Salida","drink":"Mates","music":"Rock"}'),
            ("43112233", "Sofía Romero", 24, "Centro", "Diseñadora, fan de los viajes a Tafí del Valle y las charlas profundas.", "¿Empanadas de carne o pollo?", "Mates al atardecer en la Plaza Urquiza 🧉", "Buen Plan 🥪🔥", "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500", 1, '["Arte","Viajes","Mascotas","Café"]', '{"night":"Series","drink":"Mates","music":"Pop"}'),
            ("48998877", "Mateo Posse", 28, "Yerba Buena", "Deportista, fan del trekking por las Yungas y la buena cerveza.", "¿Cuál es tu lugar preferido para la primera cita?", "Cerveza artesanal en Yerba Buena 🍺", "Buen Plan 🥪🔥", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500", 1, '["Gimnasio","Trekking","Cerveza","Deportes"]', '{"night":"Salida","drink":"Previa","music":"Rock"}')
        ]
        cursor.executemany("""
            INSERT INTO users (dni, name, age, zone, bio, icebreaker, ideal_date, milanesa_stance, photo_url, is_verified, interests, answers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_users)
        conn.commit()
    conn.close()

init_db()

class UserCreate(BaseModel):
    dni: str
    name: str
    age: int
    zone: str
    bio: Optional[str] = ""
    icebreaker: Optional[str] = ""
    ideal_date: Optional[str] = "Mates en la Plaza Urquiza 🧉"
    milanesa_stance: Optional[str] = "Buen Plan 🥪🔥"
    photo_url: Optional[str] = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=500"
    interests: Optional[str] = "[]"
    answers: Optional[str] = "{}"

@app.get("/")
def read_root():
    return {"message": "TucuMatch Backend Online"}

@app.get("/users/")
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, dni, name, age, zone, bio, icebreaker, ideal_date, milanesa_stance, photo_url, is_verified, interests, answers FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

@app.post("/users/")
def create_user(user: UserCreate):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (dni, name, age, zone, bio, icebreaker, ideal_date, milanesa_stance, photo_url, interests, answers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user.dni, user.name, user.age, user.zone, user.bio, user.icebreaker, user.ideal_date, user.milanesa_stance, user.photo_url, user.interests, user.answers))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"id": new_id, "message": "Usuario creado con éxito en TucuMatch"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="El DNI ya se encuentra registrado.")

@app.post("/verify_selfie/{user_id}")
def verify_selfie(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Perfil verificado con éxito"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)