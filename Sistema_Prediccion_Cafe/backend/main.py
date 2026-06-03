from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="Sistema de Predicción de Calidad de Café")


DB_PATH = "sistema_cafe.db"

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Aseguramos la existencia de la tabla con la estructura correcta
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

# Inicializamos la base de datos al encender el servidor
inicializar_db()

# --- MODELOS DE DATOS (SCHEMAS) ---
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

# --- RUTAS DE LA API ---

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
    
    # Inserción explícita en el historial de SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historial (usuario, altitud, variedad, humedad, status, puntaje, calidad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datos.usuario, 
            datos.altitud, 
            datos.variedad, 
            datos.humedad, 
            datos.status, 
            datos.puntaje,        # Guarda el puntaje numérico de la taza
            resultado_calidad     # Guarda la etiqueta predictiva final
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error crítico al guardar en SQLite: {e}")
        raise HTTPException(status_code=500, detail="No se pudo registrar en el historial")

    return {"calidad": resultado_calidad}

@app.get("/api/historial")
def obtener_historial():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, altitud, variedad, humedad, status, puntaje, calidad FROM historial ORDER BY id DESC")
        filas = cursor.fetchall()
        conn.close()
        
        historial_json = []
        for f in filas:
            historial_json.append({
                "usuario": f[0],
                "altitud": f[1],
                "variedad": f[2],
                "humedad": f[3],
                "status": f[4],
                "puntaje": f[5],
                "calidad": f[6]
            })
        return historial_json
    except Exception as e:
        print(f"Error al leer la base de datos: {e}")
        return []

# --- SERVIDORES DE ARCHIVOS ESTÁTICOS (FRONTEND) ---
# Esta línea va estrictamente al final para no interferir con las rutas de la API
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")