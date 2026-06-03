import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


MODEL_DIR = os.path.join("backend", "models")
DATA_DIR = os.path.join("backend", "database")
os.makedirs(MODEL_DIR, exist_ok=True)

def generar_dataset_500():
    np.random.seed(42)
    num_registros = 500
    variedades = ['Arábica', 'Catuaí', 'Geisha', 'Caturra', 'Bourbon', 'Catimor', 'Typica']
    status_opciones = ['Orgánico', 'Convencional']
    datos = []

    for _ in range(num_registros):
        variedad = np.random.choice(variedades)
        status = np.random.choice(status_opciones)
        tipo_calidad = np.random.choice(['Comercial', 'Especial', 'Especialidad', 'Excelencia', 'Excelencia Rara'], 
                                        p=[0.25, 0.25, 0.20, 0.20, 0.10])
        
        if tipo_calidad == 'Excelencia Rara':
            puntaje = round(np.random.uniform(95.0, 100.0), 2)
            altitud = int(np.random.uniform(1700, 2100))
            humedad = round(np.random.uniform(11.0, 11.8), 2)
            calidad_final = 'Taza de Excelencia Rara'
        elif tipo_calidad == 'Excelencia':
            puntaje = round(np.random.uniform(86.0, 94.9), 2)
            altitud = int(np.random.uniform(1450, 1850))
            humedad = round(np.random.uniform(11.0, 12.0), 2)
            calidad_final = 'Taza de Excelencia'
        elif tipo_calidad == 'Especialidad':
            puntaje = round(np.random.uniform(84.0, 85.9), 2)
            altitud = int(np.random.uniform(1200, 1600))
            humedad = round(np.random.uniform(11.2, 12.2), 2)
            calidad_final = 'Café de Especialidad'
        elif tipo_calidad == 'Especial':
            puntaje = round(np.random.uniform(80.0, 83.9), 2)
            altitud = int(np.random.uniform(1000, 1400))
            humedad = round(np.random.uniform(11.5, 12.5), 2)
            calidad_final = 'Café Especial'
        else:
            puntaje = round(np.random.uniform(76.0, 79.9), 2)
            altitud = int(np.random.uniform(800, 1200))
            humedad = round(np.random.uniform(11.8, 13.0), 2)
            calidad_final = 'Café Comercial'
            
        datos.append({
            'altitud_msnm': altitud, 'humedad': humedad, 'variedad': variedad,
            'status': status, 'puntaje_taza': puntaje, 'calidad_objetivo': calidad_final
        })

    df = pd.DataFrame(datos)
    df.to_csv(os.path.join(DATA_DIR, "dataset_cafe.csv"), index=False)
    return df

def entrenar_sistema():
    df = generar_dataset_500()
    le_variedad, le_status = LabelEncoder(), LabelEncoder()
    
    df['variedad_cod'] = le_variedad.fit_transform(df['variedad'])
    df['status_cod'] = le_status.fit_transform(df['status'])
    
    X = df[['altitud_msnm', 'humedad', 'variedad_cod', 'status_cod', 'puntaje_taza']]
    y = df['calidad_objetivo']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    with open(os.path.join(MODEL_DIR, "predictor_rf.pkl"), 'wb') as f:
        pickle.dump(model, f)
    with open(os.path.join(MODEL_DIR, "encoders.pkl"), 'wb') as f:
        pickle.dump({'variedad': le_variedad, 'status': le_status}, f)
    print("-> ¡Dataset de 500 filas!")

if __name__ == "__main__":
    entrenar_sistema()