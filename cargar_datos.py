"""
Carga 30 reportes de prueba en MongoDB (la colección principal del caso 8).
Los 10 primeros son los del Producto de la Unidad 2 (Corte 1); los otros 20 son nuevos.
Se puede ejecutar varias veces: usa el código del reporte para no duplicar documentos.

Uso:  python cargar_datos.py
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "infraestructura_alcaldia")
if not MONGO_URI:
    raise SystemExit("Falta MONGO_URI. Copia .env.example a .env y complétalo.")


def rep(codigo, tipo, barrio, descripcion, severidad, personas, estado, fecha, etiquetas, fotos):
    anio, mes, dia = map(int, fecha.split("-"))
    return {
        "codigo": codigo, "tipo_estructura": tipo, "barrio": barrio, "descripcion": descripcion,
        "severidad": severidad, "personas_afectadas": personas, "estado": estado,
        "fecha_reporte": datetime(anio, mes, dia), "etiquetas": etiquetas, "fotos": fotos,
    }


REPORTES = [
    # --- Los 10 del Producto U2 (Corte 1) ---
    rep("REP-001", "via", "Cuba", "Hundimiento del pavimento en la calzada principal", 4, 120, "pendiente", "2026-09-12", ["hundimiento", "pavimento", "transito"], ["rep001_a.jpg", "rep001_b.jpg"]),
    rep("REP-002", "edificio", "Centro", "Grietas en columnas del segundo piso de un edificio", 5, 48, "en_reparacion", "2026-09-10", ["grietas", "columnas", "riesgo_colapso"], ["rep002_a.jpg"]),
    rep("REP-003", "puente", "Pinares", "Barandas sueltas en puente peatonal sobre el río", 3, 300, "pendiente", "2026-09-15", ["barandas", "peatonal"], ["rep003_a.jpg"]),
    rep("REP-004", "anden", "Boston", "Baldosas levantadas en el andén frente a un colegio", 2, 15, "resuelto", "2026-09-03", ["baldosas", "colegio"], ["rep004_a.jpg"]),
    rep("REP-005", "via", "Kennedy", "Deslizamiento de talud que bloquea un carril", 5, 600, "en_reparacion", "2026-09-14", ["deslizamiento", "talud", "carril_bloqueado"], ["rep005_a.jpg", "rep005_b.jpg", "rep005_c.jpg"]),
    rep("REP-006", "edificio", "Cuba", "Fisuras leves en la fachada de una casa", 1, 0, "resuelto", "2026-09-01", ["fisuras", "fachada"], ["rep006_a.jpg"]),
    rep("REP-007", "via", "Centro", "Hueco profundo en la vía que afecta a los vehículos", 3, 80, "pendiente", "2026-09-18", ["hueco", "pavimento"], ["rep007_a.jpg"]),
    rep("REP-008", "puente", "Boston", "Corrosión en las vigas metálicas de un puente vehicular", 4, 900, "en_reparacion", "2026-09-08", ["corrosion", "vigas", "riesgo_estructural"], ["rep008_a.jpg", "rep008_b.jpg"]),
    rep("REP-009", "edificio", "Pinares", "Muro medianero inclinado en una vivienda abandonada", 2, 0, "pendiente", "2026-09-20", ["muro", "vivienda_abandonada"], ["rep009_a.jpg"]),
    rep("REP-010", "anden", "Kennedy", "Raíz de árbol que levanta el andén y obstruye el paso", 1, 25, "pendiente", "2026-09-22", ["raiz", "anden", "peatonal"], ["rep010_a.jpg"]),
    # --- 20 reportes nuevos ---
    rep("REP-011", "via", "Álamos", "Socavón en la calzada tras lluvias fuertes", 5, 450, "pendiente", "2026-09-25", ["socavon", "lluvia", "riesgo_vehicular"], ["rep011_a.jpg", "rep011_b.jpg"]),
    rep("REP-012", "puente", "Providencia", "Pasamanos oxidados en puente peatonal", 2, 150, "pendiente", "2026-09-26", ["pasamanos", "oxido", "peatonal"], ["rep012_a.jpg"]),
    rep("REP-013", "edificio", "Boston", "Fachada con desprendimiento de revoque", 3, 60, "en_reparacion", "2026-09-27", ["fachada", "desprendimiento"], ["rep013_a.jpg"]),
    rep("REP-014", "anden", "Centro", "Andén hundido frente a un local comercial", 2, 40, "pendiente", "2026-09-28", ["hundimiento", "comercio"], ["rep014_a.jpg"]),
    rep("REP-015", "via", "Pinares", "Alcantarilla colapsada que inunda la vía", 4, 220, "en_reparacion", "2026-09-29", ["alcantarilla", "inundacion"], ["rep015_a.jpg", "rep015_b.jpg"]),
    rep("REP-016", "edificio", "Kennedy", "Cubierta de colegio con filtraciones y daño estructural", 4, 350, "pendiente", "2026-10-01", ["cubierta", "filtraciones", "colegio"], ["rep016_a.jpg", "rep016_b.jpg"]),
    rep("REP-017", "via", "Villa Santana", "Muro de contención con fisuras junto a la vía", 5, 500, "pendiente", "2026-10-02", ["muro_contencion", "fisuras", "riesgo_colapso"], ["rep017_a.jpg", "rep017_b.jpg", "rep017_c.jpg"]),
    rep("REP-018", "puente", "Cuba", "Juntas de dilatación dañadas en puente vehicular", 3, 700, "pendiente", "2026-10-03", ["juntas", "vehicular"], ["rep018_a.jpg"]),
    rep("REP-019", "anden", "Álamos", "Poste inclinado sobre el andén", 3, 90, "resuelto", "2026-10-04", ["poste", "inclinado"], ["rep019_a.jpg"]),
    rep("REP-020", "edificio", "Centro", "Balcón con riesgo de caída sobre la vía pública", 5, 200, "en_reparacion", "2026-10-05", ["balcon", "riesgo_caida"], ["rep020_a.jpg", "rep020_b.jpg"]),
    rep("REP-021", "via", "Providencia", "Semáforo caído por deslizamiento", 2, 120, "resuelto", "2026-10-06", ["semaforo", "deslizamiento"], ["rep021_a.jpg"]),
    rep("REP-022", "anden", "Pinares", "Escaleras públicas con peldaños rotos", 3, 260, "pendiente", "2026-10-07", ["escaleras", "peatonal"], ["rep022_a.jpg"]),
    rep("REP-023", "via", "Boston", "Hundimiento por rotura de tubería de acueducto", 4, 310, "en_reparacion", "2026-10-08", ["hundimiento", "tuberia"], ["rep023_a.jpg", "rep023_b.jpg"]),
    rep("REP-024", "edificio", "Villa Santana", "Vivienda con muros agrietados tras un sismo", 4, 12, "pendiente", "2026-10-09", ["grietas", "sismo", "vivienda"], ["rep024_a.jpg"]),
    rep("REP-025", "puente", "Kennedy", "Cimentación de puente peatonal socavada por la quebrada", 5, 800, "en_reparacion", "2026-10-10", ["cimentacion", "socavacion", "peatonal"], ["rep025_a.jpg", "rep025_b.jpg"]),
    rep("REP-026", "via", "Cuba", "Baches múltiples en el corredor de buses", 2, 1500, "pendiente", "2026-10-11", ["baches", "transporte_publico"], ["rep026_a.jpg"]),
    rep("REP-027", "anden", "Kennedy", "Rampa de acceso para personas con discapacidad destruida", 3, 35, "pendiente", "2026-10-12", ["rampa", "accesibilidad"], ["rep027_a.jpg"]),
    rep("REP-028", "edificio", "Álamos", "Edificio de apartamentos con columnas agrietadas", 5, 96, "pendiente", "2026-10-13", ["columnas", "grietas", "riesgo_colapso"], ["rep028_a.jpg", "rep028_b.jpg"]),
    rep("REP-029", "via", "Centro", "Pavimento agrietado en el cruce principal", 1, 400, "resuelto", "2026-10-14", ["pavimento", "grietas"], ["rep029_a.jpg"]),
    rep("REP-030", "puente", "Villa Santana", "Tablero de madera deteriorado en puente rural", 4, 75, "pendiente", "2026-10-15", ["madera", "tablero"], ["rep030_a.jpg", "rep030_b.jpg"]),
]

if __name__ == "__main__":
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    coleccion = cliente[MONGO_DB]["reportes"]
    coleccion.create_index("codigo", unique=True)
    # upsert: si el código ya existe se actualiza; si no, se inserta
    operaciones = [UpdateOne({"codigo": d["codigo"]}, {"$set": d}, upsert=True) for d in REPORTES]
    resultado = coleccion.bulk_write(operaciones)
    print(f"Insertados: {resultado.upserted_count} · Actualizados: {resultado.modified_count}")
    print(f"Total en la colección {MONGO_DB}.reportes: {coleccion.count_documents({})}")
