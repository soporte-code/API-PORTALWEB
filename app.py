from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS
from datetime import timedelta
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
def create_app():
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, resources={
        r"/*": {
            "origins": [
                # Dominio personalizado principal
                "https://portal-web.lahornilla.cl",
                # Dominios de producción Firebase
                "https://front-portalweb.web.app",
                "https://front-portalweb.firebaseapp.com",
                # Dominios de desarrollo local
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:*", 
                "http://192.168.1.52:*", 
                "http://192.168.1.208:*", 
                "http://192.168.1.60:*"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    })

    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=10)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    jwt = JWTManager(app)

    # Registrar los blueprints
    from blueprints.usuarios import usuarios_bp
    from blueprints.auth import auth_bp
    from blueprints.opciones import opciones_bp
    from blueprints.cuarteles import cuarteles_bp
    from blueprints.hileras import hileras_bp
    from blueprints.plantas import plantas_bp
    from blueprints.mapeo import mapeo_bp
    from blueprints.variedades import variedades_bp
    from blueprints.conteo import conteo_bp

    
    # Registrar blueprints
    
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(opciones_bp, url_prefix="/api/opciones")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(cuarteles_bp, url_prefix="/api")
    app.register_blueprint(hileras_bp, url_prefix="/api/hileras")
    app.register_blueprint(plantas_bp, url_prefix="/api/plantas")
    app.register_blueprint(mapeo_bp, url_prefix="/api/mapeo")
    app.register_blueprint(variedades_bp, url_prefix="/api/variedades")
    app.register_blueprint(conteo_bp, url_prefix="/api/conteo")

    # Crear un nuevo blueprint para las rutas raíz
    root_bp = Blueprint('root_bp', __name__)
    
    # Importar y registrar las rutas raíz
    from blueprints.opciones import obtener_sucursales
    root_bp.add_url_rule('/sucursales/', 'obtener_sucursales', obtener_sucursales, methods=['GET', 'OPTIONS'])

    # Endpoints de atributos y especies para CORS
    @root_bp.route('/atributos', methods=['GET'])
    def listar_atributos():
        """
        Listar todos los atributos base
        """
        try:
            from utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    id,
                    nombre,
                    descripcion,
                    id_estado
                FROM conteo_dim_atributo
                WHERE id_estado = 1
                ORDER BY nombre
            """
            
            cursor.execute(query)
            atributos = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": "Atributos obtenidos exitosamente",
                "data": {
                    "atributos": atributos,
                    "total": len(atributos)
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo atributos: {str(e)}")
            # Si la tabla no existe, retornar lista vacía
            if "doesn't exist" in str(e) or "Unknown table" in str(e):
                return jsonify({
                    "success": True,
                    "message": "Tabla de atributos no existe aún",
                    "data": {
                        "atributos": [],
                        "total": 0
                    }
                }), 200
            return jsonify({
                "success": False,
                "message": "Error interno del servidor",
                "error": str(e)
            }), 500

    @root_bp.route('/atributos/<int:atributo_id>', methods=['GET'])
    def obtener_atributo(atributo_id):
        """
        Obtener un atributo específico
        """
        try:
            from utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    id,
                    nombre,
                    descripcion,
                    id_estado
                FROM conteo_dim_atributo
                WHERE id = %s AND id_estado = 1
            """
            
            cursor.execute(query, (atributo_id,))
            atributo = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not atributo:
                return jsonify({
                    "success": False,
                    "message": "Atributo no encontrado"
                }), 404
            
            return jsonify({
                "success": True,
                "message": "Atributo obtenido exitosamente",
                "data": atributo
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo atributo {atributo_id}: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Error interno del servidor",
                "error": str(e)
            }), 500

    @root_bp.route('/especies', methods=['GET'])
    def listar_especies():
        """
        Listar todas las especies
        """
        try:
            from utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    id,
                    nombre,
                    caja_equivalente,
                    id_estado
                FROM general_dim_especie
                WHERE id_estado = 1
                ORDER BY nombre
            """
            
            cursor.execute(query)
            especies = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": "Especies obtenidas exitosamente",
                "data": {
                    "especies": especies,
                    "total": len(especies)
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo especies: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Error interno del servidor",
                "error": str(e)
            }), 500

    @root_bp.route('/especies/<int:especie_id>', methods=['GET'])
    def obtener_especie(especie_id):
        """
        Obtener una especie específica
        """
        try:
            from utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    id,
                    nombre,
                    caja_equivalente,
                    id_estado
                FROM general_dim_especie
                WHERE id = %s AND id_estado = 1
            """
            
            cursor.execute(query, (especie_id,))
            especie = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not especie:
                return jsonify({
                    "success": False,
                    "message": "Especie no encontrada"
                }), 404
            
            return jsonify({
                "success": True,
                "message": "Especie obtenida exitosamente",
                "data": especie
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo especie {especie_id}: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Error interno del servidor",
                "error": str(e)
            }), 500

    # Endpoint de prueba para verificar conexión a BD
    @root_bp.route('/test-db', methods=['GET'])
    def test_database():
        try:
            logger.info("🔍 Iniciando prueba de conexión a BD...")
            from utils.db import get_db_connection
            logger.info(f"📊 Configuración: DATABASE_URL={getattr(Config, 'DATABASE_URL', 'No definido')}")
            
            conn = get_db_connection()
            logger.info("✅ Conexión establecida")
            
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"📊 MySQL Version: {version[0]}")
            
            cursor.close()
            conn.close()
            logger.info("✅ Prueba completada exitosamente")
            
            return {"status": "success", "message": "Conexión exitosa", "mysql_version": version[0]}, 200
        except Exception as e:
            logger.error(f"❌ Error en prueba de BD: {str(e)}")
            return {"status": "error", "message": str(e)}, 500
    
    # Endpoint de configuración para debug
    @root_bp.route('/config', methods=['GET'])
    def show_config():
        try:
            config_info = {
                "DATABASE_URL": getattr(Config, 'DATABASE_URL', 'No definido'),
                "DB_HOST": getattr(Config, 'DB_HOST', 'No definido'),
                "DB_USER": getattr(Config, 'DB_USER', 'No definido'),
                "DB_NAME": getattr(Config, 'DB_NAME', 'No definido'),
                "K_SERVICE": os.getenv('K_SERVICE', 'No definido'),
                "FLASK_ENV": os.getenv('FLASK_ENV', 'No definido')
            }
            return {"status": "success", "config": config_info}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    
    # Registrar el blueprint raíz
    app.register_blueprint(root_bp, url_prefix="/api")

    return app

# Crear una única instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Obtener el puerto de la variable de entorno PORT (requerido por Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

