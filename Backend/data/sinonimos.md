# Sinónimos de rubros

- **Fuente:** elaborado por el equipo de Data (sin fuente externa)
- **Códigos de rubro:** tomados de la lista de rubros piloto del documento de tareas del backend y de su devolución del 04/11/2026
- **Fecha de elaboración:** 2026-10-28
- **Última actualización:** 2026-11-13
- **Fecha de descarga:** no aplica (no se descargó de ningún sitio)

## Columnas

| Columna | Significado |
|---|---|
| termino | Palabra o frase que usa la gente para nombrar una actividad. Cada término figura con tilde y sin tilde |
| rubro_code | Código del rubro oficial al que corresponde, con formato rubro_{número} |

## Notas

- Cada término apunta a un solo rubro. Se verificó que ninguno esté repetido en dos rubros.
- Rubros cubiertos: rubro_4, rubro_16, rubro_66, rubro_102, rubro_104, rubro_136, rubro_137, rubro_169, rubro_245, rubro_309, rubro_315, rubro_471.
- "confitería" se mantiene en rubro_102 ("Alimentación en general y gastronomía"): el Cuadro de Usos del Suelo N° 3.3 y las habilitaciones publicadas en el Boletín Oficial la ubican en el rubro 1.5 junto con restaurante, café bar y casa de lunch.
- Tras la devolución del backend se quitó "comercio minorista" (demasiado general).
- "veterinaria" pasó de rubro_136 (venta de animales) a rubro_104 (consultorio veterinario), a propuesta del backend: el Cuadro 3.3 trata el consultorio veterinario (5.1.1) y la venta de animales domésticos (1.8.9) como rubros distintos.
- rubro_104 no figura entre los rubros piloto del documento de tareas; se incluye a propuesta del backend.
- Se agregó "mascotas" a rubro_136 para cubrir la consulta "quiero vender mascotas".
- Los errores de tipeo (por ejemplo "peluqeria") no figuran: se espera que el backend los reconozca con búsqueda aproximada.
- Los rubros que el backend ya tenía con sinónimos propios (lavandería, gimnasio, hotel, etc.) no están en este archivo, salvo rubro_104.
- Este archivo se actualiza cada sprint, sumando las consultas que el sistema no entendió.
- Cantidad de filas: 67.
