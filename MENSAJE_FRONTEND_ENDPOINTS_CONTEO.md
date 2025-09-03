# 🚀 **ENDPOINTS DE CONTEO - ATRIBUTOS ÓPTIMOS Y ESPECIES**

---

## 📋 **DESCRIPCIÓN GENERAL**

Se han implementado nuevos endpoints para gestionar los parámetros de conteo del sistema agrícola. Estos endpoints permiten:

1. **Atributos Óptimos**: Configurar rangos óptimos de producción por hectárea según la edad de las plantas
2. **Atributos por Especie**: Asociar atributos específicos a cada especie de planta

---

## 🌱 **ENDPOINTS DE ATRIBUTO ÓPTIMO**

### **1. Listar Atributos Óptimos**
```http
GET /api/conteo/atributo-optimo
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributos óptimos obtenidos exitosamente",
  "data": {
    "atributos": [
      {
        "id": 1,
        "id_atributo": 1,
        "edad_min": 1,
        "edad_max": 3,
        "optimo_ha": 15000,
        "min_ha": 12000,
        "max_ha": 18000,
        "nombre_atributo": "Racimos por planta"
      }
    ],
    "total": 1
  }
}
```

### **2. Obtener Atributo Óptimo Específico**
```http
GET /api/conteo/atributo-optimo/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributo óptimo obtenido exitosamente",
  "data": {
    "id": 1,
    "id_atributo": 1,
    "edad_min": 1,
    "edad_max": 3,
    "optimo_ha": 15000,
    "min_ha": 12000,
    "max_ha": 18000,
    "nombre_atributo": "Racimos por planta"
  }
}
```

### **3. Crear Atributo Óptimo**
```http
POST /api/conteo/atributo-optimo
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 1,
  "edad_min": 1,
  "edad_max": 3,
  "optimo_ha": 15000,
  "min_ha": 12000,
  "max_ha": 18000
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Atributo óptimo creado exitosamente",
  "data": {
    "id": 2,
    "id_atributo": 1,
    "edad_min": 1,
    "edad_max": 3,
    "optimo_ha": 15000,
    "min_ha": 12000,
    "max_ha": 18000,
    "nombre_atributo": "Racimos por planta"
  }
}
```

### **4. Actualizar Atributo Óptimo**
```http
PUT /api/conteo/atributo-optimo/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "edad_min": 2,
  "edad_max": 4,
  "optimo_ha": 16000
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributo óptimo actualizado exitosamente",
  "data": {
    "id": 1,
    "id_atributo": 1,
    "edad_min": 2,
    "edad_max": 4,
    "optimo_ha": 16000,
    "min_ha": 12000,
    "max_ha": 18000,
    "nombre_atributo": "Racimos por planta"
  }
}
```

### **5. Eliminar Atributo Óptimo**
```http
DELETE /api/conteo/atributo-optimo/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributo óptimo eliminado exitosamente",
  "data": {
    "id": 1
  }
}
```

### **6. Obtener Atributos Óptimos por Atributo**
```http
GET /api/conteo/atributo-optimo/por-atributo/{atributo_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributos óptimos obtenidos exitosamente",
  "data": {
    "atributos": [
      {
        "id": 1,
        "id_atributo": 1,
        "edad_min": 1,
        "edad_max": 3,
        "optimo_ha": 15000,
        "min_ha": 12000,
        "max_ha": 18000,
        "nombre_atributo": "Racimos por planta"
      }
    ],
    "total": 1
  }
}
```

---

## 🍇 **ENDPOINTS DE ATRIBUTO ESPECIE**

### **1. Listar Relaciones Atributo-Especie**
```http
GET /api/conteo/atributo-especie
Authorization: Bearer {token}
```

**Response (200):**
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
        "nombre_atributo": "Racimos por planta",
        "nombre_especie": "Uva de Mesa"
      }
    ],
    "total": 1
  }
}
```

### **2. Obtener Relación Específica**
```http
GET /api/conteo/atributo-especie/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Relación atributo-especie obtenida exitosamente",
  "data": {
    "id": 1,
    "id_atributo": 1,
    "id_especie": 1,
    "nombre_atributo": "Racimos por planta",
    "nombre_especie": "Uva de Mesa"
  }
}
```

### **3. Crear Relación Atributo-Especie**
```http
POST /api/conteo/atributo-especie
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 1,
  "id_especie": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Relación atributo-especie creada exitosamente",
  "data": {
    "id": 2,
    "id_atributo": 1,
    "id_especie": 1,
    "nombre_atributo": "Racimos por planta",
    "nombre_especie": "Uva de Mesa"
  }
}
```

### **4. Actualizar Relación**
```http
PUT /api/conteo/atributo-especie/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_atributo": 2,
  "id_especie": 1
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Relación atributo-especie actualizada exitosamente",
  "data": {
    "id": 1,
    "id_atributo": 2,
    "id_especie": 1,
    "nombre_atributo": "Peso por racimo",
    "nombre_especie": "Uva de Mesa"
  }
}
```

### **5. Eliminar Relación**
```http
DELETE /api/conteo/atributo-especie/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Relación atributo-especie eliminada exitosamente",
  "data": {
    "id": 1
  }
}
```

### **6. Obtener Atributos por Especie**
```http
GET /api/conteo/atributo-especie/por-especie/{especie_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Atributos de especie obtenidos exitosamente",
  "data": {
    "atributos": [
      {
        "id": 1,
        "id_atributo": 1,
        "id_especie": 1,
        "nombre_atributo": "Racimos por planta",
        "nombre_especie": "Uva de Mesa"
      }
    ],
    "total": 1
  }
}
```

---

## 📊 **ESTRUCTURA DE DATOS**

### **Tabla: conteo_dim_atributooptimo**
```sql
CREATE TABLE conteo_dim_atributooptimo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_atributo INT NOT NULL,
    edad_min INT NOT NULL,
    edad_max INT NOT NULL,
    optimo_ha DECIMAL(10,2) NOT NULL,
    min_ha DECIMAL(10,2) NOT NULL,
    max_ha DECIMAL(10,2) NOT NULL,
    id_estado INT DEFAULT 1,
    FOREIGN KEY (id_atributo) REFERENCES conteo_dim_atributo(id)
);
```

### **Tabla: conteo_pivot_atributo_especie**
```sql
CREATE TABLE conteo_pivot_atributo_especie (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_atributo INT NOT NULL,
    id_especie INT NOT NULL,
    id_estado INT DEFAULT 1,
    FOREIGN KEY (id_atributo) REFERENCES conteo_dim_atributo(id),
    FOREIGN KEY (id_especie) REFERENCES general_dim_especie(id)
);
```

---

## 🔧 **TIPOS DE DATOS**

### **Campos Numéricos:**
- `id`: INT (Auto-increment)
- `id_atributo`: INT (Referencia a atributo)
- `id_especie`: INT (Referencia a especie)
- `edad_min`: INT (Edad mínima en años)
- `edad_max`: INT (Edad máxima en años)
- `optimo_ha`: DECIMAL(10,2) (Valor óptimo por hectárea)
- `min_ha`: DECIMAL(10,2) (Valor mínimo por hectárea)
- `max_ha`: DECIMAL(10,2) (Valor máximo por hectárea)
- `id_estado`: INT (1=activo, 0=inactivo)

### **Campos de Texto:**
- `nombre_atributo`: VARCHAR (Nombre del atributo)
- `nombre_especie`: VARCHAR (Nombre de la especie)

---

## 🛡️ **VALIDACIONES**

### **Atributos Óptimos:**
- ✅ `id_atributo` debe existir en `conteo_dim_atributo`
- ✅ `edad_min` debe ser menor que `edad_max`
- ✅ `min_ha` debe ser menor que `optimo_ha`
- ✅ `optimo_ha` debe ser menor que `max_ha`
- ✅ Todos los campos son requeridos

### **Atributos por Especie:**
- ✅ `id_atributo` debe existir en `conteo_dim_atributo`
- ✅ `id_especie` debe existir en `general_dim_especie`
- ✅ No se permiten duplicados de la misma relación
- ✅ Ambos campos son requeridos

---

## 📝 **EJEMPLOS DE USO**

### **Configurar Atributo Óptimo para Racimos:**
```javascript
// Crear configuración para racimos por planta
const racimosConfig = {
  id_atributo: 1,        // ID del atributo "Racimos por planta"
  edad_min: 1,          // Plantas de 1 año
  edad_max: 3,          // hasta 3 años
  optimo_ha: 15000,     // 15,000 racimos por hectárea (óptimo)
  min_ha: 12000,        // Mínimo 12,000 racimos por hectárea
  max_ha: 18000         // Máximo 18,000 racimos por hectárea
};

fetch('/api/conteo/atributo-optimo', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(racimosConfig)
});
```

### **Asociar Atributo a Especie:**
```javascript
// Asociar "Racimos por planta" a "Uva de Mesa"
const relacion = {
  id_atributo: 1,       // ID del atributo "Racimos por planta"
  id_especie: 1         // ID de la especie "Uva de Mesa"
};

fetch('/api/conteo/atributo-especie', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(relacion)
});
```

### **Obtener Configuración por Especie:**
```javascript
// Obtener todos los atributos configurados para "Uva de Mesa"
fetch('/api/conteo/atributo-especie/por-especie/1', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 🚀 **INTEGRACIÓN CON FRONTEND**

### **TypeScript Interfaces:**
```typescript
interface AtributoOptimo {
  id: number;
  id_atributo: number;
  edad_min: number;
  edad_max: number;
  optimo_ha: number;
  min_ha: number;
  max_ha: number;
  nombre_atributo: string;
}

interface AtributoEspecie {
  id: number;
  id_atributo: number;
  id_especie: number;
  nombre_atributo: string;
  nombre_especie: string;
}

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}
```

### **Servicios Frontend:**
```typescript
class ConteoService {
  private baseUrl = '/api/conteo';
  
  // Atributos Óptimos
  async getAtributosOptimos(): Promise<ApiResponse<{atributos: AtributoOptimo[], total: number}>> {
    return fetch(`${this.baseUrl}/atributo-optimo`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    }).then(res => res.json());
  }
  
  async createAtributoOptimo(data: Partial<AtributoOptimo>): Promise<ApiResponse<AtributoOptimo>> {
    return fetch(`${this.baseUrl}/atributo-optimo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(res => res.json());
  }
  
  // Atributos por Especie
  async getAtributosEspecie(): Promise<ApiResponse<{atributos_especie: AtributoEspecie[], total: number}>> {
    return fetch(`${this.baseUrl}/atributo-especie`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    }).then(res => res.json());
  }
  
  async createAtributoEspecie(data: {id_atributo: number, id_especie: number}): Promise<ApiResponse<AtributoEspecie>> {
    return fetch(`${this.baseUrl}/atributo-especie`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(res => res.json());
  }
}
```

---

## ✅ **ESTADO DE IMPLEMENTACIÓN**

- ✅ **Backend**: Endpoints implementados y registrados
- ✅ **Autenticación**: JWT requerido en todos los endpoints
- ✅ **Validaciones**: Campos requeridos y relaciones verificadas
- ✅ **Soft Delete**: Implementado para mantener integridad de datos
- ✅ **Logging**: Errores registrados para debugging
- ✅ **CORS**: Configurado para permitir peticiones del frontend

---

**📅 Fecha de implementación**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ LISTO PARA INTEGRACIÓN
