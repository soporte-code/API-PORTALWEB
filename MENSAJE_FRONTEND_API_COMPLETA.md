# 📘 API Portal Web – Documentación Completa

## Autenticación
- JWT en header: `Authorization: Bearer <token>`
- Content-Type: `application/json`
- CORS habilitado para `portal-web.lahornilla.cl` y dev localhost

## Convenciones
- Respuestas: `{ success, message, data }` en endpoints nuevos; endpoints legados pueden devolver arreglos/objetos directos
- Errores: 400 (validación), 401 (no autenticado), 403 (no autorizado), 404 (no encontrado), 500 (error interno)

---

## Auth (`/api/auth`)
- POST `/login`
  - Body: `{ "usuario":"", "clave":"" }`
  - 200: `{ access_token, refresh_token, user: {...} }`

---

## Usuarios (`/api/usuarios`)
- GET `/` – listar usuarios
- GET `/{id}` – detalle usuario con `sucursales_permitidas`, `apps_permitidas`, `permisos_asignados`
- POST `/` – crear usuario
- PUT `/{id}` – actualizar usuario
- DELETE `/{id}` – desactivar usuario

Perfiles:
- GET `/perfiles` – listar
- POST `/perfiles` – crear

Permisos:
- GET `/permisos` – listar
- POST `/permisos` – crear
- POST `/{id}/permisos` – asignar al usuario `{ permisos_ids: [] }`

Aplicaciones:
- GET `/aplicaciones` – listar
- POST `/aplicaciones` – crear
- POST `/{id}/aplicaciones` – asignar al usuario `{ apps_ids: [] }`

Sucursales y sucursal activa:
- GET `/sucursal` – sucursal activa del logueado `{ id_sucursal }`
- GET `/sucursal-activa` – sucursal activa `{ sucursal_activa }`
- POST `/sucursal-activa` – actualizar `{ id_sucursal }`
- GET `/sucursales` – listar sucursales (admin)
- GET `/{id}/sucursales-permitidas` – listar (admin)
- POST `/{id}/sucursales-permitidas` – asignar `{ sucursales_ids: [] }` (admin)
- DELETE `/{id}/sucursales-permitidas` – eliminar todas (admin)

---

## Pautas (`/api/pautas`)
- GET `/labor-especie` – combinaciones labor-especie
- GET `/atributo-especie` – relaciones atributo-especie
- GET `/configuraciones` – configuraciones de pauta
- GET `/configuraciones-agrupadas` – configuraciones agrupadas por labor-especie
- GET `/cuartel-especie/{cuartel_id}` – especie del cuartel
- GET `/labores-por-especie/{especie_id}` – labores por especie
- GET `/atributos-por-labor-especie/{labor_id}/{especie_id}`
- GET `/formulario-dinamico/{labor_id}/{especie_id}` – estructura de formulario

CRUD de catálogo:
- Atributos cultivo: `GET/POST/PUT/DELETE /atributos-cultivo`
- Labores conteo: `GET/POST/PUT/DELETE /labores-conteo`
- Pivot labor-especie: `GET/POST/PUT/DELETE /labor-especie`
- Pivot atributo-especie: `GET/POST/PUT/DELETE /atributo-especie`

Fact pauta:
- GET `/pautas` – listar
- POST `/pautas` – crear
- GET `/pautas/{id}` – obtener
- POST `/pautas/{id}/detalles` – crear detalle
- POST `/pautas/{id}/detalles-masivo` – crear detalles masivos

---

## Conteo (`/api/conteo`)
- GET `/atributo-optimo` – listar configuraciones óptimas
- GET `/atributo-especie` – listar relaciones atributo-especie (conteo)

---

## Cuarteles (`/api`)
- GET `/cuarteles` – listar
- GET `/cuarteles/{id}` – obtener
- GET `/cuarteles/sucursal-activa` – por sucursal activa

---

## Variedades y Especies (`/api/variedades` y `/api`)
- GET `/variedades/especies` – especies (protegido)
- GET `/especies` – especies (público CORS para catálogos)
- GET `/especies/{id}` – especie específica (público CORS)

---

## Temporadas (`/api`)
- GET `/temporadas`
- GET `/temporadas/{id}`

---

## Mapeo / Plantas / Hileras
- `GET /api/mapeo/...`
- `GET /api/plantas/...`
- `GET /api/hileras/...`

---

## Ejemplos rápidos (curl)

Login:
```bash
curl -s -X POST "$API/auth/login" \
 -H "Content-Type: application/json" \
 -d '{"usuario":"admin","clave":"Secret@123"}'
```

Crear usuario:
```bash
curl -s -X POST "$API/usuarios/" \
 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"usuario":"jdoe","nombre":"Juan","apellido_paterno":"Doe","clave":"Secreta123!","correo":"jdoe@empresa.cl"}'
```

Asignar permisos:
```bash
curl -s -X POST "$API/usuarios/$USER_ID/permisos" \
 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"permisos_ids":["<permiso-uuid>"]}'
```

Formulario dinámico:
```bash
curl -s -X GET "$API/pautas/formulario-dinamico/2/5" \
 -H "Authorization: Bearer $TOKEN"
```

---

## Errores comunes
- 401 Not enough segments: token malformado → renovar token
- 403 No autorizado: falta permiso/perfil requerido
- 400 Campo requerido ausente o duplicado (usuario/correo)
- 500 Error interno: contactar backend con `requestId`/logs

---

## Notas
- Tipos de planta: usar `mapeo_dim_tipoplanta` y join con `LPAD(cp.id_tipoplanta, 2, '0') = tp.id`
- Para crear pautas, seguir flujo: Cuartel → Variedad → Especie → Labores → Formulario dinámico → Guardado
- Endpoints de catálogos (`/api/atributos`, `/api/especies`) expuestos vía CORS para precarga en front
