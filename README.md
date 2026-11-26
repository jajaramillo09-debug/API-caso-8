"""
Proyecto final · Bases de Datos III (CIAF)
API del Caso 8: reporte y seguimiento de infraestructura dañada (alcaldía o curaduría)

- MongoDB Atlas guarda los datos principales (los reportes ciudadanos): no se pueden perder.
- Redis acelera la aplicación: caché del reporte, estado de las cuadrillas y un contador.
  Son datos que se pueden perder o que se vuelven a calcular.
"""

# API de infraestructura dañada · Caso 8 (Bases de Datos III, CIAF)

API hecha con **FastAPI** que usa dos bases de datos:

- **MongoDB Atlas**: guarda los reportes ciudadanos (colección `reportes`), los datos que no se pueden perder.
- **Redis**: caché del reporte por barrio (cache-aside con tiempo de vida), estado en tiempo real de las cuadrillas y un contador.

## Archivos

| Archivo | Para qué sirve |
| --- | --- |
| `API/main.py` | Crea la aplicación FastAPI y registra las rutas |
| `API/routes/` | Endpoints agrupados por dominio |
| `API/schemas/` | Modelos de validación de reportes y cuadrillas |
| `API/database.py` | Configuración y conexiones a MongoDB y Redis |
| `cargar_datos.py` | Carga 30 reportes de prueba en MongoDB |
| `requirements.txt` | Librerías: fastapi, uvicorn, pymongo, redis, python-dotenv |
| `.env.example` | Nombres de las variables de entorno (sin contraseñas reales) |

## Cómo ejecutarla

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Windows  (en Mac/Linux: cp .env.example .env)
# Edita .env con tu MONGO_URI y tu REDIS_URL
python cargar_datos.py           # carga 30 reportes
uvicorn API.main:app --reload
```

Abre http://127.0.0.1:8000/docs para probar los endpoints en Swagger.

## Endpoints

| Método y ruta | Base | Qué hace |
| --- | --- | --- |
| `GET /ping` | Mongo + Redis | Comprueba la conexión a las dos bases |
| `GET /reportes` | Mongo | Lista reportes (filtros opcionales y límite) |
| `GET /reportes/{id}` | Mongo | Devuelve un reporte (400 id inválido, 404 no existe) |
| `POST /reportes` | Mongo | Crea un reporte validado (422 si faltan campos) e invalida la caché |
| `PUT /reportes/{id}` | Mongo | Actualiza campos (400 / 404) e invalida la caché |
| `DELETE /reportes/{id}` | Mongo | Borra un reporte (400 / 404) e invalida la caché |
| `GET /reportes/resumen/barrios` | Mongo + Redis | Reporte con pipeline y caché; indica `"origen": "mongo"` o `"redis"` |
| `PUT /cuadrillas/{id}/estado` | Redis | Guarda el estado de una cuadrilla (hash con tiempo de vida) |
| `GET /cuadrillas/{id}/estado` | Redis | Consulta el estado de una cuadrilla |
| `GET /cuadrillas` | Redis | Lista las cuadrillas con estado vigente |
| `GET /estadisticas/consultas` | Redis | Contador de consultas al reporte |

## Claves de Redis (formato `tipo:entidad:id`)

- `cache:reporte:resumen_barrios` → string con el JSON del reporte (vence en 60 s)
- `estado:cuadrilla:C-01` → hash con el estado de la cuadrilla (vence en 300 s)
- `contador:reporte:consultas` → número (INCR)
