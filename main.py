import subprocess
import sys
import modulo_limpieza_filtrado as mlf

def ejecutar_script(nombre_archivo):
    """Ejecuta un módulo de scraping respetando el entorno de Python actual."""
    print(f"\n🚀 Ejecutando módulo: {nombre_archivo} ...")
    resultado = subprocess.run([sys.executable, nombre_archivo])
    if resultado.returncode == 0:
        print(f"✅ {nombre_archivo} finalizado correctamente.")
    else:
        print(f"⚠️ {nombre_archivo} terminó con errores (código {resultado.returncode}).")

def ejecutar_pipeline_completo():
    """Flujo completo ETL: Fase 1 -> Fase 2 -> Fase 3 (Limpieza y Homogeneización)."""
    print("\n=== INICIANDO PIPELINE COMPLETO DE EXTRACCIÓN Y LIMPIEZA ===")
    confirmacion = input("Aviso: El scraping completo puede tardar 30-45 min. ¿Continuar? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Operación cancelada. Volviendo al menú principal.")
        return

    # Fase 1: Scraping Superficial
    ejecutar_script("scraper_housinganywhere.py")
    ejecutar_script("scraper_idealista.py")

    # Fase 2: Deep Scraping
    ejecutar_script("fase2_housing.py")
    ejecutar_script("fase2_idealista.py")

    # Fase 3: Limpieza, Integración y Homogeneización
    mlf.limpiar_y_homogeneizar()
    print("\n🎉 ¡Pipeline completo ejecutado con éxito!")

def menu_principal():
    while True:
        print("\n" + "="*55)
        print("  ANALIZADOR DE ALOJAMIENTO ESTUDIANTIL - VALENCIA")
        print("  Proyecto Individual | Mohamed Yassine Khelifi")
        print("="*55)
        print("1. Ejecutar Pipeline Completo (Scraping Fases 1 y 2 + Limpieza)")
        print("2. Ejecutar Limpieza, Integración y Homogeneización (Fase 3)")
        print("3. Buscador Interactivo (Filtrar habitaciones por criterios)")
        print("4. Ver Resumen Comparativo (Idealista vs HousingAnywhere)")
        print("5. Salir")
        print("-"*55)

        opcion = input("Selecciona una opción (1-5): ").strip()

        if opcion == "1":
            ejecutar_pipeline_completo()
        elif opcion == "2":
            mlf.limpiar_y_homogeneizar()
        elif opcion == "3":
            mlf.filtrar_habitaciones_usuario()
        elif opcion == "4":
            mlf.mostrar_resumen_comparativo()
        elif opcion == "5":
            print("\n👋 Cerrando el programa. ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida. Elige un número del 1 al 5.")

if __name__ == "__main__":
    menu_principal()