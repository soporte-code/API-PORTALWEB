from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

plantas_bp = Blueprint('plantas_bp', __name__)
logger = logging.getLogger(__name__)

# Obtener todas las plantas del usuario logueado
@plantas_bp.route('/', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_plantas():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener plantas de cuarteles accesibles al usuario
        cursor.execute("""
            SELECT p.*, h.hilera, c.nombre as cuartel_nombre, c.id_ceco
            FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
            AND p.id_estado = 1
            ORDER BY c.nombre ASC, h.hilera ASC, p.planta ASC
        """, (usuario_id,))
        
        plantas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(plantas), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantas: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener una planta específica
@plantas_bp.route('/<int:planta_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_planta(planta_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la planta
        cursor.execute("""
            SELECT p.*, h.hilera, c.nombre as cuartel_nombre, c.id_ceco
            FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE p.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
        """, (planta_id, usuario_id))
        
        planta = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not planta:
            return jsonify({"error": "Planta no encontrada"}), 404
            
        return jsonify(planta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo planta {planta_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear una nueva planta
@plantas_bp.route('/', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_planta():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['planta', 'id_hilera']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
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
        """, (data['id_hilera'], usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "No tienes acceso a esta hilera"}), 403
        
        # Verificar que no exista una planta con el mismo número en la hilera
        cursor.execute("""
            SELECT 1 FROM general_dim_planta 
            WHERE planta = %s AND id_hilera = %s AND id_estado = 1
        """, (data['planta'], data['id_hilera']))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe una planta con este número en la hilera"}), 400
        
        # Insertar la planta
        cursor.execute("""
            INSERT INTO general_dim_planta (planta, id_hilera, ubicacion, fecha_creacion, id_estado)
            VALUES (%s, %s, %s, CURRENT_DATE, %s)
        """, (
            data['planta'],
            data['id_hilera'],
            data.get('ubicacion'),
            1  # id_estado activo
        ))
        
        planta_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Planta creada exitosamente",
            "id": planta_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando planta: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Actualizar una planta
@plantas_bp.route('/<int:planta_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def actualizar_planta(planta_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la planta
        cursor.execute("""
            SELECT p.*, h.id as hilera_id FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE p.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
        """, (planta_id, usuario_id))
        
        planta_actual = cursor.fetchone()
        if not planta_actual:
            cursor.close()
            conn.close()
            return jsonify({"error": "Planta no encontrada o sin acceso"}), 404
        
        # Si se está cambiando el número de planta, verificar que no exista duplicado
        if 'planta' in data and data['planta'] != planta_actual['planta']:
            cursor.execute("""
                SELECT 1 FROM general_dim_planta 
                WHERE planta = %s AND id_hilera = %s AND id != %s AND id_estado = 1
            """, (data['planta'], planta_actual['hilera_id'], planta_id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Ya existe una planta con este número en la hilera"}), 400
        
        # Actualizar la planta
        campos_actualizables = ['planta', 'ubicacion']
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
        
        valores.append(planta_id)
        
        cursor.execute(f"""
            UPDATE general_dim_planta 
            SET {', '.join(set_clause)}
            WHERE id = %s
        """, valores)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Planta actualizada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error actualizando planta {planta_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Eliminar (desactivar) una planta
@plantas_bp.route('/<int:planta_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def eliminar_planta(planta_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario tenga acceso a la planta
        cursor.execute("""
            SELECT 1 FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE p.id = %s AND c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
        """, (planta_id, usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Planta no encontrada o sin acceso"}), 404
        
        # Verificar si hay registros de mapeo asociados
        cursor.execute("""
            SELECT COUNT(*) as total FROM mapeo_fact_registro 
            WHERE id_planta = %s
        """, (planta_id,))
        
        registros_count = cursor.fetchone()['total']
        if registros_count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"No se puede eliminar la planta porque tiene {registros_count} registros de mapeo asociados"
            }), 400
        
        # Desactivar la planta (soft delete)
        cursor.execute("""
            UPDATE general_dim_planta 
            SET id_estado = 0
            WHERE id = %s
        """, (planta_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Planta eliminada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error eliminando planta {planta_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear múltiples plantas para una hilera
@plantas_bp.route('/bulk', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_plantas_masivo():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        if 'id_hilera' not in data or 'plantas' not in data:
            return jsonify({"error": "Se requiere id_hilera y plantas"}), 400
        
        if not isinstance(data['plantas'], list) or len(data['plantas']) == 0:
            return jsonify({"error": "plantas debe ser una lista no vacía"}), 400
        
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
        """, (data['id_hilera'], usuario_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "No tienes acceso a esta hilera"}), 403
        
        # Verificar que no existan plantas duplicadas
        plantas_existentes = []
        for planta_data in data['plantas']:
            planta_num = planta_data if isinstance(planta_data, str) else planta_data.get('planta', planta_data)
            cursor.execute("""
                SELECT planta FROM general_dim_planta 
                WHERE planta = %s AND id_hilera = %s AND id_estado = 1
            """, (planta_num, data['id_hilera']))
            
            if cursor.fetchone():
                plantas_existentes.append(planta_num)
        
        if plantas_existentes:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"Las siguientes plantas ya existen: {', '.join(map(str, plantas_existentes))}"
            }), 400
        
        # Insertar todas las plantas
        plantas_creadas = []
        for planta_data in data['plantas']:
            if isinstance(planta_data, dict):
                planta_num = planta_data['planta']
                ubicacion = planta_data.get('ubicacion')
            else:
                planta_num = planta_data
                ubicacion = None
            
            cursor.execute("""
                INSERT INTO general_dim_planta (planta, id_hilera, ubicacion, fecha_creacion, id_estado)
                VALUES (%s, %s, %s, CURRENT_DATE, %s)
            """, (planta_num, data['id_hilera'], ubicacion, 1))
            
            plantas_creadas.append({
                "id": cursor.lastrowid,
                "planta": planta_num
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"{len(plantas_creadas)} plantas creadas exitosamente",
            "plantas": plantas_creadas
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando plantas masivo: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Buscar plantas por filtros
@plantas_bp.route('/buscar', methods=['GET', 'OPTIONS'])
@jwt_required()
def buscar_plantas():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        usuario_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener parámetros de búsqueda
        cuartel_id = request.args.get('cuartel_id')
        hilera_id = request.args.get('hilera_id')
        planta_num = request.args.get('planta')
        
        # Construir query base
        query = """
            SELECT p.*, h.hilera, c.nombre as cuartel_nombre, c.id_ceco
            FROM general_dim_planta p
            JOIN general_dim_hilera h ON p.id_hilera = h.id
            JOIN general_dim_cuartel c ON h.id_cuartel = c.id
            WHERE c.id_sucursal IN (
                SELECT DISTINCT p2.id_sucursal 
                FROM usuario_pivot_sucursal_usuario p2 
                WHERE p2.id_usuario = %s
            )
            AND p.id_estado = 1
        """
        valores = [usuario_id]
        
        # Agregar filtros
        if cuartel_id:
            query += " AND c.id = %s"
            valores.append(cuartel_id)
        
        if hilera_id:
            query += " AND h.id = %s"
            valores.append(hilera_id)
        
        if planta_num:
            query += " AND p.planta LIKE %s"
            valores.append(f"%{planta_num}%")
        
        query += " ORDER BY c.nombre ASC, h.hilera ASC, p.planta ASC"
        
        cursor.execute(query, valores)
        plantas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(plantas), 200
        
    except Exception as e:
        logger.error(f"Error buscando plantas: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
