from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint para estimaciones
estimaciones_bp = Blueprint('estimaciones', __name__)

# Utilidades locales para compatibilidad de esquemas
def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    try:
        cursor.execute("SHOW COLUMNS FROM %s LIKE %%s" % table_name, (column_name,))
        return cursor.fetchone() is not None
    except Exception:
        return False

def _first_existing_column(cursor, table_name: str, candidates: list) -> str:
    for candidate in candidates:
        if _column_exists(cursor, table_name, candidate):
            return candidate
    return None

@estimaciones_bp.route('/', methods=['GET'])
@jwt_required()
def listar_estimaciones():
    """
    Listar todas las estimaciones del usuario autenticado
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                c.nombre as nombre_cuartel,
                t.nombre as nombre_tipo_estimacion
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id_usuario = %s
            ORDER BY e.hora_registro DESC
        """
        
        cursor.execute(query, (user_id,))
        estimaciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimaciones obtenidas exitosamente",
            "data": {
                "estimaciones": estimaciones,
                "total": len(estimaciones)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estimaciones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/<string:estimacion_id>', methods=['GET'])
@jwt_required()
def obtener_estimacion(estimacion_id):
    """
    Obtener una estimación específica
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                c.nombre as nombre_cuartel,
                t.nombre as nombre_tipo_estimacion
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id = %s AND e.id_usuario = %s
        """
        
        cursor.execute(query, (estimacion_id, user_id))
        estimacion = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not estimacion:
            return jsonify({
                "success": False,
                "message": "Estimación no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Estimación obtenida exitosamente",
            "data": estimacion
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estimación {estimacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/', methods=['POST'])
@jwt_required()
def crear_estimacion():
    """
    Crear una nueva estimación
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_cuartel', 'id_tipoestimacion', 'embalaje_cajas', 'embalaje_kg', 'industria_kg']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido: {campo}"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel existe y pertenece al usuario
        cuartel_query = """
            SELECT c.id 
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE c.id = %s AND usu.id_usuario = %s
        """
        cursor.execute(cuartel_query, (data['id_cuartel'], user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar que el tipo de estimación existe
        tipo_query = "SELECT id FROM estimacion_dim_tipo WHERE id = %s"
        cursor.execute(tipo_query, (data['id_tipoestimacion'],))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Tipo de estimación no encontrado"
            }), 404
        
        # Insertar nueva estimación
        insert_query = """
            INSERT INTO estimacion_fact_registroadministradores 
            (id_usuario, id_cuartel, id_tipoestimacion, embalaje_cajas, embalaje_kg, industria_kg) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            user_id,
            data['id_cuartel'],
            data['id_tipoestimacion'],
            data['embalaje_cajas'],
            data['embalaje_kg'],
            data['industria_kg']
        ))
        
        estimacion_id = cursor.lastrowid
        
        # Obtener la estimación creada
        select_query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                c.nombre as nombre_cuartel,
                t.nombre as nombre_tipo_estimacion
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id = %s
        """
        
        cursor.execute(select_query, (estimacion_id,))
        estimacion_creada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimación creada exitosamente",
            "data": estimacion_creada
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando estimación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/<string:estimacion_id>', methods=['PUT'])
@jwt_required()
def actualizar_estimacion(estimacion_id):
    """
    Actualizar una estimación existente
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la estimación existe y pertenece al usuario
        check_query = """
            SELECT id FROM estimacion_fact_registroadministradores 
            WHERE id = %s AND id_usuario = %s
        """
        cursor.execute(check_query, (estimacion_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Estimación no encontrada"
            }), 404
        
        # Construir query de actualización dinámicamente
        campos_actualizables = ['id_cuartel', 'id_tipoestimacion', 'embalaje_cajas', 'embalaje_kg', 'industria_kg']
        campos_a_actualizar = []
        valores = []
        
        for campo in campos_actualizables:
            if campo in data:
                campos_a_actualizar.append(f"{campo} = %s")
                valores.append(data[campo])
        
        if not campos_a_actualizar:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "No se proporcionaron campos para actualizar"
            }), 400
        
        valores.append(estimacion_id)
        update_query = f"""
            UPDATE estimacion_fact_registroadministradores 
            SET {', '.join(campos_a_actualizar)}
            WHERE id = %s
        """
        
        cursor.execute(update_query, valores)
        
        # Obtener la estimación actualizada
        select_query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                c.nombre as nombre_cuartel,
                t.nombre as nombre_tipo_estimacion
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id = %s
        """
        
        cursor.execute(select_query, (estimacion_id,))
        estimacion_actualizada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimación actualizada exitosamente",
            "data": estimacion_actualizada
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando estimación {estimacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/<string:estimacion_id>', methods=['DELETE'])
@jwt_required()
def eliminar_estimacion(estimacion_id):
    """
    Eliminar una estimación
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la estimación existe y pertenece al usuario
        check_query = """
            SELECT id FROM estimacion_fact_registroadministradores 
            WHERE id = %s AND id_usuario = %s
        """
        cursor.execute(check_query, (estimacion_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Estimación no encontrada"
            }), 404
        
        # Eliminar estimación
        delete_query = "DELETE FROM estimacion_fact_registroadministradores WHERE id = %s"
        cursor.execute(delete_query, (estimacion_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimación eliminada exitosamente"
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando estimación {estimacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/tipos', methods=['GET'])
@jwt_required()
def listar_tipos_estimacion():
    """
    Listar todos los tipos de estimación disponibles
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                nombre
            FROM estimacion_dim_tipo
            ORDER BY nombre
        """
        
        cursor.execute(query)
        tipos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Tipos de estimación obtenidos exitosamente",
            "data": {
                "tipos": tipos,
                "total": len(tipos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de estimación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/tipos/<int:tipo_id>', methods=['GET'])
@jwt_required()
def obtener_tipo_estimacion(tipo_id):
    """
    Obtener un tipo de estimación específico
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                nombre
            FROM estimacion_dim_tipo
            WHERE id = %s
        """
        
        cursor.execute(query, (tipo_id,))
        tipo = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not tipo:
            return jsonify({
                "success": False,
                "message": "Tipo de estimación no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Tipo de estimación obtenido exitosamente",
            "data": tipo
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tipo de estimación {tipo_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/por-cuartel/<int:cuartel_id>', methods=['GET'])
@jwt_required()
def obtener_estimaciones_cuartel(cuartel_id):
    """
    Obtener todas las estimaciones de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar acceso al cuartel
        cuartel_query = """
            SELECT c.id 
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE c.id = %s AND usu.id_usuario = %s
        """
        cursor.execute(cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Obtener estimaciones del cuartel
        query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                c.nombre as nombre_cuartel,
                t.nombre as nombre_tipo_estimacion
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id_cuartel = %s
            ORDER BY e.hora_registro DESC
        """
        
        cursor.execute(query, (cuartel_id,))
        estimaciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimaciones del cuartel obtenidas exitosamente",
            "data": {
                "estimaciones": estimaciones,
                "total": len(estimaciones)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estimaciones del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/resumen', methods=['GET'])
@jwt_required()
def obtener_resumen_estimaciones():
    """
    Obtener resumen de estimaciones del usuario
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Resumen por tipo de estimación
        resumen_tipo_query = """
            SELECT 
                t.nombre as tipo_estimacion,
                COUNT(e.id) as total_estimaciones,
                SUM(e.embalaje_cajas) as total_cajas,
                SUM(e.embalaje_kg) as total_kg_embalaje,
                SUM(e.industria_kg) as total_kg_industria
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            WHERE e.id_usuario = %s
            GROUP BY t.id, t.nombre
            ORDER BY total_estimaciones DESC
        """
        
        cursor.execute(resumen_tipo_query, (user_id,))
        resumen_tipo = cursor.fetchall()
        
        # Resumen por cuartel
        resumen_cuartel_query = """
            SELECT 
                c.nombre as nombre_cuartel,
                COUNT(e.id) as total_estimaciones,
                SUM(e.embalaje_cajas) as total_cajas,
                SUM(e.embalaje_kg) as total_kg_embalaje,
                SUM(e.industria_kg) as total_kg_industria
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
            WHERE e.id_usuario = %s
            GROUP BY c.id, c.nombre
            ORDER BY total_estimaciones DESC
        """
        
        cursor.execute(resumen_cuartel_query, (user_id,))
        resumen_cuartel = cursor.fetchall()
        
        # Totales generales
        totales_query = """
            SELECT 
                COUNT(*) as total_estimaciones,
                SUM(embalaje_cajas) as total_cajas,
                SUM(embalaje_kg) as total_kg_embalaje,
                SUM(industria_kg) as total_kg_industria
            FROM estimacion_fact_registroadministradores
            WHERE id_usuario = %s
        """
        
        cursor.execute(totales_query, (user_id,))
        totales = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Resumen de estimaciones obtenido exitosamente",
            "data": {
                "resumen_por_tipo": resumen_tipo,
                "resumen_por_cuartel": resumen_cuartel,
                "totales_generales": totales
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de estimaciones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuarteles-disponibles', methods=['GET'])
@jwt_required()
def obtener_cuarteles_disponibles():
    """
    Obtener cuarteles disponibles para el usuario (para crear estimaciones)
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT DISTINCT
                c.id,
                c.nombre,
                c.descripcion,
                ce.nombre as nombre_ceco,
                s.nombre as nombre_sucursal,
                COUNT(e.id) as total_estimaciones
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            LEFT JOIN estimacion_fact_registroadministradores e ON c.id = e.id_cuartel AND e.id_usuario = %s
            WHERE usu.id_usuario = %s
            GROUP BY c.id, c.nombre, c.descripcion, ce.nombre, s.nombre
            ORDER BY c.nombre
        """
        
        cursor.execute(query, (user_id, user_id))
        cuarteles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Cuarteles disponibles obtenidos exitosamente",
            "data": {
                "cuarteles": cuarteles,
                "total": len(cuarteles)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cuarteles disponibles: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/historial-cuartel/<int:cuartel_id>', methods=['GET'])
@jwt_required()
def obtener_historial_cuartel(cuartel_id):
    """
    Obtener historial completo de estimaciones de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar acceso al cuartel
        cuartel_query = """
            SELECT c.id, c.nombre
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE c.id = %s AND usu.id_usuario = %s
        """
        cursor.execute(cuartel_query, (cuartel_id, user_id))
        cuartel_info = cursor.fetchone()
        
        if not cuartel_info:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Obtener historial de estimaciones del cuartel
        historial_query = """
            SELECT 
                e.id,
                e.id_usuario,
                e.id_cuartel,
                e.id_tipoestimacion,
                e.hora_registro,
                e.embalaje_cajas,
                e.embalaje_kg,
                e.industria_kg,
                t.nombre as nombre_tipo_estimacion,
                u.nombre as nombre_usuario,
                u.apellido as apellido_usuario
            FROM estimacion_fact_registroadministradores e
            LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
            LEFT JOIN usuario_dim_usuario u ON e.id_usuario = u.id
            WHERE e.id_cuartel = %s
            ORDER BY e.hora_registro DESC
        """
        
        cursor.execute(historial_query, (cuartel_id,))
        historial = cursor.fetchall()
        
        # Estadísticas del cuartel
        estadisticas_query = """
            SELECT 
                COUNT(*) as total_estimaciones,
                SUM(embalaje_cajas) as total_cajas,
                SUM(embalaje_kg) as total_kg_embalaje,
                SUM(industria_kg) as total_kg_industria,
                AVG(embalaje_cajas) as promedio_cajas,
                AVG(embalaje_kg) as promedio_kg_embalaje,
                AVG(industria_kg) as promedio_kg_industria,
                MIN(hora_registro) as primera_estimacion,
                MAX(hora_registro) as ultima_estimacion
            FROM estimacion_fact_registroadministradores
            WHERE id_cuartel = %s
        """
        
        cursor.execute(estadisticas_query, (cuartel_id,))
        estadisticas = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Historial del cuartel obtenido exitosamente",
            "data": {
                "cuartel": cuartel_info,
                "historial": historial,
                "estadisticas": estadisticas,
                "total_estimaciones": len(historial)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def obtener_dashboard_estimaciones():
    """
    Obtener dashboard completo con cuarteles agrupados por especie
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si las tablas de estimaciones existen
        cursor.execute("SHOW TABLES LIKE 'estimacion_fact_registroadministradores'")
        tabla_estimaciones_existe = cursor.fetchone()
        
        cursor.execute("SHOW TABLES LIKE 'estimacion_dim_tipo'")
        tabla_tipos_existe = cursor.fetchone()
        
        # Verificar si las tablas básicas existen
        cursor.execute("SHOW TABLES LIKE 'general_dim_especie'")
        tabla_especies_existe = cursor.fetchone()
        
        cursor.execute("SHOW TABLES LIKE 'general_dim_cuartel'")
        tabla_cuarteles_existe = cursor.fetchone()
        
        # Si las tablas básicas no existen, retornar mensaje claro
        if not tabla_especies_existe or not tabla_cuarteles_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "No hay datos disponibles. Las tablas de especies y cuarteles no existen en la base de datos.",
                "error": "TABLAS_NO_EXISTEN"
            }), 404
        
        # Obtener especies con sus cuarteles de la sucursal activa del usuario
        especies_query = """
            SELECT DISTINCT
                e.id as especie_id,
                e.nombre as especie_nombre,
                e.caja_equivalente
            FROM general_dim_especie e
            INNER JOIN general_dim_variedad v ON v.id_especie = e.id
            INNER JOIN general_dim_cuartel c ON c.id_variedad = v.id
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE usu.id_usuario = %s
            ORDER BY e.nombre
        """
        
        cursor.execute(especies_query, (user_id,))
        especies = cursor.fetchall()
        
        # Si no hay especies con cuarteles, retornar mensaje claro
        if not especies:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "No hay datos disponibles. No se encontraron especies con cuarteles asignados a tu sucursal.",
                "error": "SIN_DATOS_DISPONIBLES"
            }), 404
        
        # Procesar cada especie y obtener sus cuarteles
        especies_agrupadas = []
        for especie in especies:
            # Obtener cuarteles para esta especie
            cuarteles_query = """
                SELECT DISTINCT
                    c.id,
                    c.nombre,
                    ce.nombre as nombre_ceco,
                    s.nombre as nombre_sucursal,
                    CASE WHEN c.id_estado = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END as estado
                FROM general_dim_cuartel c
                INNER JOIN general_dim_variedad v ON c.id_variedad = v.id
                INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
                INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
                INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
                WHERE v.id_especie = %s AND usu.id_usuario = %s
                ORDER BY c.nombre
            """
            
            cursor.execute(cuarteles_query, (especie['especie_id'], user_id))
            cuarteles = cursor.fetchall()
            
            # Agregar estadísticas de estimaciones a cada cuartel si las tablas existen
            cuarteles_con_stats = []
            for cuartel in cuarteles:
                cuartel_data = {
                    "id": cuartel['id'],
                    "nombre": cuartel['nombre'],
                    "descripcion": "",  # Campo no disponible en la tabla
                    "nombre_ceco": cuartel['nombre_ceco'],
                    "nombre_sucursal": cuartel['nombre_sucursal'],
                    "estado": cuartel['estado'],
                    "total_estimaciones": 0,
                    "total_cajas": 0,
                    "total_kg_embalaje": 0,
                    "total_kg_industria": 0,
                    "ultima_estimacion": None
                }
                
                # Si las tablas de estimaciones existen, agregar estadísticas
                if tabla_estimaciones_existe and tabla_tipos_existe:
                    estadisticas_query = """
                        SELECT 
                            COUNT(*) as total_estimaciones,
                            COALESCE(SUM(embalaje_cajas), 0) as total_cajas,
                            COALESCE(SUM(embalaje_kg), 0) as total_kg_embalaje,
                            COALESCE(SUM(industria_kg), 0) as total_kg_industria,
                            MAX(hora_registro) as ultima_estimacion
                        FROM estimacion_fact_registroadministradores
                        WHERE id_cuartel = %s AND id_usuario = %s
                    """
                    
                    cursor.execute(estadisticas_query, (cuartel['id'], user_id))
                    stats = cursor.fetchone()
                    
                    if stats:
                        cuartel_data['total_estimaciones'] = stats['total_estimaciones']
                        cuartel_data['total_cajas'] = stats['total_cajas']
                        cuartel_data['total_kg_embalaje'] = stats['total_kg_embalaje']
                        cuartel_data['total_kg_industria'] = stats['total_kg_industria']
                        cuartel_data['ultima_estimacion'] = stats['ultima_estimacion']
                
                cuarteles_con_stats.append(cuartel_data)
            
            especies_agrupadas.append({
                "especie_id": especie['especie_id'],
                "especie_nombre": especie['especie_nombre'],
                "caja_equivalente": especie['caja_equivalente'],
                "total_cuarteles": len(cuarteles_con_stats),
                "cuarteles": cuarteles_con_stats
            })
        
        # Obtener tipos de estimación y totales si las tablas existen
        if tabla_estimaciones_existe and tabla_tipos_existe:
            # Obtener tipos de estimación
            tipos_query = """
                SELECT 
                    id,
                    nombre
                FROM estimacion_dim_tipo
                ORDER BY nombre
            """
            
            cursor.execute(tipos_query)
            tipos = cursor.fetchall()
            
            # Totales generales
            totales_query = """
                SELECT 
                    COUNT(*) as total_estimaciones,
                    COALESCE(SUM(embalaje_cajas), 0) as total_cajas,
                    COALESCE(SUM(embalaje_kg), 0) as total_kg_embalaje,
                    COALESCE(SUM(industria_kg), 0) as total_kg_industria
                FROM estimacion_fact_registroadministradores
                WHERE id_usuario = %s
            """
            
            cursor.execute(totales_query, (user_id,))
            totales = cursor.fetchone()
        else:
            # Si las tablas no existen, usar datos básicos
            tipos = []
            totales = {
                "total_estimaciones": 0,
                "total_cajas": 0,
                "total_kg_embalaje": 0,
                "total_kg_industria": 0
            }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Dashboard de estimaciones obtenido exitosamente",
            "data": {
                "especies_agrupadas": especies_agrupadas,
                "tipos_estimacion": tipos,
                "totales_generales": totales,
                "total_especies": len(especies_agrupadas),
                "tablas_existen": tabla_estimaciones_existe is not None and tabla_tipos_existe is not None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard de estimaciones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# ============================================================================
# VISTA DETALLADA DE CUARTELES
# ============================================================================

@estimaciones_bp.route('/debug-columnas/<string:tabla>', methods=['GET'])
@jwt_required()
def debug_columnas_tabla(tabla):
    """
    Endpoint temporal para debuggear columnas de una tabla
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todas las columnas de la tabla
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        columnas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Columnas de {tabla} obtenidas",
            "data": {
                "tabla": tabla,
                "columnas": [col['Field'] for col in columnas]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error obteniendo columnas de {tabla}",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/informacion-general', methods=['GET'])
@jwt_required()
def obtener_informacion_general_cuartel(cuartel_id):
    """
    Obtener información general detallada de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Obtener información detallada del cuartel (versión simplificada)
        info_query = """
            SELECT 
                c.id,
                c.nombre,
                v.nombre as variedad,
                c.superficie as superficie_productiva,
                c.ano_plantacion as año_plantacion,
                NULL as plantas_ha_teoricas,
                c.id_portainjerto as portainjerto,
                CASE 
                    WHEN c.id_estadoproductivo = 1 THEN 'Productivo'
                    WHEN c.id_estadoproductivo = 2 THEN 'En Desarrollo'
                    WHEN c.id_estadoproductivo = 3 THEN 'No Productivo'
                    ELSE 'Desconocido'
                END as estado_productivo,
                c.subdivisionesplanta as numero_brazos_ejes,
                ce.nombre as nombre_ceco,
                s.nombre as nombre_sucursal
            FROM general_dim_cuartel c
            INNER JOIN general_dim_variedad v ON c.id_variedad = v.id
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            WHERE c.id = %s
        """

        cursor.execute(info_query, (cuartel_id,))
        cuartel_info = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not cuartel_info:
            return jsonify({
                "success": False,
                "message": "Información del cuartel no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Información general del cuartel obtenida exitosamente",
            "data": {
                "cuartel": cuartel_info
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo información general del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/estimaciones', methods=['GET'])
@jwt_required()
def obtener_estimaciones_cuartel_detalle(cuartel_id):
    """
    Obtener estimaciones detalladas de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si la tabla de estimaciones existe
        cursor.execute("SHOW TABLES LIKE 'estimacion_fact_registroadministradores'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de estimaciones no existe aún",
                "data": {
                    "estimaciones": [],
                    "total": 0
                }
            }), 200
        
        # Obtener estimaciones del cuartel
        # Resolver tipo de estimación de forma resiliente si la dimensión no existe
        cursor.execute("SHOW TABLES LIKE 'estimacion_dim_tipo'")
        tabla_dim_tipo = cursor.fetchone()
        if tabla_dim_tipo:
            estimaciones_query = """
                SELECT 
                    e.id,
                    t.nombre as tipo_estimacion,
                    e.embalaje_cajas as estimacion_cajas_ha,
                    e.embalaje_cajas as estimacion,
                    DATE(e.hora_registro) as fecha,
                    u.nombre as usuario
                FROM estimacion_fact_registroadministradores e
                LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
                LEFT JOIN general_dim_usuario u ON e.id_usuario = u.id
                WHERE e.id_cuartel = %s AND e.id_usuario = %s
                ORDER BY e.hora_registro DESC
                LIMIT 50
            """
        else:
            estimaciones_query = """
                SELECT 
                    e.id,
                    CAST(e.id_tipoestimacion AS CHAR) as tipo_estimacion,
                    e.embalaje_cajas as estimacion_cajas_ha,
                    e.embalaje_cajas as estimacion,
                    DATE(e.hora_registro) as fecha,
                    u.nombre as usuario
                FROM estimacion_fact_registroadministradores e
                LEFT JOIN general_dim_usuario u ON e.id_usuario = u.id
                WHERE e.id_cuartel = %s AND e.id_usuario = %s
                ORDER BY e.hora_registro DESC
                LIMIT 50
            """
        
        cursor.execute(estimaciones_query, (cuartel_id, user_id))
        estimaciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Estimaciones del cuartel obtenidas exitosamente",
            "data": {
                "estimaciones": estimaciones,
                "total": len(estimaciones)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estimaciones del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/pautas', methods=['GET'])
@jwt_required()
def obtener_pautas_cuartel(cuartel_id):
    """
    Obtener pautas de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si la tabla de pautas existe
        cursor.execute("SHOW TABLES LIKE 'conteo_fact_pauta'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de pautas no existe aún",
                "data": {
                    "pautas": [],
                    "total": 0
                }
            }), 200
        
        # Obtener pautas del cuartel
        # Resolver columnas de estado/usuario en pauta
        estado_col = _first_existing_column(cursor, 'conteo_fact_pauta', ['id_estado', 'estado'])
        usuario_col = _first_existing_column(cursor, 'conteo_fact_pauta', ['id_usuario', 'usuario', 'id_evaluador'])
        where_usuario = f"AND p.{usuario_col} = %s" if usuario_col else ""
        select_estado = (
            f"CASE WHEN p.{estado_col} = 1 THEN 'Completada' WHEN p.{estado_col} = 0 THEN 'Pendiente' ELSE 'Desconocida' END"
            if estado_col else "'Desconocida'"
        )
        join_usuario = (
            f"LEFT JOIN general_dim_usuario u ON p.{usuario_col} = u.id" if usuario_col else "LEFT JOIN general_dim_usuario u ON 1=0"
        )
        pautas_query = f"""
            SELECT 
                p.id,
                DATE(p.fecha) as fecha_inicio,
                l.nombre as labor,
                {select_estado} as estado,
                u.nombre as usuario
            FROM conteo_fact_pauta p
            LEFT JOIN conteo_dim_laborconteo l ON p.id_labor = l.id
            {join_usuario}
            WHERE p.id_cuartel = %s {where_usuario}
            ORDER BY p.fecha DESC
            LIMIT 50
        """
        
        params = [cuartel_id]
        if usuario_col:
            params.append(user_id)
        cursor.execute(pautas_query, tuple(params))
        pautas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Pautas del cuartel obtenidas exitosamente",
            "data": {
                "pautas": pautas,
                "total": len(pautas)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pautas del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/rendimiento-packing', methods=['GET'])
@jwt_required()
def obtener_rendimiento_packing_cuartel(cuartel_id):
    """
    Obtener rendimiento packing de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si la tabla de rendimiento existe
        cursor.execute("SHOW TABLES LIKE 'estimacion_fact_rendimientocuartel'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de rendimiento packing no existe aún",
                "data": {
                    "rendimientos": [],
                    "total": 0
                }
            }), 200
        
        # Obtener rendimientos del cuartel
        rendimientos_query = """
            SELECT 
                r.id,
                r.rendimiento,
                DATE(r.fecha) as fecha,
                u.nombre as usuario
            FROM estimacion_fact_rendimientocuartel r
            LEFT JOIN general_dim_usuario u ON r.id_usuario = u.id
            WHERE r.id_cuartel = %s AND r.id_usuario = %s
            ORDER BY r.fecha DESC
            LIMIT 50
        """
        
        cursor.execute(rendimientos_query, (cuartel_id, user_id))
        rendimientos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Rendimiento packing del cuartel obtenido exitosamente",
            "data": {
                "rendimientos": rendimientos,
                "total": len(rendimientos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo rendimiento packing del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/mapeos', methods=['GET'])
@jwt_required()
def obtener_mapeos_cuartel(cuartel_id):
    """
    Obtener mapeos de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si la tabla de mapeo existe
        cursor.execute("SHOW TABLES LIKE 'mapeo_fact_registromapeo'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de mapeos no existe aún",
                "data": {
                    "mapeos": [],
                    "total": 0
                }
            }), 200
        
        # Obtener mapeos del cuartel con conteo real de plantas por tipo
        mapeos_query = """
            SELECT 
                rm.id,
                DATE(rm.fecha_inicio) as fecha,
                COUNT(CASE WHEN r.id_tipoplanta = 7 THEN 1 END) as plantas_7,
                COUNT(CASE WHEN r.id_tipoplanta = 5 THEN 1 END) as plantas_5,
                COUNT(CASE WHEN r.id_tipoplanta = 3 THEN 1 END) as plantas_3,
                COUNT(r.id) as total_plantas,
                u.nombre as usuario
            FROM mapeo_fact_registromapeo rm
            LEFT JOIN mapeo_fact_registro r ON rm.id = r.id_mapeo
            LEFT JOIN general_dim_usuario u ON r.id_evaluador = u.id
            WHERE rm.id_cuartel = %s
            GROUP BY rm.id, rm.fecha_inicio, u.nombre
            ORDER BY rm.fecha_inicio DESC
            LIMIT 50
        """
        
        cursor.execute(mapeos_query, (cuartel_id,))
        mapeos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Mapeos del cuartel obtenidos exitosamente",
            "data": {
                "mapeos": mapeos,
                "total": len(mapeos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo mapeos del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/frutos-ramilla-historico', methods=['GET'])
@jwt_required()
def obtener_frutos_ramilla_historico_cuartel(cuartel_id):
    """
    Obtener histórico de frutos/ramilla de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si la tabla de peso racimo histórico existe
        cursor.execute("SHOW TABLES LIKE 'produccion_fact_pesoracimohistorico'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tabla de frutos/ramilla histórico no existe aún",
                "data": {
                    "frutos_ramilla": [],
                    "total": 0
                }
            }), 200
        
        # Obtener histórico de frutos/ramilla del cuartel
        # Resolver columna de fecha en historial de frutos/ramilla
        fecha_frutos_col = _first_existing_column(cursor, 'produccion_fact_pesoracimohistorico', ['fecha', 'fecha_registro', 'hora_registro']) or 'fecha'
        frutos_query = f"""
            SELECT 
                p.id,
                p.peso_racimo as frutos_ramilla,
                DATE(p.{fecha_frutos_col}) as fecha,
                u.nombre as usuario
            FROM produccion_fact_pesoracimohistorico p
            LEFT JOIN general_dim_usuario u ON p.id_usuario = u.id
            WHERE p.id_cuartel = %s AND p.id_usuario = %s
            ORDER BY p.{fecha_frutos_col} DESC
            LIMIT 50
        """
        
        cursor.execute(frutos_query, (cuartel_id, user_id))
        frutos_ramilla = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Histórico de frutos/ramilla del cuartel obtenido exitosamente",
            "data": {
                "frutos_ramilla": frutos_ramilla,
                "total": len(frutos_ramilla)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo histórico de frutos/ramilla del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/cuartel/<int:cuartel_id>/calibres-historicos', methods=['GET'])
@jwt_required()
def obtener_calibres_historicos_cuartel(cuartel_id):
    """
    Obtener calibres históricos de un cuartel específico
    """
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel pertenece a la sucursal activa del usuario
        verificar_cuartel_query = """
            SELECT 1
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN general_dim_usuario u ON s.id = u.id_sucursalactiva
            WHERE c.id = %s AND u.id = %s
        """
        
        cursor.execute(verificar_cuartel_query, (cuartel_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Verificar si las tablas de calibres existen
        cursor.execute("SHOW TABLES LIKE 'produccion_dim_calibretipo'")
        tabla_tipo_existe = cursor.fetchone()
        
        cursor.execute("SHOW TABLES LIKE 'produccion_dim_calibrevalor'")
        tabla_valor_existe = cursor.fetchone()
        
        if not tabla_tipo_existe or not tabla_valor_existe:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": "Tablas de calibres no existen aún",
                "data": {
                    "calibres": [],
                    "total": 0
                }
            }), 200
        
        # Obtener calibres históricos del cuartel
        calibres_query = """
            SELECT 
                cv.id,
                DATE(cv.fecha) as fecha,
                CONCAT(ct.nombre, ' ', cv.valor) as calibre,
                cv.cantidad,
                u.nombre as usuario
            FROM produccion_dim_calibrevalor cv
            LEFT JOIN produccion_dim_calibretipo ct ON cv.id_calibretipo = ct.id
            LEFT JOIN general_dim_usuario u ON cv.id_usuario = u.id
            WHERE cv.id_cuartel = %s AND cv.id_usuario = %s
            ORDER BY cv.fecha DESC, ct.nombre, cv.valor
            LIMIT 50
        """
        
        cursor.execute(calibres_query, (cuartel_id, user_id))
        calibres = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Calibres históricos del cuartel obtenidos exitosamente",
            "data": {
                "calibres": calibres,
                "total": len(calibres)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo calibres históricos del cuartel {cuartel_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@estimaciones_bp.route('/crear-masivo', methods=['POST'])
@jwt_required()
def crear_estimaciones_masivo():
    """
    Crear múltiples estimaciones para un cuartel específico (modo tabla)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        if 'id_cuartel' not in data:
            return jsonify({
                "success": False,
                "message": "Campo requerido: id_cuartel"
            }), 400
        
        if 'estimaciones' not in data or not isinstance(data['estimaciones'], list):
            return jsonify({
                "success": False,
                "message": "Campo requerido: estimaciones (array)"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el cuartel existe y pertenece al usuario
        cuartel_query = """
            SELECT c.id, c.nombre
            FROM general_dim_cuartel c
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE c.id = %s AND usu.id_usuario = %s
        """
        cursor.execute(cuartel_query, (data['id_cuartel'], user_id))
        cuartel_info = cursor.fetchone()
        
        if not cuartel_info:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Cuartel no encontrado o sin acceso"
            }), 404
        
        # Validar cada estimación
        estimaciones_validas = []
        for i, estimacion in enumerate(data['estimaciones']):
            campos_requeridos = ['id_tipoestimacion', 'embalaje_cajas', 'embalaje_kg', 'industria_kg']
            for campo in campos_requeridos:
                if campo not in estimacion:
                    return jsonify({
                        "success": False,
                        "message": f"Estimación {i+1}: Campo requerido: {campo}"
                    }), 400
            
            # Verificar que el tipo de estimación existe
            tipo_query = "SELECT id FROM estimacion_dim_tipo WHERE id = %s"
            cursor.execute(tipo_query, (estimacion['id_tipoestimacion'],))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({
                    "success": False,
                    "message": f"Estimación {i+1}: Tipo de estimación no encontrado"
                }), 404
            
            estimaciones_validas.append({
                'id_tipoestimacion': estimacion['id_tipoestimacion'],
                'embalaje_cajas': estimacion['embalaje_cajas'],
                'embalaje_kg': estimacion['embalaje_kg'],
                'industria_kg': estimacion['industria_kg']
            })
        
        # Insertar todas las estimaciones
        estimaciones_creadas = []
        for estimacion in estimaciones_validas:
            insert_query = """
                INSERT INTO estimacion_fact_registroadministradores 
                (id_usuario, id_cuartel, id_tipoestimacion, embalaje_cajas, embalaje_kg, industria_kg) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                user_id,
                data['id_cuartel'],
                estimacion['id_tipoestimacion'],
                estimacion['embalaje_cajas'],
                estimacion['embalaje_kg'],
                estimacion['industria_kg']
            ))
            
            estimacion_id = cursor.lastrowid
            
            # Obtener la estimación creada
            select_query = """
                SELECT 
                    e.id,
                    e.id_usuario,
                    e.id_cuartel,
                    e.id_tipoestimacion,
                    e.hora_registro,
                    e.embalaje_cajas,
                    e.embalaje_kg,
                    e.industria_kg,
                    c.nombre as nombre_cuartel,
                    t.nombre as nombre_tipo_estimacion
                FROM estimacion_fact_registroadministradores e
                LEFT JOIN general_dim_cuartel c ON e.id_cuartel = c.id
                LEFT JOIN estimacion_dim_tipo t ON e.id_tipoestimacion = t.id
                WHERE e.id = %s
            """
            
            cursor.execute(select_query, (estimacion_id,))
            estimacion_creada = cursor.fetchone()
            estimaciones_creadas.append(estimacion_creada)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"{len(estimaciones_creadas)} estimaciones creadas exitosamente",
            "data": {
                "cuartel": cuartel_info,
                "estimaciones_creadas": estimaciones_creadas,
                "total_creadas": len(estimaciones_creadas)
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando estimaciones masivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

