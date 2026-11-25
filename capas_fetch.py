#!/usr/bin/env python3
"""Capas del mapa: descarga (BA Data) o lee archivos locales, normaliza y escribe data/capas/*.geojson.

Uso:
  python scripts/capas_fetch.py                     # descarga comunas, barrios y oferta gastronomica
  python scripts/capas_fetch.py --local ./descargas # usa comunas.geojson, barrios.geojson y oferta-gastronomica.geojson ya descargados
  python scripts/capas_fetch.py --oficinas app/db/offices_snapshot.json   # genera ademas la capa de oficinas

Solo usa la biblioteca estándar. Escribe en data/capas/ y actualiza n_features/estado en data/capas.csv.
"""
import argparse, csv, json, re, unicodedata, urllib.request
from datetime import date
from pathlib import Path

CDN = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/"
CAPAS = {
    "comunas": dict(id="layer-ba-comunas", file="comunas.geojson", url=CDN + "innovacion-transformacion-digital/comunas/comunas.geojson", local="comunas.geojson"),
    "barrios": dict(id="layer-ba-barrios", file="barrios.geojson", url=CDN + "innovacion-transformacion-digital/barrios/barrios.geojson", local="barrios.geojson"),
    "gastro":  dict(id="layer-ba-gastro-geojson", file="oferta_gastronomica.geojson", url=CDN + "ente-de-turismo/oferta-establecimientos-gastronomicos/oferta-gastronomica.geojson", local="oferta-gastronomica.geojson"),
}
# Correcciones manuales de nombres que el origen trae irrecuperables: {id: "NOMBRE CORRECTO"}. Se aplican cada vez que se genera la capa.
NOMBRES_CORREGIDOS = {}   # ej.: {1786: "NOMBRE CORRECTO", 360: "OTRO NOMBRE CORRECTO"}

BBOX = (-58.54, -34.72, -58.32, -34.51)  # lng_min, lat_min, lng_max, lat_max (CABA con margen)

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()

def fix_text(s):
    """Repara texto con doble codificación (ej. 'NuÃ\x83Â±ez' -> 'Nuñez'); no toca texto sano."""
    if not isinstance(s, str) or not re.search("[ÃÂâ]", s): return s
    for enc in ("latin-1", "cp1252"):
        t = s
        for _ in range(3):
            try: u = t.encode(enc).decode("utf-8")
            except Exception: break
            if u == t: break
            t = u
        if t != s and "Ã" not in t: return t
    return s

def prop(props, *names):
    low = {k.lower(): v for k, v in props.items()}
    for n in names:
        if n.lower() in low and low[n.lower()] not in (None, ""): return low[n.lower()]
    return None

def to_int(v):
    try: return int(float(str(v).replace(",", ".")))
    except Exception: return None

def clean_coords(c, nd=6):
    if isinstance(c, (int, float)): return round(float(c), nd)
    return [clean_coords(x, nd) for x in c]

def first_point(c):
    while isinstance(c[0], list): c = c[0]
    return c

def geom_ok(g, stats):
    """Valida/repara la geometría. Devuelve None si hay que descartar la feature."""
    if not g or not g.get("coordinates"): stats["sin_geometria"] += 1; return None
    lng, lat = first_point(g["coordinates"])[:2]
    if not (BBOX[1] <= lat <= BBOX[3]) and (BBOX[1] <= lng <= BBOX[3]):      # [lat, lng] invertido
        stats["coords_invertidas"] += 1
        sw = lambda c: [c[1], c[0]] + list(c[2:]) if isinstance(c[0], (int, float)) else [sw(x) for x in c]
        g = dict(g, coordinates=sw(g["coordinates"])); lng, lat = first_point(g["coordinates"])[:2]
    if not (BBOX[0] <= lng <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]): stats["fuera_de_caba"] += 1; return None
    return dict(g, coordinates=clean_coords(g["coordinates"]))

def reconciliar_barrio(k, claves):
    """Hace coincidir 'boca' con 'la boca' (o al revés) usando las claves de la capa de barrios."""
    if not k or k in claves: return k, False
    sin = re.sub(r"^(la|el|los|las) ", "", k)
    for cand in ("la " + k, "el " + k, "los " + k, "las " + k, sin):
        if cand in claves: return cand, True
    return k, False

def ajustar_gastro(props, stats):
    """Limpieza final de la capa gastronómica: espacios, dirección faltante y texto que no se pudo reparar."""
    props.pop("texto_revisar", None)   # se recalcula al final
    if props.get("id") in NOMBRES_CORREGIDOS: props["nombre"] = NOMBRES_CORREGIDOS[props["id"]]; stats["nombres_corregidos"] = stats.get("nombres_corregidos", 0) + 1
    for k in ("nombre", "direccion", "calle_nombre", "cocina", "ambientacion", "barrio"):
        if isinstance(props.get(k), str): props[k] = re.sub(r"\s+", " ", props[k]).strip()      # incluye espacios no separables
    c = props.get("cocina")
    if isinstance(c, str) and re.match(r"^PANQUEQUER\S{1,3}A$", c) and re.search("[ÃÂ\ufffd]", c):
        props["cocina"] = "PANQUEQUERÍA"                                                         # caso conocido del origen
    if not props.get("direccion") and props.get("calle_nombre") and props.get("calle_altura"):
        props["direccion"] = f"{props['calle_nombre']} {props['calle_altura']}"; props["direccion_derivada"] = True
        stats["direccion_derivada"] = stats.get("direccion_derivada", 0) + 1
    if any(isinstance(v, str) and re.search("[ÃÂâ\ufffd]", v) for v in props.values()):
        props["texto_revisar"] = True; stats["texto_irrecuperable"] = stats.get("texto_irrecuperable", 0) + 1

def procesar(nombre, data, ctx=None):
    stats = dict(entrada=len(data.get("features", [])), sin_geometria=0, coords_invertidas=0, fuera_de_caba=0, texto_reparado=0)
    ctx = ctx or {}
    fuentes = data.get("features", [])
    if fuentes: stats["campos_origen"] = list((fuentes[0].get("properties") or {}).keys())
    out = []
    for f in data.get("features", []):
        p = f.get("properties") or {}; g = geom_ok(f.get("geometry"), stats)
        if g is None: continue
        reparado = {k: fix_text(v) for k, v in p.items()}
        stats["texto_reparado"] += sum(1 for k in p if reparado[k] != p[k])
        com = to_int(prop(reparado, "comuna", "comunas"))
        if nombre == "comunas":
            props = dict(comuna=com, nombre=f"Comuna {com}", barrios=prop(reparado, "barrios"),
                         perimetro=prop(reparado, "perimetro"), area=prop(reparado, "area"))
        elif nombre == "barrios":
            b = prop(reparado, "barrio", "nombre")
            props = dict(barrio=b, barrio_key=norm(b) if b else None, comuna=com, perimetro=prop(reparado, "perimetro"), area=prop(reparado, "area"))
        else:
            b = prop(reparado, "barrio")
            k = norm(b) if b else None
            if ctx.get("claves"):
                k, cambio = reconciliar_barrio(k, ctx["claves"])
                stats["barrio_reconciliado"] = stats.get("barrio_reconciliado", 0) + int(cambio)
                if k and k not in ctx["claves"]: stats["barrio_sin_match"] = stats.get("barrio_sin_match", 0) + 1
            der = False
            if com is None and k and k in ctx.get("barrio_comuna", {}): com, der = ctx["barrio_comuna"][k], True
            stats["comuna_derivada"] = stats.get("comuna_derivada", 0) + int(der)
            mapeadas = {"nombre", "name", "categoria", "direccion", "direccion_completa", "domicilio", "barrio", "comuna", "comunas", "lat", "long", "lng", "lon"}   # lat/long ya están en la geometría
            extras = {kk.lower(): vv for kk, vv in reparado.items() if kk.lower() not in mapeadas}   # no se pierde ningún campo de origen
            props = dict(nombre=prop(reparado, "nombre", "name"), categoria=prop(reparado, "categoria"), direccion=prop(reparado, "direccion", "direccion_completa", "domicilio"),
                         barrio=b, barrio_key=k, comuna=com, comuna_derivada=der or None, **extras)
        if nombre == "gastro": ajustar_gastro(props, stats)
        out.append(dict(type="Feature", properties={k: v for k, v in props.items() if v is not None}, geometry=g))
    stats["salida"] = len(out)
    return dict(type="FeatureCollection", features=out), stats

def oficinas(path):
    off = json.load(open(path, encoding="utf-8"))["offices"]
    derivada = {"balvanera": 3}   # AGC viene sin comuna; Balvanera pertenece a la comuna 3
    feats = []
    for o in off:
        if o.get("type") != "physical_office" or o.get("latitude") is None: continue   # el canal online no tiene ubicación propia
        b = o.get("neighborhood"); com = o.get("commune"); der = False
        if com in (None, "") and b and norm(b) in derivada: com, der = derivada[norm(b)], True
        props = dict(id=o["id"], nombre=o["name"], organizacion=o.get("organization"), tipo=o.get("kind") or "oficina_agc", direccion=o.get("address"),
                     horario=o.get("opening_hours"), barrio=b, barrio_key=norm(b) if b else None, comuna=to_int(com), comuna_derivada=der or None,
                     url=o.get("url"), estado=o.get("status"))
        feats.append(dict(type="Feature", properties={k: v for k, v in props.items() if v is not None},
                          geometry=dict(type="Point", coordinates=[round(o["longitude"], 6), round(o["latitude"], 6)])))
    return dict(type="FeatureCollection", features=feats), dict(entrada=len(off), salida=len(feats))

def leer(spec, local):
    if local: return json.load(open(Path(local) / spec["local"], encoding="utf-8"))
    with urllib.request.urlopen(spec["url"], timeout=120) as r: return json.loads(r.read().decode("utf-8"))

def actualizar_csv(csv_path, id_, n):
    if not csv_path.exists(): return
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    for r in rows:
        if r["id"] == id_: r.update(n_features=str(n), status="available", generada_el=str(date.today()))
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--local"); ap.add_argument("--oficinas"); ap.add_argument("--data", default="data")
    a, _ = ap.parse_known_args();   # parse_known_args: tolera los argumentos extra que agrega Colab/Jupyter
    data = Path(a.data); (data / "capas").mkdir(parents=True, exist_ok=True)
    jobs = [(k, CAPAS[k]) for k in CAPAS]
    ctx = {}
    for k, spec in jobs:
        try: fc, st = procesar(k, leer(spec, a.local), ctx)
        except Exception as e: print(f"[{k}] NO SE PUDO: {e}"); continue
        (data / "capas" / spec["file"]).write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        actualizar_csv(data / "capas.csv", spec["id"], st["salida"]); print(f"[{k}] {st}")
        if k == "barrios":
            ctx = dict(claves={f["properties"]["barrio_key"] for f in fc["features"] if f["properties"].get("barrio_key")},
                       barrio_comuna={f["properties"]["barrio_key"]: f["properties"]["comuna"] for f in fc["features"] if f["properties"].get("comuna") is not None})
    if a.oficinas:
        fc, st = oficinas(a.oficinas)
        (data / "capas" / "oficinas.geojson").write_text(json.dumps(fc, ensure_ascii=False, indent=1), encoding="utf-8")
        actualizar_csv(data / "capas.csv", "layer-oficinas-atencion", st["salida"]); print(f"[oficinas] {st}")

if __name__ == "__main__":
    main()
