import json, os
from datetime import datetime
import boto3
from pymongo import MongoClient

S3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]

cli = MongoClient(os.environ["MONGO_URI"])
col = cli.get_default_database()["calificaciones"]

def limpiar(doc):
    doc["_id"] = str(doc["_id"])
    for k, v in list(doc.items()):
        if isinstance(v, datetime):
            doc[k] = v.strftime("%Y-%m-%dT%H:%M:%SZ")
    mod = doc.pop("moderacion", {}) or {}
    doc["moderacion_estado"] = mod.get("estado")
    doc["moderacion_reportes"] = mod.get("reportes", 0)
    resp = doc.pop("respuesta_conductor", None)
    doc["respuesta_texto"] = (resp or {}).get("texto")
    return doc

lineas = []
for doc in col.find({}):
    lineas.append(json.dumps(limpiar(doc), ensure_ascii=False))

S3.put_object(Bucket=BUCKET, Key="raw/calificaciones/calificaciones.json",
              Body=("\n".join(lineas)).encode("utf-8"))
print(f"calificaciones: {len(lineas):,} documentos")

