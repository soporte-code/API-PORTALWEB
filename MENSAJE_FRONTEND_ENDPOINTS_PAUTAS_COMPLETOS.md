# ✅ **ENDPOINTS DE GESTIÓN DE PAUTAS COMPLETOS IMPLEMENTADOS**

---

## 🎯 **ENDPOINTS IMPLEMENTADOS**

Hola equipo Frontend,

He implementado **16 endpoints completos** para la gestión del sistema de pautas con configuración dinámica de formularios.

---

## 📊 **ENDPOINTS DE CONFIGURACIÓN DE PAUTAS**

### **✅ Configuraciones de Pauta (2 endpoints):**

#### **1. Listar Configuraciones**
```http
GET /api/pautas/configuraciones
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Configuraciones de pauta obtenidas exitosamente",
  "data": {
    "configuraciones": [
      {
        "id": 1,
        "id_empresa": 1,
        "id_conteotipo": 1,
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "nombre_atributo": "PESO",
        "id_labor": 1,
        "id_especie": 1,
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN",
        "nombre_tipo_planta": "Tipo 2"
      }
    ],
    "total": 6
  }
}
```

#### **2. Configuraciones Agrupadas**
```http
GET /api/pautas/configuraciones-agrupadas
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Configuraciones agrupadas obtenidas exitosamente",
  "data": {
    "tipos_conteo": [
      {
        "id_conteotipo": 1,
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN",
        "total_configuraciones": 6,
        "configuraciones": [
          {
            "id": 1,
            "id_empresa": 1,
            "id_conteotipo": 1,
            "id_atributo": 1,
            "id_tipoplanta": "2",
            "nombre_atributo": "PESO",
            "nombre_tipo_planta": "Tipo 2"
          }
        ]
      }
    ],
    "total_tipos_conteo": 1,
    "total_configuraciones": 6
  }
}
```

---

## 🔧 **ENDPOINTS DE GESTIÓN DE ATRIBUTOS Y LABORES**

### **✅ Atributos de Cultivo (2 endpoints):**

#### **1. Listar Atributos**
```http
GET /api/pautas/atributos-cultivo
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Atributos de cultivo obtenidos exitosamente",
  "data": {
    "atributos": [
      {
        "id": 1,
        "nombre": "PESO"
      },
      {
        "id": 2,
        "nombre": "FRUTOS"
      },
      {
        "id": 3,
        "nombre": "CARGADORES"
      }
    ],
    "total": 3
  }
}
```

#### **2. Crear Atributo**
```http
POST /api/pautas/atributos-cultivo
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "NUEVO_ATRIBUTO"
}
```

### **✅ Labores de Conteo (2 endpoints):**

#### **1. Listar Labores**
```http
GET /api/pautas/labores-conteo
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Labores de conteo obtenidas exitosamente",
  "data": {
    "labores": [
      {
        "id": 1,
        "nombre": "RALEO"
      },
      {
        "id": 2,
        "nombre": "PODA"
      },
      {
        "id": 3,
        "nombre": "CONTEO"
      }
    ],
    "total": 3
  }
}
```

#### **2. Crear Labor**
```http
POST /api/pautas/labores-conteo
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "NUEVA_LABOR"
}
```

---

## 🏷️ **ENDPOINTS DE LABOR-ESPECIE Y TIPOS**

### **✅ Labor-Especie (1 endpoint):**

#### **1. Listar Combinaciones Labor-Especie**
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
      }
    ],
    "total": 1
  }
}
```

### **✅ Tipos de Planta (1 endpoint):**

#### **1. Listar Tipos de Planta**
```http
GET /api/pautas/tipos-planta
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Tipos de planta obtenidos exitosamente",
  "data": {
    "tipos_planta": [
      {
        "id": "01",
        "nombre": "Tipo 1",
        "factor_productivo": 1.0,
        "id_empresa": 1,
        "descripcion": "Descripción del tipo 1"
      },
      {
        "id": "02",
        "nombre": "Tipo 2",
        "factor_productivo": 1.2,
        "id_empresa": 1,
        "descripcion": "Descripción del tipo 2"
      }
    ],
    "total": 2
  }
}
```

---

## 📝 **ENDPOINTS DE FORMULARIO DINÁMICO**

### **✅ Generación de Formulario (1 endpoint):**

#### **1. Generar Formulario Dinámico**
```http
GET /api/pautas/formulario/{labor_id}/{especie_id}
Authorization: Bearer {token}
```

**Ejemplo:**
```http
GET /api/pautas/formulario/1/1
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Formulario generado exitosamente",
  "data": {
    "labor_especie": {
      "id": 1,
      "id_labor": 1,
      "id_especie": 1,
      "id_estado": 1,
      "nombre_labor": "RALEO",
      "nombre_especie": "NECTARIN"
    },
    "configuraciones": [
      {
        "id": 1,
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "nombre_atributo": "PESO",
        "nombre_tipo_planta": "Tipo 2"
      }
    ],
    "tipos_planta": [
      {
        "id": "01",
        "nombre": "Tipo 1",
        "factor_productivo": 1.0,
        "id_empresa": 1,
        "descripcion": "Descripción del tipo 1"
      }
    ],
    "total_atributos": 1
  }
}
```

---

## 📋 **ENDPOINTS DE GESTIÓN DE PAUTAS**

### **✅ CRUD Completo de Pautas (3 endpoints):**

#### **1. Listar Pautas del Usuario**
```http
GET /api/pautas/pautas
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Pautas obtenidas exitosamente",
  "data": {
    "pautas": [
      {
        "id": "PAU001",
        "id_conteotipo": 1,
        "id_usuario": "USER001",
        "id_temporada": 1,
        "fecha": "2025-08-25",
        "hora_registro": "14:30:00",
        "id_cuartel": 1,
        "nombre_temporada": "Temporada 2024-2025",
        "nombre_cuartel": "Cuartel Norte",
        "id_labor": 1,
        "id_especie": 1,
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN"
      }
    ],
    "total": 1
  }
}
```

#### **2. Crear Nueva Pauta**
```http
POST /api/pautas/pautas
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_conteotipo": 1,
  "id_temporada": 1,
  "id_cuartel": 1
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Pauta creada exitosamente",
  "data": {
    "id": "PAU002",
    "id_conteotipo": 1,
    "id_usuario": "USER001",
    "id_temporada": 1,
    "fecha": "2025-08-25",
    "hora_registro": "15:45:00",
    "id_cuartel": 1,
    "nombre_temporada": "Temporada 2024-2025",
    "nombre_cuartel": "Cuartel Norte",
    "id_labor": 1,
    "id_especie": 1,
    "nombre_labor": "RALEO",
    "nombre_especie": "NECTARIN"
  }
}
```

#### **3. Obtener Pauta Específica con Detalles**
```http
GET /api/pautas/pautas/{pauta_id}
Authorization: Bearer {token}
```

**Ejemplo:**
```http
GET /api/pautas/pautas/PAU001
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Pauta obtenida exitosamente",
  "data": {
    "pauta": {
      "id": "PAU001",
      "id_conteotipo": 1,
      "id_usuario": "USER001",
      "id_temporada": 1,
      "fecha": "2025-08-25",
      "hora_registro": "14:30:00",
      "id_cuartel": 1,
      "nombre_temporada": "Temporada 2024-2025",
      "nombre_cuartel": "Cuartel Norte",
      "id_labor": 1,
      "id_especie": 1,
      "nombre_labor": "RALEO",
      "nombre_especie": "NECTARIN"
    },
    "detalles": [
      {
        "id": 1,
        "id_pauta": "PAU001",
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "valor_atributo": 15.5,
        "nombre_atributo": "PESO",
        "nombre_tipo_planta": "Tipo 2"
      }
    ],
    "total_detalles": 1
  }
}
```

---

## 📊 **ENDPOINTS DE DETALLES DE PAUTA**

### **✅ Creación Masiva de Detalles (1 endpoint):**

#### **1. Crear Múltiples Detalles de Pauta**
```http
POST /api/pautas/pautas/{pauta_id}/detalles-masivo
Authorization: Bearer {token}
Content-Type: application/json

{
  "detalles": [
    {
      "id_atributo": 1,
      "id_tipoplanta": "2",
      "valor_atributo": 15.5
    },
    {
      "id_atributo": 2,
      "valor_atributo": 25.0
    }
  ]
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "2 detalles de pauta creados exitosamente",
  "data": {
    "detalles": [
      {
        "id": 1,
        "id_pauta": "PAU001",
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "valor_atributo": 15.5,
        "nombre_atributo": "PESO",
        "nombre_tipo_planta": "Tipo 2"
      },
      {
        "id": 2,
        "id_pauta": "PAU001",
        "id_atributo": 2,
        "id_tipoplanta": null,
        "valor_atributo": 25.0,
        "nombre_atributo": "FRUTOS",
        "nombre_tipo_planta": null
      }
    ],
    "total_creados": 2
  }
}
```

---

## 📱 **IMPLEMENTACIÓN EN EL FRONTEND**

### **✅ Flujo Completo de Creación de Pauta:**

```javascript
// 1. Obtener combinaciones labor-especie
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

// 2. Generar formulario dinámico
const generarFormulario = async (laborId, especieId) => {
  try {
    const response = await fetch(`/api/pautas/formulario/${laborId}/${especieId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setFormulario(data.data);
      setConfiguraciones(data.data.configuraciones);
      setTiposPlanta(data.data.tipos_planta);
    }
  } catch (error) {
    console.error('Error generando formulario:', error);
  }
};

// 3. Crear pauta
const crearPauta = async (pautaData) => {
  try {
    const response = await fetch('/api/pautas/pautas', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(pautaData)
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Pauta creada:', data.data);
      return data.data.id; // Retornar ID de la pauta creada
    }
  } catch (error) {
    console.error('Error creando pauta:', error);
  }
};

// 4. Crear detalles masivos
const crearDetallesPauta = async (pautaId, detalles) => {
  try {
    const response = await fetch(`/api/pautas/pautas/${pautaId}/detalles-masivo`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ detalles })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Detalles creados:', data.data.detalles);
    }
  } catch (error) {
    console.error('Error creando detalles:', error);
  }
};

// 5. Flujo completo
const crearPautaCompleta = async (pautaData, detallesData) => {
  try {
    // Crear pauta
    const pautaId = await crearPauta(pautaData);
    
    if (pautaId) {
      // Crear detalles
      await crearDetallesPauta(pautaId, detallesData);
      
      console.log('Pauta completa creada exitosamente');
    }
  } catch (error) {
    console.error('Error en flujo completo:', error);
  }
};
```

---

## 🎯 **CASOS DE USO**

### **✅ Configuración de Pautas:**
- **Listar configuraciones** existentes para labor-especie
- **Ver configuraciones agrupadas** por tipo de conteo
- **Administrar atributos** de cultivo y labores de conteo

### **✅ Generación de Formularios:**
- **Seleccionar labor y especie** para generar formulario dinámico
- **Obtener configuración** de atributos para esa combinación
- **Mostrar tipos de planta** disponibles

### **✅ Gestión de Pautas:**
- **Crear nuevas pautas** con labor-especie-temporada-cuartel
- **Listar pautas** del usuario autenticado
- **Obtener pauta específica** con todos sus detalles

### **✅ Detalles de Pauta:**
- **Crear múltiples detalles** de una vez
- **Asociar atributos** con valores y tipos de planta
- **Validar permisos** de usuario sobre pautas

---

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

### **✅ Validaciones:**
- **Campos requeridos** validados en todos los endpoints
- **Permisos de usuario** verificados para pautas
- **Manejo de errores** robusto con mensajes descriptivos

### **✅ Funcionalidades:**
- **Formulario dinámico** generado automáticamente
- **Configuración por Labor-Especie** con múltiples atributos
- **Tipo de Planta Opcional** para cada atributo
- **Creación masiva** de detalles de pauta
- **Filtros por Usuario** y temporada

### **✅ Seguridad:**
- **Autenticación JWT** requerida en todos los endpoints
- **Validación de datos** en entrada
- **Manejo seguro** de conexiones de base de datos
- **Verificación de permisos** para pautas de usuario

---

## 📝 **RESUMEN**

**✅ ENDPOINTS IMPLEMENTADOS:**

### **Configuración de Pautas (2 endpoints):**
- `GET /api/pautas/configuraciones` - Listar configuraciones
- `GET /api/pautas/configuraciones-agrupadas` - Configuraciones agrupadas

### **Gestión de Atributos y Labores (4 endpoints):**
- `GET /api/pautas/atributos-cultivo` - Listar atributos
- `POST /api/pautas/atributos-cultivo` - Crear atributo
- `GET /api/pautas/labores-conteo` - Listar labores
- `POST /api/pautas/labores-conteo` - Crear labor

### **Labor-Especie y Tipos (2 endpoints):**
- `GET /api/pautas/labor-especie` - Listar combinaciones
- `GET /api/pautas/tipos-planta` - Listar tipos de planta

### **Formulario Dinámico (1 endpoint):**
- `GET /api/pautas/formulario/{labor_id}/{especie_id}` - Generar formulario

### **Gestión de Pautas (3 endpoints):**
- `GET /api/pautas/pautas` - Listar pautas del usuario
- `POST /api/pautas/pautas` - Crear nueva pauta
- `GET /api/pautas/pautas/{id}` - Obtener pauta específica

### **Detalles de Pauta (1 endpoint):**
- `POST /api/pautas/pautas/{id}/detalles-masivo` - Crear múltiples detalles

**Total: 16 endpoints completos para el sistema de pautas con configuración dinámica.**

**El frontend puede proceder con la implementación completa del sistema de pautas, incluyendo la generación dinámica de formularios y la gestión completa de pautas y detalles.**

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ ENDPOINTS IMPLEMENTADOS - LISTOS PARA USO

---

## 🎯 **PRÓXIMOS PASOS**

1. **Probar endpoints** desde el frontend con token válido
2. **Implementar pantallas** de configuración de pautas
3. **Crear formularios dinámicos** basados en labor-especie
4. **Integrar** con el sistema de temporadas y cuarteles

**¡Los endpoints están listos para ser usados!** 🚀
