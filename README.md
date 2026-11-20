# Análisis de Alojamiento Estudiantil en Valencia (2026-2027)

Proyecto individual de **Mohamed Yassine Khelifi** para la asignatura ATD (UPV).  
Sistema modular en Python para la extracción, integración, homogeneización y consulta interactiva de habitaciones para estudiantes en Valencia comparando **Idealista** y **HousingAnywhere**.

## Estructura del Proyecto
- `main.py`: Orquestador principal con menú interactivo.
- `scraper_idealista.py` / `scraper_housinganywhere.py`: Extracción base (Fase 1).
- `fase2_idealista.py` / `fase2_housing.py`: *Deep scraping* de descripciones completas (Fase 2).
- `modulo_limpieza_filtrado.py`: Integración, homogeneización, minería de texto y buscador interactivo (Fase 3).
- `dataset_master_valencia_limpio.csv`: Dataset final unificado (233 propiedades).

## Ejecución
```bash
python main.py
