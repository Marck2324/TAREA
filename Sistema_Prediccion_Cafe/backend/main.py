from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="Sistema de Predicción de Calidad de Café")

# --- RUTAS ABSOLUTAS (importantes para Render) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Carpeta backend/
DB_PATH = os.path.join(BASE_DIR, "sistema_cafe.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            altitud REAL,
            variedad TEXT,
            humedad REAL,
            status TEXT,
            puntaje REAL,
            calidad TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_db()

# --- MODELOS ---
class LoginSchema(BaseModel):
    username: str
    password: str

class PredictSchema(BaseModel):
    usuario: str
    altitud: float
    variedad: str
    humedad: float
    status: str
    puntaje: float

# --- RUTAS API ---

@app.post("/api/login")
def login(datos: LoginSchema):
    if datos.username == "uacceso" and datos.password == "uacceso":
        return {"status": "success", "username": datos.username}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")

@app.post("/api/predict")
def predict(datos: PredictSchema):
    if datos.puntaje >= 85.0:
        resultado_calidad = "Taza de Excelencia"
    elif datos.puntaje >= 80.0:
        resultado_calidad = "Café de Especialidad"
    else:
        resultado_calidad = "Café Comercial / Estándar"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historial (usuario, altitud, variedad, humedad, status, puntaje, calidad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datos.usuario, datos.altitud, datos.variedad, 
              datos.humedad, datos.status, datos.puntaje, resultado_calidad))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar: {e}")
        raise HTTPException(status_code=500, detail="No se pudo registrar")

    return {"calidad": resultado_calidad}

@app.get("/api/historial")
def obtener_historial():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, altitud, variedad, humedad, status, puntaje, calidad FROM historial ORDER BY id DESC")
        filas = cursor.fetchall()
        conn.close()
        return [{"usuario": f[0], "altitud": f[1], "variedad": f[2], 
                 "humedad": f[3], "status": f[4], "puntaje": f[5], "calidad": f[6]} 
                for f in filas]
    except Exception as e:
        print(f"Error: {e}")
        return []

# --- SERVIR FRONTEND ---

# Ruta raíz: redirige a login
@app.get("/")
def root():
    login_path = os.path.join(FRONTEND_DIR, "src", "login.html")
    with open(login_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Servir archivos estáticos (imágenes, CSS, etc.)
app.mount("/src", StaticFiles(directory=os.path.join(FRONTEND_DIR, "src")), name="static")

# Servir cada HTML individualmente
@app.get("/login.html")
def login_html():
    with open(os.path.join(FRONTEND_DIR, "src", "login.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/predictor.html")
def predictor_html():
    with open(os.path.join(FRONTEND_DIR, "src", "predictor.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/historial.html")
def historial_html():
    with open(os.path.join(FRONTEND_DIR, "src", "historial.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
