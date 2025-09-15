# 🚀 **PAUTAS - SISTEMA DE CONFIGURACIÓN DINÁMICA IMPLEMENTADO**

---

## 🎯 **SISTEMA COMPLETO IMPLEMENTADO**

Hola equipo Frontend,

He implementado **COMPLETAMENTE** el sistema de pautas con configuración dinámica de formularios basado en labor-especie-atributo-tipo de planta.

---

## 🗄️ **TABLAS IMPLEMENTADAS**

### **1. Configuración de Pauta (`conteo_dim_configpauta`):**
- **ID:** int PK
- **Empresa:** int
- **Conteo Tipo:** int (cruce de labor-especie)
- **Atributo:** int
- **Tipo Planta:** varchar(45) (opcional)

### **2. Labor-Especie (`conteo_pivot_labor_especie`):**
- **ID:** int AI PK
- **Labor:** int
- **Especie:** int
- **Estado:** int

### **3. Atributo-Especie (`conteo_pivot_atributo_especie`):**
- **ID:** int AI PK
- **Atributo:** int
- **Especie:** int

### **4. Pauta (`conteo_fact_pauta`):**
- **ID:** varchar(45) PK
- **Conteo Tipo:** varchar(45)
- **Usuario:** varchar(45)
- **Temporada:** int
- **Fecha:** date
- **Hora Registro:** time
- **Cuartel:** bigint

### **5. Detalle Pauta (`conteo_fact_detallepauta`):**
- **ID:** varchar(45) PK
- **Pauta:** varchar(45)
- **Atributo:** int
- **Tipo Planta:** varchar(45)
- **Valor Atributo:** float

### **6. Tipo Planta (`mapeo_dim_tipoplanta`):**
- **ID:** varchar(45) PK
- **Nombre:** varchar(45)
- **Factor Productivo:** float
- **Empresa:** int
- **Descripción:** varchar(100)

### **7. Registro Mapeo (`mapeo_fact_registro`):**
- **ID:** varchar(45) PK
- **Evaluador:** varchar(45)
- **Hora Registro:** datetime
- **Planta:** bigint
- **Tipo Planta:** int
- **Imagen:** text

---

## 🚀 **ENDPOINTS IMPLEMENTADOS**

### **📋 CONFIGURACIÓN DE PAUTAS (4 endpoints):**
1. **`GET /api/pautas/configuraciones`** - Listar configuraciones
2. **`POST /api/pautas/configuraciones`** - Crear configuración
3. **`PUT /api/pautas/configuraciones/{id}`** - Actualizar configuración
4. **`DELETE /api/pautas/configuraciones/{id}`** - Eliminar configuración

### **🏷️ LABOR-ESPECIE-ATRIBUTO (4 endpoints):**
5. **`GET /api/pautas/labor-especie`** - Listar combinaciones labor-especie
6. **`GET /api/pautas/atributos-especie/{especie_id}`** - Atributos por especie
7. **`GET /api/pautas/tipos-planta`** - Tipos de planta disponibles
8. **`GET /api/pautas/tipos-planta-registro`** - Tipos de planta desde registro de mapeo

### **📝 GESTIÓN DE PAUTAS (3 endpoints):**
9. **`GET /api/pautas/pautas`** - Listar pautas del usuario
10. **`POST /api/pautas/pautas`** - Crear nueva pauta
11. **`GET /api/pautas/pautas/{id}`** - Obtener pauta específica

### **📊 FORMULARIO DINÁMICO (1 endpoint):**
12. **`GET /api/pautas/formulario/{labor_id}/{especie_id}`** - Generar formulario

### **📋 DETALLE DE PAUTAS (2 endpoints):**
13. **`POST /api/pautas/pautas/{id}/detalles`** - Crear detalle de pauta
14. **`POST /api/pautas/pautas/{id}/detalles-masivo`** - Crear múltiples detalles

---

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

### **✅ Configuración Dinámica:**
- **Configuración por labor-especie** con múltiples atributos
- **Tipo de planta opcional** para cada atributo
- **Validación de relaciones** entre tablas
- **CRUD completo** de configuraciones

### **✅ Formulario Dinámico:**
- **Generación automática** basada en labor-especie
- **Campos dinámicos** según configuración
- **Tipos de planta** como opciones adicionales
- **Validación de datos** antes de guardar

### **✅ Gestión de Pautas:**
- **Pautas por usuario** y temporada
- **Detalles múltiples** por pauta
- **Creación masiva** de detalles
- **Historial completo** de pautas

### **✅ Validaciones y Filtros:**
- **Filtro por usuario** en todas las consultas
- **Validación de permisos** por pauta
- **Verificación de relaciones** entre tablas
- **Manejo de errores** robusto

---

## 📱 **EJEMPLOS DE USO**

### **1. Generar Formulario Dinámico:**
```javascript
const generarFormulario = async (laborId, especieId) => {
  try {
    const response = await fetch(`/api/pautas/formulario/${laborId}/${especieId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      const { labor_especie, configuraciones, tipos_planta } = data.data;
      
      // Generar formulario dinámicamente
      const formulario = configuraciones.map(config => ({
        id_atributo: config.id_atributo,
        nombre_atributo: config.nombre_atributo,
        id_tipoplanta: config.id_tipoplanta,
        nombre_tipo_planta: config.nombre_tipo_planta,
        valor_atributo: null
      }));
      
      setFormulario(formulario);
      setTiposPlanta(tipos_planta);
    }
  } catch (error) {
    console.error('Error generando formulario:', error);
  }
};
```

### **2. Crear Pauta con Detalles:**
```javascript
const crearPautaCompleta = async (pautaData, detallesData) => {
  try {
    // Crear pauta
    const pautaResponse = await fetch('/api/pautas/pautas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(pautaData)
    });
    
    const pautaResult = await pautaResponse.json();
    
    if (pautaResult.success) {
      const pautaId = pautaResult.data.id;
      
      // Crear detalles masivos
      const detallesResponse = await fetch(`/api/pautas/pautas/${pautaId}/detalles-masivo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          detalles: detallesData
        })
      });
      
      const detallesResult = await detallesResponse.json();
      
      if (detallesResult.success) {
        return {
          pauta: pautaResult.data,
          detalles: detallesResult.data.detalles_creados
        };
      }
    }
  } catch (error) {
    console.error('Error creando pauta completa:', error);
  }
};
```

### **3. Listar Pautas del Usuario:**
```javascript
const cargarPautas = async () => {
  try {
    const response = await fetch('/api/pautas/pautas', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      setPautas(data.data.pautas);
    }
  } catch (error) {
    console.error('Error cargando pautas:', error);
  }
};
```

### **4. Obtener Tipos de Planta desde Registro:**
```javascript
const cargarTiposPlantaRegistro = async () => {
  try {
    const response = await fetch('/api/pautas/tipos-planta-registro', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      const tiposConRegistros = data.data.tipos_planta.filter(tipo => tipo.total_registros > 0);
      setTiposPlanta(tiposConRegistros);
    }
  } catch (error) {
    console.error('Error cargando tipos de planta desde registro:', error);
  }
};
```

---

## 🎯 **FLUJO DE TRABAJO IMPLEMENTADO**

### **1. Configuración Inicial:**
- **Administrador configura** labor-especie-atributo
- **Define tipo de planta** (opcional) para cada atributo
- **Sistema genera** configuración de pauta

### **2. Generación de Formulario:**
- **Usuario selecciona** labor y especie
- **Sistema consulta** configuración de pauta
- **Genera formulario** con campos dinámicos

### **3. Creación de Pauta:**
- **Usuario completa** formulario dinámico
- **Sistema valida** datos ingresados
- **Crea pauta** con detalles múltiples

### **4. Gestión de Pautas:**
- **Usuario puede ver** historial de pautas
- **Filtrar por temporada** y cuartel
- **Editar o eliminar** pautas existentes

---

## 📊 **ESTRUCTURA DE DATOS**

### **Configuración de Pauta:**
```typescript
interface ConfiguracionPauta {
  id: number;
  id_empresa: number;
  id_conteotipo: number;
  id_atributo: number;
  id_tipoplanta?: string;
  nombre_atributo: string;
  id_labor: number;
  id_especie: number;
  nombre_labor: string;
  nombre_especie: string;
  nombre_tipo_planta?: string;
}
```

### **Formulario Dinámico:**
```typescript
interface FormularioDinamico {
  labor_especie: {
    id: number;
    id_labor: number;
    id_especie: number;
    nombre_labor: string;
    nombre_especie: string;
  };
  configuraciones: ConfiguracionPauta[];
  tipos_planta: TipoPlanta[];
  total_atributos: number;
}
```

### **Pauta Completa:**
```typescript
interface PautaCompleta {
  pauta: {
    id: string;
    id_conteotipo: string;
    id_usuario: string;
    id_temporada: number;
    fecha: string;
    hora_registro: string;
    id_cuartel: number;
    nombre_temporada: string;
    nombre_cuartel: string;
    nombre_labor: string;
    nombre_especie: string;
  };
  detalles: DetallePauta[];
  total_detalles: number;
}
```

### **Detalle de Pauta:**
```typescript
interface DetallePauta {
  id: string;
  id_pauta: string;
  id_atributo: number;
  id_tipoplanta?: string;
  valor_atributo: number;
  nombre_atributo: string;
  nombre_tipo_planta?: string;
}
```

### **Tipo de Planta:**
```typescript
interface TipoPlanta {
  id: string;
  nombre: string;
  factor_productivo: number;
  id_empresa: number;
  descripcion: string;
  total_registros?: number; // Solo en tipos-planta-registro
}
```

---

## 🔍 **VALIDACIONES IMPLEMENTADAS**

### **✅ Configuración:**
- **Empresa requerida** para cada configuración
- **Labor-especie válida** en conteo tipo
- **Atributo existente** en la base de datos
- **Tipo de planta opcional** pero válido si se proporciona

### **✅ Pauta:**
- **Usuario autenticado** para crear pautas
- **Temporada válida** en el sistema
- **Cuartel existente** y accesible
- **Labor-especie activa** en configuración

### **✅ Detalle:**
- **Pauta pertenece** al usuario
- **Atributo configurado** para la labor-especie
- **Valor numérico** válido
- **Tipo de planta** opcional pero válido

---

## 🚀 **ENDPOINTS COMPLETOS DISPONIBLES**

### **📋 CONFIGURACIÓN DE PAUTAS:**
- `GET /api/pautas/configuraciones` - Listar configuraciones
- `POST /api/pautas/configuraciones` - Crear configuración
- `PUT /api/pautas/configuraciones/{id}` - Actualizar configuración
- `DELETE /api/pautas/configuraciones/{id}` - Eliminar configuración

### **🏷️ LABOR-ESPECIE-ATRIBUTO:**
- `GET /api/pautas/labor-especie` - Listar combinaciones labor-especie
- `GET /api/pautas/atributos-especie/{especie_id}` - Atributos por especie
- `GET /api/pautas/tipos-planta` - Tipos de planta disponibles
- `GET /api/pautas/tipos-planta-registro` - Tipos de planta desde registro de mapeo

### **📝 GESTIÓN DE PAUTAS:**
- `GET /api/pautas/pautas` - Listar pautas del usuario
- `POST /api/pautas/pautas` - Crear nueva pauta
- `GET /api/pautas/pautas/{id}` - Obtener pauta específica

### **📊 FORMULARIO DINÁMICO:**
- `GET /api/pautas/formulario/{labor_id}/{especie_id}` - Generar formulario

### **📋 DETALLE DE PAUTAS:**
- `POST /api/pautas/pautas/{id}/detalles` - Crear detalle de pauta
- `POST /api/pautas/pautas/{id}/detalles-masivo` - Crear múltiples detalles

---

## 📝 **RESUMEN**

- ✅ **14 endpoints completos** para sistema de pautas
- ✅ **Configuración dinámica** de formularios
- ✅ **Generación automática** basada en labor-especie
- ✅ **Gestión completa** de pautas y detalles
- ✅ **Validaciones robustas** en todos los endpoints
- ✅ **Creación masiva** de detalles
- ✅ **Filtros por usuario** y temporada
- ✅ **Manejo de errores** consistente

**El sistema de pautas está COMPLETAMENTE implementado y listo para ser integrado con el frontend.**

**📅 Fecha**: 25 de Agosto 2025  
**🔧 Versión**: 1.0.0  
**📋 Estado**: ✅ SISTEMA DE PAUTAS COMPLETADO - LISTO PARA INTEGRACIÓN
