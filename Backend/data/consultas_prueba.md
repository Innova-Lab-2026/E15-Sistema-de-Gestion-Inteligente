# Consultas de prueba

- **Fuente:** elaborado por el equipo de Data (sin fuente externa)
- **Uso:** probar si el sistema detecta bien el rubro y el barrio de una pregunta escrita como la haría una persona, y si responde como corresponde
- **Fecha de elaboración:** 2026-10-28
- **Última actualización:** 2026-11-12 
- **Fecha de descarga:** no aplica (no se descargó de ningún sitio)

## Columnas

| Columna | Significado |
|---|---|
| pregunta | Texto de ejemplo, escrito como lo escribiría una persona |
| rubro_esperado | Código del rubro que el sistema debería detectar. Vacío si la pregunta no menciona ningún rubro |
| barrio_esperado | barrio_id del barrio que el sistema debería detectar, igual al de barrios.csv. Vacío si la pregunta no nombra un barrio |
| estado_esperado | Qué debería responder el sistema: `completa` (tiene rubro y ubicación, puede responder), `pide_aclaracion` (falta el rubro o la ubicación) o `fuera_de_alcance` (no trata de abrir un comercio) |

## Contenido

- Total: 30 preguntas (23 `completa`, 3 `pide_aclaracion`, 4 `fuera_de_alcance`).
- Rubros cubiertos: rubro_102, rubro_471, rubro_16, rubro_309, rubro_66, rubro_137, rubro_169, rubro_245, rubro_4, rubro_136 y rubro_315.
- Incluye barrios que pueden confundirse con rubros: Flores, Floresta, Retiro, Parque Chas y Parque Patricios.
- Incluye errores de tipeo y variantes de escritura: "peluqeria", "cafeteria", "ferreteria", "kiosko", "Nuñes", "Nunez" y "Av. Cabildo".
- Incluye preguntas con falta de información (por ejemplo, una farmacia sin ubicación) y preguntas sin relación con el caso (DNI, ABL, clima, pasaje).

## Notas

- Cuando solo hay calle y altura, el barrio esperado se completó a mano. Corrientes 2500 figura como balvanera según el documento del backend. Pendiente de confirmar.
- Cabildo 2000 figura como belgrano según el ejemplo del backend.
- No se incluyeron direcciones con formato "Cabildo al 2000" ni "Corrientes y Callao", ni casos con un rubro o un barrio que no estén en la lista.