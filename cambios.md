# Resumen de Funcionalidades: Búsqueda y Filtrado

Este documento resume las funcionalidades de búsqueda y filtrado implementadas en la aplicación.

## 1. Filtrado Avanzado en Catálogos

-   **Filtro por Género**: En las páginas de `Películas` y `Series`, existe un menú desplegable que se carga dinámicamente con los géneros de la API de TMDB.
-   **Filtros de Ordenación**: Se puede ordenar el contenido por "Populares", "Mejor Valoradas", etc.
-   **Combinación de Filtros**: El sistema permite combinar filtros. Por ejemplo, se puede seleccionar un género y luego ordenarlo por "Mejor Valoradas", y ambos filtros se mantendrán activos.

## 2. Sistema de Búsqueda Integrado

-   **Búsqueda Específica por Catálogo**: Cada página de catálogo (`peliculas.html` y `series.html`) tiene su propio campo de búsqueda para buscar por nombre dentro de esa categoría.
-   **Búsqueda Global en Navegación**: El buscador principal en la barra de navegación (`base.html`) ahora inicia la búsqueda por defecto en el catálogo de **películas**.
-   **Enlace de Búsqueda Cruzada**: Al realizar una búsqueda desde la barra global, la página de resultados de películas muestra un enlace para ejecutar la misma consulta en el catálogo de series, conectando ambos flujos de manera intuitiva.

## 3. Mejoras de Interfaz de Usuario (UI/UX)

-   **Diseño de Cabecera de Catálogo**: Se ha establecido un diseño claro con el título y el buscador específico a la izquierda, y los filtros de ordenación/género a la derecha.
-   **Ocultación de Buscador Global**: Para una interfaz más limpia, el buscador de la barra de navegación se oculta en las páginas de catálogo, donde ya existe un buscador específico. En el resto del sitio (ej. Inicio), el buscador global permanece visible.

## 4. Lógica de Backend

-   **Vistas (`movies/views.py`)**: Las vistas `catalogo_peliculas` y `catalogo_series` gestionan la lógica para recibir los parámetros de búsqueda (`q`), filtro (`filtro`) y género (`genre`) desde la URL y obtener los datos correspondientes.
-   **Servicios (`movies/tmdb_service.py`)**: Se han creado funciones específicas como `discover_movies`, `search_movies`, `get_movie_genres`, etc., para mantener la lógica de las llamadas a la API de TMDB encapsulada y organizada.