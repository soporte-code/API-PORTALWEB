# 🏢 MENSAJE PARA EL FRONTEND - CAMBIAR SUCURSAL ACTIVA

## ✅ **¡ENDPOINTS PARA CAMBIAR SUCURSAL ACTIVA DISPONIBLES!**

**El sistema permite a los usuarios cambiar su sucursal activa de forma segura y validada.**

---

## 📋 **ENDPOINTS DISPONIBLES:**

### **1. 🔄 Cambiar Sucursal Activa**
```http
POST /api/auth/cambiar-sucursal
Authorization: Bearer {token}
Content-Type: application/json
```

**Datos que envía el frontend:**
```json
{
  "id_sucursal": 103
}
```

**Respuesta exitosa:**
```json
{
  "message": "Sucursal actualizada correctamente",
  "id_sucursal": 103,
  "sucursal_nombre": "SANTA VICTORIA"
}
```

**Respuesta de error (sin acceso):**
```json
{
  "error": "No tienes acceso a esta sucursal"
}
```

### **2. 📊 Obtener Sucursal Activa Actual**
```http
GET /api/usuarios/sucursal-activa
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "sucursal_activa": 103
}
```

### **3. 👤 Obtener Información Completa del Usuario**
```http
GET /api/auth/me
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "id": "d113f68b-6bab-4531-bb99-0e337e24e22a",
  "usuario": "usuario123",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "correo": "juan.perez@empresa.com",
  "id_sucursalactiva": 103,
  "sucursal_nombre": "SANTA VICTORIA",
  "id_estado": 1,
  "id_rol": 2,
  "id_perfil": 1,
  "fecha_creacion": "2024-01-15"
}
```

### **4. 🏢 Obtener Sucursales Disponibles del Usuario**
```http
GET /api/sucursales/
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": 103,
    "nombre": "SANTA VICTORIA",
    "ubicacion": "Santiago"
  },
  {
    "id": 104,
    "nombre": "LAS CONDES",
    "ubicacion": "Santiago"
  }
]
```

---

## 🔧 **IMPLEMENTACIÓN EN FRONTEND:**

### **TypeScript Functions:**
```typescript
// Función para cambiar sucursal activa
async function cambiarSucursalActiva(idSucursal: number): Promise<ApiResponse<any>> {
  const response = await fetch('/api/auth/cambiar-sucursal', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ id_sucursal: idSucursal })
  });
  return response.json();
}

// Función para obtener sucursal activa actual
async function obtenerSucursalActiva(): Promise<ApiResponse<any>> {
  const response = await fetch('/api/usuarios/sucursal-activa', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Función para obtener información completa del usuario
async function obtenerUsuarioActual(): Promise<ApiResponse<any>> {
  const response = await fetch('/api/auth/me', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}

// Función para obtener sucursales disponibles
async function obtenerSucursalesDisponibles(): Promise<ApiResponse<any>> {
  const response = await fetch('/api/sucursales/', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return response.json();
}
```

---

## 🎯 **FLUJO RECOMENDADO PARA CAMBIAR SUCURSAL:**

### **Paso 1: Obtener sucursales disponibles**
```javascript
// Obtener lista de sucursales a las que tiene acceso el usuario
const sucursales = await obtenerSucursalesDisponibles();
console.log('Sucursales disponibles:', sucursales);
```

### **Paso 2: Mostrar selector de sucursal**
```javascript
// Crear selector en el frontend
const selector = document.createElement('select');
sucursales.forEach(sucursal => {
  const option = document.createElement('option');
  option.value = sucursal.id;
  option.textContent = sucursal.nombre;
  selector.appendChild(option);
});
```

### **Paso 3: Cambiar sucursal activa**
```javascript
// Cuando el usuario selecciona una nueva sucursal
async function onSucursalChange(event) {
  const nuevaSucursalId = parseInt(event.target.value);
  
  try {
    const resultado = await cambiarSucursalActiva(nuevaSucursalId);
    
    if (resultado.message) {
      // ✅ Éxito
      console.log('Sucursal cambiada:', resultado.sucursal_nombre);
      
      // Actualizar UI
      actualizarInterfazSucursal(resultado.sucursal_nombre);
      
      // Mostrar mensaje de éxito
      mostrarNotificacion('Sucursal cambiada exitosamente', 'success');
      
    } else {
      // ❌ Error
      console.error('Error:', resultado.error);
      mostrarNotificacion(resultado.error, 'error');
    }
  } catch (error) {
    console.error('Error en la petición:', error);
    mostrarNotificacion('Error al cambiar sucursal', 'error');
  }
}
```

### **Paso 4: Actualizar interfaz**
```javascript
// Actualizar elementos de la UI con la nueva sucursal
function actualizarInterfazSucursal(nombreSucursal) {
  // Actualizar header/navbar
  const sucursalElement = document.getElementById('sucursal-actual');
  if (sucursalElement) {
    sucursalElement.textContent = nombreSucursal;
  }
  
  // Actualizar título de página
  document.title = `Portal Web - ${nombreSucursal}`;
  
  // Recargar datos específicos de la sucursal
  cargarDatosSucursal();
}
```

---

## 🔒 **VALIDACIONES DE SEGURIDAD:**

### **✅ Validaciones implementadas:**
- **Autenticación requerida:** Token JWT obligatorio
- **Verificación de acceso:** Solo sucursales permitidas
- **Validación de datos:** ID de sucursal requerido
- **Transacciones seguras:** Base de datos con commit/rollback

### **❌ Casos de error manejados:**
- **Sin token:** 401 Unauthorized
- **Sin acceso a sucursal:** 403 Forbidden
- **ID inválido:** 400 Bad Request
- **Error interno:** 500 Internal Server Error

---

## 📱 **EJEMPLO DE COMPONENTE REACT:**

```jsx
import React, { useState, useEffect } from 'react';

const SelectorSucursal = () => {
  const [sucursales, setSucursales] = useState([]);
  const [sucursalActiva, setSucursalActiva] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargarSucursales();
    cargarSucursalActiva();
  }, []);

  const cargarSucursales = async () => {
    try {
      const response = await obtenerSucursalesDisponibles();
      setSucursales(response);
    } catch (error) {
      console.error('Error cargando sucursales:', error);
    }
  };

  const cargarSucursalActiva = async () => {
    try {
      const response = await obtenerSucursalActiva();
      setSucursalActiva(response.sucursal_activa);
    } catch (error) {
      console.error('Error cargando sucursal activa:', error);
    }
  };

  const handleCambiarSucursal = async (event) => {
    const nuevaSucursalId = parseInt(event.target.value);
    setLoading(true);

    try {
      const resultado = await cambiarSucursalActiva(nuevaSucursalId);
      
      if (resultado.message) {
        setSucursalActiva(nuevaSucursalId);
        alert(`Sucursal cambiada a: ${resultado.sucursal_nombre}`);
        
        // Recargar datos de la aplicación
        window.location.reload();
      } else {
        alert(`Error: ${resultado.error}`);
      }
    } catch (error) {
      alert('Error al cambiar sucursal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="selector-sucursal">
      <label htmlFor="sucursal">Sucursal Activa:</label>
      <select 
        id="sucursal" 
        value={sucursalActiva || ''} 
        onChange={handleCambiarSucursal}
        disabled={loading}
      >
        {sucursales.map(sucursal => (
          <option key={sucursal.id} value={sucursal.id}>
            {sucursal.nombre}
          </option>
        ))}
      </select>
      {loading && <span>Cambiando...</span>}
    </div>
  );
};

export default SelectorSucursal;
```

---

## 🎯 **CASOS DE USO:**

### **1. Cambio manual por usuario:**
- Usuario selecciona nueva sucursal en dropdown
- Sistema valida acceso y actualiza
- Interfaz se actualiza automáticamente

### **2. Cambio automático por permisos:**
- Usuario accede a módulo específico
- Sistema detecta que necesita otra sucursal
- Cambia automáticamente y notifica

### **3. Validación de acceso:**
- Usuario intenta acceder a datos de otra sucursal
- Sistema verifica permisos
- Cambia sucursal si es necesario

---

## 🚀 **¡LISTO PARA INTEGRACIÓN!**

**Los endpoints para cambiar sucursal activa están funcionando y listos para usar:**

1. ✅ **Cambiar sucursal** - POST `/api/auth/cambiar-sucursal`
2. ✅ **Obtener sucursal actual** - GET `/api/usuarios/sucursal-activa`
3. ✅ **Información del usuario** - GET `/api/auth/me`
4. ✅ **Sucursales disponibles** - GET `/api/sucursales/`

**¡El frontend puede implementar el cambio de sucursal de forma segura y eficiente!** 🎯

---

## 📞 **SOPORTE:**

**Si tienen alguna pregunta sobre el cambio de sucursal, estamos disponibles para ayudar.**

**¡Los endpoints están 100% funcionales y seguros!** 🚀

---

**Equipo Backend** 🔧
