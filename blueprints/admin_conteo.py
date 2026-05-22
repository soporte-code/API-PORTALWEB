"""Blueprint admin_conteo — endpoints de configuracion del modulo Conteo.

Sirve la edicion de catalogos y reglas que la app movil LH Conteo lee:
  - atributos del cultivo (catalogo)
  - labores de conteo (catalogo)
  - asociaciones labor + especie (que combos son validos + a_supervisar)
  - configuracion del formulario (que atributos se piden por combinacion + cantidad/subdivision)

NO toca las tablas de pauta (conteo_fact_pauta y derivadas) — esas se gestionan
desde otra plataforma segun decision del 2026-04-28.

Patron:
  - jsonify de listas para los GET de coleccion
  - {"error": "..."} para errores con HTTP code
  - jwt_required en todos los endpoints (consistente con usuarios.py)
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from utils.db import get_db_connection

logger = logging.getLogger(__name__)
admin_conteo_bp = Blueprint("admin_conteo_bp", __name__)


# ============================================================================
# Helpers
# ============================================================================

def _bad_request(msg: str):
    return jsonify({"error": msg}), 400


def _not_found(msg: str = "No encontrado"):
    return jsonify({"error": msg}), 404


# ============================================================================
# DEBUG (sin auth) — quitar despues
# ============================================================================

@admin_conteo_bp.route("/_debug/config/<int:conteotipo_id>", methods=["GET"])
def _debug_config(conteotipo_id: int):
    """Endpoint diagnostico, sin auth. Devuelve el raw de configconteo +
    indica si la columna id_atributo_padre existe y su valor por fila."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'conteo_dim_configconteo'
              AND column_name = 'id_atributo_padre'
            """
        )
        columna_existe = cursor.fetchone() is not None
        cursor.execute(
            """
            SELECT cc.id, cc.id_atributo, cc.id_atributo_padre,
                   a.nombre AS atributo_nombre,
                   ap.nombre AS padre_nombre
            FROM conteo_dim_configconteo cc
            INNER JOIN conteo_dim_atributocultivo a ON cc.id_atributo = a.id
            LEFT JOIN conteo_dim_atributocultivo ap ON cc.id_atributo_padre = ap.id
            WHERE cc.id_conteotipo = %s
            ORDER BY cc.orden, a.nombre
            """,
            (conteotipo_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            "conteotipo_id": conteotipo_id,
            "columna_id_atributo_padre_existe": columna_existe,
            "rows": rows,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500


def _server_error(e: Exception):
    logger.exception("admin_conteo: %s", e)
    return jsonify({"error": str(e)}), 500


# ============================================================================
# 1. ATRIBUTOS DE CULTIVO  (conteo_dim_atributocultivo)
# ============================================================================

# Tipos de campo permitidos. Si llega cualquier otro, se rechaza.
TIPOS_CAMPO_VALIDOS = {"decimal", "entero", "porcentaje", "si_no", "seleccion"}


def _normalizar_atributo(data: dict) -> dict:
    """Normaliza/valida campos de un atributo. Devuelve dict listo para SQL.
    Lanza ValueError con mensaje legible si algo no cuadra."""
    out: dict = {}

    nombre = (data.get("nombre") or "").strip().upper()
    if not nombre:
        raise ValueError("Falta nombre")
    out["nombre"] = nombre

    tipo = (data.get("tipo_campo") or "decimal").strip().lower()
    if tipo not in TIPOS_CAMPO_VALIDOS:
        raise ValueError(f"tipo_campo invalido. Validos: {sorted(TIPOS_CAMPO_VALIDOS)}")
    out["tipo_campo"] = tipo

    # Solo si decimal: decimales 0-3
    decimales = data.get("decimales", 2 if tipo == "decimal" else 0)
    try:
        decimales = max(0, min(3, int(decimales)))
    except (TypeError, ValueError):
        decimales = 0
    out["decimales"] = decimales if tipo == "decimal" else 0

    # min/max numericos opcionales (no aplican a si_no/seleccion)
    if tipo in ("decimal", "entero", "porcentaje"):
        out["min_valor"] = _to_decimal(data.get("min_valor"))
        out["max_valor"] = _to_decimal(data.get("max_valor"))
        if (
            out["min_valor"] is not None
            and out["max_valor"] is not None
            and out["min_valor"] > out["max_valor"]
        ):
            raise ValueError("min_valor no puede ser mayor que max_valor")
    else:
        out["min_valor"] = None
        out["max_valor"] = None

    # Unidad: solo si decimal/entero/porcentaje (en porcentaje queda fijo "%")
    if tipo == "porcentaje":
        out["unidad"] = "%"
    elif tipo in ("decimal", "entero"):
        u = (data.get("unidad") or "").strip()
        out["unidad"] = u or None
    else:
        out["unidad"] = None

    # Opciones: solo si tipo=seleccion. JSON con lista de strings no vacios.
    if tipo == "seleccion":
        opciones = data.get("opciones")
        if not isinstance(opciones, list) or not opciones:
            raise ValueError("Para tipo seleccion, opciones debe ser una lista no vacia")
        opciones = [str(o).strip() for o in opciones if str(o).strip()]
        if not opciones:
            raise ValueError("Las opciones no pueden estar vacias")
        out["opciones"] = opciones  # se serializa con json.dumps al guardar
    else:
        out["opciones"] = None

    ayuda = (data.get("ayuda") or "").strip()
    out["ayuda"] = ayuda or None

    id_estado = data.get("id_estado", 1)
    try:
        id_estado = int(id_estado)
    except (TypeError, ValueError):
        id_estado = 1
    out["id_estado"] = 1 if id_estado not in (1, 2) else id_estado

    out["id_empresa"] = data.get("id_empresa")  # NULL = global

    return out


def _to_decimal(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@admin_conteo_bp.route("/atributos", methods=["GET"])
@jwt_required()
def listar_atributos():
    try:
        import json as _json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.id, a.nombre, a.tipo_campo, a.unidad,
                   a.min_valor, a.max_valor, a.decimales, a.opciones,
                   a.ayuda, a.id_estado, a.id_empresa,
                   (SELECT COUNT(*) FROM conteo_dim_configconteo cc
                    WHERE cc.id_atributo = a.id) AS uso_en_config,
                   (SELECT COUNT(*) FROM conteo_pivot_atributo_especie pae
                    WHERE pae.id_atributo = a.id) AS uso_en_especies
            FROM conteo_dim_atributocultivo a
            ORDER BY a.nombre
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Parsear opciones JSON a lista para que el front no tenga que parsearlo
        for r in rows:
            if r.get("opciones") and isinstance(r["opciones"], str):
                try:
                    r["opciones"] = _json.loads(r["opciones"])
                except Exception:
                    r["opciones"] = None
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/atributos", methods=["POST"])
@jwt_required()
def crear_atributo():
    try:
        import json as _json
        data = request.get_json() or {}
        try:
            v = _normalizar_atributo(data)
        except ValueError as ve:
            return _bad_request(str(ve))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM conteo_dim_atributocultivo WHERE nombre = %s", (v["nombre"],)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Ya existe un atributo con ese nombre")

        cursor.execute(
            """
            INSERT INTO conteo_dim_atributocultivo
              (nombre, tipo_campo, unidad, min_valor, max_valor, decimales,
               opciones, ayuda, id_estado, id_empresa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                v["nombre"], v["tipo_campo"], v["unidad"],
                v["min_valor"], v["max_valor"], v["decimales"],
                _json.dumps(v["opciones"]) if v["opciones"] is not None else None,
                v["ayuda"], v["id_estado"], v["id_empresa"],
            ),
        )
        new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": new_id, "nombre": v["nombre"]}), 201
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/atributos/<int:atributo_id>", methods=["PUT"])
@jwt_required()
def actualizar_atributo(atributo_id: int):
    try:
        import json as _json
        data = request.get_json() or {}
        try:
            v = _normalizar_atributo(data)
        except ValueError as ve:
            return _bad_request(str(ve))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM conteo_dim_atributocultivo WHERE id = %s", (atributo_id,)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return _not_found("Atributo no encontrado")

        cursor.execute(
            "SELECT id FROM conteo_dim_atributocultivo WHERE nombre = %s AND id <> %s",
            (v["nombre"], atributo_id),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Ya existe otro atributo con ese nombre")

        cursor.execute(
            """
            UPDATE conteo_dim_atributocultivo
            SET nombre = %s, tipo_campo = %s, unidad = %s,
                min_valor = %s, max_valor = %s, decimales = %s,
                opciones = %s, ayuda = %s, id_estado = %s, id_empresa = %s
            WHERE id = %s
            """,
            (
                v["nombre"], v["tipo_campo"], v["unidad"],
                v["min_valor"], v["max_valor"], v["decimales"],
                _json.dumps(v["opciones"]) if v["opciones"] is not None else None,
                v["ayuda"], v["id_estado"], v["id_empresa"],
                atributo_id,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Atributo actualizado", "id": atributo_id}), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/atributos/<int:atributo_id>", methods=["DELETE"])
@jwt_required()
def eliminar_atributo(atributo_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Bloquear borrado si tiene uso
        cursor.execute(
            "SELECT COUNT(*) AS n FROM conteo_dim_configconteo WHERE id_atributo = %s",
            (atributo_id,),
        )
        if cursor.fetchone()["n"] > 0:
            cursor.close()
            conn.close()
            return _bad_request(
                "No se puede eliminar: el atributo esta en uso en configuraciones de formulario"
            )

        cursor.execute(
            "SELECT COUNT(*) AS n FROM conteo_fact_detalleconteo WHERE id_atributo = %s",
            (atributo_id,),
        )
        if cursor.fetchone()["n"] > 0:
            cursor.close()
            conn.close()
            return _bad_request(
                "No se puede eliminar: hay conteos historicos que usan este atributo"
            )

        cursor.execute(
            "DELETE FROM conteo_dim_atributocultivo WHERE id = %s", (atributo_id,)
        )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Atributo no encontrado")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Atributo eliminado"}), 200
    except Exception as e:
        return _server_error(e)


# ============================================================================
# 2. LABORES DE CONTEO  (conteo_dim_laborconteo)
# ============================================================================

@admin_conteo_bp.route("/labores", methods=["GET"])
@jwt_required()
def listar_labores():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT l.id, l.nombre,
                   (SELECT COUNT(*) FROM conteo_pivot_labor_especie ple
                    WHERE ple.id_labor = l.id) AS asociaciones
            FROM conteo_dim_laborconteo l
            ORDER BY l.nombre
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labores", methods=["POST"])
@jwt_required()
def crear_labor():
    try:
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip().upper()
        if not nombre:
            return _bad_request("Falta nombre")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM conteo_dim_laborconteo WHERE nombre = %s", (nombre,)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Ya existe una labor con ese nombre")

        cursor.execute(
            "INSERT INTO conteo_dim_laborconteo (nombre) VALUES (%s)", (nombre,)
        )
        new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": new_id, "nombre": nombre}), 201
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labores/<int:labor_id>", methods=["PUT"])
@jwt_required()
def actualizar_labor(labor_id: int):
    try:
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip().upper()
        if not nombre:
            return _bad_request("Falta nombre")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM conteo_dim_laborconteo WHERE id = %s", (labor_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return _not_found("Labor no encontrada")

        cursor.execute(
            "SELECT id FROM conteo_dim_laborconteo WHERE nombre = %s AND id <> %s",
            (nombre, labor_id),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Ya existe otra labor con ese nombre")

        cursor.execute(
            "UPDATE conteo_dim_laborconteo SET nombre = %s WHERE id = %s",
            (nombre, labor_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Labor actualizada", "id": labor_id}), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labores/<int:labor_id>", methods=["DELETE"])
@jwt_required()
def eliminar_labor(labor_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS n FROM conteo_pivot_labor_especie WHERE id_labor = %s",
            (labor_id,),
        )
        if cursor.fetchone()["n"] > 0:
            cursor.close()
            conn.close()
            return _bad_request(
                "No se puede eliminar: la labor esta asociada a especies"
            )

        cursor.execute("DELETE FROM conteo_dim_laborconteo WHERE id = %s", (labor_id,))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Labor no encontrada")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Labor eliminada"}), 200
    except Exception as e:
        return _server_error(e)


# ============================================================================
# 3. ESPECIES (solo lectura — el catalogo se gestiona desde otro modulo)
# ============================================================================

@admin_conteo_bp.route("/especies", methods=["GET"])
@jwt_required()
def listar_especies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nombre, caja_equivalente
            FROM general_dim_especie
            ORDER BY nombre
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


# ============================================================================
# 4. ASOCIACIONES LABOR + ESPECIE  (conteo_pivot_labor_especie)
# ============================================================================

@admin_conteo_bp.route("/labor-especie", methods=["GET"])
@jwt_required()
def listar_labor_especie():
    """Devuelve cada combinacion con nombres legibles + numero de atributos
    configurados en el formulario. Util para flagear filas vacias."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
              ple.id,
              ple.id_labor,
              l.nombre AS labor_nombre,
              ple.id_especie,
              e.nombre AS especie_nombre,
              ple.a_supervisar,
              ple.id_estado,
              (SELECT COUNT(*) FROM conteo_dim_configconteo cc
               WHERE cc.id_conteotipo = ple.id) AS atributos_configurados
            FROM conteo_pivot_labor_especie ple
            LEFT JOIN conteo_dim_laborconteo l ON ple.id_labor = l.id
            LEFT JOIN general_dim_especie e ON ple.id_especie = e.id
            ORDER BY l.nombre, e.nombre
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labor-especie", methods=["POST"])
@jwt_required()
def crear_labor_especie():
    try:
        data = request.get_json() or {}
        id_labor = data.get("id_labor")
        id_especie = data.get("id_especie")
        a_supervisar = 1 if data.get("a_supervisar") else 0
        id_estado = int(data.get("id_estado") or 1)

        if not id_labor or not id_especie:
            return _bad_request("Faltan id_labor o id_especie")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id FROM conteo_pivot_labor_especie
            WHERE id_labor = %s AND id_especie = %s
            """,
            (id_labor, id_especie),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Esa combinacion labor + especie ya existe")

        cursor.execute(
            """
            INSERT INTO conteo_pivot_labor_especie
              (id_labor, id_especie, a_supervisar, id_estado)
            VALUES (%s, %s, %s, %s)
            """,
            (id_labor, id_especie, a_supervisar, id_estado),
        )
        new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": new_id}), 201
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labor-especie/<int:assoc_id>", methods=["PUT"])
@jwt_required()
def actualizar_labor_especie(assoc_id: int):
    """Permite cambiar a_supervisar y id_estado. NO permite cambiar id_labor /
    id_especie — para eso se borra y se crea otra (mantiene integridad de los
    conteos historicos)."""
    try:
        data = request.get_json() or {}
        sets = []
        vals = []
        if "a_supervisar" in data:
            sets.append("a_supervisar = %s")
            vals.append(1 if data["a_supervisar"] else 0)
        if "id_estado" in data:
            sets.append("id_estado = %s")
            vals.append(int(data["id_estado"]))
        if not sets:
            return _bad_request("Sin cambios")

        vals.append(assoc_id)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"UPDATE conteo_pivot_labor_especie SET {', '.join(sets)} WHERE id = %s",
            vals,
        )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Asociacion no encontrada")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Asociacion actualizada", "id": assoc_id}), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/labor-especie/<int:assoc_id>", methods=["DELETE"])
@jwt_required()
def eliminar_labor_especie(assoc_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS n FROM conteo_fact_conteo WHERE id_laborespecie = %s",
            (assoc_id,),
        )
        if cursor.fetchone()["n"] > 0:
            cursor.close()
            conn.close()
            return _bad_request(
                "No se puede eliminar: hay conteos historicos con esta asociacion. "
                "Cambia el estado a Inactivo en su lugar."
            )

        # Eliminar tambien las configuraciones de formulario asociadas
        cursor.execute(
            "DELETE FROM conteo_dim_configconteo WHERE id_conteotipo = %s",
            (assoc_id,),
        )
        cursor.execute(
            "DELETE FROM conteo_pivot_labor_especie WHERE id = %s", (assoc_id,)
        )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Asociacion no encontrada")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Asociacion eliminada"}), 200
    except Exception as e:
        return _server_error(e)


# ============================================================================
# 5. CONFIGURACION DEL FORMULARIO  (conteo_dim_configconteo)
#    Modela: por cada combinacion labor+especie (id_conteotipo), que atributos
#    se piden y como (cantidad_atributo, muestra_sub_div).
# ============================================================================

@admin_conteo_bp.route("/config-formulario", methods=["GET"])
@jwt_required()
def listar_config_formulario():
    """Lista todas las filas de config con sus nombres legibles."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
              cc.id,
              cc.id_empresa,
              cc.id_conteotipo,
              cc.id_atributo,
              cc.muestra_sub_div,
              cc.cantidad_atributo,
              cc.orden,
              cc.id_estado,
              a.nombre AS atributo_nombre,
              a.tipo_campo,
              a.unidad,
              ple.id_labor,
              ple.id_especie,
              l.nombre AS labor_nombre,
              e.nombre AS especie_nombre
            FROM conteo_dim_configconteo cc
            LEFT JOIN conteo_dim_atributocultivo a ON cc.id_atributo = a.id
            LEFT JOIN conteo_pivot_labor_especie ple ON ple.id = cc.id_conteotipo
            LEFT JOIN conteo_dim_laborconteo l ON ple.id_labor = l.id
            LEFT JOIN general_dim_especie e ON ple.id_especie = e.id
            ORDER BY l.nombre, e.nombre, cc.orden
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/config-formulario/<int:conteotipo_id>", methods=["GET"])
@jwt_required()
def listar_config_por_conteotipo(conteotipo_id: int):
    """Atributos configurados para una combinacion labor+especie especifica.
    Devuelve TODA la metadata del atributo para que el portal pueda mostrar
    preview sin hacer joins adicionales."""
    try:
        import json as _json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Defensivo: con/sin columna id_atributo_padre segun BD.
        try:
            cursor.execute(
                """
                SELECT cc.id, cc.id_empresa, cc.id_atributo, cc.muestra_sub_div,
                       cc.cantidad_atributo, cc.orden, cc.id_estado,
                       cc.id_atributo_padre,
                       a.nombre AS atributo_nombre,
                       a.tipo_campo, a.unidad,
                       a.min_valor, a.max_valor, a.decimales,
                       a.opciones, a.ayuda
                FROM conteo_dim_configconteo cc
                LEFT JOIN conteo_dim_atributocultivo a ON cc.id_atributo = a.id
                WHERE cc.id_conteotipo = %s
                ORDER BY cc.orden, a.nombre
                """,
                (conteotipo_id,),
            )
        except Exception:
            cursor.execute(
                """
                SELECT cc.id, cc.id_empresa, cc.id_atributo, cc.muestra_sub_div,
                       cc.cantidad_atributo, cc.orden, cc.id_estado,
                       a.nombre AS atributo_nombre,
                       a.tipo_campo, a.unidad,
                       a.min_valor, a.max_valor, a.decimales,
                       a.opciones, a.ayuda
                FROM conteo_dim_configconteo cc
                LEFT JOIN conteo_dim_atributocultivo a ON cc.id_atributo = a.id
                WHERE cc.id_conteotipo = %s
                ORDER BY cc.orden, a.nombre
                """,
                (conteotipo_id,),
            )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for r in rows:
            if r.get("opciones") and isinstance(r["opciones"], str):
                try:
                    r["opciones"] = _json.loads(r["opciones"])
                except Exception:
                    r["opciones"] = None
            # Aseguramos que la key exista aunque la columna falte en BD.
            r.setdefault("id_atributo_padre", None)
        return jsonify(rows), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/config-formulario", methods=["POST"])
@jwt_required()
def crear_config_formulario():
    try:
        data = request.get_json() or {}
        id_conteotipo = data.get("id_conteotipo")
        id_atributo = data.get("id_atributo")
        muestra_sub_div = 1 if data.get("muestra_sub_div") else 0
        cantidad_atributo = max(1, int(data.get("cantidad_atributo") or 1))
        id_empresa = int(data.get("id_empresa") or 1)
        id_atributo_padre = data.get("id_atributo_padre")
        if id_atributo_padre is not None:
            id_atributo_padre = int(id_atributo_padre)

        if not id_conteotipo or not id_atributo:
            return _bad_request("Faltan id_conteotipo o id_atributo")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id FROM conteo_dim_configconteo
            WHERE id_conteotipo = %s AND id_atributo = %s AND id_empresa = %s
            """,
            (id_conteotipo, id_atributo, id_empresa),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return _bad_request("Ese atributo ya esta configurado para esta combinacion")

        # id de configconteo no es auto_increment — calculamos el siguiente
        cursor.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM conteo_dim_configconteo"
        )
        new_id = cursor.fetchone()["next_id"]

        # Orden por default: ultimo + 10 dentro del mismo conteotipo
        cursor.execute(
            """
            SELECT COALESCE(MAX(orden), 0) + 10 AS next_orden
            FROM conteo_dim_configconteo
            WHERE id_conteotipo = %s
            """,
            (id_conteotipo,),
        )
        next_orden = cursor.fetchone()["next_orden"]

        # Insert con/sin id_atributo_padre segun si la columna existe en BD.
        # Mientras la migracion no este aplicada, omitimos la columna.
        try:
            cursor.execute(
                """
                INSERT INTO conteo_dim_configconteo
                  (id, id_empresa, id_conteotipo, id_atributo,
                   muestra_sub_div, cantidad_atributo, orden, id_estado,
                   id_atributo_padre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
                """,
                (new_id, id_empresa, id_conteotipo, id_atributo,
                 muestra_sub_div, cantidad_atributo, next_orden,
                 id_atributo_padre),
            )
        except Exception:
            conn.rollback()
            cursor.execute(
                """
                INSERT INTO conteo_dim_configconteo
                  (id, id_empresa, id_conteotipo, id_atributo,
                   muestra_sub_div, cantidad_atributo, orden, id_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """,
                (new_id, id_empresa, id_conteotipo, id_atributo,
                 muestra_sub_div, cantidad_atributo, next_orden),
            )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": new_id, "orden": next_orden}), 201
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/config-formulario/<int:cfg_id>", methods=["PUT"])
@jwt_required()
def actualizar_config_formulario(cfg_id: int):
    try:
        data = request.get_json() or {}
        sets = []
        vals = []
        if "muestra_sub_div" in data:
            sets.append("muestra_sub_div = %s")
            vals.append(1 if data["muestra_sub_div"] else 0)
        if "cantidad_atributo" in data:
            sets.append("cantidad_atributo = %s")
            vals.append(max(1, int(data["cantidad_atributo"])))
        if "id_atributo" in data:
            sets.append("id_atributo = %s")
            vals.append(int(data["id_atributo"]))
        if "orden" in data:
            sets.append("orden = %s")
            vals.append(int(data["orden"]))
        if "id_estado" in data:
            sets.append("id_estado = %s")
            vals.append(int(data["id_estado"]))
        # id_atributo_padre puede ser null para quitar la relacion. Lo agregamos
        # al SET de forma opcional para que el UPDATE no falle si la columna
        # aun no existe en BD.
        incluir_padre = "id_atributo_padre" in data
        valor_padre = None
        if incluir_padre:
            raw = data["id_atributo_padre"]
            valor_padre = int(raw) if raw is not None else None
        if not sets and not incluir_padre:
            return _bad_request("Sin cambios")

        vals.append(cfg_id)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if incluir_padre:
            try:
                sets_padre = sets + ["id_atributo_padre = %s"]
                vals_padre = vals[:-1] + [valor_padre, cfg_id]
                cursor.execute(
                    f"UPDATE conteo_dim_configconteo SET {', '.join(sets_padre)} WHERE id = %s",
                    vals_padre,
                )
            except Exception:
                # Columna no existe aun — actualizamos lo demas sin padre.
                conn.rollback()
                if sets:
                    cursor.execute(
                        f"UPDATE conteo_dim_configconteo SET {', '.join(sets)} WHERE id = %s",
                        vals,
                    )
        else:
            cursor.execute(
                f"UPDATE conteo_dim_configconteo SET {', '.join(sets)} WHERE id = %s",
                vals,
            )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Configuracion no encontrada")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Configuracion actualizada", "id": cfg_id}), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/config-formulario/reordenar", methods=["POST"])
@jwt_required()
def reordenar_config_formulario():
    """Reordena en bloque los atributos de una combinacion. Body:
       { "id_conteotipo": 6, "orden": [12, 4, 7] }  // ids en el nuevo orden
    """
    try:
        data = request.get_json() or {}
        id_conteotipo = data.get("id_conteotipo")
        ids = data.get("orden") or []
        if not id_conteotipo or not isinstance(ids, list) or not ids:
            return _bad_request("Faltan id_conteotipo u orden")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for i, cfg_id in enumerate(ids, start=1):
                cursor.execute(
                    """
                    UPDATE conteo_dim_configconteo
                    SET orden = %s
                    WHERE id = %s AND id_conteotipo = %s
                    """,
                    (i * 10, int(cfg_id), id_conteotipo),
                )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        return jsonify({"message": "Orden actualizado", "total": len(ids)}), 200
    except Exception as e:
        return _server_error(e)


@admin_conteo_bp.route("/config-formulario/<int:cfg_id>", methods=["DELETE"])
@jwt_required()
def eliminar_config_formulario(cfg_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "DELETE FROM conteo_dim_configconteo WHERE id = %s", (cfg_id,)
        )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return _not_found("Configuracion no encontrada")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Configuracion eliminada"}), 200
    except Exception as e:
        return _server_error(e)


# ============================================================================
# 6. RENDER DEL FORMULARIO  (lo que consume la app movil)
#
# Este endpoint arma el JSON completo que necesita Flutter para pintar el
# formulario de un conteo. Acepta:
#   - id_conteotipo (= id de pivot_labor_especie)
#   - id_cuartel (opcional, para resolver subdivisiones reales)
#
# Devuelve cabecera + lista ordenada de atributos con toda su metadata.
# ============================================================================

@admin_conteo_bp.route("/render-formulario/<int:conteotipo_id>", methods=["GET"])
@jwt_required()
def render_formulario(conteotipo_id: int):
    """JSON listo para que Flutter renderice el formulario."""
    try:
        import json as _json
        cuartel_id = request.args.get("id_cuartel", type=int)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Cabecera: combinacion labor + especie
        cursor.execute(
            """
            SELECT ple.id, ple.id_labor, ple.id_especie, ple.a_supervisar,
                   ple.id_estado,
                   l.nombre AS labor_nombre,
                   e.nombre AS especie_nombre
            FROM conteo_pivot_labor_especie ple
            LEFT JOIN conteo_dim_laborconteo l ON ple.id_labor = l.id
            LEFT JOIN general_dim_especie e ON ple.id_especie = e.id
            WHERE ple.id = %s
            """,
            (conteotipo_id,),
        )
        cabecera = cursor.fetchone()
        if not cabecera:
            cursor.close()
            conn.close()
            return _not_found("Combinacion labor+especie no encontrada")

        if cabecera["id_estado"] != 1:
            cursor.close()
            conn.close()
            return _bad_request("Esta combinacion esta inactiva")

        # 2. Subdivisiones del cuartel (si se paso id_cuartel)
        subdivisiones = {"cantidad": 1, "tipo": None}
        if cuartel_id:
            cursor.execute(
                """
                SELECT c.subdivisionesplanta, cs.nombre AS tipo
                FROM general_dim_cuartel c
                LEFT JOIN general_dim_cuartelsubdivision cs ON c.id_tiposubdivision = cs.id
                WHERE c.id = %s
                """,
                (cuartel_id,),
            )
            cuartel = cursor.fetchone()
            if cuartel:
                subdivisiones = {
                    "cantidad": int(cuartel["subdivisionesplanta"] or 1),
                    "tipo": cuartel["tipo"],  # "BRAZO", "RAMILLA", etc o None
                }

        # 3. Atributos configurados — solo activos y ordenados
        cursor.execute(
            """
            SELECT cc.id AS config_id,
                   cc.id_atributo,
                   cc.cantidad_atributo,
                   cc.muestra_sub_div,
                   cc.orden,
                   a.nombre,
                   a.tipo_campo,
                   a.unidad,
                   a.min_valor,
                   a.max_valor,
                   a.decimales,
                   a.opciones,
                   a.ayuda
            FROM conteo_dim_configconteo cc
            INNER JOIN conteo_dim_atributocultivo a ON cc.id_atributo = a.id
            WHERE cc.id_conteotipo = %s
              AND cc.id_estado = 1
              AND a.id_estado = 1
            ORDER BY cc.orden, a.nombre
            """,
            (conteotipo_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        atributos = []
        for r in rows:
            opciones = r.get("opciones")
            if opciones and isinstance(opciones, str):
                try:
                    opciones = _json.loads(opciones)
                except Exception:
                    opciones = None
            atributos.append({
                "id": r["id_atributo"],
                "config_id": r["config_id"],
                "nombre": r["nombre"],
                "tipo": r["tipo_campo"],
                "unidad": r["unidad"],
                "min": float(r["min_valor"]) if r["min_valor"] is not None else None,
                "max": float(r["max_valor"]) if r["max_valor"] is not None else None,
                "decimales": int(r["decimales"] or 0),
                "opciones": opciones,
                "ayuda": r["ayuda"],
                "orden": int(r["orden"] or 0),
                "repeticiones": int(r["cantidad_atributo"] or 1),
                "por_subdivision": bool(r["muestra_sub_div"]),
            })

        return jsonify({
            "conteotipo": {
                "id": cabecera["id"],
                "id_labor": cabecera["id_labor"],
                "id_especie": cabecera["id_especie"],
                "labor": cabecera["labor_nombre"],
                "especie": cabecera["especie_nombre"],
                "a_supervisar": bool(cabecera["a_supervisar"]),
            },
            "subdivisiones": subdivisiones,
            "atributos": atributos,
        }), 200
    except Exception as e:
        return _server_error(e)
