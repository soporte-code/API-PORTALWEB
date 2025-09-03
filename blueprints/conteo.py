from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from utils.db import get_db_connection
from datetime import datetime

conteo_bp = Blueprint('conteo_bp', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS PARA ATRIBUTO ÓPTIMO
# ============================================================================

@conteo_bp.route('/atributo-optimo', methods=['GET'])
@jwt_required()
def listar_atributos_optimos():
    """
    Listar todos los atributos óptimos
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ao.id,
                ao.id_atributo,
                ao.edad_min,
                ao.edad_max,
                ao.optimo_ha,
                ao.min_ha,
                ao.max_ha,
                a.nombre as nombre_atributo
            FROM conteo_dim_atributooptimo ao
            LEFT JOIN conteo_dim_atributo a ON ao.id_atributo = a.id
            WHERE ao.id_estado = 1
            ORDER BY ao.id_atributo, ao.edad_min
        """
        
        cursor.execute(query)
        atributos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributos óptimos obtenidos exitosamente",
            "data": {
                "atributos": atributos,
                "total": len(atributos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos óptimos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-optimo/<int:atributo_id>', methods=['GET'])
@jwt_required()
def obtener_atributo_optimo(atributo_id):
    """
    Obtener un atributo óptimo específico
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ao.id,
                ao.id_atributo,
                ao.edad_min,
                ao.edad_max,
                ao.optimo_ha,
                ao.min_ha,
                ao.max_ha,
                a.nombre as nombre_atributo
            FROM conteo_dim_atributooptimo ao
            LEFT JOIN conteo_dim_atributo a ON ao.id_atributo = a.id
            WHERE ao.id = %s AND ao.id_estado = 1
        """
        
        cursor.execute(query, (atributo_id,))
        atributo = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not atributo:
            return jsonify({
                "success": False,
                "message": "Atributo óptimo no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Atributo óptimo obtenido exitosamente",
            "data": atributo
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributo óptimo {atributo_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-optimo', methods=['POST'])
@jwt_required()
def crear_atributo_optimo():
    """
    Crear un nuevo atributo óptimo
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_atributo', 'edad_min', 'edad_max', 'optimo_ha', 'min_ha', 'max_ha']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Se requiere el campo '{campo}'"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insertar nuevo atributo óptimo
        insert_query = """
            INSERT INTO conteo_dim_atributooptimo 
            (id_atributo, edad_min, edad_max, optimo_ha, min_ha, max_ha, id_estado) 
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """
        
        cursor.execute(insert_query, (
            data['id_atributo'],
            data['edad_min'],
            data['edad_max'],
            data['optimo_ha'],
            data['min_ha'],
            data['max_ha']
        ))
        
        # Obtener el ID generado
        atributo_id = cursor.lastrowid
        
        # Obtener el atributo creado
        select_query = """
            SELECT 
                ao.id,
                ao.id_atributo,
                ao.edad_min,
                ao.edad_max,
                ao.optimo_ha,
                ao.min_ha,
                ao.max_ha,
                a.nombre as nombre_atributo
            FROM conteo_dim_atributooptimo ao
            LEFT JOIN conteo_dim_atributo a ON ao.id_atributo = a.id
            WHERE ao.id = %s
        """
        
        cursor.execute(select_query, (atributo_id,))
        atributo_creado = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributo óptimo creado exitosamente",
            "data": atributo_creado
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando atributo óptimo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-optimo/<int:atributo_id>', methods=['PUT'])
@jwt_required()
def actualizar_atributo_optimo(atributo_id):
    """
    Actualizar un atributo óptimo existente
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el atributo existe
        check_query = "SELECT id FROM conteo_dim_atributooptimo WHERE id = %s AND id_estado = 1"
        cursor.execute(check_query, (atributo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Atributo óptimo no encontrado"
            }), 404
        
        # Construir query de actualización dinámicamente
        campos_actualizables = ['id_atributo', 'edad_min', 'edad_max', 'optimo_ha', 'min_ha', 'max_ha']
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
        
        valores.append(atributo_id)
        update_query = f"""
            UPDATE conteo_dim_atributooptimo 
            SET {', '.join(campos_a_actualizar)}
            WHERE id = %s
        """
        
        cursor.execute(update_query, valores)
        
        # Obtener el atributo actualizado
        select_query = """
            SELECT 
                ao.id,
                ao.id_atributo,
                ao.edad_min,
                ao.edad_max,
                ao.optimo_ha,
                ao.min_ha,
                ao.max_ha,
                a.nombre as nombre_atributo
            FROM conteo_dim_atributooptimo ao
            LEFT JOIN conteo_dim_atributo a ON ao.id_atributo = a.id
            WHERE ao.id = %s
        """
        
        cursor.execute(select_query, (atributo_id,))
        atributo_actualizado = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributo óptimo actualizado exitosamente",
            "data": atributo_actualizado
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando atributo óptimo {atributo_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-optimo/<int:atributo_id>', methods=['DELETE'])
@jwt_required()
def eliminar_atributo_optimo(atributo_id):
    """
    Eliminar un atributo óptimo (soft delete)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el atributo existe
        check_query = "SELECT id FROM conteo_dim_atributooptimo WHERE id = %s AND id_estado = 1"
        cursor.execute(check_query, (atributo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Atributo óptimo no encontrado"
            }), 404
        
        # Soft delete
        delete_query = "UPDATE conteo_dim_atributooptimo SET id_estado = 0 WHERE id = %s"
        cursor.execute(delete_query, (atributo_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributo óptimo eliminado exitosamente",
            "data": {"id": atributo_id}
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando atributo óptimo {atributo_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# ============================================================================
# ENDPOINTS PARA ATRIBUTO ESPECIE
# ============================================================================

@conteo_bp.route('/atributo-especie', methods=['GET'])
@jwt_required()
def listar_atributos_especie():
    """
    Listar todas las relaciones atributo-especie
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
            LEFT JOIN conteo_dim_atributo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id_estado = 1
            ORDER BY ae.id_atributo, ae.id_especie
        """
        
        cursor.execute(query)
        atributos_especie = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Relaciones atributo-especie obtenidas exitosamente",
            "data": {
                "atributos_especie": atributos_especie,
                "total": len(atributos_especie)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos especie: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-especie/<int:relacion_id>', methods=['GET'])
@jwt_required()
def obtener_atributo_especie(relacion_id):
    """
    Obtener una relación atributo-especie específica
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
            LEFT JOIN conteo_dim_atributo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id = %s AND ae.id_estado = 1
        """
        
        cursor.execute(query, (relacion_id,))
        relacion = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not relacion:
            return jsonify({
                "success": False,
                "message": "Relación atributo-especie no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Relación atributo-especie obtenida exitosamente",
            "data": relacion
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributo especie {relacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-especie', methods=['POST'])
@jwt_required()
def crear_atributo_especie():
    """
    Crear una nueva relación atributo-especie
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_atributo', 'id_especie']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Se requiere el campo '{campo}'"
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que no existe ya esta relación
        check_query = """
            SELECT id FROM conteo_pivot_atributo_especie 
            WHERE id_atributo = %s AND id_especie = %s AND id_estado = 1
        """
        cursor.execute(check_query, (data['id_atributo'], data['id_especie']))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Ya existe una relación entre este atributo y especie"
            }), 400
        
        # Insertar nueva relación
        insert_query = """
            INSERT INTO conteo_pivot_atributo_especie 
            (id_atributo, id_especie, id_estado) 
            VALUES (%s, %s, 1)
        """
        
        cursor.execute(insert_query, (data['id_atributo'], data['id_especie']))
        relacion_id = cursor.lastrowid
        
        # Obtener la relación creada
        select_query = """
            SELECT 
                ae.id,
                ae.id_atributo,
                ae.id_especie,
                a.nombre as nombre_atributo,
                e.nombre as nombre_especie
            FROM conteo_pivot_atributo_especie ae
            LEFT JOIN conteo_dim_atributo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id = %s
        """
        
        cursor.execute(select_query, (relacion_id,))
        relacion_creada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Relación atributo-especie creada exitosamente",
            "data": relacion_creada
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando atributo especie: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-especie/<int:relacion_id>', methods=['PUT'])
@jwt_required()
def actualizar_atributo_especie(relacion_id):
    """
    Actualizar una relación atributo-especie existente
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la relación existe
        check_query = "SELECT id FROM conteo_pivot_atributo_especie WHERE id = %s AND id_estado = 1"
        cursor.execute(check_query, (relacion_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Relación atributo-especie no encontrada"
            }), 404
        
        # Construir query de actualización dinámicamente
        campos_actualizables = ['id_atributo', 'id_especie']
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
        
        valores.append(relacion_id)
        update_query = f"""
            UPDATE conteo_pivot_atributo_especie 
            SET {', '.join(campos_a_actualizar)}
            WHERE id = %s
        """
        
        cursor.execute(update_query, valores)
        
        # Obtener la relación actualizada
        select_query = """
            SELECT 
                ae.id,
                ae.id_atributo,
                ae.id_especie,
                a.nombre as nombre_atributo,
                e.nombre as nombre_especie
            FROM conteo_pivot_atributo_especie ae
            LEFT JOIN conteo_dim_atributo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id = %s
        """
        
        cursor.execute(select_query, (relacion_id,))
        relacion_actualizada = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Relación atributo-especie actualizada exitosamente",
            "data": relacion_actualizada
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando atributo especie {relacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-especie/<int:relacion_id>', methods=['DELETE'])
@jwt_required()
def eliminar_atributo_especie(relacion_id):
    """
    Eliminar una relación atributo-especie (soft delete)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la relación existe
        check_query = "SELECT id FROM conteo_pivot_atributo_especie WHERE id = %s AND id_estado = 1"
        cursor.execute(check_query, (relacion_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Relación atributo-especie no encontrada"
            }), 404
        
        # Soft delete
        delete_query = "UPDATE conteo_pivot_atributo_especie SET id_estado = 0 WHERE id = %s"
        cursor.execute(delete_query, (relacion_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Relación atributo-especie eliminada exitosamente",
            "data": {"id": relacion_id}
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando atributo especie {relacion_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

# ============================================================================
# ENDPOINTS ADICIONALES ÚTILES
# ============================================================================

@conteo_bp.route('/atributo-optimo/por-atributo/<int:atributo_id>', methods=['GET'])
@jwt_required()
def obtener_atributos_optimos_por_atributo(atributo_id):
    """
    Obtener todos los atributos óptimos de un atributo específico
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ao.id,
                ao.id_atributo,
                ao.edad_min,
                ao.edad_max,
                ao.optimo_ha,
                ao.min_ha,
                ao.max_ha,
                a.nombre as nombre_atributo
            FROM conteo_dim_atributooptimo ao
            LEFT JOIN conteo_dim_atributo a ON ao.id_atributo = a.id
            WHERE ao.id_atributo = %s AND ao.id_estado = 1
            ORDER BY ao.edad_min
        """
        
        cursor.execute(query, (atributo_id,))
        atributos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributos óptimos obtenidos exitosamente",
            "data": {
                "atributos": atributos,
                "total": len(atributos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos óptimos por atributo {atributo_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500

@conteo_bp.route('/atributo-especie/por-especie/<int:especie_id>', methods=['GET'])
@jwt_required()
def obtener_atributos_por_especie(especie_id):
    """
    Obtener todos los atributos asociados a una especie específica
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
            LEFT JOIN conteo_dim_atributo a ON ae.id_atributo = a.id
            LEFT JOIN general_dim_especie e ON ae.id_especie = e.id
            WHERE ae.id_especie = %s AND ae.id_estado = 1
            ORDER BY a.nombre
        """
        
        cursor.execute(query, (especie_id,))
        atributos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Atributos de especie obtenidos exitosamente",
            "data": {
                "atributos": atributos,
                "total": len(atributos)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo atributos por especie {especie_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        }), 500
