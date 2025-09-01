from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection
import logging

variedades_bp = Blueprint('variedades_bp', __name__)
logger = logging.getLogger(__name__)

# ============================================================================
# ESPECIES
# ============================================================================

# Obtener todas las especies
@variedades_bp.route('/especies', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_especies():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM general_dim_especie 
            WHERE id_estado = 1
            ORDER BY nombre ASC
        """)
        
        especies = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(especies), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo especies: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener una especie específica
@variedades_bp.route('/especies/<int:especie_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_especie(especie_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM general_dim_especie 
            WHERE id = %s AND id_estado = 1
        """, (especie_id,))
        
        especie = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not especie:
            return jsonify({"error": "Especie no encontrada"}), 404
            
        return jsonify(especie), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo especie {especie_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear una nueva especie
@variedades_bp.route('/especies', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_especie():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['nombre']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que no exista una especie con el mismo nombre
        cursor.execute("""
            SELECT 1 FROM general_dim_especie 
            WHERE nombre = %s AND id_estado = 1
        """, (data['nombre'],))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe una especie con este nombre"}), 400
        
        # Insertar la especie
        cursor.execute("""
            INSERT INTO general_dim_especie (nombre, caja_equivalente, id_estado)
            VALUES (%s, %s, %s)
        """, (
            data['nombre'],
            data.get('caja_equivalente'),
            1  # id_estado activo
        ))
        
        especie_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Especie creada exitosamente",
            "id": especie_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando especie: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Actualizar una especie
@variedades_bp.route('/especies/<int:especie_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def actualizar_especie(especie_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la especie existe
        cursor.execute("""
            SELECT nombre FROM general_dim_especie 
            WHERE id = %s AND id_estado = 1
        """, (especie_id,))
        
        especie_actual = cursor.fetchone()
        if not especie_actual:
            cursor.close()
            conn.close()
            return jsonify({"error": "Especie no encontrada"}), 404
        
        # Si se está cambiando el nombre, verificar que no exista duplicado
        if 'nombre' in data and data['nombre'] != especie_actual['nombre']:
            cursor.execute("""
                SELECT 1 FROM general_dim_especie 
                WHERE nombre = %s AND id != %s AND id_estado = 1
            """, (data['nombre'], especie_id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Ya existe una especie con este nombre"}), 400
        
        # Actualizar la especie
        campos_actualizables = ['nombre', 'caja_equivalente']
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
        
        valores.append(especie_id)
        
        cursor.execute(f"""
            UPDATE general_dim_especie 
            SET {', '.join(set_clause)}
            WHERE id = %s
        """, valores)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Especie actualizada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error actualizando especie {especie_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Eliminar (desactivar) una especie
@variedades_bp.route('/especies/<int:especie_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def eliminar_especie(especie_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la especie existe
        cursor.execute("""
            SELECT 1 FROM general_dim_especie 
            WHERE id = %s AND id_estado = 1
        """, (especie_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Especie no encontrada"}), 404
        
        # Verificar si hay variedades asociadas
        cursor.execute("""
            SELECT COUNT(*) as total FROM general_dim_variedad 
            WHERE id_especie = %s AND id_estado = 1
        """, (especie_id,))
        
        variedades_count = cursor.fetchone()['total']
        if variedades_count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"No se puede eliminar la especie porque tiene {variedades_count} variedades asociadas"
            }), 400
        
        # Desactivar la especie (soft delete)
        cursor.execute("""
            UPDATE general_dim_especie 
            SET id_estado = 0
            WHERE id = %s
        """, (especie_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Especie eliminada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error eliminando especie {especie_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ============================================================================
# VARIEDADES
# ============================================================================

# Obtener todas las variedades
@variedades_bp.route('/variedades', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_variedades():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT v.*, e.nombre as especie_nombre
            FROM general_dim_variedad v
            LEFT JOIN general_dim_especie e ON v.id_especie = e.id
            WHERE v.id_estado = 1
            ORDER BY e.nombre ASC, v.nombre ASC
        """)
        
        variedades = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(variedades), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo variedades: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener una variedad específica
@variedades_bp.route('/variedades/<int:variedad_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_variedad(variedad_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT v.*, e.nombre as especie_nombre
            FROM general_dim_variedad v
            LEFT JOIN general_dim_especie e ON v.id_especie = e.id
            WHERE v.id = %s AND v.id_estado = 1
        """, (variedad_id,))
        
        variedad = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not variedad:
            return jsonify({"error": "Variedad no encontrada"}), 404
            
        return jsonify(variedad), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo variedad {variedad_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Crear una nueva variedad
@variedades_bp.route('/variedades', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_variedad():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'id_especie']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la especie existe
        cursor.execute("""
            SELECT 1 FROM general_dim_especie 
            WHERE id = %s AND id_estado = 1
        """, (data['id_especie'],))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Especie no encontrada"}), 400
        
        # Verificar que no exista una variedad con el mismo nombre en la especie
        cursor.execute("""
            SELECT 1 FROM general_dim_variedad 
            WHERE nombre = %s AND id_especie = %s AND id_estado = 1
        """, (data['nombre'], data['id_especie']))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe una variedad con este nombre en la especie"}), 400
        
        # Insertar la variedad
        cursor.execute("""
            INSERT INTO general_dim_variedad (
                nombre, id_especie, id_forma, id_color, id_estado
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            data['nombre'],
            data['id_especie'],
            data.get('id_forma'),
            data.get('id_color'),
            1  # id_estado activo
        ))
        
        variedad_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Variedad creada exitosamente",
            "id": variedad_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando variedad: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Actualizar una variedad
@variedades_bp.route('/variedades/<int:variedad_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def actualizar_variedad(variedad_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la variedad existe
        cursor.execute("""
            SELECT nombre, id_especie FROM general_dim_variedad 
            WHERE id = %s AND id_estado = 1
        """, (variedad_id,))
        
        variedad_actual = cursor.fetchone()
        if not variedad_actual:
            cursor.close()
            conn.close()
            return jsonify({"error": "Variedad no encontrada"}), 404
        
        # Si se está cambiando el nombre, verificar que no exista duplicado
        if 'nombre' in data and data['nombre'] != variedad_actual['nombre']:
            cursor.execute("""
                SELECT 1 FROM general_dim_variedad 
                WHERE nombre = %s AND id_especie = %s AND id != %s AND id_estado = 1
            """, (data['nombre'], variedad_actual['id_especie'], variedad_id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Ya existe una variedad con este nombre en la especie"}), 400
        
        # Actualizar la variedad
        campos_actualizables = ['nombre', 'id_especie', 'id_forma', 'id_color']
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
        
        valores.append(variedad_id)
        
        cursor.execute(f"""
            UPDATE general_dim_variedad 
            SET {', '.join(set_clause)}
            WHERE id = %s
        """, valores)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Variedad actualizada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error actualizando variedad {variedad_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Eliminar (desactivar) una variedad
@variedades_bp.route('/variedades/<int:variedad_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def eliminar_variedad(variedad_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la variedad existe
        cursor.execute("""
            SELECT 1 FROM general_dim_variedad 
            WHERE id = %s AND id_estado = 1
        """, (variedad_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Variedad no encontrada"}), 404
        
        # Verificar si hay cuarteles asociados
        cursor.execute("""
            SELECT COUNT(*) as total FROM general_dim_cuartel 
            WHERE id_variedad = %s AND id_estado = 1
        """, (variedad_id,))
        
        cuarteles_count = cursor.fetchone()['total']
        if cuarteles_count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"No se puede eliminar la variedad porque tiene {cuarteles_count} cuarteles asociados"
            }), 400
        
        # Desactivar la variedad (soft delete)
        cursor.execute("""
            UPDATE general_dim_variedad 
            SET id_estado = 0
            WHERE id = %s
        """, (variedad_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Variedad eliminada exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error eliminando variedad {variedad_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Obtener variedades por especie
@variedades_bp.route('/especies/<int:especie_id>/variedades', methods=['GET', 'OPTIONS'])
@jwt_required()
def obtener_variedades_especie(especie_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la especie existe
        cursor.execute("""
            SELECT 1 FROM general_dim_especie 
            WHERE id = %s AND id_estado = 1
        """, (especie_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Especie no encontrada"}), 404
        
        # Obtener variedades de la especie
        cursor.execute("""
            SELECT v.*, e.nombre as especie_nombre
            FROM general_dim_variedad v
            LEFT JOIN general_dim_especie e ON v.id_especie = e.id
            WHERE v.id_especie = %s AND v.id_estado = 1
            ORDER BY v.nombre ASC
        """, (especie_id,))
        
        variedades = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(variedades), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo variedades de especie {especie_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
