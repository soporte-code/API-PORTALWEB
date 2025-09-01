# 👥 MENSAJE PARA EL FRONTEND - GESTIÓN COMPLETA DE USUARIOS

## ✅ **¡SISTEMA DE GESTIÓN DE USUARIOS IMPLEMENTADO COMPLETAMENTE!**

**El sistema ahora incluye gestión completa de usuarios, perfiles, aplicaciones y permisos con control granular de acceso.**

---

## 📋 **ENDPOINTS NUEVOS IMPLEMENTADOS:**

### **1. 👤 GESTIÓN DE USUARIOS (CRUD Completo)**

#### **🔹 Listar Usuarios**
```http
GET /api/usuarios/
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": "d113f68b-6bab-4531-bb99-0e337e24e22a",
    "usuario": "admin",
    "nombre": "Administrador",
    "apellido_paterno": "Sistema",
    "apellido_materno": null,
    "correo": "admin@sistema.com",
    "id_sucursalactiva": 103,
    "sucursal_activa_nombre": "SANTA VICTORIA",
    "id_estado": 1,
    "id_rol": 1,
    "id_perfil": 3,
    "perfil_nombre": "Administrador",
    "fecha_creacion": "2024-01-15"
  }
]
```

#### **🔹 Obtener Usuario Específico**
```http
GET /api/usuarios/{usuario_id}
Authorization: Bearer {token}
```

**Respuesta completa:**
```json
{
  "id": "d113f68b-6bab-4531-bb99-0e337e24e22a",
  "usuario": "usuario123",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "correo": "juan.perez@empresa.com",
  "id_sucursalactiva": 103,
  "sucursal_activa_nombre": "SANTA VICTORIA",
  "id_estado": 1,
  "id_rol": 3,
  "id_perfil": 1,
  "perfil_nombre": "Usuario Básico",
  "fecha_creacion": "2024-01-15",
  "sucursales_permitidas": [
    {
      "id": 103,
      "nombre": "SANTA VICTORIA",
      "ubicacion": "Santiago"
    }
  ],
  "apps_permitidas": [
    {
      "id": 1,
      "nombre": "Portal Web",
      "descripcion": "Sistema principal de gestión"
    }
  ],
  "permisos_asignados": [
    {
      "id": "perm-001",
      "nombre": "ver_cuarteles",
      "id_app": 1,
      "app_nombre": "Portal Web"
    }
  ]
}
```

#### **🔹 Crear Usuario**
```http
POST /api/usuarios/
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "usuario": "nuevo_usuario",
  "nombre": "María",
  "apellido_paterno": "González",
  "apellido_materno": "López",
  "clave": "password123",
  "correo": "maria.gonzalez@empresa.com",
  "id_estado": 1,
  "id_rol": 3,
  "id_perfil": 1,
  "id_sucursalactiva": 103
}
```

**Respuesta:**
```json
{
  "message": "Usuario creado exitosamente",
  "id": "nuevo-uuid-generado",
  "usuario": "nuevo_usuario"
}
```

#### **🔹 Actualizar Usuario**
```http
PUT /api/usuarios/{usuario_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "nombre": "María Elena",
  "correo": "maria.elena@empresa.com",
  "id_perfil": 2,
  "clave": "nueva_password"
}
```

**Respuesta:**
```json
{
  "message": "Usuario actualizado correctamente",
  "id": "usuario_id"
}
```

#### **🔹 Eliminar Usuario (Desactivar)**
```http
DELETE /api/usuarios/{usuario_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "message": "Usuario desactivado correctamente",
  "id": "usuario_id"
}
```

---

### **2. 🏷️ GESTIÓN DE PERFILES**

#### **🔹 Listar Perfiles**
```http
GET /api/usuarios/perfiles
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Usuario Básico"
  },
  {
    "id": 2,
    "nombre": "Supervisor"
  },
  {
    "id": 3,
    "nombre": "Administrador"
  }
]
```

#### **🔹 Crear Perfil**
```http
POST /api/usuarios/perfiles
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "nombre": "Coordinador"
}
```

**Respuesta:**
```json
{
  "message": "Perfil creado exitosamente",
  "id": 4,
  "nombre": "Coordinador"
}
```

---

### **3. 📱 GESTIÓN DE APLICACIONES**

#### **🔹 Listar Aplicaciones**
```http
GET /api/usuarios/aplicaciones
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Portal Web",
    "descripcion": "Sistema principal de gestión agrícola",
    "URL": "https://portal.empresa.com"
  },
  {
    "id": 2,
    "nombre": "App Móvil",
    "descripcion": "Aplicación móvil para campo",
    "URL": "https://app.empresa.com"
  }
]
```

#### **🔹 Crear Aplicación**
```http
POST /api/usuarios/aplicaciones
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "nombre": "Dashboard Analytics",
  "descripcion": "Panel de análisis y reportes",
  "URL": "https://analytics.empresa.com"
}
```

**Respuesta:**
```json
{
  "message": "Aplicación creada exitosamente",
  "id": 3,
  "nombre": "Dashboard Analytics"
}
```

---

### **4. 🔐 GESTIÓN DE PERMISOS**

#### **🔹 Listar Permisos**
```http
GET /api/usuarios/permisos
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": "perm-001",
    "nombre": "ver_cuarteles",
    "id_app": 1,
    "app_nombre": "Portal Web"
  },
  {
    "id": "perm-002",
    "nombre": "crear_cuarteles",
    "id_app": 1,
    "app_nombre": "Portal Web"
  },
  {
    "id": "perm-003",
    "nombre": "ver_reportes",
    "id_app": 2,
    "app_nombre": "App Móvil"
  }
]
```

#### **🔹 Crear Permiso**
```http
POST /api/usuarios/permisos
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "nombre": "editar_plantas",
  "id_app": 1
}
```

**Respuesta:**
```json
{
  "message": "Permiso creado exitosamente",
  "id": "nuevo-uuid-permiso",
  "nombre": "editar_plantas"
}
```

---

### **5. 🔗 ASIGNACIÓN DE PERMISOS Y ACCESOS**

#### **🔹 Asignar Permisos a Usuario**
```http
POST /api/usuarios/{usuario_id}/permisos
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "permisos_ids": ["perm-001", "perm-002", "perm-003"]
}
```

**Respuesta:**
```json
{
  "message": "Permisos asignados correctamente",
  "usuario_id": "usuario_id",
  "permisos_asignados": 3
}
```

#### **🔹 Asignar Acceso a Aplicaciones**
```http
POST /api/usuarios/{usuario_id}/aplicaciones
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "apps_ids": [1, 2]
}
```

**Respuesta:**
```json
{
  "message": "Acceso a aplicaciones asignado correctamente",
  "usuario_id": "usuario_id",
  "apps_asignadas": 2
}
```

---

## 🔧 **IMPLEMENTACIÓN EN FRONTEND:**

### **TypeScript Functions para Gestión de Usuarios:**
```typescript
// ============================================================================
// GESTIÓN DE USUARIOS
// ============================================================================

// Listar usuarios
async function listarUsuarios(): Promise<ApiResponse<any[]>> {
  const response = await fetch('/api/usuarios/', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Obtener usuario específico
async function obtenerUsuario(usuarioId: string): Promise<ApiResponse<any>> {
  const response = await fetch(`/api/usuarios/${usuarioId}`, {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Crear usuario
async function crearUsuario(datosUsuario: any): Promise<ApiResponse<any>> {
  const response = await fetch('/api/usuarios/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(datosUsuario)
  });
  return response.json();
}

// Actualizar usuario
async function actualizarUsuario(usuarioId: string, datosActualizacion: any): Promise<ApiResponse<any>> {
  const response = await fetch(`/api/usuarios/${usuarioId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(datosActualizacion)
  });
  return response.json();
}

// Eliminar usuario
async function eliminarUsuario(usuarioId: string): Promise<ApiResponse<any>> {
  const response = await fetch(`/api/usuarios/${usuarioId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// ============================================================================
// GESTIÓN DE PERFILES
// ============================================================================

// Listar perfiles
async function listarPerfiles(): Promise<ApiResponse<any[]>> {
  const response = await fetch('/api/usuarios/perfiles', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Crear perfil
async function crearPerfil(nombrePerfil: string): Promise<ApiResponse<any>> {
  const response = await fetch('/api/usuarios/perfiles', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ nombre: nombrePerfil })
  });
  return response.json();
}

// ============================================================================
// GESTIÓN DE APLICACIONES
// ============================================================================

// Listar aplicaciones
async function listarAplicaciones(): Promise<ApiResponse<any[]>> {
  const response = await fetch('/api/usuarios/aplicaciones', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Crear aplicación
async function crearAplicacion(datosApp: any): Promise<ApiResponse<any>> {
  const response = await fetch('/api/usuarios/aplicaciones', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(datosApp)
  });
  return response.json();
}

// ============================================================================
// GESTIÓN DE PERMISOS
// ============================================================================

// Listar permisos
async function listarPermisos(): Promise<ApiResponse<any[]>> {
  const response = await fetch('/api/usuarios/permisos', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Crear permiso
async function crearPermiso(datosPermiso: any): Promise<ApiResponse<any>> {
  const response = await fetch('/api/usuarios/permisos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(datosPermiso)
  });
  return response.json();
}

// ============================================================================
// ASIGNACIÓN DE PERMISOS Y ACCESOS
// ============================================================================

// Asignar permisos a usuario
async function asignarPermisos(usuarioId: string, permisosIds: string[]): Promise<ApiResponse<any>> {
  const response = await fetch(`/api/usuarios/${usuarioId}/permisos`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ permisos_ids: permisosIds })
  });
  return response.json();
}

// Asignar aplicaciones a usuario
async function asignarAplicaciones(usuarioId: string, appsIds: number[]): Promise<ApiResponse<any>> {
  const response = await fetch(`/api/usuarios/${usuarioId}/aplicaciones`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}` 
    },
    body: JSON.stringify({ apps_ids: appsIds })
  });
  return response.json();
}
```

---

## 🎯 **FLUJO RECOMENDADO PARA GESTIÓN DE USUARIOS:**

### **Paso 1: Crear Perfiles Base**
```javascript
// Crear perfiles básicos del sistema
const perfilesBase = [
  { nombre: "Usuario Básico" },
  { nombre: "Supervisor" },
  { nombre: "Administrador" }
];

for (const perfil of perfilesBase) {
  await crearPerfil(perfil.nombre);
}
```

### **Paso 2: Crear Aplicaciones**
```javascript
// Crear aplicaciones del sistema
const aplicaciones = [
  {
    nombre: "Portal Web",
    descripcion: "Sistema principal de gestión agrícola",
    URL: "https://portal.empresa.com"
  },
  {
    nombre: "App Móvil",
    descripcion: "Aplicación móvil para trabajo en campo",
    URL: "https://app.empresa.com"
  }
];

for (const app of aplicaciones) {
  await crearAplicacion(app);
}
```

### **Paso 3: Crear Permisos**
```javascript
// Crear permisos básicos
const permisos = [
  { nombre: "ver_cuarteles", id_app: 1 },
  { nombre: "crear_cuarteles", id_app: 1 },
  { nombre: "editar_cuarteles", id_app: 1 },
  { nombre: "ver_plantas", id_app: 1 },
  { nombre: "crear_plantas", id_app: 1 },
  { nombre: "ver_reportes", id_app: 2 }
];

for (const permiso of permisos) {
  await crearPermiso(permiso);
}
```

### **Paso 4: Crear Usuario**
```javascript
// Crear nuevo usuario
const nuevoUsuario = {
  usuario: "maria.gonzalez",
  nombre: "María",
  apellido_paterno: "González",
  apellido_materno: "López",
  clave: "password123",
  correo: "maria.gonzalez@empresa.com",
  id_estado: 1,
  id_rol: 3,
  id_perfil: 1,
  id_sucursalactiva: 103
};

const resultado = await crearUsuario(nuevoUsuario);
console.log('Usuario creado:', resultado.id);
```

### **Paso 5: Asignar Accesos**
```javascript
// Asignar aplicaciones al usuario
await asignarAplicaciones(resultado.id, [1, 2]);

// Asignar permisos al usuario
await asignarPermisos(resultado.id, ["perm-001", "perm-002", "perm-003"]);

// Asignar sucursales al usuario
await asignarSucursalesPermitidas(resultado.id, [103, 104]);
```

---

## 🔒 **VALIDACIONES DE SEGURIDAD:**

### **✅ Validaciones implementadas:**
- **Autenticación requerida:** Token JWT obligatorio en todos los endpoints
- **Verificación de administrador:** Solo usuarios con `id_perfil = 3` pueden gestionar
- **Validación de datos:** Campos requeridos y formatos validados
- **Prevención de duplicados:** Usuarios, correos y nombres únicos
- **Verificación de relaciones:** Aplicaciones y permisos deben existir
- **Soft delete:** Usuarios se desactivan, no se eliminan físicamente

### **❌ Casos de error manejados:**
- **Sin token:** 401 Unauthorized
- **Sin permisos de admin:** 403 Forbidden
- **Datos inválidos:** 400 Bad Request
- **Recurso no encontrado:** 404 Not Found
- **Conflicto de duplicados:** 400 Bad Request
- **Error interno:** 500 Internal Server Error

---

## 📱 **EJEMPLO DE COMPONENTE REACT PARA GESTIÓN:**

```jsx
import React, { useState, useEffect } from 'react';

const GestionUsuarios = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [perfiles, setPerfiles] = useState([]);
  const [aplicaciones, setAplicaciones] = useState([]);
  const [permisos, setPermisos] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [usuariosRes, perfilesRes, appsRes, permisosRes] = await Promise.all([
        listarUsuarios(),
        listarPerfiles(),
        listarAplicaciones(),
        listarPermisos()
      ]);
      
      setUsuarios(usuariosRes);
      setPerfiles(perfilesRes);
      setAplicaciones(appsRes);
      setPermisos(permisosRes);
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCrearUsuario = async (datosUsuario) => {
    try {
      const resultado = await crearUsuario(datosUsuario);
      alert(`Usuario creado: ${resultado.usuario}`);
      cargarDatos(); // Recargar lista
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleAsignarPermisos = async (usuarioId, permisosSeleccionados) => {
    try {
      await asignarPermisos(usuarioId, permisosSeleccionados);
      alert('Permisos asignados correctamente');
      cargarDatos();
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="gestion-usuarios">
      <h2>Gestión de Usuarios</h2>
      
      {/* Lista de usuarios */}
      <div className="usuarios-lista">
        <h3>Usuarios del Sistema</h3>
        {usuarios.map(usuario => (
          <div key={usuario.id} className="usuario-item">
            <span>{usuario.nombre} {usuario.apellido_paterno}</span>
            <span>{usuario.usuario}</span>
            <span>{usuario.perfil_nombre}</span>
            <span>{usuario.sucursal_activa_nombre}</span>
            <button onClick={() => handleAsignarPermisos(usuario.id, [])}>
              Gestionar Permisos
            </button>
          </div>
        ))}
      </div>

      {/* Formulario para crear usuario */}
      <div className="crear-usuario">
        <h3>Crear Nuevo Usuario</h3>
        {/* Formulario aquí */}
      </div>
    </div>
  );
};

export default GestionUsuarios;
```

---

## 🎯 **CASOS DE USO IMPLEMENTADOS:**

### **1. Gestión de Usuarios:**
- ✅ Crear usuarios con perfiles específicos
- ✅ Asignar roles y estados
- ✅ Gestionar información personal
- ✅ Control de acceso por sucursal

### **2. Gestión de Perfiles:**
- ✅ Crear perfiles personalizados
- ✅ Asignar perfiles a usuarios
- ✅ Jerarquía de permisos

### **3. Gestión de Aplicaciones:**
- ✅ Registrar nuevas aplicaciones
- ✅ Control de acceso por app
- ✅ URLs y descripciones

### **4. Gestión de Permisos:**
- ✅ Permisos granulares por aplicación
- ✅ Asignación masiva de permisos
- ✅ Control de acceso detallado

### **5. Asignación de Accesos:**
- ✅ Usuario ↔ Sucursales
- ✅ Usuario ↔ Aplicaciones
- ✅ Usuario ↔ Permisos

---

## 🚀 **¡LISTO PARA INTEGRACIÓN!**

**El sistema de gestión de usuarios está completamente implementado con:**

1. ✅ **CRUD completo de usuarios** - Crear, leer, actualizar, desactivar
2. ✅ **Gestión de perfiles** - Crear y asignar perfiles
3. ✅ **Gestión de aplicaciones** - Registrar apps del sistema
4. ✅ **Gestión de permisos** - Permisos granulares por aplicación
5. ✅ **Asignación de accesos** - Control completo de permisos y apps
6. ✅ **Validaciones de seguridad** - Solo administradores pueden gestionar
7. ✅ **Soft delete** - Usuarios se desactivan, no se eliminan

**¡El frontend puede implementar un panel completo de administración de usuarios!** 🎯

---

## 📞 **SOPORTE:**

**Si tienen alguna pregunta sobre la gestión de usuarios, estamos disponibles para ayudar.**

**¡Todos los endpoints están 100% funcionales y seguros!** 🚀

---

**Equipo Backend** 🔧
