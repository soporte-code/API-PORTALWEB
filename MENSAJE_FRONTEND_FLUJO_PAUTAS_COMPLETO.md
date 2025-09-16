# ✅ **SISTEMA DE PAUTAS - FLUJO COMPLETO IMPLEMENTADO**

---

## 🎯 **FLUJO CORRECTO DE CREACIÓN DE PAUTAS**

Hola equipo Frontend,

He implementado **4 endpoints nuevos** que siguen el flujo correcto para la creación de pautas:

**Cuartel → Variedad → Especie → Labores → Formulario Dinámico**

---

## 🔄 **FLUJO PASO A PASO**

### **PASO 1: SELECCIÓN DE CUARTEL**
- Usuario selecciona **Cuartel** de la lista disponible
- Sistema obtiene automáticamente **Variedad** y **Especie** del cuartel

### **PASO 2: SELECCIÓN DE LABOR**
- Sistema muestra **Labores** disponibles para esa **Especie**
- Usuario selecciona **Labor** específica

### **PASO 3: FORMULARIO DINÁMICO**
- Sistema genera formulario basado en **Labor-Especie**
- Usuario completa valores para cada atributo

### **PASO 4: GUARDAR PAUTA**
- Sistema crea pauta principal y detalles
- Usuario puede ver historial y crear más pautas

---

## 📊 **ENDPOINTS IMPLEMENTADOS (4 nuevos)**

### **1. Obtener Especie por Cuartel**
```http
GET /api/pautas/cuartel-especie/{cuartel_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Especie del cuartel obtenida exitosamente",
  "data": {
    "id_cuartel": 1,
    "nombre_cuartel": "Cuartel Norte",
    "id_variedad": 1,
    "nombre_variedad": "NECTARIN ROJO",
    "id_especie": 1,
    "nombre_especie": "NECTARIN",
    "caja_equivalente": 18.0
  }
}
```

### **2. Listar Labores por Especie**
```http
GET /api/pautas/labores-por-especie/{especie_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Labores de la especie obtenidas exitosamente",
  "data": {
    "labores": [
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

### **3. Listar Atributos por Labor-Especie**
```http
GET /api/pautas/atributos-por-labor-especie/{labor_id}/{especie_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Atributos de la combinación labor-especie obtenidos exitosamente",
  "data": {
    "atributos": [
      {
        "id": 1,
        "id_empresa": 1,
        "id_conteotipo": 1,
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "nombre_atributo": "PESO",
        "nombre_tipo_planta": "Tipo 2",
        "factor_productivo": 1.2,
        "descripcion_tipo_planta": "Planta de alta producción"
      },
      {
        "id": 2,
        "id_empresa": 1,
        "id_conteotipo": 1,
        "id_atributo": 2,
        "id_tipoplanta": null,
        "nombre_atributo": "FRUTOS",
        "nombre_tipo_planta": null,
        "factor_productivo": null,
        "descripcion_tipo_planta": null
      }
    ],
    "total": 2
  }
}
```

### **4. Generar Formulario Dinámico Completo**
```http
GET /api/pautas/formulario-dinamico/{labor_id}/{especie_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Formulario dinámico generado exitosamente",
  "data": {
    "labor_especie": {
      "nombre_labor": "RALEO",
      "nombre_especie": "NECTARIN",
      "caja_equivalente": 18.0
    },
    "atributos": [
      {
        "id": 1,
        "id_atributo": 1,
        "id_tipoplanta": "2",
        "nombre_atributo": "PESO",
        "nombre_tipo_planta": "Tipo 2",
        "factor_productivo": 1.2,
        "descripcion_tipo_planta": "Planta de alta producción"
      },
      {
        "id": 2,
        "id_atributo": 2,
        "id_tipoplanta": null,
        "nombre_atributo": "FRUTOS",
        "nombre_tipo_planta": null,
        "factor_productivo": null,
        "descripcion_tipo_planta": null
      }
    ],
    "total_atributos": 2
  }
}
```

---

## 🖥️ **IMPLEMENTACIÓN EN EL FRONTEND**

### **✅ Pantalla 1: Selección de Cuartel**
```
┌─────────────────────────────────────┐
│        CREAR NUEVA PAUTA            │
├─────────────────────────────────────┤
│ Paso 1: Seleccionar Cuartel          │
│                                     │
│ Cuartel: [Cuartel Norte ▼]          │
│                                     │
│ [SIGUIENTE]                         │
└─────────────────────────────────────┘
```

### **✅ Pantalla 2: Selección de Labor**
```
┌─────────────────────────────────────┐
│        CREAR NUEVA PAUTA            │
├─────────────────────────────────────┤
│ Paso 2: Seleccionar Labor           │
│                                     │
│ Cuartel: Cuartel Norte              │
│ Especie: NECTARIN                   │
│                                     │
│ Labor: [RALEO ▼]                    │
│                                     │
│ [SIGUIENTE]                         │
└─────────────────────────────────────┘
```

### **✅ Pantalla 3: Formulario Dinámico**
```
┌─────────────────────────────────────┐
│     FORMULARIO: RALEO - NECTARIN    │
├─────────────────────────────────────┤
│ Cuartel: Cuartel Norte              │
│ Especie: NECTARIN                   │
│ Labor: RALEO                        │
│                                     │
│ PESO (kg): [15.5    ]              │
│ Tipo Planta: [Tipo 2 ▼]            │
│                                     │
│ FRUTOS: [25    ]                    │
│ Tipo Planta: [Sin tipo ▼]          │
│                                     │
│ [GUARDAR PAUTA]                     │
└─────────────────────────────────────┘
```

### **✅ Pantalla 4: Confirmación**
```
┌─────────────────────────────────────┐
│        PAUTA CREADA                 │
├─────────────────────────────────────┤
│ ✅ Pauta PAU001 creada exitosamente │
│                                     │
│ Cuartel: Cuartel Norte              │
│ Especie: NECTARIN                   │
│ Labor: RALEO                        │
│ Temporada: 2024-2025                │
│                                     │
│ Detalles:                           │
│ • PESO: 15.5 kg (Tipo 2)           │
│ • FRUTOS: 25 (Sin tipo)             │
│                                     │
│ [CREAR OTRA PAUTA] [VER HISTORIAL]  │
└─────────────────────────────────────┘
```

---

## 🔧 **EJEMPLO DE IMPLEMENTACIÓN**

### **✅ JavaScript/React:**

```javascript
// 1. Obtener especie del cuartel seleccionado
const obtenerEspeciePorCuartel = async (cuartelId) => {
  try {
    const response = await fetch(`/api/pautas/cuartel-especie/${cuartelId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setEspecieInfo(data.data);
      setEspecieId(data.data.id_especie);
      return data.data;
    }
  } catch (error) {
    console.error('Error obteniendo especie del cuartel:', error);
  }
};

// 2. Cargar labores disponibles para la especie
const cargarLaboresPorEspecie = async (especieId) => {
  try {
    const response = await fetch(`/api/pautas/labores-por-especie/${especieId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setLaboresDisponibles(data.data.labores);
    }
  } catch (error) {
    console.error('Error cargando labores por especie:', error);
  }
};

// 3. Generar formulario dinámico
const generarFormularioDinamico = async (laborId, especieId) => {
  try {
    const response = await fetch(`/api/pautas/formulario-dinamico/${laborId}/${especieId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setFormularioData(data.data);
      setAtributosFormulario(data.data.atributos);
      return data.data;
    }
  } catch (error) {
    console.error('Error generando formulario dinámico:', error);
  }
};

// 4. Flujo completo de creación de pauta
const crearPautaCompleta = async () => {
  try {
    // Paso 1: Obtener especie del cuartel
    const especieInfo = await obtenerEspeciePorCuartel(cuartelId);
    
    // Paso 2: Cargar labores disponibles
    await cargarLaboresPorEspecie(especieInfo.id_especie);
    
    // Paso 3: Generar formulario cuando se seleccione labor
    if (laborId && especieInfo.id_especie) {
      await generarFormularioDinamico(laborId, especieInfo.id_especie);
    }
    
  } catch (error) {
    console.error('Error en flujo de creación de pauta:', error);
  }
};

// 5. Componente de selección de cuartel
const SeleccionarCuartel = () => {
  const [cuarteles, setCuarteles] = useState([]);
  const [cuartelSeleccionado, setCuartelSeleccionado] = useState(null);
  
  useEffect(() => {
    // Cargar lista de cuarteles disponibles
    cargarCuarteles();
  }, []);
  
  const handleCuartelChange = async (cuartelId) => {
    setCuartelSeleccionado(cuartelId);
    
    // Obtener especie del cuartel
    const especieInfo = await obtenerEspeciePorCuartel(cuartelId);
    
    // Cargar labores disponibles
    await cargarLaboresPorEspecie(especieInfo.id_especie);
  };
  
  return (
    <div>
      <h3>Paso 1: Seleccionar Cuartel</h3>
      <select onChange={(e) => handleCuartelChange(e.target.value)}>
        <option value="">Seleccionar Cuartel</option>
        {cuarteles.map(cuartel => (
          <option key={cuartel.id} value={cuartel.id}>
            {cuartel.nombre}
          </option>
        ))}
      </select>
    </div>
  );
};

// 6. Componente de selección de labor
const SeleccionarLabor = ({ especieId }) => {
  const [labores, setLabores] = useState([]);
  const [laborSeleccionada, setLaborSeleccionada] = useState(null);
  
  useEffect(() => {
    if (especieId) {
      cargarLaboresPorEspecie(especieId);
    }
  }, [especieId]);
  
  const handleLaborChange = async (laborId) => {
    setLaborSeleccionada(laborId);
    
    // Generar formulario dinámico
    await generarFormularioDinamico(laborId, especieId);
  };
  
  return (
    <div>
      <h3>Paso 2: Seleccionar Labor</h3>
      <select onChange={(e) => handleLaborChange(e.target.value)}>
        <option value="">Seleccionar Labor</option>
        {labores.map(labor => (
          <option key={labor.id} value={labor.id_labor}>
            {labor.nombre_labor}
          </option>
        ))}
      </select>
    </div>
  );
};

// 7. Componente de formulario dinámico
const FormularioDinamico = ({ atributos }) => {
  const [valores, setValores] = useState({});
  
  const handleValorChange = (atributoId, valor) => {
    setValores(prev => ({
      ...prev,
      [atributoId]: valor
    }));
  };
  
  return (
    <div>
      <h3>Paso 3: Completar Formulario</h3>
      {atributos.map(atributo => (
        <div key={atributo.id}>
          <label>{atributo.nombre_atributo}:</label>
          <input
            type="number"
            value={valores[atributo.id_atributo] || ''}
            onChange={(e) => handleValorChange(atributo.id_atributo, e.target.value)}
          />
          
          {atributo.nombre_tipo_planta && (
            <select>
              <option value="">Seleccionar Tipo</option>
              <option value={atributo.id_tipoplanta}>
                {atributo.nombre_tipo_planta}
              </option>
            </select>
          )}
        </div>
      ))}
      
      <button onClick={guardarPauta}>
        Guardar Pauta
      </button>
    </div>
  );
};
```

---

## 🎯 **CASOS DE USO PRÁCTICOS**

### **✅ CASO 1: RALEO DE NECTARIN**
1. **Usuario selecciona**: Cuartel "Cuartel Norte"
2. **Sistema obtiene**: Especie "NECTARIN" automáticamente
3. **Sistema muestra**: Labores disponibles para NECTARIN (RALEO, PODA, etc.)
4. **Usuario selecciona**: Labor "RALEO"
5. **Sistema genera**: Formulario con campos PESO, FRUTOS, CARGADORES
6. **Usuario completa**: Valores específicos
7. **Sistema guarda**: Pauta completa con todos los detalles

### **✅ CASO 2: PODA DE MANZANA**
1. **Usuario selecciona**: Cuartel "Cuartel Sur"
2. **Sistema obtiene**: Especie "MANZANA" automáticamente
3. **Sistema muestra**: Labores disponibles para MANZANA (PODA, CONTEO, etc.)
4. **Usuario selecciona**: Labor "PODA"
5. **Sistema genera**: Formulario con campos diferentes (RAMAS, HOJAS, etc.)
6. **Usuario completa**: Valores específicos para poda
7. **Sistema guarda**: Nueva pauta con configuración de poda

---

## 🔧 **CONFIGURACIÓN PREVIA NECESARIA**

### **ANTES DE USAR EL SISTEMA:**
1. **Configurar Labor-Especie**: ¿Qué combinaciones existen?
2. **Configurar Atributos**: ¿Qué se va a medir? (PESO, FRUTOS, etc.)
3. **Configurar Tipos de Planta**: ¿Qué tipos existen? (Tipo 1, Tipo 2, etc.)
4. **Configurar Pautas**: ¿Qué atributos se usan para cada labor-especie?

### **EJEMPLO DE CONFIGURACIÓN:**
```
RALEO + NECTARIN = [PESO, FRUTOS, CARGADORES]
PODA + MANZANA = [RAMAS, HOJAS, FLORES]
CONTEO + PERA = [UNIDADES, CALIDAD]
```

---

## 📊 **VENTAJAS DEL SISTEMA**

### **✅ PARA EL USUARIO:**
- **Flujo intuitivo**: Cuartel → Labor → Formulario
- **Formulario automático**: No necesita saber qué campos llenar
- **Configuración flexible**: Se adapta a diferentes labor-especie
- **Validación automática**: Solo muestra campos relevantes
- **Historial completo**: Puede ver todas sus pautas anteriores

### **✅ PARA EL ADMINISTRADOR:**
- **Configuración centralizada**: Define qué se mide en cada labor-especie
- **Flexibilidad**: Puede agregar/quitar atributos según necesidad
- **Trazabilidad**: Ve quién hizo qué pauta y cuándo
- **Reportes**: Puede generar estadísticas por labor-especie

---

## 🎯 **FLUJO DE NAVEGACIÓN**

### **PANTALLA PRINCIPAL:**
```
┌─────────────────────────────────────┐
│           SISTEMA DE PAUTAS         │
├─────────────────────────────────────┤
│ [NUEVA PAUTA] [HISTORIAL] [CONFIG]  │
│                                     │
│ Últimas Pautas:                     │
│ • PAU001 - RALEO NECTARIN (Hoy)     │
│ • PAU002 - PODA MANZANA (Ayer)      │
│ • PAU003 - CONTEO PERA (Ayer)       │
└─────────────────────────────────────┘
```

### **PANTALLA DE HISTORIAL:**
```
┌─────────────────────────────────────┐
│           HISTORIAL DE PAUTAS       │
├─────────────────────────────────────┤
│ Filtros: [Labor ▼] [Especie ▼] [Fecha] │
│                                     │
│ PAU001 | RALEO | NECTARIN | 25/08   │
│ PAU002 | PODA  | MANZANA  | 24/08   │
│ PAU003 | CONTEO| PERA     | 24/08   │
│                                     │
│ [VER DETALLES] [EDITAR] [ELIMINAR]  │
└─────────────────────────────────────┘
```

---

## 🎯 **RESUMEN DEL FLUJO**

1. **Usuario selecciona** cuartel
2. **Sistema obtiene** especie automáticamente
3. **Sistema muestra** labores disponibles para esa especie
4. **Usuario selecciona** labor
5. **Sistema genera** formulario automáticamente
6. **Usuario completa** los valores requeridos
7. **Sistema guarda** pauta y detalles
8. **Usuario puede** ver historial y crear más pautas

**El sistema es completamente dinámico y se adapta a la configuración previa, haciendo que el usuario solo tenga que seleccionar el contexto y completar los valores, sin preocuparse por qué campos llenar.**

---

## 📝 **RESUMEN DE ENDPOINTS**

**✅ ENDPOINTS IMPLEMENTADOS:**

### **Flujo de Creación de Pautas (4 endpoints):**
- `GET /api/pautas/cuartel-especie/{cuartel_id}` - Obtener especie del cuartel
- `GET /api/pautas/labores-por-especie/{especie_id}` - Listar labores por especie
- `GET /api/pautas/atributos-por-labor-especie/{labor_id}/{especie_id}` - Listar atributos por labor-especie
- `GET /api/pautas/formulario-dinamico/{labor_id}/{especie_id}` - Generar formulario dinámico completo

### **Gestión de Tablas Pivot (8 endpoints):**
- `GET /api/pautas/labor-especie` - Listar combinaciones labor-especie
- `POST /api/pautas/labor-especie` - Crear combinación labor-especie
- `PUT /api/pautas/labor-especie/{id}` - Actualizar combinación labor-especie
- `DELETE /api/pautas/labor-especie/{id}` - Eliminar combinación labor-especie
- `GET /api/pautas/atributo-especie` - Listar relaciones atributo-especie
- `POST /api/pautas/atributo-especie` - Crear relación atributo-especie
- `PUT /api/pautas/atributo-especie/{id}` - Actualizar relación atributo-especie
- `DELETE /api/pautas/atributo-especie/{id}` - Eliminar relación atributo-especie

### **Gestión de Pautas (8 endpoints):**
- `GET /api/pautas/pautas` - Listar pautas del usuario
- `POST /api/pautas/pautas` - Crear nueva pauta
- `GET /api/pautas/pautas/{id}` - Obtener pauta específica
- `PUT /api/pautas/pautas/{id}` - Actualizar pauta
- `DELETE /api/pautas/pautas/{id}` - Eliminar pauta
- `GET /api/pautas/pautas/{id}/detalles` - Listar detalles de pauta
- `POST /api/pautas/pautas/{id}/detalles` - Crear detalle de pauta
- `POST /api/pautas/pautas/{id}/detalles-masivo` - Crear múltiples detalles

**Total: 20 endpoints completos para el sistema de pautas.**

**El frontend puede proceder con la implementación del flujo completo de creación de pautas.**

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ FLUJO COMPLETO IMPLEMENTADO - LISTO PARA USO

---

## 🎯 **PRÓXIMOS PASOS**

1. **Probar endpoints** desde el frontend con token válido
2. **Implementar pantallas** del flujo completo (Cuartel → Labor → Formulario)
3. **Integrar** con las pantallas existentes de configuración
4. **Validar** que el flujo funcione correctamente

**¡El sistema de pautas está completamente implementado y listo para usar!** 🚀
