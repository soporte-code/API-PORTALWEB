# 🚀 **API DE ESTIMACIONES - ENDPOINTS COMPLETOS**

---

## 📋 **INFORMACIÓN GENERAL**

Hola equipo Frontend,

He creado el **módulo completo de Estimaciones** con todos los endpoints necesarios para gestionar las estimaciones de producción agrícola.

---

## 🗄️ **TABLAS DE BASE DE DATOS**

### **1. Tabla Principal: `estimacion_fact_registroadministradores`**
```sql
Columns:
- id varchar(45) PK 
- id_usuario varchar(45) 
- id_cuartel int 
- id_tipoestimacion int 
- hora_registro datetime 
- embalaje_cajas int 
- embalaje_kg int 
- industria_kg int
```

### **2. Tabla de Tipos: `estimacion_dim_tipo`**
```sql
Columns:
- id int AI PK 
- nombre varchar(45)
```

---

## 🎯 **ENDPOINTS DISPONIBLES**

### **📊 GESTIÓN DE ESTIMACIONES**

#### **1. Listar Estimaciones**
```http
GET /api/estimaciones
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimaciones obtenidas exitosamente",
  "data": {
    "estimaciones": [
      {
        "id": "EST001",
        "id_usuario": "user123",
        "id_cuartel": 1,
        "id_tipoestimacion": 1,
        "hora_registro": "2025-08-25T10:30:00",
        "embalaje_cajas": 150,
        "embalaje_kg": 7500,
        "industria_kg": 8000,
        "nombre_cuartel": "Cuartel Norte",
        "nombre_tipo_estimacion": "Estimación Temprana"
      }
    ],
    "total": 1
  }
}
```

#### **2. Obtener Estimación Específica**
```http
GET /api/estimaciones/{estimacion_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimación obtenida exitosamente",
  "data": {
    "id": "EST001",
    "id_usuario": "user123",
    "id_cuartel": 1,
    "id_tipoestimacion": 1,
    "hora_registro": "2025-08-25T10:30:00",
    "embalaje_cajas": 150,
    "embalaje_kg": 7500,
    "industria_kg": 8000,
    "nombre_cuartel": "Cuartel Norte",
    "nombre_tipo_estimacion": "Estimación Temprana"
  }
}
```

#### **3. Crear Nueva Estimación**
```http
POST /api/estimaciones
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "id_cuartel": 1,
  "id_tipoestimacion": 1,
  "embalaje_cajas": 150,
  "embalaje_kg": 7500,
  "industria_kg": 8000
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimación creada exitosamente",
  "data": {
    "id": "EST001",
    "id_usuario": "user123",
    "id_cuartel": 1,
    "id_tipoestimacion": 1,
    "hora_registro": "2025-08-25T10:30:00",
    "embalaje_cajas": 150,
    "embalaje_kg": 7500,
    "industria_kg": 8000,
    "nombre_cuartel": "Cuartel Norte",
    "nombre_tipo_estimacion": "Estimación Temprana"
  }
}
```

#### **4. Actualizar Estimación**
```http
PUT /api/estimaciones/{estimacion_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "embalaje_cajas": 200,
  "embalaje_kg": 10000,
  "industria_kg": 12000
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimación actualizada exitosamente",
  "data": {
    "id": "EST001",
    "id_usuario": "user123",
    "id_cuartel": 1,
    "id_tipoestimacion": 1,
    "hora_registro": "2025-08-25T10:30:00",
    "embalaje_cajas": 200,
    "embalaje_kg": 10000,
    "industria_kg": 12000,
    "nombre_cuartel": "Cuartel Norte",
    "nombre_tipo_estimacion": "Estimación Temprana"
  }
}
```

#### **5. Eliminar Estimación**
```http
DELETE /api/estimaciones/{estimacion_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimación eliminada exitosamente"
}
```

---

### **📋 GESTIÓN DE TIPOS DE ESTIMACIÓN**

#### **6. Listar Tipos de Estimación**
```http
GET /api/estimaciones/tipos
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Tipos de estimación obtenidos exitosamente",
  "data": {
    "tipos": [
      {
        "id": 1,
        "nombre": "Estimación Temprana"
      },
      {
        "id": 2,
        "nombre": "Estimación Media"
      },
      {
        "id": 3,
        "nombre": "Estimación Tardía"
      }
    ],
    "total": 3
  }
}
```

#### **7. Obtener Tipo de Estimación Específico**
```http
GET /api/estimaciones/tipos/{tipo_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Tipo de estimación obtenido exitosamente",
  "data": {
    "id": 1,
    "nombre": "Estimación Temprana"
  }
}
```

---

### **🏞️ ESTIMACIONES POR CUARTEL**

#### **8. Obtener Estimaciones por Cuartel**
```http
GET /api/estimaciones/por-cuartel/{cuartel_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Estimaciones del cuartel obtenidas exitosamente",
  "data": {
    "estimaciones": [
      {
        "id": "EST001",
        "id_usuario": "user123",
        "id_cuartel": 1,
        "id_tipoestimacion": 1,
        "hora_registro": "2025-08-25T10:30:00",
        "embalaje_cajas": 150,
        "embalaje_kg": 7500,
        "industria_kg": 8000,
        "nombre_cuartel": "Cuartel Norte",
        "nombre_tipo_estimacion": "Estimación Temprana"
      }
    ],
    "total": 1
  }
}
```

---

### **📊 RESUMEN Y ESTADÍSTICAS**

#### **9. Obtener Resumen de Estimaciones**
```http
GET /api/estimaciones/resumen
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Resumen de estimaciones obtenido exitosamente",
  "data": {
    "resumen_por_tipo": [
      {
        "tipo_estimacion": "Estimación Temprana",
        "total_estimaciones": 5,
        "total_cajas": 750,
        "total_kg_embalaje": 37500,
        "total_kg_industria": 40000
      }
    ],
    "resumen_por_cuartel": [
      {
        "nombre_cuartel": "Cuartel Norte",
        "total_estimaciones": 3,
        "total_cajas": 450,
        "total_kg_embalaje": 22500,
        "total_kg_industria": 24000
      }
    ],
    "totales_generales": {
      "total_estimaciones": 5,
      "total_cajas": 750,
      "total_kg_embalaje": 37500,
      "total_kg_industria": 40000
    }
  }
}
```

---

## 🔧 **TIPOS DE DATOS**

### **Estimación:**
```typescript
interface Estimacion {
  id: string;
  id_usuario: string;
  id_cuartel: number;
  id_tipoestimacion: number;
  hora_registro: string; // ISO 8601 datetime
  embalaje_cajas: number;
  embalaje_kg: number;
  industria_kg: number;
  nombre_cuartel?: string;
  nombre_tipo_estimacion?: string;
}
```

### **Tipo de Estimación:**
```typescript
interface TipoEstimacion {
  id: number;
  nombre: string;
}
```

### **Resumen por Tipo:**
```typescript
interface ResumenTipo {
  tipo_estimacion: string;
  total_estimaciones: number;
  total_cajas: number;
  total_kg_embalaje: number;
  total_kg_industria: number;
}
```

### **Resumen por Cuartel:**
```typescript
interface ResumenCuartel {
  nombre_cuartel: string;
  total_estimaciones: number;
  total_cajas: number;
  total_kg_embalaje: number;
  total_kg_industria: number;
}
```

### **Totales Generales:**
```typescript
interface TotalesGenerales {
  total_estimaciones: number;
  total_cajas: number;
  total_kg_embalaje: number;
  total_kg_industria: number;
}
```

---

## 🎯 **EJEMPLOS DE USO FRONTEND**

### **1. Cargar Lista de Estimaciones:**
```javascript
const cargarEstimaciones = async () => {
  try {
    const response = await fetch('/api/estimaciones', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setEstimaciones(data.data.estimaciones);
      setTotalEstimaciones(data.data.total);
    }
  } catch (error) {
    console.error('Error cargando estimaciones:', error);
  }
};
```

### **2. Crear Nueva Estimación:**
```javascript
const crearEstimacion = async (estimacionData) => {
  try {
    const response = await fetch('/api/estimaciones', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(estimacionData)
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Actualizar lista de estimaciones
      cargarEstimaciones();
      return data.data;
    }
  } catch (error) {
    console.error('Error creando estimación:', error);
  }
};
```

### **3. Cargar Tipos de Estimación:**
```javascript
const cargarTiposEstimacion = async () => {
  try {
    const response = await fetch('/api/estimaciones/tipos', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setTiposEstimacion(data.data.tipos);
    }
  } catch (error) {
    console.error('Error cargando tipos:', error);
  }
};
```

### **4. Obtener Resumen:**
```javascript
const cargarResumen = async () => {
  try {
    const response = await fetch('/api/estimaciones/resumen', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setResumenPorTipo(data.data.resumen_por_tipo);
      setResumenPorCuartel(data.data.resumen_por_cuartel);
      setTotalesGenerales(data.data.totales_generales);
    }
  } catch (error) {
    console.error('Error cargando resumen:', error);
  }
};
```

---

## 🔒 **SEGURIDAD Y VALIDACIONES**

### **Autenticación:**
- Todos los endpoints requieren token JWT válido
- El `id_usuario` se obtiene automáticamente del token

### **Validaciones:**
- **Campos requeridos:** `id_cuartel`, `id_tipoestimacion`, `embalaje_cajas`, `embalaje_kg`, `industria_kg`
- **Acceso a cuarteles:** Solo cuarteles asignados al usuario
- **Existencia de tipos:** Verificación de tipos de estimación válidos

### **Permisos:**
- Los usuarios solo pueden ver/editar sus propias estimaciones
- Acceso restringido a cuarteles asignados por sucursal

---

## 📱 **PANTALLAS SUGERIDAS**

### **1. Lista de Estimaciones:**
- Tabla con todas las estimaciones del usuario
- Filtros por cuartel, tipo, fecha
- Botones de editar/eliminar

### **2. Formulario de Estimación:**
- Selector de cuartel (solo cuarteles asignados)
- Selector de tipo de estimación
- Campos numéricos para cajas y kg
- Validación de campos requeridos

### **3. Dashboard de Resumen:**
- Gráficos por tipo de estimación
- Gráficos por cuartel
- Totales generales
- Tendencias temporales

### **4. Detalle de Estimación:**
- Vista completa de una estimación
- Información del cuartel y tipo
- Historial de cambios

---

## 🚀 **PRÓXIMOS PASOS**

### **Para el Frontend:**
1. **Implementar pantallas** de gestión de estimaciones
2. **Integrar con módulo de cuarteles** para selección
3. **Crear formularios** de creación/edición
4. **Implementar dashboard** de resumen y estadísticas

### **Para el Backend:**
1. **Desplegar cambios** al servidor
2. **Probar endpoints** con datos reales
3. **Verificar permisos** y validaciones

---

## 📝 **RESUMEN**

- ✅ **9 endpoints completos** para gestión de estimaciones
- ✅ **CRUD completo** para estimaciones
- ✅ **Gestión de tipos** de estimación
- ✅ **Filtros por cuartel** y resúmenes
- ✅ **Seguridad JWT** y validaciones
- ✅ **Documentación completa** para frontend

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ MÓDULO COMPLETO - LISTO PARA INTEGRACIÓN
