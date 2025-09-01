from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

hileras_bp = Blueprint('hileras_bp', __name__)
logger = logging.getLogger(__name__)

# Obtener todas las hileras del usuario logueado
@hileras_bp.route('/', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_hileras():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener hileras de cuarteles accesibles al usuario
        cursor.execute("""
            SELECT h.*, c.nombre as cuartel_nombre, c.id_ceco
            FROM general_dim_hilera h
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
            AND h.id_estado = 1
            ORDER BY c.nombre ASC, h.hilera ASC
        """, (usuario_id,))
        
        hileras = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(hileras), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo hileras: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener una hilera específica
@hileras_bp.route('/<int:hilera_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_hilera(hilera_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la hilera
        cursor.execute("""
            SELECT h.*, c.nombre as cuartel_nombre, c.id_ceco
            FROM general_dim_hilera h
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE h.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
        """, (hilera_id, usuario_id))
        
        hilera = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not hilera:
            return jsonify({"error": "Hilera no encontrada"}), 404
            
        return jsonify(hilera), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo hilera {hilera_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear una nueva hilera
@hileras_bp.route('/', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_hilera():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['hilera', 'id_cuartel']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso al cuartel
        cursor.execute("""
            SELECT 1 FROM general_dim_cuartel c
            WHERE c.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
        """, (data['id_cuartel'], usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "No tienes acceso a este cuartel"}), 403
        
        # Verificar que no exista una hilera con el mismo número en el cuartel
        cursor.execute("""
            SELECT 1 FROM general_dim_hilera 
            WHERE hilera = %s AND id_cuartel = %s AND id_estado = 1
        """, (data['hilera'], data['id_cuartel']))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe una hilera con este número en el cuartel"}), 400
        
        # Insertar la hilera
        cursor.execute("""
            INSERT INTO general_dim_hilera (hilera, id_cuartel, id_estado)
            VALUES (%s, %s, %s)
        """, (data['hilera'], data['id_cuartel'], 1))
        
        hilera_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Hilera creada exitosamente",
            "id": hilera_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando hilera: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Actualizar una hilera
@hileras_bp.route('/<int:hilera_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def actualizar_hilera(hilera_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la hilera
        cursor.execute("""
            SELECT h.*, c.id as cuartel_id FROM general_dim_hilera h
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE h.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
        """, (hilera_id, usuario_id))
        
        hilera_actual = cursor.fetchone()
        if not hilera_actual:
            cursor.close()
            conn.close()
            return jsonify({"error": "Hilera no encontrada o sin acceso"}), 404
        
        # Si se está cambiando el número de hilera, verificar que no exista duplicado
        if 'hilera' in data and data['hilera'] != hilera_actual['hilera']:
            cursor.execute("""
                SELECT 1 FROM general_dim_hilera 
                WHERE hilera = %s AND id_cuartel = %s AND id != %s AND id_estado = 1
            """, (data['hilera'], hilera_actual['cuartel_id'], hilera_id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Ya existe una hilera con este número en el cuartel"}), 400
        
        # Actualizar la hilera
        campos_actualizables = ['hilera']
        set_clause = []
        valores = []
        
        for campo in campos_actualizables:
            if campo in data:
                set_clause.append(f"{campo} = %s")
                valores.append(data[campo])
        
        if not set_clause:
            cursor.close()
            conn.close()
            return jsonify({"error": "No hay campos para actualizar"}), 400
        
        valores.append(hilera_id)
        
        cursor.execute(f"""
            UPDATE general_dim_hilera 
            SET {', '.join(set_clause)}
            WHERE id = %s
        """, valores)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Hilera actualizada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error actualizando hilera {hilera_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Eliminar (desactivar) una hilera
@hileras_bp.route('/<int:hilera_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def eliminar_hilera(hilera_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la hilera
        cursor.execute("""
            SELECT 1 FROM general_dim_hilera h
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE h.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
        """, (hilera_id, usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Hilera no encontrada o sin acceso"}), 404
        
        # Verificar si hay plantas asociadas
        cursor.execute("""
            SELECT COUNT(*) as total FROM general_dim_planta 
            WHERE id_hilera = %s AND id_estado = 1
        """, (hilera_id,))
        
        plantas_count = cursor.fetchone()['total']
        if plantas_count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"No se puede eliminar la hilera porque tiene {plantas_count} plantas asociadas"
            }), 400
        
        # Desactivar la hilera (soft delete)
        cursor.execute("""
            UPDATE general_dim_hilera 
            SET id_estado = 0
            WHERE id = %s
        """, (hilera_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Hilera eliminada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error eliminando hilera {hilera_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener plantas de una hilera
@hileras_bp.route('/<int:hilera_id>/plantas', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_plantas_hilera(hilera_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar acceso a la hilera y obtener plantas
        cursor.execute("""
            SELECT p.*
            FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE h.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
            AND p.id_estado = 1
            ORDER BY p.planta ASC
        """, (hilera_id, usuario_id))
        
        plantas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not plantas:
            return jsonify([]), 200
            
        return jsonify(plantas), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantas de la hilera {hilera_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear múltiples hileras para un cuartel
@hileras_bp.route('/bulk', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_hileras_masivo():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        if 'id_cuartel' not in data or 'hileras' not in data:
            return jsonify({"error": "Se requiere id_cuartel y hileras"}), 400
        
        if not isinstance(data['hileras'], list) or len(data['hileras']) == 0:
            return jsonify({"error": "hileras debe ser una lista no vacía"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso al cuartel
        cursor.execute("""
            SELECT 1 FROM general_dim_cuartel c
            WHERE c.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p 
                WHERE p.id_usuario = %s
            )
        """, (data['id_cuartel'], usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "No tienes acceso a este cuartel"}), 403
        
        # Verificar que no existan hileras duplicadas
        hileras_existentes = []
        for hilera_num in data['hileras']:
            cursor.execute("""
                SELECT hilera FROM general_dim_hilera 
                WHERE hilera = %s AND id_cuartel = %s AND id_estado = 1
            """, (hilera_num, data['id_cuartel']))
            
            if cursor.fetchone():
                hileras_existentes.append(hilera_num)
        
        if hileras_existentes:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"Las siguientes hileras ya existen: {', '.join(map(str, hileras_existentes))}"
            }), 400
        
        # Insertar todas las hileras
        hileras_creadas = []
        for hilera_num in data['hileras']:
            cursor.execute("""
                INSERT INTO general_dim_hilera (hilera, id_cuartel, id_estado)
                VALUES (%s, %s, %s)
            """, (hilera_num, data['id_cuartel'], 1))
            
            hileras_creadas.append({
                "id": cursor.lastrowid,
                "hilera": hilera_num
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"{len(hileras_creadas)} hileras creadas exitosamente",
            "hileras": hileras_creadas
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando hileras masivo: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
