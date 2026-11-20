import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

url_base = "https://housinganywhere.com/es/s/Valencia--España/habitaciones-privadas?calendarMode=exact&endDate=2028-06-30&startDate=2027-09-01&view=noMap"

print("Arrancando Selenium en modo sigiloso para HousingAnywhere...")
opciones = webdriver.ChromeOptions()
opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
opciones.add_experimental_option('useAutomationExtension', False)
opciones.add_argument("--disable-blink-features=AutomationControlled")

servicio = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servicio, options=opciones)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
})

lista_habitaciones = []
textos_procesados = set()
pagina_num = 1

try:
    while pagina_num <= 6:
        print(f"\n--- Navegando a la página {pagina_num} ---")
        url_actual = f"{url_base}&page={pagina_num}"
        driver.get(url_actual)
        time.sleep(8) 
        
        print("Haciendo scroll como un humano para cargar imágenes ocultas...")
        for _ in range(6):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(1.5)
            
        lista_imagenes = driver.find_elements(By.TAG_NAME, "img")
        habitaciones_en_esta_pagina = 0
        
        for i in lista_imagenes:
            texto_alt = i.get_attribute("alt")
            
            if texto_alt and "alquiler por" in texto_alt and texto_alt not in textos_procesados:
                textos_procesados.add(texto_alt)
                
                try:
                    texto_limpio = texto_alt.replace('\xa0', ' ')
                    patron = r"por\s+(\d+)\s*€.*?en\s+(.*)"
                    coincidencia = re.search(patron, texto_limpio)
                    
                    if coincidencia:
                        precio_limpio = int(coincidencia.group(1))
                        ubicacion_str = coincidencia.group(2)
                        
                        if ", " in ubicacion_str:
                            ciudad = ubicacion_str.split(", ")[0].strip()
                            calle = ubicacion_str.split(", ")[1].strip()
                        else:
                            ciudad = ubicacion_str.strip()
                            calle = "Desconocida"
                            
                        # --- NUEVA LÓGICA DE URL ---
                        try:
                            # Buscamos al "padre" de la imagen que sea un enlace <a>
                            enlace_padre = i.find_element(By.XPATH, "./ancestor::a")
                            url_parcial = enlace_padre.get_attribute("href")
                            
                            # Si HousingAnywhere da una ruta relativa, le ponemos el dominio delante
                            if url_parcial and url_parcial.startswith("/"):
                                url_completa = "https://housinganywhere.com" + url_parcial
                            else:
                                url_completa = url_parcial
                        except Exception:
                            url_completa = "Sin enlace"
                        
                        # --- AÑADIMOS LA URL AL DICCIONARIO ---
                        habitacion = {
                            "precio_eur": precio_limpio,
                            "ciudad": ciudad,
                            "calle": calle,
                            "url": url_completa,
                            "fuente": "HousingAnywhere"
                        }
                        
                        lista_habitaciones.append(habitacion)
                        habitaciones_en_esta_pagina += 1
                        
                except Exception:
                    continue
                    
        print(f"Guardadas {habitaciones_en_esta_pagina} habitaciones únicas de la página {pagina_num}.")
        pagina_num += 1

finally:
    driver.quit()
    print("\nNavegador cerrado.")

if len(lista_habitaciones) > 0:
    df_housing = pd.DataFrame(lista_habitaciones)
    df_housing.to_csv("housing_valencia_completo.csv", index=False, encoding="utf-8")
    print(f"\n¡ÉXITO TOTAL! Se han guardado {len(df_housing)} habitaciones con sus URLs en 'housing_valencia_completo.csv'")
else:
    print("\nNo se extrajeron datos.")