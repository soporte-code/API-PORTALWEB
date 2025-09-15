from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint para estimaciones
estimaciones_bp = Blueprint('estimaciones', __name__)

@estimaciones_bp.route('/api/estimaciones', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/<string:estimacion_id>', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones', methods=['POST'])
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

@estimaciones_bp.route('/api/estimaciones/<string:estimacion_id>', methods=['PUT'])
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

@estimaciones_bp.route('/api/estimaciones/<string:estimacion_id>', methods=['DELETE'])
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

@estimaciones_bp.route('/api/estimaciones/tipos', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/tipos/<int:tipo_id>', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/por-cuartel/<int:cuartel_id>', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/resumen', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/cuarteles-disponibles', methods=['GET'])
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

@estimaciones_bp.route('/api/estimaciones/historial-cuartel/<int:cuartel_id>', methods=['GET'])
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
            SELECT c.id, c.nombre, c.descripcion
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

@estimaciones_bp.route('/api/estimaciones/dashboard', methods=['GET'])
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
        
        # Obtener cuarteles agrupados por especie de la sucursal activa del usuario
        cuarteles_por_especie_query = """
            SELECT DISTINCT
                e.id as especie_id,
                e.nombre as especie_nombre,
                e.caja_equivalente,
                COUNT(DISTINCT c.id) as total_cuarteles,
                GROUP_CONCAT(
                    CONCAT(
                        '{"id":', c.id, 
                        ',"nombre":"', c.nombre, '",',
                        '"descripcion":"', COALESCE(c.descripcion, ''), '",',
                        '"ceco":"', ce.nombre, '",',
                        '"sucursal":"', s.nombre, '"',
                        '}'
                    ) 
                    ORDER BY c.nombre 
                    SEPARATOR ','
                ) as cuarteles_json
            FROM general_dim_especie e
            INNER JOIN general_dim_cuartel c ON c.id_especie = e.id
            INNER JOIN general_dim_ceco ce ON c.id_ceco = ce.id
            INNER JOIN general_dim_sucursal s ON ce.id_sucursal = s.id
            INNER JOIN usuario_pivot_sucursal_usuario usu ON s.id = usu.id_sucursal
            WHERE usu.id_usuario = %s
            GROUP BY e.id, e.nombre, e.caja_equivalente
            ORDER BY e.nombre
        """
        
        cursor.execute(cuarteles_por_especie_query, (user_id,))
        especies_con_cuarteles = cursor.fetchall()
        
        # Si no hay especies con cuarteles, retornar mensaje claro
        if not especies_con_cuarteles:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "No hay datos disponibles. No se encontraron especies con cuarteles asignados a tu sucursal.",
                "error": "SIN_DATOS_DISPONIBLES"
            }), 404
        
        # Procesar los cuarteles JSON para cada especie
        especies_agrupadas = []
        for especie in especies_con_cuarteles:
            cuarteles_data = []
            if especie['cuarteles_json']:
                # Parsear el JSON de cuarteles
                cuarteles_str = especie['cuarteles_json']
                cuarteles_list = cuarteles_str.split(',')
                
                for cuartel_str in cuarteles_list:
                    try:
                        # Limpiar y parsear cada cuartel
                        cuartel_str = cuartel_str.strip()
                        if cuartel_str.startswith('{"id":'):
                            # Extraer datos del cuartel
                            import re
                            id_match = re.search(r'"id":(\d+)', cuartel_str)
                            nombre_match = re.search(r'"nombre":"([^"]*)"', cuartel_str)
                            descripcion_match = re.search(r'"descripcion":"([^"]*)"', cuartel_str)
                            ceco_match = re.search(r'"ceco":"([^"]*)"', cuartel_str)
                            sucursal_match = re.search(r'"sucursal":"([^"]*)"', cuartel_str)
                            
                            if id_match and nombre_match:
                                cuartel_data = {
                                    "id": int(id_match.group(1)),
                                    "nombre": nombre_match.group(1),
                                    "descripcion": descripcion_match.group(1) if descripcion_match else "",
                                    "nombre_ceco": ceco_match.group(1) if ceco_match else "",
                                    "nombre_sucursal": sucursal_match.group(1) if sucursal_match else "",
                                    "total_estimaciones": 0,
                                    "total_cajas": 0,
                                    "total_kg_embalaje": 0,
                                    "total_kg_industria": 0,
                                    "ultima_estimacion": None
                                }
                                cuarteles_data.append(cuartel_data)
                    except Exception as parse_error:
                        logger.warning(f"Error parseando cuartel: {parse_error}")
                        continue
            
            especies_agrupadas.append({
                "especie_id": especie['especie_id'],
                "especie_nombre": especie['especie_nombre'],
                "caja_equivalente": especie['caja_equivalente'],
                "total_cuarteles": especie['total_cuarteles'],
                "cuarteles": cuarteles_data
            })
        
        # Si las tablas de estimaciones existen, agregar estadísticas
        if tabla_estimaciones_existe and tabla_tipos_existe:
            # Agregar estadísticas de estimaciones a cada cuartel
            for especie in especies_agrupadas:
                for cuartel in especie['cuarteles']:
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
                        cuartel['total_estimaciones'] = stats['total_estimaciones']
                        cuartel['total_cajas'] = stats['total_cajas']
                        cuartel['total_kg_embalaje'] = stats['total_kg_embalaje']
                        cuartel['total_kg_industria'] = stats['total_kg_industria']
                        cuartel['ultima_estimacion'] = stats['ultima_estimacion']
            
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

@estimaciones_bp.route('/api/estimaciones/crear-masivo', methods=['POST'])
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
            SELECT c.id, c.nombre, c.descripcion
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

