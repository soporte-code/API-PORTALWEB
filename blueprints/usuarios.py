from flask import Blueprint, jsonify, request
from utils.db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
from datetime import date
import uuid
import logging

# Configurar logging
logger = logging.getLogger(__name__)

usuarios_bp = Blueprint('usuarios_bp', __name__)

def verificar_admin(usuario_id):
    """Verifica si el usuario tiene perfil de administrador (id_perfil = 3)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_perfil FROM general_dim_usuario WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario and usuario['id_perfil'] == 3

# ============================================================================
# GESTIÓN DE USUARIOS
# ============================================================================

# 🔹 Listar todos los usuarios (solo administradores)
@usuarios_bp.route('/', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """Lista todos los usuarios del sistema (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                u.id, u.usuario, u.nombre, u.apellido_paterno, u.apellido_materno,
                u.correo, u.id_sucursalactiva, u.id_estado, u.id_rol, u.id_perfil,
                u.fecha_creacion,
                s.nombre as sucursal_activa_nombre,
                p.nombre as perfil_nombre
            FROM general_dim_usuario u
            LEFT JOIN general_dim_sucursal s ON u.id_sucursalactiva = s.id
            LEFT JOIN usuario_dim_perfil p ON u.id_perfil = p.id
            ORDER BY u.nombre, u.apellido_paterno
        """)
        
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(usuarios), 200
        
    except Exception as e:
        logger.error(f"Error listando usuarios: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Obtener usuario específico
@usuarios_bp.route('/<string:usuario_id>', methods=['GET'])
@jwt_required()
def obtener_usuario(usuario_id):
    """Obtiene información detallada de un usuario específico (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información del usuario
        cursor.execute("""
            SELECT 
                u.*, s.nombre as sucursal_activa_nombre,
                p.nombre as perfil_nombre
            FROM general_dim_usuario u
            LEFT JOIN general_dim_sucursal s ON u.id_sucursalactiva = s.id
            LEFT JOIN usuario_dim_perfil p ON u.id_perfil = p.id
            WHERE u.id = %s
        """, (usuario_id,))
        
        usuario = cursor.fetchone()
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Obtener sucursales permitidas
        cursor.execute("""
            SELECT s.id, s.nombre, s.ubicacion
            FROM general_dim_sucursal s
            INNER JOIN usuario_pivot_sucursal_usuario p ON s.id = p.id_sucursal
            WHERE p.id_usuario = %s
            ORDER BY s.nombre
        """, (usuario_id,))
        
        sucursales_permitidas = cursor.fetchall()
        
        # Obtener aplicaciones permitidas
        cursor.execute("""
            SELECT a.id, a.nombre, a.descripcion
            FROM general_dim_app a
            INNER JOIN usuario_pivot_app_usuario p ON a.id = p.id_app
            WHERE p.id_usuario = %s
            ORDER BY a.nombre
        """, (usuario_id,))
        
        apps_permitidas = cursor.fetchall()
        
        # Obtener permisos asignados
        cursor.execute("""
            SELECT p.id, p.nombre, p.id_app, a.nombre as app_nombre
            FROM usuario_dim_permiso p
            INNER JOIN usuario_pivot_permiso_usuario up ON p.id = up.id_permiso
            LEFT JOIN general_dim_app a ON p.id_app = a.id
            WHERE up.id_usuario = %s
            ORDER BY a.nombre, p.nombre
        """, (usuario_id,))
        
        permisos_asignados = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Construir respuesta completa
        usuario_completo = {
            **usuario,
            'sucursales_permitidas': sucursales_permitidas,
            'apps_permitidas': apps_permitidas,
            'permisos_asignados': permisos_asignados
        }
        
        return jsonify(usuario_completo), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Crear nuevo usuario
@usuarios_bp.route('/', methods=['POST'])
@jwt_required()
def crear_usuario():
    """Crea un nuevo usuario en el sistema (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['usuario', 'nombre', 'apellido_paterno', 'clave', 'correo']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        # Validar que el usuario no exista
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE usuario = %s", (data['usuario'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "El nombre de usuario ya existe"}), 400
        
        # Validar que el correo no exista
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE correo = %s", (data['correo'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "El correo electrónico ya existe"}), 400
        
        # Generar ID único para el usuario
        usuario_id = str(uuid.uuid4())
        
        # Encriptar contraseña
        clave_hash = bcrypt.hashpw(data['clave'].encode('utf-8'), bcrypt.gensalt())
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO general_dim_usuario (
                id, usuario, nombre, apellido_paterno, apellido_materno,
                clave, correo, id_estado, id_rol, id_perfil, fecha_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            usuario_id,
            data['usuario'],
            data['nombre'],
            data['apellido_paterno'],
            data.get('apellido_materno'),
            clave_hash.decode('utf-8'),
            data['correo'],
            data.get('id_estado', 1),  # Activo por defecto
            data.get('id_rol', 3),     # Usuario por defecto
            data.get('id_perfil', 1),  # Perfil básico por defecto
            date.today()
        ))
        
        # Asignar sucursal activa por defecto (primera disponible)
        if data.get('id_sucursalactiva'):
            cursor.execute("""
                UPDATE general_dim_usuario 
                SET id_sucursalactiva = %s 
                WHERE id = %s
            """, (data['id_sucursalactiva'], usuario_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Usuario creado exitosamente",
            "id": usuario_id,
            "usuario": data['usuario']
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando usuario: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Actualizar usuario
@usuarios_bp.route('/<string:usuario_id>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(usuario_id):
    """Actualiza información de un usuario existente (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Construir consulta de actualización dinámicamente
        campos_actualizar = []
        valores = []
        
        # Campos que se pueden actualizar
        campos_permitidos = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'correo',
            'id_estado', 'id_rol', 'id_perfil', 'id_sucursalactiva'
        ]
        
        for campo in campos_permitidos:
            if campo in data:
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data[campo])
        
        # Si se proporciona nueva contraseña, encriptarla
        if 'clave' in data:
            clave_hash = bcrypt.hashpw(data['clave'].encode('utf-8'), bcrypt.gensalt())
            campos_actualizar.append("clave = %s")
            valores.append(clave_hash.decode('utf-8'))
        
        if not campos_actualizar:
            cursor.close()
            conn.close()
            return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400
        
        valores.append(usuario_id)
        
        # Ejecutar actualización
        sql = f"""
            UPDATE general_dim_usuario 
            SET {', '.join(campos_actualizar)}
            WHERE id = %s
        """
        
        cursor.execute(sql, valores)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Usuario actualizado correctamente",
            "id": usuario_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando usuario: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Eliminar usuario (desactivar)
@usuarios_bp.route('/<string:usuario_id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(usuario_id):
    """Desactiva un usuario del sistema (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Desactivar usuario (soft delete)
        cursor.execute("""
            UPDATE general_dim_usuario 
            SET id_estado = 0 
            WHERE id = %s
        """, (usuario_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Usuario desactivado correctamente",
            "id": usuario_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error eliminando usuario: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# GESTIÓN DE PERFILES
# ============================================================================

# 🔹 Listar perfiles disponibles
@usuarios_bp.route('/perfiles', methods=['GET'])
@jwt_required()
def listar_perfiles():
    """Lista todos los perfiles disponibles en el sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre
            FROM usuario_dim_perfil
            ORDER BY nombre
        """)
        
        perfiles = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(perfiles), 200
        
    except Exception as e:
        logger.error(f"Error listando perfiles: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Crear nuevo perfil
@usuarios_bp.route('/perfiles', methods=['POST'])
@jwt_required()
def crear_perfil():
    """Crea un nuevo perfil (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        
        if 'nombre' not in data:
            return jsonify({"error": "Campo requerido: nombre"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que no exista un perfil con el mismo nombre
        cursor.execute("SELECT 1 FROM usuario_dim_perfil WHERE nombre = %s", (data['nombre'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe un perfil con este nombre"}), 400
        
        # Insertar perfil
        cursor.execute("""
            INSERT INTO usuario_dim_perfil (nombre)
            VALUES (%s)
        """, (data['nombre'],))
        
        perfil_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Perfil creado exitosamente",
            "id": perfil_id,
            "nombre": data['nombre']
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando perfil: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# GESTIÓN DE APLICACIONES
# ============================================================================

# 🔹 Listar aplicaciones disponibles
@usuarios_bp.route('/aplicaciones', methods=['GET'])
@jwt_required()
def listar_aplicaciones():
    """Lista todas las aplicaciones disponibles en el sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, descripcion, URL
            FROM general_dim_app
            ORDER BY nombre
        """)
        
        aplicaciones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(aplicaciones), 200
        
    except Exception as e:
        logger.error(f"Error listando aplicaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Crear nueva aplicación
@usuarios_bp.route('/aplicaciones', methods=['POST'])
@jwt_required()
def crear_aplicacion():
    """Crea una nueva aplicación (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        
        campos_requeridos = ['nombre', 'descripcion', 'URL']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que no exista una app con el mismo nombre
        cursor.execute("SELECT 1 FROM general_dim_app WHERE nombre = %s", (data['nombre'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Ya existe una aplicación con este nombre"}), 400
        
        # Insertar aplicación
        cursor.execute("""
            INSERT INTO general_dim_app (nombre, descripcion, URL)
            VALUES (%s, %s, %s)
        """, (data['nombre'], data['descripcion'], data['URL']))
        
        app_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Aplicación creada exitosamente",
            "id": app_id,
            "nombre": data['nombre']
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando aplicación: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# GESTIÓN DE PERMISOS
# ============================================================================

# 🔹 Listar permisos disponibles
@usuarios_bp.route('/permisos', methods=['GET'])
@jwt_required()
def listar_permisos():
    """Lista todos los permisos disponibles en el sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.id, p.nombre, p.id_app, a.nombre as app_nombre
            FROM usuario_dim_permiso p
            LEFT JOIN general_dim_app a ON p.id_app = a.id
            WHERE p.id_estado = 1
            ORDER BY a.nombre, p.nombre
        """)
        
        permisos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(permisos), 200
        
    except Exception as e:
        logger.error(f"Error listando permisos: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Crear nuevo permiso
@usuarios_bp.route('/permisos', methods=['POST'])
@jwt_required()
def crear_permiso():
    """Crea un nuevo permiso (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        
        campos_requeridos = ['nombre', 'id_app']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la aplicación existe
        cursor.execute("SELECT 1 FROM general_dim_app WHERE id = %s", (data['id_app'],))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "La aplicación especificada no existe"}), 400
        
        # Generar ID único para el permiso
        permiso_id = str(uuid.uuid4())
        
        # Insertar permiso
        cursor.execute("""
            INSERT INTO usuario_dim_permiso (id, nombre, id_app, id_estado)
            VALUES (%s, %s, %s, %s)
        """, (permiso_id, data['nombre'], data['id_app'], 1))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Permiso creado exitosamente",
            "id": permiso_id,
            "nombre": data['nombre']
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando permiso: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ASIGNACIÓN DE PERMISOS Y ACCESOS
# ============================================================================

# 🔹 Asignar permisos a un usuario
@usuarios_bp.route('/<string:usuario_id>/permisos', methods=['POST'])
@jwt_required()
def asignar_permisos(usuario_id):
    """Asigna permisos específicos a un usuario (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        permisos_ids = data.get('permisos_ids', [])
        
        if not isinstance(permisos_ids, list):
            return jsonify({"error": "permisos_ids debe ser una lista"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verificar que todos los permisos existen
        if permisos_ids:
            placeholders = ','.join(['%s'] * len(permisos_ids))
            cursor.execute(f"""
                SELECT id FROM usuario_dim_permiso 
                WHERE id IN ({placeholders}) AND id_estado = 1
            """, permisos_ids)
            
            permisos_validos = cursor.fetchall()
            if len(permisos_validos) != len(permisos_ids):
                cursor.close()
                conn.close()
                return jsonify({"error": "Uno o más permisos no existen o están inactivos"}), 400
        
        # Eliminar permisos actuales del usuario
        cursor.execute("DELETE FROM usuario_pivot_permiso_usuario WHERE id_usuario = %s", (usuario_id,))
        
        # Asignar nuevos permisos
        for permiso_id in permisos_ids:
            cursor.execute("""
                INSERT INTO usuario_pivot_permiso_usuario (id_usuario, id_permiso)
                VALUES (%s, %s)
            """, (usuario_id, permiso_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Permisos asignados correctamente",
            "usuario_id": usuario_id,
            "permisos_asignados": len(permisos_ids)
        }), 200
        
    except Exception as e:
        logger.error(f"Error asignando permisos: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 🔹 Asignar acceso a aplicaciones
@usuarios_bp.route('/<string:usuario_id>/aplicaciones', methods=['POST'])
@jwt_required()
def asignar_aplicaciones(usuario_id):
    """Asigna acceso a aplicaciones específicas a un usuario (TEMPORAL: permitido para todos los usuarios autenticados)"""
    # TEMPORAL: Permitir acceso a todos los usuarios autenticados
    # TODO: Restaurar verificación de admin cuando se implemente el sistema de permisos completo
    # usuario_logueado = get_jwt_identity()
    # if not verificar_admin(usuario_logueado):
    #     return jsonify({"error": "No autorizado"}), 403

    try:
        data = request.get_json()
        apps_ids = data.get('apps_ids', [])
        
        if not isinstance(apps_ids, list):
            return jsonify({"error": "apps_ids debe ser una lista"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT 1 FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verificar que todas las aplicaciones existen
        if apps_ids:
            placeholders = ','.join(['%s'] * len(apps_ids))
            cursor.execute(f"""
                SELECT id FROM general_dim_app 
                WHERE id IN ({placeholders})
            """, apps_ids)
            
            apps_validas = cursor.fetchall()
            if len(apps_validas) != len(apps_ids):
                cursor.close()
                conn.close()
                return jsonify({"error": "Una o más aplicaciones no existen"}), 400
        
        # Eliminar accesos actuales del usuario
        cursor.execute("DELETE FROM usuario_pivot_app_usuario WHERE id_usuario = %s", (usuario_id,))
        
        # Asignar nuevos accesos
        for app_id in apps_ids:
            cursor.execute("""
                INSERT INTO usuario_pivot_app_usuario (id_usuario, id_app)
                VALUES (%s, %s)
            """, (usuario_id, app_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Acceso a aplicaciones asignado correctamente",
            "usuario_id": usuario_id,
            "apps_asignadas": len(apps_ids)
        }), 200
        
    except Exception as e:
        logger.error(f"Error asignando aplicaciones: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINTS EXISTENTES (MANTENER)
# ============================================================================

# 🔹 Obtener sucursal activa del usuario logueado
@usuarios_bp.route('/sucursal', methods=['GET'])
@jwt_required()
def obtener_sucursal_usuario():
    try:
        usuario_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_sucursalactiva FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if not usuario or not usuario['id_sucursalactiva']:
            return jsonify({"error": "Usuario no encontrado o sin sucursal asignada"}), 404

        return jsonify({"id_sucursal": usuario['id_sucursalactiva']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 🔹 Actualizar sucursal activa del usuario logueado
@usuarios_bp.route('/sucursal-activa', methods=['POST'])
@jwt_required()
def actualizar_sucursal_activa():
    try:
        usuario_id = get_jwt_identity()
        data = request.json
        nueva_sucursal = data.get("id_sucursal")

        if not nueva_sucursal:
            return jsonify({"error": "Sucursal no especificada"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar que el usuario tenga acceso a la sucursal
        cursor.execute("""
            SELECT 1 
            FROM usuario_pivot_sucursal_usuario 
            WHERE id_usuario = %s AND id_sucursal = %s
        """, (usuario_id, nueva_sucursal))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "No tienes acceso a esta sucursal"}), 403

        # Actualizar la sucursal activa
        cursor.execute("""
            UPDATE general_dim_usuario 
            SET id_sucursalactiva = %s 
            WHERE id = %s
        """, (nueva_sucursal, usuario_id))
        
        conn.commit()

        # Obtener el nombre de la sucursal para la respuesta
        cursor.execute("""
            SELECT nombre 
            FROM general_dim_sucursal 
            WHERE id = %s
        """, (nueva_sucursal,))
        
        sucursal = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Sucursal actualizada correctamente",
            "id_sucursal": nueva_sucursal,
            "sucursal_nombre": sucursal['nombre'] if sucursal else None
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Obtener sucursal activa del usuario logueado
@usuarios_bp.route('/sucursal-activa', methods=['GET'])
@jwt_required()
def obtener_sucursal_activa():
    usuario_id = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_sucursalactiva FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if not usuario or usuario['id_sucursalactiva'] is None:
            return jsonify({"error": "No se encontró la sucursal activa"}), 404

        return jsonify({"sucursal_activa": usuario['id_sucursalactiva']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener todas las sucursales disponibles (para crear usuarios)
@usuarios_bp.route('/sucursales', methods=['GET'])
@jwt_required()
def obtener_sucursales():
    usuario_id = get_jwt_identity()
    if not verificar_admin(usuario_id):
        return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener solo sucursales con id_sucursaltipo = 1
        cursor.execute("""
            SELECT id, nombre, ubicacion
            FROM general_dim_sucursal
            WHERE id_sucursaltipo = 1
            ORDER BY nombre ASC
        """)
        
        sucursales = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(sucursales), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener sucursales permitidas de un usuario
@usuarios_bp.route('/<string:usuario_id>/sucursales-permitidas', methods=['GET'])
@jwt_required()
def obtener_sucursales_permitidas(usuario_id):
    usuario_logueado = get_jwt_identity()
    if not verificar_admin(usuario_logueado):
        return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener las sucursales permitidas del usuario
        cursor.execute("""
            SELECT s.id, s.nombre, s.ubicacion
            FROM general_dim_sucursal s
            INNER JOIN usuario_pivot_sucursal_usuario p ON s.id = p.id_sucursal
            WHERE p.id_usuario = %s AND s.id_sucursaltipo = 1
            ORDER BY s.nombre ASC
        """, (usuario_id,))
        
        sucursales_permitidas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(sucursales_permitidas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Asignar sucursales permitidas a un usuario
@usuarios_bp.route('/<string:usuario_id>/sucursales-permitidas', methods=['POST'])
@jwt_required()
def asignar_sucursales_permitidas(usuario_id):
    usuario_logueado = get_jwt_identity()
    if not verificar_admin(usuario_logueado):
        return jsonify({"error": "No autorizado"}), 403

    data = request.json
    sucursales_ids = data.get('sucursales_ids', [])  # Lista de IDs de sucursales

    if not isinstance(sucursales_ids, list):
        return jsonify({"error": "sucursales_ids debe ser una lista"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Verificar que todas las sucursales existen y son del tipo correcto
        if sucursales_ids:
            placeholders = ','.join(['%s'] * len(sucursales_ids))
            cursor.execute(f"""
                SELECT id FROM general_dim_sucursal 
                WHERE id IN ({placeholders}) AND id_sucursaltipo = 1
            """, sucursales_ids)
            sucursales_validas = cursor.fetchall()
            
            if len(sucursales_validas) != len(sucursales_ids):
                cursor.close()
                conn.close()
                return jsonify({"error": "Una o más sucursales no existen o no son del tipo correcto"}), 400

        # Eliminar todas las asignaciones actuales del usuario
        cursor.execute("DELETE FROM usuario_pivot_sucursal_usuario WHERE id_usuario = %s", (usuario_id,))
        
        # Insertar las nuevas asignaciones
        if sucursales_ids:
            for sucursal_id in sucursales_ids:
                cursor.execute("""
                    INSERT INTO usuario_pivot_sucursal_usuario (id_sucursal, id_usuario)
                    VALUES (%s, %s)
                """, (sucursal_id, usuario_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Sucursales permitidas asignadas correctamente",
            "usuario_id": usuario_id,
            "sucursales_asignadas": len(sucursales_ids)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar todas las sucursales permitidas de un usuario
@usuarios_bp.route('/<string:usuario_id>/sucursales-permitidas', methods=['DELETE'])
@jwt_required()
def eliminar_sucursales_permitidas(usuario_id):
    usuario_logueado = get_jwt_identity()
    if not verificar_admin(usuario_logueado):
        return jsonify({"error": "No autorizado"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id FROM general_dim_usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Eliminar todas las asignaciones del usuario
        cursor.execute("DELETE FROM usuario_pivot_sucursal_usuario WHERE id_usuario = %s", (usuario_id,))
        filas_eliminadas = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Sucursales permitidas eliminadas correctamente",
            "usuario_id": usuario_id,
            "sucursales_eliminadas": filas_eliminadas
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

