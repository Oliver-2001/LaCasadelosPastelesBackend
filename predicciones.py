import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from app import db
from models import PrediccionesIA
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtener_datos_ventas():
    query = text("""
        SELECT 
            dv.id_producto,
            CONVERT(date, v.fecha) AS fecha,
            SUM(dv.cantidad) AS cantidad_vendida
        FROM DetallesVenta dv
        JOIN Ventas v ON dv.id_venta = v.id_venta
        GROUP BY dv.id_producto, CONVERT(date, v.fecha)
        ORDER BY dv.id_producto, fecha;
    """)
    result = db.session.execute(query)
    rows = result.fetchall()
    return pd.DataFrame(rows, columns=['id_producto', 'fecha', 'cantidad_vendida'])

def prediccion_ya_existe(id_producto, fecha, id_sucursal=1):
    # Convertir tipos numpy y pandas a tipos nativos Python
    id_producto_py = int(id_producto)
    if isinstance(fecha, pd.Timestamp):
        fecha_py = fecha.to_pydatetime().date()
    elif isinstance(fecha, datetime):
        fecha_py = fecha.date()
    else:
        fecha_py = fecha  # asume que ya es date o string aceptable

    id_sucursal_py = int(id_sucursal)

    return db.session.query(PrediccionesIA).filter_by(
        id_producto=id_producto_py,
        fecha_prediccion=fecha_py,
        id_sucursal=id_sucursal_py
    ).first() is not None

def generar_predicciones(dias_a_predecir=7, id_sucursal=1):
    df = obtener_datos_ventas()

    logger.info("Datos obtenidos de ventas:")
    logger.info(df.head())
    logger.info(f"Total de registros: {len(df)}")

    if df.empty:
        logger.warning("No hay datos de ventas para generar predicciones.")
        return "No hay datos de ventas para generar predicciones."

    productos = df['id_producto'].unique()
    logger.info(f"Productos encontrados: {productos}")

    for prod_id in productos:
        df_prod = df[df['id_producto'] == prod_id].copy()
        df_prod['fecha'] = pd.to_datetime(df_prod['fecha'])
        df_prod = df_prod.sort_values('fecha')

        df_prod['dias'] = (df_prod['fecha'] - df_prod['fecha'].min()).dt.days
        X = df_prod[['dias']]
        y = df_prod['cantidad_vendida']

        if len(X) < 2:
            logger.warning(f"Producto {prod_id} ignorado por tener solo {len(X)} registros.")
            continue

        model = LinearRegression()
        model.fit(X, y)

        max_dia = df_prod['dias'].max()
        fecha_inicio = df_prod['fecha'].max() + timedelta(days=1)

        for i in range(dias_a_predecir):
            dia_futuro = max_dia + i + 1
            fecha_pred = fecha_inicio + timedelta(days=i)
            cantidad_predicha = model.predict(pd.DataFrame({'dias': [dia_futuro]}))[0]
            cantidad_predicha = max(round(cantidad_predicha, 2), 0)

            if prediccion_ya_existe(prod_id, fecha_pred, id_sucursal):
                logger.info(f"Predicción ya existe para producto {prod_id} en fecha {fecha_pred}, se omite.")
                continue

            logger.info(f"Producto {prod_id} - Fecha: {fecha_pred} - Predicción: {cantidad_predicha}")

            prediccion = PrediccionesIA(
                id_producto=int(prod_id),
                fecha_prediccion=fecha_pred.date() if isinstance(fecha_pred, datetime) else fecha_pred,
                cantidad_prediccion=cantidad_predicha,
                id_sucursal=int(id_sucursal)
            )
            db.session.add(prediccion)

    try:
        db.session.commit()
        logger.info("Predicciones guardadas en la base de datos.")
        return "Predicciones generadas con éxito."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al guardar predicciones: {e}")
        return f"Error al guardar predicciones: {str(e)}"
