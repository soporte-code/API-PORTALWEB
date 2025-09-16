# ✅ **ENDPOINTS DE GESTIÓN DE TABLAS PIVOT IMPLEMENTADOS**

---

## 🎯 **ENDPOINTS PARA CONFIGURAR ASOCIACIONES**

Hola equipo Frontend,

He implementado **8 endpoints completos** para gestionar las **tablas pivot** que asocian labores con especies y atributos con especies.

---

## 🔗 **TABLAS PIVOT IMPLEMENTADAS**

### **✅ Labor ↔ Especie (`conteo_pivot_labor_especie`)**
- **Propósito**: Asociar qué labores se pueden realizar en qué especies
- **Ejemplo**: RALEO se puede hacer en NECTARIN, MANZANA, PERA

### **✅ Atributo ↔ Especie (`conteo_pivot_atributo_especie`)**
- **Propósito**: Asociar qué atributos se pueden medir en qué especies
- **Ejemplo**: PESO se puede medir en NECTARIN, FRUTOS en MANZANA

---

## 📊 **ENDPOINTS DE LABOR-ESPECIE (4 endpoints)**

### **1. Listar Combinaciones Labor-Especie**
```http
GET /api/pautas/labor-especie
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Combinaciones labor-especie obtenidas exitosamente",
  "data": {
    "labor_especies": [
      {
        "id": 1,
        "id_labor": 1,
        "id_especie": 1,
        "id_estado": 1,
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN",
        "caja_equivalente": 18.0
      },
      {
        "id": 2,
        "id_labor": 2,
        "id_especie": 1,
        "id_estado": 1,
        "nombre_labor": "PODA",
        "nombre_especie": "NECTARIN",
        "caja_equivalente": 18.0
      }
    ],
    "total": 2
  }
}
```

### **2. Crear Nueva Combinación Labor-Especie**
```http
POST /api/pautas/labor-especie
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_labor": 1,
  "id_especie": 2,
  "id_estado": 1
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Combinación labor-especie creada exitosamente",
  "data": {
    "id": 3,
    "id_labor": 1,
    "id_especie": 2,
    "id_estado": 1,
    "nombre_labor": "RALEO",
    "nombre_especie": "MANZANA",
    "caja_equivalente": 20.0
  }
}
```

### **3. Actualizar Combinación Labor-Especie**
```http
PUT /api/pautas/labor-especie/{relacion_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_estado": 0
}
```

**Ejemplo:**
```http
PUT /api/pautas/labor-especie/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_estado": 0
}
```

### **4. Eliminar Combinación Labor-Especie**
```http
DELETE /api/pautas/labor-especie/{relacion_id}
Authorization: Bearer {token}
```

**Ejemplo:**
```http
DELETE /api/pautas/labor-especie/1
Authorization: Bearer {token}
```

---

## 📊 **ENDPOINTS DE ATRIBUTO-ESPECIE (4 endpoints)**

### **1. Listar Relaciones Atributo-Especie**
```http
GET /api/pautas/atributo-especie
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Relaciones atributo-especie obtenidas exitosamente",
  "data": {
    "atributos_especie": [
      {
        "id": 1,
        "id_atributo": 1,
        "id_especie": 1,
        "nombre_atributo": "PESO",
        "nombre_especie": "NECTARIN",
        "caja_equivalente": 18.0
      },
      {
        "id": 2,
        "id_atributo": 2,
        "id_especie": 1,
        "nombre_atributo": "FRUTOS",
        "nombre_especie": "NECTARIN",
        "caja_equivalente": 18.0
      }
    ],
    "total": 2
  }
}
```

### **2. Crear Nueva Relación Atributo-Especie**
```http
POST /api/pautas/atributo-especie
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 3,
  "id_especie": 2
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Relación atributo-especie creada exitosamente",
  "data": {
    "id": 3,
    "id_atributo": 3,
    "id_especie": 2,
    "nombre_atributo": "CARGADORES",
    "nombre_especie": "MANZANA",
    "caja_equivalente": 20.0
  }
}
```

### **3. Actualizar Relación Atributo-Especie**
```http
PUT /api/pautas/atributo-especie/{relacion_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 4,
  "id_especie": 1
}
```

**Ejemplo:**
```http
PUT /api/pautas/atributo-especie/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 4,
  "id_especie": 1
}
```

### **4. Eliminar Relación Atributo-Especie**
```http
DELETE /api/pautas/atributo-especie/{relacion_id}
Authorization: Bearer {token}
```

**Ejemplo:**
```http
DELETE /api/pautas/atributo-especie/1
Authorization: Bearer {token}
```

---

## 🖥️ **IMPLEMENTACIÓN EN EL FRONTEND**

### **✅ Pantalla de Configuración de Labor-Especie:**

```
┌─────────────────────────────────────┐
│     CONFIGURAR LABOR-ESPECIE        │
├─────────────────────────────────────┤
│ Nueva Asociación:                   │
│ Labor: [RALEO ▼]                    │
│ Especie: [NECTARIN ▼]               │
│ Estado: [Activo ▼]                  │
│                                     │
│ [+ CREAR ASOCIACIÓN]                │
│                                     │
│ Asociaciones Existentes:            │
│ ┌─────────────────────────────────┐ │
│ │ RALEO - NECTARIN (Activo) [✏️][🗑️] │ │
│ │ PODA - NECTARIN (Activo) [✏️][🗑️] │ │
│ │ RALEO - MANZANA (Inactivo)[✏️][🗑️] │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **✅ Pantalla de Configuración de Atributo-Especie:**

```
┌─────────────────────────────────────┐
│   CONFIGURAR ATRIBUTO-ESPECIE        │
├─────────────────────────────────────┤
│ Nueva Asociación:                   │
│ Atributo: [PESO ▼]                  │
│ Especie: [NECTARIN ▼]               │
│                                     │
│ [+ CREAR ASOCIACIÓN]                │
│                                     │
│ Asociaciones Existentes:            │
│ ┌─────────────────────────────────┐ │
│ │ PESO - NECTARIN [✏️][🗑️]          │ │
│ │ FRUTOS - NECTARIN [✏️][🗑️]        │ │
│ │ CARGADORES - MANZANA [✏️][🗑️]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **✅ Ejemplo de Implementación:**

```javascript
// 1. Cargar combinaciones labor-especie
const cargarLaborEspecie = async () => {
  try {
    const response = await fetch('/api/pautas/labor-especie', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setLaborEspecies(data.data.labor_especies);
    }
  } catch (error) {
    console.error('Error cargando labor-especie:', error);
  }
};

// 2. Crear nueva combinación labor-especie
const crearLaborEspecie = async (laborId, especieId, estado = 1) => {
  try {
    const response = await fetch('/api/pautas/labor-especie', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id_labor: laborId,
        id_especie: especieId,
        id_estado: estado
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Combinación creada:', data.data);
      // Recargar la lista
      await cargarLaborEspecie();
    }
  } catch (error) {
    console.error('Error creando labor-especie:', error);
  }
};

// 3. Eliminar combinación labor-especie
const eliminarLaborEspecie = async (relacionId) => {
  try {
    const response = await fetch(`/api/pautas/labor-especie/${relacionId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Combinación eliminada');
      // Recargar la lista
      await cargarLaborEspecie();
    }
  } catch (error) {
    console.error('Error eliminando labor-especie:', error);
  }
};

// 4. Cargar relaciones atributo-especie
const cargarAtributoEspecie = async () => {
  try {
    const response = await fetch('/api/pautas/atributo-especie', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setAtributosEspecie(data.data.atributos_especie);
    }
  } catch (error) {
    console.error('Error cargando atributo-especie:', error);
  }
};

// 5. Crear nueva relación atributo-especie
const crearAtributoEspecie = async (atributoId, especieId) => {
  try {
    const response = await fetch('/api/pautas/atributo-especie', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id_atributo: atributoId,
        id_especie: especieId
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Relación creada:', data.data);
      // Recargar la lista
      await cargarAtributoEspecie();
    }
  } catch (error) {
    console.error('Error creando atributo-especie:', error);
  }
};
```

---

## 🎯 **CASOS DE USO**

### **✅ Configuración de Labor-Especie:**
- **Asociar labores** con especies específicas
- **Activar/desactivar** combinaciones según temporada
- **Gestionar** qué labores se pueden hacer en cada especie

### **✅ Configuración de Atributo-Especie:**
- **Asociar atributos** con especies específicas
- **Definir** qué se puede medir en cada especie
- **Configurar** el sistema de pautas dinámicas

### **✅ Flujo de Configuración:**
1. **Crear labores** (ej: RALEO, PODA, CONTEO)
2. **Crear atributos** (ej: PESO, FRUTOS, CARGADORES)
3. **Asociar labores** con especies (ej: RALEO ↔ NECTARIN)
4. **Asociar atributos** con especies (ej: PESO ↔ NECTARIN)
5. **Configurar pautas** basadas en estas asociaciones

---

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

### **✅ Validaciones:**
- **Campos requeridos** validados en todos los endpoints
- **Duplicados** verificados antes de crear
- **Manejo de errores** robusto con mensajes descriptivos

### **✅ Funcionalidades:**
- **CRUD completo** para ambas tablas pivot
- **Estados** para labor-especie (activo/inactivo)
- **JOINs** con tablas relacionadas para nombres
- **Ordenamiento** por nombre de labor/atributo

### **✅ Seguridad:**
- **Autenticación JWT** requerida en todos los endpoints
- **Validación de datos** en entrada
- **Manejo seguro** de conexiones de base de datos

---

## 📝 **RESUMEN**

**✅ ENDPOINTS IMPLEMENTADOS:**

### **Labor-Especie (4 endpoints):**
- `GET /api/pautas/labor-especie` - Listar combinaciones
- `POST /api/pautas/labor-especie` - Crear combinación
- `PUT /api/pautas/labor-especie/{id}` - Actualizar combinación
- `DELETE /api/pautas/labor-especie/{id}` - Eliminar combinación

### **Atributo-Especie (4 endpoints):**
- `GET /api/pautas/atributo-especie` - Listar relaciones
- `POST /api/pautas/atributo-especie` - Crear relación
- `PUT /api/pautas/atributo-especie/{id}` - Actualizar relación
- `DELETE /api/pautas/atributo-especie/{id}` - Eliminar relación

**Total: 8 endpoints completos para gestionar las tablas pivot.**

**El frontend puede proceder con la implementación de las pantallas de configuración de asociaciones labor-especie y atributo-especie.**

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ ENDPOINTS IMPLEMENTADOS - LISTOS PARA USO

---

## 🎯 **PRÓXIMOS PASOS**

1. **Probar endpoints** desde el frontend con token válido
2. **Implementar pantallas** de configuración de asociaciones
3. **Integrar** con las pantallas existentes de labores y atributos
4. **Validar** que las asociaciones funcionen correctamente

**¡Los endpoints están listos para configurar las tablas pivot!** 🚀
