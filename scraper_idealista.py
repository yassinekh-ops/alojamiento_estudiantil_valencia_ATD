import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. URL inicial (la primera página)
url_actual = "https://www.idealista.com/en/alquiler-habitacion/valencia-valencia/con-fecha-desde_2027-09-01,fecha-hasta_2028-06-30/"

# 2. Configuración Selenium (Modo Sigiloso)
print("Arrancando el motor de Selenium en modo sigiloso...")
opciones = webdriver.ChromeOptions()
opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
opciones.add_experimental_option('useAutomationExtension', False)
opciones.add_argument("--disable-blink-features=AutomationControlled")

servicio = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servicio, options=opciones)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})

# Aquí guardaremos TODAS las habitaciones de todas las páginas
lista_habitaciones = []
pagina_num = 1

try:
    # BUCLE WHILE: Se repetirá mientras estemos en la página 3 o inferior.
    # (Si quieres sacar todas las páginas, cambia esto a 'while True:')
    while pagina_num <= 4:
        print(f"\n--- Navegando a la página {pagina_num} ---")
        driver.get(url_actual)
        
        # OJO: Dejamos 15 segundos. Si sale un Captcha, resuélvelo rápido con el ratón.
        time.sleep(15) 
        
        html_crudo = driver.page_source
        soup = BeautifulSoup(html_crudo, "html.parser")
        
        anuncios = soup.find_all("article", class_="item")
        print(f"Encontrados {len(anuncios)} anuncios en la página {pagina_num}.")
        
        for anuncio in anuncios:
            try:
                # Precio
                precio_tag = anuncio.find("span", class_="item-price")
                precio_texto = precio_tag.get_text() if precio_tag else "0"
                precio_limpio = int(precio_texto.replace("€/month", "").replace("€/mes", "").replace("€", "").replace(",", "").strip())
                
                # Título y enlace
                titulo_tag = anuncio.find("a", class_="item-link")
                titulo_texto = titulo_tag.get_text().strip() if titulo_tag else "Zona desconocida"
                enlace = "https://www.idealista.com" + titulo_tag['href'] if (titulo_tag and 'href' in titulo_tag.attrs) else "Sin enlace"
                
                # Detalles
                detalles = anuncio.find_all("span", class_="item-detail")
                detalles_texto = [d.get_text().strip() for d in detalles]
                
                # Descripción
                desc_tag = anuncio.find("div", class_="item-description") or anuncio.find("p", class_="description")
                if not desc_tag:
                     desc_tag = anuncio.find(class_="item-description")
                descripcion_texto = desc_tag.get_text().strip().replace("\n", " ") if desc_tag else "Sin descripción"
                
                habitacion = {
                    "precio_eur": precio_limpio,
                    "titulo_zona": titulo_texto,
                    "detalles_basicos": detalles_texto,
                    "descripcion": descripcion_texto,
                    "url": enlace,
                    "fuente": "Idealista"
                }
                
                lista_habitaciones.append(habitacion)
                
            except Exception as e:
                continue
        
        # --- APLICAMOS LA LÓGICA DE LA PIZARRA DEL PROFE ---
        # Buscamos la etiqueta <a> que nos lleva a la página siguiente
        boton_siguiente = soup.find("a", class_="icon-arrow-right-after")
        
        if boton_siguiente and 'href' in boton_siguiente.attrs:
            # Extraemos la nueva URL y la guardamos en url_actual para la siguiente vuelta del bucle
            url_actual = "https://www.idealista.com" + boton_siguiente['href']
            pagina_num += 1
            print("¡Botón 'Siguiente' encontrado! Preparando salto...")
        else:
            print("\nNo se ha encontrado el botón 'Siguiente' o hemos llegado a la última página.")
            break # Rompemos el bucle de forma segura

except Exception as e:
    print(f"Ocurrió un error en el proceso: {e}")

finally:
    driver.quit()
    print("Navegador cerrado.")

# Al terminar el bucle (ya sea por límite de páginas o por no haber más), guardamos todo
if len(lista_habitaciones) > 0:
    df_idealista = pd.DataFrame(lista_habitaciones)
    df_idealista.to_csv("idealista_valencia_completo.csv", index=False, encoding="utf-8")
    print(f"\n¡MISIÓN CUMPLIDA! Se han guardado {len(df_idealista)} habitaciones en total en 'idealista_valencia_completo.csv'")
else:
    print("\nNo se extrajeron datos.")