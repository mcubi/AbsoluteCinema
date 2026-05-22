# AbsoluteCinema

Una plataforma de streaming de contenido audiovisual estilo Netflix, desarrollada como Proyecto Fin de Grado (TFG). La aplicación permite explorar catálogos de películas y series, con funcionalidades avanzadas de recomendación mediante IA y gestión completa de usuarios.

## Características

### Exploración de Contenido

- **Catálogo completo**: Navegación por películas y series con información detallada
- **Búsqueda avanzada**: Sistema de búsqueda por título, género, año y más
- **Chatbot de recomendación IA**: Asistente inteligente que sugiere contenido basado en preferencias del usuario mediante WebSocket
- **Preferencias de interfaz**: Personalización de la experiencia de usuario

### Gestión de Usuarios

- **Registro e autenticación**: Sistema de registro tradicional y autenticación social
- **Inicio de sesión con Google**: Integración OAuth 2.0 mediante django-allauth
- **Espacio personal**: Área privada del usuario con sus datos y configuraciones
- **Lista de favoritos**: Tablero personal para guardar contenido favorito
- **Sistema de puntos de fidelidad**: Gamificación con recompensas por actividad
- **Personalización de perfil**: Gestión de avatar y preferencias

### Seguridad

- **Autenticación Google**: Login seguro mediante OAuth 2.0
- **Validación de contraseñas**: Sistema robusto de validación
- **Protección CSRF**: Middleware de seguridad integrado
- **Gestión de sesiones**: Control seguro de sesiones de usuario

## Tecnologías Utilizadas

### Backend

- **Python 3**: Lenguaje de programación principal
- **Django 5.2.7**: Framework web para desarrollo rápido
- **Django Channels 4.0**: Soporte para WebSockets en tiempo real
- **Django REST Framework**: API REST para servicios web
- **django-allauth**: Autenticación social (Google OAuth)
- **SQLite**: Base de datos ligera para desarrollo
- **Redis 5.0**: Sistema de caché y channel layer para WebSockets
- **Daphne 4.2**: Servidor ASGI para Django Channels

### Frontend

- **HTML5/CSS3**: Estructura y estilos base
- **Tailwind CSS**: Framework de utilidades CSS
- **django-tailwind**: Integración de Tailwind con Django
- **JavaScript**: Interactividad del lado del cliente
- **WebSocket**: Comunicación en tiempo real para el chatbot

### APIs Externas

- **TMDB API**: The Movie Database para información de películas y series
- **Google OAuth API**: Autenticación social

### DevOps

- **Docker**: Contenedorización de la aplicación
- **Docker Compose**: Orquestación de servicios (web + redis)
- **Pipenv**: Gestión de dependencias y entornos virtuales
- **Gunicorn**: Servidor WSGI para producción

## Guía de Instalación

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Docker y Docker Compose (opcional, para instalación con contenedores)
- Git (para clonar el repositorio)

### Opción 1: Instalación Local (Desarrollo)

#### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd AbsoluteCinema-main
```

#### 2. Crear entorno virtual

```bash
# Usando venv
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O usando Pipenv:

```bash
pip install pipenv
pipenv install
pipenv shell
```

#### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=django-insecure-tu-clave-secreta-aqui
TMDB_API_KEY=tu-api-key-de-tmdb
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000
```

**Obtener API Keys:**

- **TMDB API Key**: Regístrate en [https://www.themoviedb.org/](https://www.themoviedb.org/) y crea una aplicación para obtener tu API key
- **Google OAuth**: Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/), habilita Google+ API y configura OAuth 2.0 con las credenciales

#### 5. Instalar Redis (requerido para WebSockets)

```bash
# Windows: Descargar e instalar desde https://redis.io/download
# Linux:
sudo apt-get install redis-server
# Mac:
brew install redis
```

Iniciar Redis:

```bash
redis-server
```

#### 6. Ejecutar migraciones de la base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Crear superusuario (opcional, para panel de administración)

```bash
python manage.py createsuperuser
```

#### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://localhost:8000`

### Opción 2: Instalación con Docker (Recomendado)

#### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd AbsoluteCinema-main
```

#### 2. Configurar variables de entorno

Crear o editar el archivo `.env` con las mismas variables que en la instalación local.

#### 3. Construir y ejecutar con Docker Compose

```bash
docker-compose up --build
```

Docker Compose automáticamente:

- Construirá la imagen de la aplicación
- Iniciará el contenedor de Redis
- Iniciará el contenedor de la aplicación web
- Configurará las redes y volúmenes necesarios

La aplicación estará disponible en `http://localhost:8142`

#### 4. Ejecutar migraciones dentro del contenedor

```bash
docker-compose exec web python manage.py migrate
```

#### 5. Crear superusuario (opcional)

```bash
docker-compose exec web python manage.py createsuperuser
```

#### Comandos útiles de Docker

```bash
# Detener contenedores
docker-compose down

# Ver logs
docker-compose logs -f

# Ejecutar comandos en el contenedor
docker-compose exec web <comando>

# Reconstruir sin caché
docker-compose build --no-cache
```

## Configuración

### Variables de Entorno

| Variable               | Descripción                               | Ejemplo                                      |
| ---------------------- | ----------------------------------------- | -------------------------------------------- |
| `SECRET_KEY`           | Clave secreta de Django para criptografía | `django-insecure-...`                        |
| `TMDB_API_KEY`         | API key de The Movie Database             | `3980138dc1ed5795da2a72694d5a0a3f`           |
| `GOOGLE_CLIENT_ID`     | ID de cliente OAuth de Google             | `675808723964-...apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Secreto de cliente OAuth de Google        | `GOCSPX-...`                                 |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos por Django               | `localhost,127.0.0.1`                        |
| `SITE_URL`             | URL base del sitio                        | `http://localhost:8000`                      |

### Configuración de Google OAuth

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar la API de Google+
4. Ir a "Credentials" > "Create Credentials" > "OAuth client ID"
5. Seleccionar "Web application"
6. Configurar URIs de redirección autorizadas:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://localhost:8142/accounts/google/login/callback/` (para Docker)
7. Copiar Client ID y Client Secret al archivo `.env`

## Estructura del Proyecto

```
ABSOLUTECINEMA/
├── absolute_cinema/          # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py             # Configuración ASGI para WebSockets
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs principales del proyecto
│   └── wsgi.py             # Configuración WSGI
├── movies/                  # App de catálogo de películas
│   ├── consumers.py        # WebSocket consumers para chatbot
│   ├── models.py           # Modelos de datos de películas
│   ├── tmdb_service.py     # Servicio de integración con TMDB API
│   ├── views.py            # Vistas del catálogo
│   ├── urls.py             # URLs de películas
│   ├── templates/          # Plantillas HTML de películas
│   └── migrations/        # Migraciones de la base de datos
├── users/                   # App de gestión de usuarios
│   ├── adapter.py          # Adaptador personalizado para allauth
│   ├── forms.py            # Formularios de usuario
│   ├── models.py           # Modelos extendidos de usuario
│   ├── views.py            # Vistas de autenticación y perfil
│   ├── urls.py             # URLs de usuarios
│   ├── templates/          # Plantillas HTML de usuarios
│   └── migrations/        # Migraciones de la base de datos
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── templates/               # Plantillas base globales
├── media/                   # Archivos multimedia subidos por usuarios
├── manage.py               # Script de gestión de Django
├── requirements.txt        # Dependencias de Python
├── Pipfile                 # Configuración de Pipenv
├── .env                    # Variables de entorno (no versionar)
├── dockerfile              # Configuración de Docker
├── compose.yml             # Configuración de Docker Compose
├── entrypoint.sh           # Script de entrada para Docker
└── db.sqlite3              # Base de datos SQLite (desarrollo)
```

## Uso

### Acceso a la Aplicación

1. **Página principal**: `http://localhost:8000` o `http://localhost:8142` (Docker)
2. **Panel de administración**: `http://localhost:8000/admin`
3. **Perfil de usuario**: `http://localhost:8000/profile/`

### Funcionalidades Principales

#### Exploración de Contenido

- Navega por el catálogo de películas y series
- Usa la barra de búsqueda para encontrar contenido específico
- Filtra por género, año, popularidad
- Accede a detalles de cada película/serie

#### Chatbot de Recomendaciones

- Abre el chatbot desde la interfaz principal
- Interactúa en tiempo real mediante WebSocket
- Recibe recomendaciones personalizadas basadas en tus preferencias

#### Gestión de Usuario

- Regístrate con email o Google OAuth
- Personaliza tu perfil con avatar
- Añade películas a tu lista de favoritos
- Acumula puntos de fidelidad por actividad

## Desarrollo

### Ejecutar Tests

```bash
python manage.py test
```

### Crear Nuevas Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Shell de Django

```bash
python manage.py shell
```

### Recoger Archivos Estáticos

```bash
python manage.py collectstatic
```

## Despliegue

### Preparación para Producción

1. **Cambiar `DEBUG` a `False` en `settings.py`**
2. **Configurar `ALLOWED_HOSTS` con el dominio de producción**
3. **Usar una base de datos robusta (PostgreSQL recomendado)**
4. **Configurar servidor de producción (Gunicorn + Nginx)**
5. **Usar variables de entorno seguras**
6. **Configurar HTTPS con certificados SSL**
7. **Configurar correo electrónico real para recuperación de contraseñas**

### Despliegue con Docker en Producción

Modificar `compose.yml` para producción:

- Cambiar `DJANGO_DEBUG=False`
- Configurar volúmenes persistentes
- Usar imagen de PostgreSQL en lugar de SQLite
- Configurar Nginx como reverse proxy

## Troubleshooting

### Problemas Comunes

**Error: TMDB_API_KEY no encontrada**

- Verifica que el archivo `.env` existe y tiene la variable configurada
- Reinicia el servidor después de modificar el archivo `.env`

**Error de conexión con Redis**

- Asegúrate de que Redis está ejecutándose: `redis-server`
- Verifica que el puerto 6379 no está en uso
- En Docker, verifica que el contenedor de Redis está activo

**Error de autenticación Google**

- Verifica que las credenciales OAuth son correctas
- Confirma que las URIs de redirección están configuradas en Google Console
- Verifica que `SITE_URL` en `.env` coincide con la configuración de Google

**Error de migraciones**

- Elimina el archivo `db.sqlite3` y ejecuta las migraciones nuevamente
- O usa: `python manage.py migrate --run-syncdb`

## Contribución

Este es un proyecto académico para el TFG. Para contribuir:

1. Fork del repositorio
2. Crear rama para la feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es desarrollado como Proyecto Fin de Grado. Contactar con el autor para más información sobre licencia.

## Contacto

Para preguntas o soporte sobre este proyecto, contactar con el desarrollador principal.

---

**Última actualización**: Mayo 2026
