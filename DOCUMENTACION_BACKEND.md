# Documentación Backend - API Portal Web

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Tecnologías](#tecnologías)
4. [Configuración](#configuración)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Endpoints de la API](#endpoints-de-la-api)
7. [Autenticación y Seguridad](#autenticación-y-seguridad)
8. [Base de Datos](#base-de-datos)
9. [Despliegue](#despliegue)
10. [Desarrollo](#desarrollo)

---

## 📖 Descripción General

La API Portal Web es una aplicación REST desarrollada en Flask que proporciona servicios backend para un sistema de gestión agrícola. Permite gestionar información sobre cuarteles, plantas, mapeos, conteos, estimaciones, pautas de trabajo, usuarios, roles y permisos.

### Funcionalidades Principales

- **Autenticación y Autorización**: Sistema de login con JWT, gestión de usuarios, roles y permisos
- **Gestión de Cuarteles**: CRUD completo de cuarteles con información detallada
- **Gestión de Plantas**: Registro y consulta de plantas por cuartel
- **Mapeo Agrícola**: Gestión de mapeos y registros de campo
- **Conteo de Plantas**: Sistema de conteo inteligente y final
- **Estimaciones**: Gestión de estimaciones de producción
- **Pautas de Trabajo**: Configuración y gestión de pautas de conteo
- **Variedades y Especies**: Catálogo de variedades y especies
- **Rendimiento Packing**: Gestión de rendimientos de packing

---

## 🏗️ Arquitectura

La aplicación sigue una arquitectura modular basada en **Blueprints de Flask**, lo que permite una organización clara y escalable del código.

### Patrón de Diseño

- **MVC (Model-View-Controller)**: Separación de responsabilidades
- **Blueprint Pattern**: Organización modular de rutas
- **Repository Pattern**: Abstracción de acceso a datos mediante `utils/db.py`

### Componentes Principales

```
API_PORTAL_WEB/
├── app.py                 # Aplicación principal Flask
├── config.py              # Configuración de la aplicación
├── blueprints/            # Módulos de endpoints
│   ├── auth.py           # Autenticación
│   ├── usuarios.py       # Gestión de usuarios
│   ├── cuarteles.py      # Gestión de cuarteles
│   ├── plantas.py        # Gestión de plantas
│   ├── mapeo.py          # Mapeo agrícola
│   ├── conteo.py         # Conteo de plantas
│   ├── estimaciones.py   # Estimaciones
│   ├── pautas.py         # Pautas de trabajo
│   ├── variedades.py     # Variedades y especies
│   └── opciones.py        # Opciones generales
├── utils/                 # Utilidades
│   ├── db.py             # Conexión a base de datos
│   └── validar_rut.py    # Validación de RUT
└── requirements.txt       # Dependencias
```

---

## 🛠️ Tecnologías

### Framework y Librerías Principales

- **Flask 2.3.3**: Framework web Python
- **Flask-JWT-Extended 4.5.3**: Autenticación basada en tokens JWT
- **Flask-CORS 4.0.0**: Manejo de CORS para comunicación con frontend
- **PyMySQL 1.1.0**: Conector MySQL para Python
- **mysql-connector-python 8.2.0**: Conector alternativo MySQL
- **bcrypt 4.1.2**: Encriptación de contraseñas
- **python-dotenv 1.0.0**: Manejo de variables de entorno
- **gunicorn 21.2.0**: Servidor WSGI para producción

### Base de Datos

- **MySQL**: Base de datos relacional
- **Cloud SQL**: Para despliegue en Google Cloud Platform

---

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DATABASE_URL=mysql+pymysql://usuario:password@host/database
DB_HOST=localhost
DB_PORT=3306
DB_USER=usuario
DB_PASSWORD=password
DB_NAME=lahornilla_base_normalizada

# JWT
JWT_SECRET_KEY=tu_clave_secreta_aqui

# Flask
DEBUG=True
FLASK_ENV=development
PORT=8080
```

### Configuración de Base de Datos

La aplicación soporta dos modos de conexión:

1. **Desarrollo Local**: Conexión directa a MySQL
2. **Cloud Run**: Conexión mediante Unix Socket a Cloud SQL

El archivo `utils/db.py` maneja automáticamente la detección del entorno y configura la conexión apropiada.

---

## 📁 Estructura del Proyecto

### Blueprints (Módulos de Endpoints)

#### 1. **auth.py** - Autenticación
- Login y refresh de tokens
- Cambio de contraseña
- Cambio de sucursal activa
- Información del usuario actual

#### 2. **usuarios.py** - Gestión de Usuarios
- CRUD de usuarios
- Gestión de perfiles
- Gestión de aplicaciones
- Gestión de permisos
- Asignación de sucursales y aplicaciones

#### 3. **cuarteles.py** - Gestión de Cuarteles
- Listado de cuarteles
- Detalle de cuartel
- Información de hileras y plantas
- Estadísticas de cuartel

#### 4. **plantas.py** - Gestión de Plantas
- Consulta de plantas por cuartel
- Filtrado por fecha
- Información detallada de plantas

#### 5. **mapeo.py** - Mapeo Agrícola
- Registro de mapeos
- Consulta de registros
- Gestión de tipos de planta

#### 6. **conteo.py** - Conteo de Plantas
- Atributos óptimos
- Conteo por atributo y especie
- Conteo inteligente
- Conteo final

#### 7. **estimaciones.py** - Estimaciones
- Listado de estimaciones
- Detalle de estimación
- Creación de estimaciones
- Dashboard de estimaciones

#### 8. **pautas.py** - Pautas de Trabajo
- Configuraciones de pauta
- Creación de pautas
- Consulta de pautas por temporada
- Rendimiento packing

#### 9. **variedades.py** - Variedades y Especies
- Listado de especies
- Listado de variedades
- Filtrado de variedades

#### 10. **opciones.py** - Opciones Generales
- Labores
- Unidades
- Tipos de CECO
- Sucursales

---

## 🔌 Endpoints de la API

### Base URL
```
https://api-portalweb-927498545444.us-central1.run.app/api
```

### Autenticación (`/api/auth`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/login` | Iniciar sesión | No |
| POST | `/refresh` | Renovar token | Refresh Token |
| POST | `/cambiar-clave` | Cambiar contraseña | JWT |
| POST | `/cambiar-sucursal` | Cambiar sucursal activa | JWT |
| GET | `/me` | Obtener usuario actual | JWT |
| PUT | `/me` | Actualizar usuario actual | JWT |

### Usuarios (`/api/usuarios`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/` | Listar usuarios | JWT |
| GET | `/<id>` | Obtener usuario | JWT |
| POST | `/` | Crear usuario | JWT |
| PUT | `/<id>` | Actualizar usuario | JWT |
| DELETE | `/<id>` | Desactivar usuario | JWT |
| GET | `/perfiles` | Listar perfiles | JWT |
| POST | `/perfiles` | Crear perfil | JWT |
| GET | `/aplicaciones` | Listar aplicaciones | JWT |
| POST | `/aplicaciones` | Crear aplicación | JWT |
| GET | `/permisos` | Listar permisos | JWT |
| POST | `/permisos` | Crear permiso | JWT |
| POST | `/<id>/permisos` | Asignar permisos | JWT |
| POST | `/<id>/aplicaciones` | Asignar aplicaciones | JWT |
| POST | `/<id>/sucursales-permitidas` | Asignar sucursales | JWT |

### Cuarteles (`/api/cuarteles`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/cuarteles` | Listar cuarteles | JWT |
| GET | `/cuarteles/<id>` | Detalle de cuartel | JWT |
| GET | `/cuarteles/<id>/hileras` | Hileras del cuartel | JWT |
| GET | `/cuarteles/<id>/plantas` | Plantas del cuartel | JWT |
| GET | `/cuarteles/<id>/estadisticas` | Estadísticas | JWT |

### Plantas (`/api/plantas`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/plantas` | Listar plantas | JWT |
| GET | `/plantas?cuartel_id=<id>` | Plantas por cuartel | JWT |
| GET | `/plantas?fecha=<fecha>` | Plantas por fecha | JWT |

### Mapeo (`/api/mapeo`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/registros` | Listar registros | JWT |
| POST | `/registros` | Crear registro | JWT |
| GET | `/tipos-planta` | Tipos de planta | JWT |

### Conteo (`/api/conteo`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/atributo-optimo` | Atributos óptimos | JWT |
| GET | `/atributo-especie` | Conteo por atributo/especie | JWT |
| POST | `/conteo-inteligente` | Conteo inteligente | JWT |
| POST | `/conteo-final` | Conteo final | JWT |

### Estimaciones (`/api/estimaciones`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/` | Listar estimaciones | JWT |
| GET | `/<id>` | Detalle estimación | JWT |
| POST | `/` | Crear estimación | JWT |
| GET | `/dashboard` | Dashboard | JWT |

### Pautas (`/api/pautas`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/configuraciones` | Listar configuraciones | JWT |
| GET | `/configuraciones-agrupadas` | Configuraciones agrupadas | JWT |
| GET | `/temporadas/<id>` | Pautas por temporada | JWT |
| POST | `/` | Crear pauta | JWT |
| GET | `/<id>` | Detalle de pauta | JWT |
| GET | `/rendimiento-packing` | Rendimiento packing | JWT |

### Variedades (`/api/variedades`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/especies` | Listar especies | JWT |
| GET | `/especies/<id>` | Detalle especie | JWT |
| GET | `/variedades` | Listar variedades | JWT |
| GET | `/variedades?especie_id=<id>` | Variedades por especie | JWT |

### Opciones (`/api/opciones`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/` | Labores, unidades, tipos CECO | JWT |
| GET | `/sucursales` | Sucursales del usuario | JWT |

### Endpoints Raíz (`/api`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/atributos` | Listar atributos | No |
| GET | `/especies` | Listar especies | No |
| GET | `/temporadas` | Listar temporadas | No |
| GET | `/test-db` | Prueba de conexión BD | No |
| GET | `/config` | Configuración (debug) | No |

---

## 🔐 Autenticación y Seguridad

### JWT (JSON Web Tokens)

La API utiliza JWT para autenticación. Los tokens incluyen:

- **Access Token**: Expira en 10 horas
- **Refresh Token**: Expira en 7 días

### Headers Requeridos

Para endpoints protegidos:

```
Authorization: Bearer <access_token>
```

### Encriptación de Contraseñas

Las contraseñas se encriptan usando **bcrypt** antes de almacenarse en la base de datos.

### CORS

La API está configurada para aceptar peticiones desde:

- `https://portal-web.lahornilla.cl`
- `https://front-portalweb.web.app`
- `https://front-portalweb.firebaseapp.com`
- `http://localhost:3000`
- `http://localhost:8080`

---

## 🗄️ Base de Datos

### Esquema Principal

La base de datos `lahornilla_base_normalizada` contiene múltiples tablas organizadas por módulos:

#### Tablas de Usuarios
- `general_dim_usuario`: Usuarios del sistema
- `usuario_dim_perfil`: Perfiles de usuario
- `usuario_dim_permiso`: Permisos
- `usuario_pivot_sucursal_usuario`: Relación usuario-sucursal
- `usuario_pivot_app_usuario`: Relación usuario-aplicación
- `usuario_pivot_permiso_usuario`: Relación usuario-permiso

#### Tablas de Cuarteles
- `general_dim_cuartel`: Cuarteles
- `general_dim_ceco`: Centros de costo
- `general_dim_sucursal`: Sucursales
- `general_dim_hilera`: Hileras
- `general_dim_planta`: Plantas

#### Tablas de Mapeo
- `mapeo_fact_registro`: Registros de mapeo
- `mapeo_dim_tipoplanta`: Tipos de planta

#### Tablas de Conteo
- `conteo_dim_atributocultivo`: Atributos de cultivo
- `conteo_dim_atributooptimo`: Atributos óptimos
- `conteo_dim_configpauta`: Configuraciones de pauta
- `conteo_fact_pauta`: Pautas de conteo

#### Tablas de Estimaciones
- `estimacion_fact_registroadministradores`: Registros de estimación
- `estimacion_dim_tipo`: Tipos de estimación

#### Tablas de Variedades
- `general_dim_especie`: Especies
- `general_dim_variedad`: Variedades

### Conexión a Base de Datos

El archivo `utils/db.py` maneja la conexión a la base de datos con soporte para:

- Conexión local mediante host/port
- Conexión a Cloud SQL mediante Unix Socket
- Parsing automático de `DATABASE_URL`

---

## 🚀 Despliegue

### Docker

La aplicación incluye un `Dockerfile` para contenedorización:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "app:app"]
```

### Google Cloud Run

La aplicación está desplegada en Google Cloud Run:

- **Servicio**: `api-portalweb`
- **Región**: `us-central1`
- **URL**: `https://api-portalweb-927498545444.us-central1.run.app`

### Cloud Build

El archivo `cloudbuild.yaml` configura el despliegue automático:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/api-portalweb', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/api-portalweb']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'api-portalweb'
      - '--image'
      - 'gcr.io/$PROJECT_ID/api-portalweb'
      - '--region'
      - 'us-central1'
```

---

## 💻 Desarrollo

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd API_PORTAL_WEB
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

### Estructura de Respuestas

#### Respuesta Exitosa
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": {
    // Datos de la respuesta
  }
}
```

#### Respuesta de Error
```json
{
  "success": false,
  "error": "Mensaje de error",
  "message": "Descripción detallada"
}
```

### Logging

La aplicación utiliza el módulo `logging` de Python. Los logs incluyen:

- Información de conexión a BD
- Errores de endpoints
- Información de autenticación

### Testing

Para probar endpoints, se pueden usar los scripts de prueba incluidos:

- `test_login.py`: Prueba de autenticación
- `test_cuartel_basico.py`: Prueba de cuarteles
- `test_endpoints_final.py`: Prueba de endpoints

---

## 📝 Notas Adicionales

### Validación de RUT

El módulo `utils/validar_rut.py` proporciona funciones para validar RUTs chilenos.

### Manejo de Errores

Todos los endpoints incluyen manejo de errores con try-catch y respuestas JSON apropiadas.

### CORS

La configuración de CORS permite comunicación desde múltiples orígenes, incluyendo desarrollo local y producción.

### Seguridad

- Contraseñas encriptadas con bcrypt
- Tokens JWT con expiración
- Validación de permisos por endpoint
- Verificación de acceso a sucursales

---

## 📞 Soporte

Para más información o soporte técnico, contactar al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024  
**Desarrollado con**: Flask 2.3.3, Python 3.9+

