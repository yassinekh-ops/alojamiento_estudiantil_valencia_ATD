import pandas as pd
import time
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

print("1. Leyendo el archivo CSV de Idealista...")
df_idealista = pd.read_csv("idealista_valencia_completo.csv", encoding="utf-8")
total_filas = len(df_idealista)

print("\n2. Arrancando Chrome en modo INDETECTABLE...")
opciones = uc.ChromeOptions()
# undetected_chromedriver ya borra las banderas de bot por nosotros
driver = uc.Chrome(options=opciones)

descripciones_extraidas = []

try:
    for index, fila in df_idealista.iterrows():
        url_anuncio = fila['url']
        print(f"\n--- [{index + 1}/{total_filas}] Extrayendo anuncio ---")
        
        if pd.isna(url_anuncio) or url_anuncio == "Sin enlace":
            descripciones_extraidas.append("Sin enlace")
            continue
            
        driver.get(url_anuncio)
        
        # Tiempo de espera aleatorio para imitar comportamiento humano
        espera_humana = random.uniform(10.5, 18.2)
        print(f"Esperando {espera_humana:.1f} segundos...")
        time.sleep(espera_humana)
        
        # Scroll para imitar lectura
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(1)
        
        try:
            # Intentamos pulsar el botón de leer más
            driver.execute_script("""
                let botones = document.querySelectorAll('button, a, span, div');
                for (let b of botones) {
                    let texto = b.innerText.toLowerCase();
                    if (texto.includes('leer más') || texto.includes('read more') || texto.includes('texto completo')) {
                        b.click();
                        break;
                    }
                }
            """)
            time.sleep(1.5)
        except Exception:
            pass

        html_crudo = driver.page_source
        soup2 = BeautifulSoup(html_crudo, "html.parser")
        
        # Buscamos el texto
        textos_candidatos = [etiqueta.get_text().strip() for etiqueta in soup2.find_all(["p", "div"]) if len(etiqueta.get_text().strip()) > 100]
        
        if textos_candidatos:
            descripcion_probable = max(textos_candidatos, key=len)
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

df_idealista['descripcion_profunda'] = descripciones_extraidas
df_idealista.to_csv("idealista_valencia_final.csv", index=False, encoding="utf-8-sig")
print("¡Fase 2 de Idealista Completada! Archivo 'idealista_valencia_final.csv' creado.")