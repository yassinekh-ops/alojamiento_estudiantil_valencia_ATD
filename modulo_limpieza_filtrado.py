import pandas as pd
import os

ARCHIVO_HOUSING = "housing_valencia_final.csv"
ARCHIVO_IDEALISTA = "idealista_valencia_final.csv"
ARCHIVO_SALIDA = "dataset_master_valencia_limpio.csv"

def limpiar_y_homogeneizar():
    """
    Lee los datos extraídos de ambos portales, los homogeneiza,
    elimina duplicados/errores, extrae características y guarda el dataset limpio.
    """
    print("\n--- INICIANDO LIMPIEZA, INTEGRACIÓN Y HOMOGENEIZACIÓN ---")
    
    if not os.path.exists(ARCHIVO_HOUSING) or not os.path.exists(ARCHIVO_IDEALISTA):
        print("❌ Error: Faltan los archivos CSV de la Fase 2. Ejecuta primero la extracción.")
        return None

    df_housing = pd.read_csv(ARCHIVO_HOUSING, encoding="utf-8-sig")
    df_idealista = pd.read_csv(ARCHIVO_IDEALISTA, encoding="utf-8-sig")

    # 1. Estandarización de columnas
    df_housing = df_housing.rename(columns={
        'precio_eur': 'precio',
        'calle': 'zona_calle',
        'descripcion_profunda': 'descripcion'
    })

    df_idealista['ciudad'] = df_idealista['titulo_zona'].apply(
        lambda x: str(x).split(',')[-1].strip() if pd.notnull(x) else 'Valencia'
    )
    if 'descripcion' in df_idealista.columns:
        df_idealista = df_idealista.drop(columns=['descripcion'])
    df_idealista = df_idealista.rename(columns={
        'precio_eur': 'precio',
        'titulo_zona': 'zona_calle',
        'descripcion_profunda': 'descripcion'
    })

    columnas_comunes = ['precio', 'ciudad', 'zona_calle', 'url', 'fuente', 'descripcion']
    df_master = pd.concat(
        [df_housing[columnas_comunes].copy(), df_idealista[columnas_comunes].copy()],
        ignore_index=True
    )

    total_inicial = len(df_master)

    # 2. Homogeneización y filtrado de datos sucios
    # Convertir precio a número y filtrar valores nulos o irreales (ej. < 100€ o > 2000€)
    df_master['precio'] = pd.to_numeric(df_master['precio'], errors='coerce')
    df_master = df_master.dropna(subset=['precio', 'url'])
    df_master = df_master[(df_master['precio'] >= 100) & (df_master['precio'] <= 2000)]

    # Homogeneizar nombres de ciudad (ej. "València" -> "Valencia")
    df_master['ciudad'] = (
        df_master['ciudad']
        .astype(str)
        .str.strip()
        .replace({'València': 'Valencia', 'valència': 'Valencia', 'valencia': 'Valencia'})
    )

    # Eliminar anuncios duplicados por URL
    df_master = df_master.drop_duplicates(subset=['url'], keep='first')

    # 3. Extracción de características (Minería de texto)
    desc_lower = df_master['descripcion'].astype(str).str.lower()
    df_master['aire_acondicionado'] = desc_lower.str.contains('aire acondicionado|air conditioning|air con', na=False)
    df_master['cama_doble'] = desc_lower.str.contains('cama doble|cama de matrimonio|double bed', na=False)
    df_master['gastos_incluidos'] = desc_lower.str.contains('gastos incluidos|utilities included|bills included', na=False)
    df_master['solo_estudiantes'] = desc_lower.str.contains('estudiantes|student', na=False)

    # Eliminar la columna de texto largo para dejar el dataset ligero y listo para análisis
    df_limpio = df_master.drop(columns=['descripcion'])
    df_limpio.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")

    print(f"✅ Proceso completado: {total_inicial} registros iniciales -> {len(df_limpio)} registros limpios y homogeneizados.")
    print(f"📁 Guardado en: {ARCHIVO_SALIDA}")
    return df_limpio


def filtrar_habitaciones_usuario():
    """
    Permite al usuario interactuar con los datos homogeneizados aplicando filtros
    y muestra el enlace directo a cada anuncio.
    """
    if not os.path.exists(ARCHIVO_SALIDA):
        print("⚠️ No existe el dataset limpio. Ejecutando limpieza primero...")
        df = limpiar_y_homogeneizar()
        if df is None:
            return
    else:
        df = pd.read_csv(ARCHIVO_SALIDA, encoding="utf-8-sig")

    print("\n--- BUSCADOR INTERACTIVO DE HABITACIONES ---")
    try:
        precio_max = input("Precio máximo mensual en € (pulsa Enter para no limitar): ").strip()
        ciudad = input("Ciudad (ej. Valencia, Burjassot — Enter para todas): ").strip()
        ac = input("¿Requiere aire acondicionado? (s/n — Enter para cualquiera): ").strip().lower()
        gastos = input("¿Gastos incluidos? (s/n — Enter para cualquiera): ").strip().lower()

        resultado = df.copy()

        if precio_max:
            resultado = resultado[resultado['precio'] <= float(precio_max)]
        if ciudad:
            resultado = resultado[resultado['ciudad'].str.lower() == ciudad.lower()]
        if ac == 's':
            resultado = resultado[resultado['aire_acondicionado'] == True]
        if gastos == 's':
            resultado = resultado[resultado['gastos_incluidos'] == True]

        resultado = resultado.sort_values(by='precio').head(15)
        print(f"\n🔎 Mostrando {len(resultado)} habitaciones (ordenadas por precio):\n")

        if len(resultado) > 0:
            for i, (_, fila) in enumerate(resultado.iterrows(), 1):
                ac_txt = "Sí" if fila['aire_acondicionado'] else "No"
                cama_txt = "Doble" if fila['cama_doble'] else "Individual/Otra"
                gastos_txt = "Incluidos" if fila['gastos_incluidos'] else "No especificados"

                print(f"{i}. [{fila['fuente']}] {fila['precio']} €/mes — {fila['ciudad']} ({fila['zona_calle']})")
                print(f"   Aire Acond.: {ac_txt} | Cama: {cama_txt} | Gastos: {gastos_txt}")
                print(f"   🔗 Enlace: {fila['url']}\n")
        else:
            print("No hay resultados con esos filtros. Prueba ampliando el presupuesto.")

    except ValueError:
        print("❌ Error: Introduce un número válido para el precio.")

def mostrar_resumen_comparativo():
    """
    Muestra métricas básicas comparando Idealista vs HousingAnywhere.
    """
    if not os.path.exists(ARCHIVO_SALIDA):
        print("⚠️ Primero debes generar el dataset limpio (Opción 2).")
        return

    df = pd.read_csv(ARCHIVO_SALIDA, encoding="utf-8-sig")
    print("\n--- RESUMEN COMPARATIVO: IDEALISTA vs HOUSINGANYWHERE ---")
    resumen = df.groupby('fuente').agg(
        total_habitaciones=('precio', 'count'),
        precio_medio=('precio', 'mean'),
        precio_min=('precio', 'min'),
        precio_max=('precio', 'max'),
        pct_aire_acondicionado=('aire_acondicionado', lambda x: x.mean() * 100),
        pct_cama_doble=('cama_doble', lambda x: x.mean() * 100)
    ).round(2)
    print(resumen.to_string())