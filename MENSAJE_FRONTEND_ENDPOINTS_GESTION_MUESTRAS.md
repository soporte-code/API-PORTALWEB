# ✅ **ENDPOINTS DE GESTIÓN DE MUESTRAS IMPLEMENTADOS**

---

## 🎯 **ENDPOINTS IMPLEMENTADOS**

Hola equipo Frontend,

He implementado **6 endpoints CRUD completos** para la gestión de muestras (`conteo_fact_muestra`) que se basan en las configuraciones de pautas establecidas.

---

## 📊 **ENDPOINTS DE MUESTRAS**

### **✅ CRUD Completo para `conteo_fact_muestra`:**

#### **1. Listar Muestras del Usuario**
```http
GET /api/pautas/muestras
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Muestras obtenidas exitosamente",
  "data": {
    "muestras": [
      {
        "id": "MUE001",
        "id_configuracion": 1,
        "id_usuario": "user123",
        "id_temporada": 1,
        "fecha": "2025-08-25",
        "hora_registro": "10:30:00",
        "id_cuartel": 1,
        "id_planta": 5,
        "id_tipoplanta": "02",
        "valor_atributo": 150.5,
        "observaciones": "Muestra tomada en planta principal",
        "nombre_temporada": "Temporada 2024-2025",
        "nombre_cuartel": "Cuartel Norte",
        "nombre_planta": "Planta 5",
        "nombre_tipo_planta": "TIPO 3",
        "id_conteotipo": 1,
        "id_atributo": 2,
        "config_tipoplanta": "2",
        "nombre_atributo": "FRUTOS",
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

#### **2. Crear Nueva Muestra**
```http
POST /api/pautas/muestras
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_configuracion": 1,
  "id_temporada": 1,
  "id_cuartel": 1,
  "valor_atributo": 150.5,
  "id_planta": 5,
  "id_tipoplanta": "02",
  "observaciones": "Muestra tomada en planta principal"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Muestra creada exitosamente",
  "data": {
    "id": "MUE002",
    "id_configuracion": 1,
    "id_usuario": "user123",
    "id_temporada": 1,
    "fecha": "2025-08-25",
    "hora_registro": "10:35:00",
    "id_cuartel": 1,
    "id_planta": 5,
    "id_tipoplanta": "02",
    "valor_atributo": 150.5,
    "observaciones": "Muestra tomada en planta principal",
    "nombre_temporada": "Temporada 2024-2025",
    "nombre_cuartel": "Cuartel Norte",
    "nombre_planta": "Planta 5",
    "nombre_tipo_planta": "TIPO 3",
    "nombre_atributo": "FRUTOS",
    "nombre_labor": "RALEO",
    "nombre_especie": "NECTARIN"
  }
}
```

#### **3. Obtener Muestra Específica**
```http
GET /api/pautas/muestras/{muestra_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Muestra obtenida exitosamente",
  "data": {
    "id": "MUE001",
    "id_configuracion": 1,
    "id_usuario": "user123",
    "id_temporada": 1,
    "fecha": "2025-08-25",
    "hora_registro": "10:30:00",
    "id_cuartel": 1,
    "id_planta": 5,
    "id_tipoplanta": "02",
    "valor_atributo": 150.5,
    "observaciones": "Muestra tomada en planta principal",
    "nombre_temporada": "Temporada 2024-2025",
    "nombre_cuartel": "Cuartel Norte",
    "nombre_planta": "Planta 5",
    "nombre_tipo_planta": "TIPO 3",
    "nombre_atributo": "FRUTOS",
    "nombre_labor": "RALEO",
    "nombre_especie": "NECTARIN"
  }
}
```

#### **4. Actualizar Muestra**
```http
PUT /api/pautas/muestras/{muestra_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "valor_atributo": 175.0,
  "observaciones": "Valor actualizado después de revisión"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Muestra actualizada exitosamente",
  "data": {
    "id": "MUE001",
    "valor_atributo": 175.0,
    "observaciones": "Valor actualizado después de revisión",
    "nombre_atributo": "FRUTOS",
    "nombre_labor": "RALEO",
    "nombre_especie": "NECTARIN"
  }
}
```

#### **5. Eliminar Muestra**
```http
DELETE /api/pautas/muestras/{muestra_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Muestra eliminada exitosamente"
}
```

#### **6. Crear Muestras Masivas**
```http
POST /api/pautas/muestras-masivo
Authorization: Bearer {token}
Content-Type: application/json

{
  "muestras": [
    {
      "id_configuracion": 1,
      "id_temporada": 1,
      "id_cuartel": 1,
      "valor_atributo": 150.5,
      "id_planta": 5,
      "observaciones": "Muestra 1"
    },
    {
      "id_configuracion": 1,
      "id_temporada": 1,
      "id_cuartel": 1,
      "valor_atributo": 200.0,
      "id_planta": 6,
      "observaciones": "Muestra 2"
    }
  ]
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "2 muestras creadas exitosamente",
  "data": {
    "muestras_creadas": [
      {
        "id": "MUE003",
        "valor_atributo": 150.5,
        "nombre_atributo": "FRUTOS",
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN"
      },
      {
        "id": "MUE004",
        "valor_atributo": 200.0,
        "nombre_atributo": "FRUTOS",
        "nombre_labor": "RALEO",
        "nombre_especie": "NECTARIN"
      }
    ],
    "total_creadas": 2
  }
}
```

---

## 📱 **IMPLEMENTACIÓN EN EL FRONTEND**

### **✅ Gestión de Muestras:**

```javascript
// Listar muestras del usuario
const cargarMuestras = async () => {
  try {
    const response = await fetch('/api/pautas/muestras', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setMuestras(data.data.muestras);
    }
  } catch (error) {
    console.error('Error cargando muestras:', error);
  }
};

// Crear muestra
const crearMuestra = async (muestraData) => {
  try {
    const response = await fetch('/api/pautas/muestras', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(muestraData)
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Muestra creada:', data.data);
      cargarMuestras(); // Recargar lista
    }
  } catch (error) {
    console.error('Error creando muestra:', error);
  }
};

// Actualizar muestra
const actualizarMuestra = async (id, datosActualizacion) => {
  try {
    const response = await fetch(`/api/pautas/muestras/${id}`, {
      method: 'PUT',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(datosActualizacion)
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Muestra actualizada:', data.data);
      cargarMuestras(); // Recargar lista
    }
  } catch (error) {
    console.error('Error actualizando muestra:', error);
  }
};

// Eliminar muestra
const eliminarMuestra = async (id) => {
  try {
    const response = await fetch(`/api/pautas/muestras/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Muestra eliminada');
      cargarMuestras(); // Recargar lista
    }
  } catch (error) {
    console.error('Error eliminando muestra:', error);
  }
};

// Crear muestras masivas
const crearMuestrasMasivas = async (muestrasArray) => {
  try {
    const response = await fetch('/api/pautas/muestras-masivo', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ muestras: muestrasArray })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log(`${data.data.total_creadas} muestras creadas`);
      cargarMuestras(); // Recargar lista
    }
  } catch (error) {
    console.error('Error creando muestras masivas:', error);
  }
};
```

### **✅ Componente de Lista de Muestras:**

```javascript
const MuestrasList = ({ muestras }) => {
  return (
    <div className="muestras-container">
      <h3>📊 Muestras Registradas</h3>
      
      {muestras.map(muestra => (
        <div key={muestra.id} className="muestra-card">
          <div className="muestra-header">
            <h4>{muestra.nombre_labor} - {muestra.nombre_especie}</h4>
            <span className="fecha">{muestra.fecha} {muestra.hora_registro}</span>
          </div>
          
          <div className="muestra-info">
            <p><strong>Atributo:</strong> {muestra.nombre_atributo}</p>
            <p><strong>Valor:</strong> {muestra.valor_atributo}</p>
            <p><strong>Cuartel:</strong> {muestra.nombre_cuartel}</p>
            <p><strong>Planta:</strong> {muestra.nombre_planta}</p>
            <p><strong>Tipo Planta:</strong> {muestra.nombre_tipo_planta}</p>
            {muestra.observaciones && (
              <p><strong>Observaciones:</strong> {muestra.observaciones}</p>
            )}
          </div>
          
          <div className="muestra-actions">
            <button onClick={() => editarMuestra(muestra.id)}>
              ✏️ Editar
            </button>
            <button onClick={() => eliminarMuestra(muestra.id)}>
              🗑️ Eliminar
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 🎯 **CASOS DE USO**

### **✅ Gestión de Muestras:**
- **Registrar muestras** tomadas en campo según configuraciones de pauta
- **Capturar valores** de atributos específicos (peso, frutos, etc.)
- **Asociar muestras** a plantas específicas y tipos de planta
- **Agregar observaciones** y notas adicionales
- **Crear múltiples muestras** de una vez para eficiencia
- **Editar valores** de muestras existentes
- **Eliminar muestras** incorrectas o duplicadas

### **✅ Flujo de Trabajo:**
1. **Seleccionar configuración** de pauta (labor-especie-atributo)
2. **Elegir temporada** y cuartel
3. **Tomar muestra** en planta específica
4. **Registrar valor** del atributo medido
5. **Agregar observaciones** si es necesario
6. **Guardar muestra** en el sistema

---

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

### **✅ Validaciones:**
- **Campos requeridos** validados en POST y PUT
- **Usuario autenticado** requerido para todas las operaciones
- **Filtrado por usuario** en todas las consultas
- **Manejo de errores** robusto con mensajes descriptivos

### **✅ Funcionalidades:**
- **CRUD completo** para muestras
- **Creación masiva** de muestras
- **JOINs completos** con todas las tablas relacionadas
- **Información contextual** completa (labor, especie, atributo, etc.)
- **Transacciones** de base de datos seguras

### **✅ Seguridad:**
- **Autenticación JWT** requerida en todos los endpoints
- **Filtrado por usuario** para evitar acceso no autorizado
- **Validación de datos** en entrada
- **Manejo seguro** de conexiones de base de datos

---

## 📊 **ESTRUCTURA DE DATOS**

### **✅ Campos de Muestra:**
- **`id`** - ID único de la muestra
- **`id_configuracion`** - Referencia a configuración de pauta
- **`id_usuario`** - Usuario que tomó la muestra
- **`id_temporada`** - Temporada de la muestra
- **`fecha`** - Fecha de toma de muestra
- **`hora_registro`** - Hora de registro
- **`id_cuartel`** - Cuartel donde se tomó la muestra
- **`id_planta`** - Planta específica (opcional)
- **`id_tipoplanta`** - Tipo de planta (opcional)
- **`valor_atributo`** - Valor medido del atributo
- **`observaciones`** - Notas adicionales (opcional)

### **✅ Información Contextual:**
- **`nombre_temporada`** - Nombre de la temporada
- **`nombre_cuartel`** - Nombre del cuartel
- **`nombre_planta`** - Nombre de la planta
- **`nombre_tipo_planta`** - Nombre del tipo de planta
- **`nombre_atributo`** - Nombre del atributo medido
- **`nombre_labor`** - Nombre de la labor
- **`nombre_especie`** - Nombre de la especie

---

## 📝 **RESUMEN**

**✅ ENDPOINTS IMPLEMENTADOS:**

### **Muestras (6 endpoints):**
- `GET /api/pautas/muestras` - Listar muestras del usuario
- `POST /api/pautas/muestras` - Crear nueva muestra
- `GET /api/pautas/muestras/{id}` - Obtener muestra específica
- `PUT /api/pautas/muestras/{id}` - Actualizar muestra
- `DELETE /api/pautas/muestras/{id}` - Eliminar muestra
- `POST /api/pautas/muestras-masivo` - Crear múltiples muestras

**Total: 6 endpoints CRUD completos para gestión de muestras basadas en configuraciones de pauta.**

**El frontend puede proceder con la implementación de las pantallas de captura de muestras en campo, incluyendo formularios dinámicos basados en las configuraciones de pauta establecidas.**

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ ENDPOINTS IMPLEMENTADOS - LISTOS PARA USO

---

## 🎯 **PRÓXIMOS PASOS**

1. **Probar endpoints** desde el frontend con token válido
2. **Implementar pantallas** de captura de muestras
3. **Crear formularios dinámicos** basados en configuraciones
4. **Integrar** con el sistema de configuraciones de pauta
5. **Agregar validaciones** adicionales en el frontend

**¡Los endpoints están listos para ser usados!** 🚀
