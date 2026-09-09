import time, os, boto3
from fastapi import FastAPI, HTTPException

PREFIX = "/ms5"
athena = boto3.client("athena", region_name=os.environ.get("AWS_REGION", "us-east-1"))
DB = os.environ.get("GLUE_DATABASE", "transporte_urbano")
SALIDA = os.environ["ATHENA_OUTPUT"]

app = FastAPI(title="MS5 - Analitico (Athena)", version="1.0.0",
              docs_url=f"{PREFIX}/docs", openapi_url=f"{PREFIX}/openapi.json")


@app.get(f"{PREFIX}/health")
def health():
    return {"status": "ok", "servicio": "ms5"}


def numero(v):
    if v is None:
        return None
    try:
        return int(v) if "." not in v else round(float(v), 2)
    except ValueError:
        return v


def consultar(sql: str, espera_max: int = 60):
    eid = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": DB},
        ResultConfiguration={"OutputLocation": SALIDA},
    )["QueryExecutionId"]

    for _ in range(espera_max):
        estado = athena.get_query_execution(QueryExecutionId=eid)["QueryExecution"]["Status"]
        if estado["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)

    if estado["State"] != "SUCCEEDED":
        raise HTTPException(500, {"error": "La consulta fallo",
                                  "detalle": estado.get("StateChangeReason")})

    res = athena.get_query_results(QueryExecutionId=eid)
    filas = res["ResultSet"]["Rows"]
    cabecera = [c.get("VarCharValue") for c in filas[0]["Data"]]
    return [dict(zip(cabecera, [numero(c.get("VarCharValue")) for c in f["Data"]]))
            for f in filas[1:]]


@app.get(f"{PREFIX}/conductores/rating-por-distrito")
def rating_por_distrito():
    sql = """
        SELECT c.distrito_base,
               count(DISTINCT c.id)     AS conductores,
               count(cal.viaje_id)      AS calificaciones,
               round(avg(cal.rating),2) AS rating_promedio
        FROM conductores c
        LEFT JOIN calificaciones cal ON cal.conductor_id = c.id
        GROUP BY c.distrito_base
        ORDER BY rating_promedio DESC
    """
    return {"items": consultar(sql)}


@app.get(f"{PREFIX}/ingresos/por-hora-distrito")
def ingresos_por_hora_distrito(distrito: str | None = None):
    filtro = f"AND v.distrito_origen = '{distrito}'" if distrito else ""
    sql = f"""
        SELECT v.distrito_origen AS distrito,
               hour(from_iso8601_timestamp(v.iniciado_en)) AS hora,
               count(*)                    AS viajes,
               round(avg(v.monto_total),2) AS ingreso_promedio,
               round(sum(v.monto_total),2) AS ingreso_total
        FROM viajes v
        WHERE v.estado = 'finalizado' {filtro}
        GROUP BY v.distrito_origen, hour(from_iso8601_timestamp(v.iniciado_en))
        ORDER BY v.distrito_origen, hora
    """
    return {"items": consultar(sql)}


@app.get(f"{PREFIX}/conductores/rating-por-antiguedad")
def rating_por_antiguedad():
    sql = """
        SELECT date_diff('year', from_iso8601_date(c.fecha_ingreso), current_date) AS anios,
               count(DISTINCT c.id)         AS conductores,
               round(avg(cal.rating),2)     AS rating_promedio,
               round(avg(v.monto_total),2)  AS ticket_promedio
        FROM conductores c
        JOIN viajes v           ON v.conductor_id = c.id
        JOIN calificaciones cal ON cal.viaje_id   = v.id
        WHERE v.estado = 'finalizado'
        GROUP BY 1 ORDER BY 1
    """
    return {"items": consultar(sql)}


@app.get(f"{PREFIX}/rutas/top-distritos")
def top_distritos(minimo: int = 50):
    sql = f"""
        SELECT v.distrito_origen, v.distrito_destino,
               count(*)                     AS viajes,
               round(avg(v.distancia_km),2) AS km_promedio,
               round(avg(cal.rating),2)     AS rating_promedio
        FROM viajes v
        LEFT JOIN calificaciones cal ON cal.viaje_id = v.id
        WHERE v.estado = 'finalizado'
        GROUP BY 1,2 HAVING count(*) > {minimo}
        ORDER BY viajes DESC
    """
    return {"items": consultar(sql)}
