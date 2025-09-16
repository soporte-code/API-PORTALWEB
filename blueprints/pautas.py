from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint para pautas
pautas_bp = Blueprint('pautas', __name__)

# =============================================================================
# CONFIGURACIÓN DE PAUTAS (conteo_dim_configpauta)
# =============================================================================

@pautas_bp.route('/configuraciones', methods=['GET'])
@jwt_required()
def listar_configuraciones_pauta():
    """
    Listar todas las configuraciones de pauta
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primero verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'conteo_dim_configpauta'")
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de configuraciones de pauta no existe",
                "data": {
                    "configuraciones": [],
                    "total": 0
                }
            }), 200
        
        # Consulta básica primero para ver qué datos hay
        query_basica = """
            SELECT 
                cp.id,
                cp.id_empresa,
                cp.id_conteotipo,
                cp.id_atributo,
                cp.id_tipoplanta
            FROM conteo_dim_configpauta cp
            ORDER BY cp.id
        """
        
        cursor.execute(query_basica)
        configuraciones_basicas = cursor.fetchall()
        
        # Si no hay configuraciones básicas, retornar vacío
        if not configuraciones_basicas:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "No hay configuraciones de pauta en la base de datos",
                "data": {
                    "configuraciones": [],
                    "total": 0
                }
            }), 200
        
        # Ahora hacer la consulta completa con JOINs
        query_completa = """
            SELECT 
                cp.id,
                cp.id_empresa,
                cp.id_conteotipo,
                cp.id_atributo,
                cp.id_tipoplanta,
                a.nombre as nombre_atributo,
                le.id_labor,
                le.id_especie,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie,
                tp.nombre as nombre_tipo_planta
            FROM conteo_dim_configpauta cp
            LEFT JOIN conteo_dim_atributocultivo a ON cp.id_atributo = a.id
            LEFT JOIN conteo_pivot_labor_especie le ON cp.id_conteotipo = le.id
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            LEFT JOIN mapeo_dim_tipoplanta tp ON LPAD(cp.id_tipoplanta, 2, '0') = tp.id
            ORDER BY cp.id
        """
        
        cursor.execute(query_completa)
        configuraciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Configuraciones de pauta obtenidas exitosamente",
            "data": {
                "configuraciones": configuraciones,
                "total": len(configuraciones)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo configuraciones de pauta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/configuraciones-agrupadas', methods=['GET'])
@jwt_required()
def listar_configuraciones_agrupadas():
    """
    Listar configuraciones de pauta agrupadas por tipo de conteo (labor-especie)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primero verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'conteo_dim_configpauta'")
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de configuraciones de pauta no existe",
                "data": {
                    "tipos_conteo": [],
                    "total_tipos_conteo": 0,
                    "total_configuraciones": 0
                }
            }), 200
        
        # Consulta para obtener configuraciones agrupadas por tipo de conteo
        query = """
            SELECT 
                cp.id_conteotipo,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie,
                COUNT(cp.id) as total_configuraciones,
                GROUP_CONCAT(
                    CONCAT(
                        cp.id, '|',
                        cp.id_empresa, '|',
                        cp.id_conteotipo, '|',
                        cp.id_atributo, '|',
                        cp.id_tipoplanta, '|',
                        a.nombre, '|',
                        COALESCE(tp.nombre, 'Sin tipo')
                    ) SEPARATOR '||'
                ) as configuraciones_raw
            FROM conteo_dim_configpauta cp
            LEFT JOIN conteo_pivot_labor_especie le ON cp.id_conteotipo = le.id
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            LEFT JOIN conteo_dim_atributocultivo a ON cp.id_atributo = a.id
            LEFT JOIN mapeo_dim_tipoplanta tp ON LPAD(cp.id_tipoplanta, 2, '0') = tp.id
            GROUP BY cp.id_conteotipo, l.nombre, e.nombre
            ORDER BY l.nombre, e.nombre
        """
        
        cursor.execute(query)
        grupos = cursor.fetchall()
        
        # Procesar los resultados
        tipos_conteo = []
        total_configuraciones = 0
        
        for grupo in grupos:
            configuraciones = []
            
            if grupo['configuraciones_raw']:
                # Parsear las configuraciones del GROUP_CONCAT
                configuraciones_raw = grupo['configuraciones_raw'].split('||')
                
                for config_raw in configuraciones_raw:
                    if config_raw:
                        partes = config_raw.split('|')
                        if len(partes) >= 7:
                            configuraciones.append({
                                'id': int(partes[0]),
                                'id_empresa': int(partes[1]),
                                'id_conteotipo': int(partes[2]),
                                'id_atributo': int(partes[3]),
                                'id_tipoplanta': partes[4] if partes[4] else None,
                                'nombre_atributo': partes[5],
                                'nombre_tipo_planta': partes[6]
                            })
            
            tipos_conteo.append({
                'id_conteotipo': grupo['id_conteotipo'],
                'nombre_labor': grupo['nombre_labor'],
                'nombre_especie': grupo['nombre_especie'],
                'total_configuraciones': grupo['total_configuraciones'],
                'configuraciones': configuraciones
            })
            
            total_configuraciones += grupo['total_configuraciones']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Configuraciones agrupadas obtenidas exitosamente",
            "data": {
                "tipos_conteo": tipos_conteo,
                "total_tipos_conteo": len(tipos_conteo),
                "total_configuraciones": total_configuraciones
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo configuraciones agrupadas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# =============================================================================
# GESTIÓN DE ATRIBUTOS DE CULTIVO (conteo_dim_atributocultivo)
# =============================================================================

@pautas_bp.route('/atributos-cultivo', methods=['GET'])
@jwt_required()
def listar_atributos_cultivo():
    """
    Listar todos los atributos de cultivo
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                nombre
            FROM conteo_dim_atributocultivo
            ORDER BY nombre
        """
        
        cursor.execute(query)
        atributos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributos de cultivo obtenidos exitosamente",
            "data": {
                "atributos": atributos,
                "total": len(atributos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos de cultivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/atributos-cultivo', methods=['POST'])
@jwt_required()
def crear_atributo_cultivo():
    """
    Crear un nuevo atributo de cultivo
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if 'nombre' not in data:
            return jsonify({
                "success": False,
                "message": "Campo requerido: nombre"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insertar nuevo atributo
        insert_query = """
            INSERT INTO conteo_dim_atributocultivo (nombre) 
            VALUES (%s)
        """
        
        cursor.execute(insert_query, (data['nombre'],))
        atributo_id = cursor.lastrowid
        
        # Obtener el atributo creado
        select_query = """
            SELECT id, nombre
            FROM conteo_dim_atributocultivo
            WHERE id = %s
        """
        
        cursor.execute(select_query, (atributo_id,))
        atributo_creado = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributo de cultivo creado exitosamente",
            "data": atributo_creado
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando atributo de cultivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# =============================================================================
# GESTIÓN DE LABORES DE CONTEO (conteo_dim_laborconteo)
# =============================================================================

@pautas_bp.route('/labores-conteo', methods=['GET'])
@jwt_required()
def listar_labores_conteo():
    """
    Listar todas las labores de conteo
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                nombre
            FROM conteo_dim_laborconteo
            ORDER BY nombre
        """
        
        cursor.execute(query)
        labores = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Labores de conteo obtenidas exitosamente",
            "data": {
                "labores": labores,
                "total": len(labores)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo labores de conteo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/labores-conteo', methods=['POST'])
@jwt_required()
def crear_labor_conteo():
    """
    Crear una nueva labor de conteo
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if 'nombre' not in data:
            return jsonify({
                "success": False,
                "message": "Campo requerido: nombre"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insertar nueva labor
        insert_query = """
            INSERT INTO conteo_dim_laborconteo (nombre) 
            VALUES (%s)
        """
        
        cursor.execute(insert_query, (data['nombre'],))
        labor_id = cursor.lastrowid
        
        # Obtener la labor creada
        select_query = """
            SELECT id, nombre
            FROM conteo_dim_laborconteo
            WHERE id = %s
        """
        
        cursor.execute(select_query, (labor_id,))
        labor_creada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Labor de conteo creada exitosamente",
            "data": labor_creada
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando labor de conteo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# =============================================================================
# LABOR-ESPECIE-ATRIBUTO
# =============================================================================

@pautas_bp.route('/labor-especie', methods=['GET'])
@jwt_required()
def listar_labor_especie():
    """
    Listar todas las combinaciones labor-especie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                le.id,
                le.id_labor,
                le.id_especie,
                le.id_estado,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie,
                e.caja_equivalente
            FROM conteo_pivot_labor_especie le
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            ORDER BY l.nombre, e.nombre
        """
        
        cursor.execute(query)
        labor_especies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Combinaciones labor-especie obtenidas exitosamente",
            "data": {
                "labor_especies": labor_especies,
                "total": len(labor_especies)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo labor-especie: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/tipos-planta', methods=['GET'])
@jwt_required()
def listar_tipos_planta():
    """
    Listar todos los tipos de planta disponibles
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                nombre,
                factor_productivo,
                id_empresa,
                descripcion
            FROM mapeo_dim_tipoplanta
            ORDER BY nombre
        """
        
        cursor.execute(query)
        tipos_planta = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Tipos de planta obtenidos exitosamente",
            "data": {
                "tipos_planta": tipos_planta,
                "total": len(tipos_planta)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de planta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# =============================================================================
# GENERACIÓN DE FORMULARIO DINÁMICO
# =============================================================================

@pautas_bp.route('/formulario/<int:labor_id>/<int:especie_id>', methods=['GET'])
@jwt_required()
def generar_formulario_dinamico(labor_id, especie_id):
    """
    Generar formulario dinámico basado en labor y especie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la combinación labor-especie existe
        labor_especie_query = """
            SELECT 
                le.id,
                le.id_labor,
                le.id_especie,
                le.id_estado,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie
            FROM conteo_pivot_labor_especie le
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            WHERE le.id_labor = %s AND le.id_especie = %s
        """
        
        cursor.execute(labor_especie_query, (labor_id, especie_id))
        labor_especie = cursor.fetchone()
        
        if not labor_especie:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Combinación labor-especie no encontrada"
            }), 404
        
        # Obtener configuración de pauta para esta combinación
        configuracion_query = """
            SELECT 
                cp.id,
                cp.id_atributo,
                cp.id_tipoplanta,
                a.nombre as nombre_atributo,
                tp.nombre as nombre_tipo_planta
            FROM conteo_dim_configpauta cp
            LEFT JOIN conteo_dim_atributocultivo a ON cp.id_atributo = a.id
            LEFT JOIN mapeo_dim_tipoplanta tp ON LPAD(cp.id_tipoplanta, 2, '0') = tp.id
            WHERE cp.id_conteotipo = %s
            ORDER BY a.nombre
        """
        
        cursor.execute(configuracion_query, (labor_especie['id'],))
        configuraciones = cursor.fetchall()
        
        # Obtener tipos de planta disponibles
        tipos_planta_query = """
            SELECT 
                id,
                nombre,
                factor_productivo,
                id_empresa,
                descripcion
            FROM mapeo_dim_tipoplanta
            ORDER BY nombre
        """
        
        cursor.execute(tipos_planta_query)
        tipos_planta = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Formulario generado exitosamente",
            "data": {
                "labor_especie": labor_especie,
                "configuraciones": configuraciones,
                "tipos_planta": tipos_planta,
                "total_atributos": len(configuraciones)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando formulario para labor {labor_id}, especie {especie_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# =============================================================================
# GESTIÓN DE PAUTAS (conteo_fact_pauta)
# =============================================================================

@pautas_bp.route('/pautas', methods=['GET'])
@jwt_required()
def listar_pautas():
    """
    Listar todas las pautas del usuario autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.id,
                p.id_conteotipo,
                p.id_usuario,
                p.id_temporada,
                p.fecha,
                p.hora_registro,
                p.id_cuartel,
                t.temporada as nombre_temporada,
                c.nombre as nombre_cuartel,
                le.id_labor,
                le.id_especie,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie
            FROM conteo_fact_pauta p
            LEFT JOIN general_dim_temporada t ON p.id_temporada = t.id
            LEFT JOIN general_dim_cuartel c ON p.id_cuartel = c.id
            LEFT JOIN conteo_pivot_labor_especie le ON p.id_conteotipo = le.id
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            WHERE p.id_usuario = %s
            ORDER BY p.fecha DESC, p.hora_registro DESC
        """
        
        cursor.execute(query, (user_id,))
        pautas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Pautas obtenidas exitosamente",
            "data": {
                "pautas": pautas,
                "total": len(pautas)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pautas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/pautas', methods=['POST'])
@jwt_required()
def crear_pauta():
    """
    Crear una nueva pauta
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_conteotipo', 'id_temporada', 'id_cuartel']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido: {campo}"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insertar nueva pauta
        insert_query = """
            INSERT INTO conteo_fact_pauta 
            (id_conteotipo, id_usuario, id_temporada, fecha, hora_registro, id_cuartel) 
            VALUES (%s, %s, %s, CURDATE(), CURTIME(), %s)
        """
        
        cursor.execute(insert_query, (
            data['id_conteotipo'],
            user_id,
            data['id_temporada'],
            data['id_cuartel']
        ))
        
        pauta_id = cursor.lastrowid
        
        # Obtener la pauta creada
        select_query = """
            SELECT 
                p.id,
                p.id_conteotipo,
                p.id_usuario,
                p.id_temporada,
                p.fecha,
                p.hora_registro,
                p.id_cuartel,
                t.temporada as nombre_temporada,
                c.nombre as nombre_cuartel,
                le.id_labor,
                le.id_especie,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie
            FROM conteo_fact_pauta p
            LEFT JOIN general_dim_temporada t ON p.id_temporada = t.id
            LEFT JOIN general_dim_cuartel c ON p.id_cuartel = c.id
            LEFT JOIN conteo_pivot_labor_especie le ON p.id_conteotipo = le.id
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            WHERE p.id = %s
        """
        
        cursor.execute(select_query, (pauta_id,))
        pauta_creada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Pauta creada exitosamente",
            "data": pauta_creada
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando pauta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/pautas/<string:pauta_id>', methods=['GET'])
@jwt_required()
def obtener_pauta(pauta_id):
    """
    Obtener una pauta específica con sus detalles
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información de la pauta
        pauta_query = """
            SELECT 
                p.id,
                p.id_conteotipo,
                p.id_usuario,
                p.id_temporada,
                p.fecha,
                p.hora_registro,
                p.id_cuartel,
                t.temporada as nombre_temporada,
                c.nombre as nombre_cuartel,
                le.id_labor,
                le.id_especie,
                l.nombre as nombre_labor,
                e.nombre as nombre_especie
            FROM conteo_fact_pauta p
            LEFT JOIN general_dim_temporada t ON p.id_temporada = t.id
            LEFT JOIN general_dim_cuartel c ON p.id_cuartel = c.id
            LEFT JOIN conteo_pivot_labor_especie le ON p.id_conteotipo = le.id
            LEFT JOIN conteo_dim_laborconteo l ON le.id_labor = l.id
            LEFT JOIN general_dim_especie e ON le.id_especie = e.id
            WHERE p.id = %s AND p.id_usuario = %s
        """
        
        cursor.execute(pauta_query, (pauta_id, user_id))
        pauta = cursor.fetchone()
        
        if not pauta:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Pauta no encontrada"
            }), 404
        
        # Obtener detalles de la pauta
        detalles_query = """
            SELECT 
                dp.id,
                dp.id_pauta,
                dp.id_atributo,
                dp.id_tipoplanta,
                dp.valor_atributo,
                a.nombre as nombre_atributo,
                tp.nombre as nombre_tipo_planta
            FROM conteo_fact_detallepauta dp
            LEFT JOIN conteo_dim_atributocultivo a ON dp.id_atributo = a.id
            LEFT JOIN mapeo_dim_tipoplanta tp ON LPAD(dp.id_tipoplanta, 2, '0') = tp.id
            WHERE dp.id_pauta = %s
            ORDER BY a.nombre
        """
        
        cursor.execute(detalles_query, (pauta_id,))
        detalles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Pauta obtenida exitosamente",
            "data": {
                "pauta": pauta,
                "detalles": detalles,
                "total_detalles": len(detalles)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pauta {pauta_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/pautas/<string:pauta_id>/detalles-masivo', methods=['POST'])
@jwt_required()
def crear_detalles_masivo(pauta_id):
    """
    Crear múltiples detalles de pauta de una vez
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar que se proporcionaron detalles
        if 'detalles' not in data or not isinstance(data['detalles'], list):
            return jsonify({
                "success": False,
                "message": "Campo requerido: detalles (array)"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la pauta pertenece al usuario
        verificar_pauta_query = """
            SELECT id FROM conteo_fact_pauta 
            WHERE id = %s AND id_usuario = %s
        """
        cursor.execute(verificar_pauta_query, (pauta_id, user_id))
        pauta_existe = cursor.fetchone()
        
        if not pauta_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Pauta no encontrada o sin permisos"
            }), 404
        
        detalles_creados = []
        
        # Insertar cada detalle
        for detalle in data['detalles']:
            # Validar campos requeridos para cada detalle
            if 'id_atributo' not in detalle or 'valor_atributo' not in detalle:
                continue  # Saltar detalles inválidos
            
            insert_query = """
                INSERT INTO conteo_fact_detallepauta 
                (id_pauta, id_atributo, id_tipoplanta, valor_atributo) 
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                pauta_id,
                detalle['id_atributo'],
                detalle.get('id_tipoplanta'),  # Opcional
                detalle['valor_atributo']
            ))
            
            detalle_id = cursor.lastrowid
            
            # Obtener el detalle creado
            select_query = """
                SELECT 
                    dp.id,
                    dp.id_pauta,
                    dp.id_atributo,
                    dp.id_tipoplanta,
                    dp.valor_atributo,
                    a.nombre as nombre_atributo,
                    tp.nombre as nombre_tipo_planta
                FROM conteo_fact_detallepauta dp
                LEFT JOIN conteo_dim_atributocultivo a ON dp.id_atributo = a.id
                LEFT JOIN mapeo_dim_tipoplanta tp ON LPAD(dp.id_tipoplanta, 2, '0') = tp.id
                WHERE dp.id = %s
            """
            
            cursor.execute(select_query, (detalle_id,))
            detalle_creado = cursor.fetchone()
            detalles_creados.append(detalle_creado)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"{len(detalles_creados)} detalles de pauta creados exitosamente",
            "data": {
                "detalles": detalles_creados,
                "total_creados": len(detalles_creados)
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando detalles masivos de pauta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500