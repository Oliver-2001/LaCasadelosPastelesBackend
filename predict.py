import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

def predecir_ventas(datos):
    # Convertir las fechas a datetime
    datos['fecha'] = pd.to_datetime(datos['fecha'])
    datos['dias'] = (datos['fecha'] - datos['fecha'].min()).dt.days

    # Crear el modelo de regresión
    X = datos[['dias']]
    y = datos['cantidad_vendida']
    model = LinearRegression()
    model.fit(X, y)

    # Hacer la predicción para el siguiente día
    next_day = pd.DataFrame([[datos['dias'].max() + 1]], columns=['dias'])
    predicted_sales = model.predict(next_day)

    return predicted_sales[0]
