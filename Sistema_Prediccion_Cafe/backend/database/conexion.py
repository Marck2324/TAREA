import sqlite3
import os
from datetime import datetime

# Definimos la ruta desde la raíz del proyecto
DB_DIR = os.path.join("backend", "database")
DB_PATH = os.path.join(DB_DIR, "sistema_cafe.db")

# Asegurar que la carpeta database exista
os.makedirs(DB_DIR, exist_ok=True)

def obtener_conexion():
    """Establece la conexión con el archivo local SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_base_de_datos():
    """Crea las tablas de login e historial si no existen."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # 1. Tabla de Usuarios para el Login
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # 2. Tabla de Historial para auditoría de predicciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_predicciones (
            id_prediccion INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            fecha TEXT NOT NULL,
            altitud REAL NOT NULL,
            humedad REAL NOT NULL,
            variedad TEXT NOT NULL,
            status TEXT NOT NULL,
            puntaje_taza REAL NOT NULL,
            calidad_predicha TEXT NOT NULL
        )
    """)
    
    # Insertar usuario administrador por defecto (admin / admin123)
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES ('admin', 'admin123')")
        
    conn.commit()
    conn.close()

def validar_usuario(username, password):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def guardar_prediccion(usuario, altitud, humedad, variedad, status, puntaje, calidad):
    conn = obtener_conexion()
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO historial_predicciones (usuario, fecha, altitud, humedad, variedad, status, puntaje_taza, calidad_predicha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (usuario, fecha_actual, altitud, humedad, variedad, status, puntaje, calidad))
    
    conn.commit()
    conn.close()

def obtener_historial():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, usuario, altitud, humedad, variedad, status, puntaje_taza, calidad_predicha FROM historial_predicciones ORDER BY fecha DESC")
    filas = cursor.fetchall()
    conn.close()
    return [dict(f) for f in filas]