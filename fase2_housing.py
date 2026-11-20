import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

print("1. Leyendo el archivo CSV con TODAS las habitaciones...")
df_housing = pd.read_csv("housing_valencia_completo.csv", encoding="utf-8")
total_filas = len(df_housing)
print(f"Total de habitaciones a procesar: {total_filas}")

print("\n2. Arrancando el motor de Selenium...")
opciones = webdriver.ChromeOptions()
opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
opciones.add_experimental_option('useAutomationExtension', False)
opciones.add_argument("--disable-blink-features=AutomationControlled")

servicio = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servicio, options=opciones)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
})

descripciones_extraidas = []

try:
    for index, fila in df_housing.iterrows():
        url_anuncio = fila['url']
        print(f"\n--- [{index + 1}/{total_filas}] Extrayendo anuncio ---")
        
        if pd.isna(url_anuncio) or url_anuncio == "Sin enlace":
            print("No hay enlace válido. Saltando...")
            descripciones_extraidas.append("Sin enlace")
            continue
            
        driver.get(url_anuncio)
        time.sleep(6) 
        
        # --- NUEVO: EL CAZADOR DE BOTONES "LEER MÁS" ---
        try:
            # Buscamos botones o enlaces que digan "leer más", "read more", "mostrar más", etc.
            # Usamos un truco de JavaScript para pulsar cualquier cosa que parezca un botón de expandir
            driver.execute_script("""
                let botones = document.querySelectorAll('button, a, span');
                for (let b of botones) {
                    let texto = b.innerText.toLowerCase();
                    if (texto.includes('read more') || texto.includes('leer más') || texto.includes('mostrar más')) {
                        b.click();
                        break;
                    }
                }
            """)
            time.sleep(1) # Le damos 1 segundo para que el texto se despliegue visualmente
            print("Botón de 'Leer más' detectado y pulsado.")
        except Exception:
            # Si no hay botón o falla, no pasa nada, la descripción será corta
            pass
        # -----------------------------------------------

        html_crudo = driver.page_source
        soup2 = BeautifulSoup(html_crudo, "html.parser")
        
        textos_parrafos = [p.get_text().strip() for p in soup2.find_all("p") if len(p.get_text().strip()) > 50]
        
        if textos_parrafos:
            descripcion_probable = max(textos_parrafos, key=len)
            print("¡Descripción capturada con éxito!")
        else:
            descripcion_probable = "No se encontró descripción"
            print("Aviso: No se encontró la descripción.")
            
        descripciones_extraidas.append(descripcion_probable)

except Exception as e:
    print(f"\nError en el bucle: {e}")
    while len(descripciones_extraidas) < total_filas:
        descripciones_extraidas.append("Error en extracción")

finally:
    driver.quit()
    print("\nNavegador cerrado.")

print("\n3. Guardando los datos maestros en un nuevo archivo...")
df_housing['descripcion_profunda'] = descripciones_extraidas

df_housing.to_csv("housing_valencia_final.csv", index=False, encoding="utf-8-sig")
print("¡Fase 2 Completada! Archivo 'housing_valencia_final.csv' creado con éxito.")