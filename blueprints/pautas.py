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
        
        query = """
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON cp.id_tipoplanta = tp.id
            ORDER BY cp.id
        """
        
        cursor.execute(query)
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

@pautas_bp.route('/configuraciones', methods=['POST'])
@jwt_required()
def crear_configuracion_pauta():
    """
    Crear una nueva configuración de pauta
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_empresa', 'id_conteotipo', 'id_atributo']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido: {campo}"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insertar nueva configuración
        insert_query = """
            INSERT INTO conteo_dim_configpauta 
            (id_empresa, id_conteotipo, id_atributo, id_tipoplanta) 
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            data['id_empresa'],
            data['id_conteotipo'],
            data['id_atributo'],
            data.get('id_tipoplanta')  # Opcional
        ))
        
        configuracion_id = cursor.lastrowid
        
        # Obtener la configuración creada
        select_query = """
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON cp.id_tipoplanta = tp.id
            WHERE cp.id = %s
        """
        
        cursor.execute(select_query, (configuracion_id,))
        configuracion_creada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Configuración de pauta creada exitosamente",
            "data": configuracion_creada
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando configuración de pauta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/configuraciones/<int:config_id>', methods=['PUT'])
@jwt_required()
def actualizar_configuracion_pauta(config_id):
    """
    Actualizar una configuración de pauta existente
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Construir query de actualización dinámicamente
        campos_actualizables = ['id_empresa', 'id_conteotipo', 'id_atributo', 'id_tipoplanta']
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
        
        valores.append(config_id)
        update_query = f"""
            UPDATE conteo_dim_configpauta 
            SET {', '.join(campos_a_actualizar)}
            WHERE id = %s
        """
        
        cursor.execute(update_query, valores)
        
        # Obtener la configuración actualizada
        select_query = """
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON cp.id_tipoplanta = tp.id
            WHERE cp.id = %s
        """
        
        cursor.execute(select_query, (config_id,))
        configuracion_actualizada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Configuración de pauta actualizada exitosamente",
            "data": configuracion_actualizada
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando configuración de pauta {config_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/configuraciones/<int:config_id>', methods=['DELETE'])
@jwt_required()
def eliminar_configuracion_pauta(config_id):
    """
    Eliminar una configuración de pauta
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Eliminar configuración
        delete_query = "DELETE FROM conteo_dim_configpauta WHERE id = %s"
        cursor.execute(delete_query, (config_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Configuración de pauta eliminada exitosamente"
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando configuración de pauta {config_id}: {str(e)}")
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

@pautas_bp.route('/atributos-especie/<int:especie_id>', methods=['GET'])
@jwt_required()
def listar_atributos_especie(especie_id):
    """
    Listar atributos disponibles para una especie específica
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ae.id,
                ae.id_atributo,
                ae.id_especie,
                a.nombre as nombre_atributo,
                e.nombre as nombre_especie
            FROM conteo_pivot_atributo_especie ae
            LEFT JOIN conteo_dim_atributocultivo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id_especie = %s
            ORDER BY a.nombre
        """
        
        cursor.execute(query, (especie_id,))
        atributos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributos de la especie obtenidos exitosamente",
            "data": {
                "atributos": atributos,
                "total": len(atributos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos de especie {especie_id}: {str(e)}")
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

@pautas_bp.route('/tipos-planta-registro', methods=['GET'])
@jwt_required()
def listar_tipos_planta_registro():
    """
    Listar tipos de planta desde el registro de mapeo
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT DISTINCT
                tp.id,
                tp.nombre,
                tp.factor_productivo,
                tp.id_empresa,
                tp.descripcion,
                COUNT(r.id) as total_registros
            FROM mapeo_dim_tipoplanta tp
            LEFT JOIN mapeo_fact_registro r ON tp.id = r.id_tipoplanta
            GROUP BY tp.id, tp.nombre, tp.factor_productivo, tp.id_empresa, tp.descripcion
            ORDER BY tp.nombre
        """
        
        cursor.execute(query)
        tipos_planta = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Tipos de planta desde registro obtenidos exitosamente",
            "data": {
                "tipos_planta": tipos_planta,
                "total": len(tipos_planta)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de planta desde registro: {str(e)}")
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON cp.id_tipoplanta = tp.id
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON dp.id_tipoplanta = tp.id
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

# =============================================================================
# DETALLE DE PAUTAS (conteo_fact_detallepauta)
# =============================================================================

@pautas_bp.route('/pautas/<string:pauta_id>/detalles', methods=['POST'])
@jwt_required()
def crear_detalle_pauta(pauta_id):
    """
    Crear un detalle de pauta
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_atributo', 'valor_atributo']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido: {campo}"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la pauta existe y pertenece al usuario
        pauta_query = "SELECT id FROM conteo_fact_pauta WHERE id = %s AND id_usuario = %s"
        cursor.execute(pauta_query, (pauta_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Pauta no encontrada"
            }), 404
        
        # Insertar nuevo detalle
        insert_query = """
            INSERT INTO conteo_fact_detallepauta 
            (id_pauta, id_atributo, id_tipoplanta, valor_atributo) 
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            pauta_id,
            data['id_atributo'],
            data.get('id_tipoplanta'),  # Opcional
            data['valor_atributo']
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
            LEFT JOIN mapeo_dim_tipoplanta tp ON dp.id_tipoplanta = tp.id
            WHERE dp.id = %s
        """
        
        cursor.execute(select_query, (detalle_id,))
        detalle_creado = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Detalle de pauta creado exitosamente",
            "data": detalle_creado
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando detalle de pauta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@pautas_bp.route('/pautas/<string:pauta_id>/detalles-masivo', methods=['POST'])
@jwt_required()
def crear_detalles_pauta_masivo(pauta_id):
    """
    Crear múltiples detalles de pauta de una vez
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        if 'detalles' not in data or not isinstance(data['detalles'], list):
            return jsonify({
                "success": False,
                "message": "Campo requerido: detalles (array)"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la pauta existe y pertenece al usuario
        pauta_query = "SELECT id FROM conteo_fact_pauta WHERE id = %s AND id_usuario = %s"
        cursor.execute(pauta_query, (pauta_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Pauta no encontrada"
            }), 404
        
        # Validar cada detalle
        detalles_validos = []
        for i, detalle in enumerate(data['detalles']):
            campos_requeridos = ['id_atributo', 'valor_atributo']
            for campo in campos_requeridos:
                if campo not in detalle:
                    return jsonify({
                        "success": False,
                        "message": f"Detalle {i+1}: Campo requerido: {campo}"
                    }), 400
            
            detalles_validos.append({
                'id_atributo': detalle['id_atributo'],
                'id_tipoplanta': detalle.get('id_tipoplanta'),
                'valor_atributo': detalle['valor_atributo']
            })
        
        # Insertar todos los detalles
        detalles_creados = []
        for detalle in detalles_validos:
            insert_query = """
                INSERT INTO conteo_fact_detallepauta 
                (id_pauta, id_atributo, id_tipoplanta, valor_atributo) 
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                pauta_id,
                detalle['id_atributo'],
                detalle['id_tipoplanta'],
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
                LEFT JOIN mapeo_dim_tipoplanta tp ON dp.id_tipoplanta = tp.id
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
                "detalles_creados": detalles_creados,
                "total_creados": len(detalles_creados)
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando detalles de pauta masivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500
