# Trámites por rubro – Sistema de Gestión Inteligente (CABA)

Equipo BI, Data & ML · Generado el 2026-11-15 · 12 rubros · 15 trámites · 21 fuentes

Cada trámite se define una sola vez (sección 3) y se relaciona con los rubros donde aplica (sección 2). Todos los datos llevan el link oficial. Los niveles de confianza son `alta` (página o guía oficial leída), `media` (aplicación por analogía o fuente enlazada sin leer) y `pendiente_verificacion` (falta leer el documento oficial).

## 1. Resumen

| Rubro | Vía de habilitación | Trámites específicos | Confianza mínima |
|---|---|---|---|
| `rubro_4` Pinturería | General o exprés | — | media |
| `rubro_16` Comercio minorista excluido comestibles como uso principal | General o exprés | — | media |
| `rubro_66` Farmacia | Solo general (no exprés) | habilitación farmacéutica (Ministerio de Salud) | pendiente_verificacion |
| `rubro_102` Alimentación en general y gastronomía | General o exprés | carnet de manipulación, limpieza de campanas | media |
| `rubro_104` Consultorio veterinario | General o exprés | limpieza de campanas, director médico veterinario matriculado (guía) | media |
| `rubro_136` Local de venta de animales domésticos | General o exprés | — | media |
| `rubro_137` Supermercado | General o exprés | carnet de manipulación | media |
| `rubro_169` Maxikiosco | General o exprés | carnet de manipulación, prohibición de vender alcohol (guía) | media |
| `rubro_245` Local de venta de golosinas envasadas (kiosco) | General o exprés | carnet de manipulación, prohibición de vender alcohol (guía) | media |
| `rubro_309` Ferretería industrial, máquinas, herramientas, motores industriales y agrícolas | General o exprés | — | media |
| `rubro_315` Salón de estética | General o exprés | — | pendiente_verificacion |
| `rubro_471` Alimentación en general para llevar | General o exprés | carnet de manipulación, limpieza de campanas | media |

## 2. Trámites por rubro

### `rubro_4` – Pinturería (1.8.32)

Términos que lo activan: casa de pinturas, pintureria, venta de pinturas

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | referencia | **Nota:** Verificar si comercializa inflamables: en ese caso no aplica la modalidad exprés | media |

### `rubro_16` – Comercio minorista excluido comestibles como uso principal (1.8)

Términos que lo activan: boutique, indumentaria, local de ropa, local de venta de ropa, tienda de ropa, zapateria

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | referencia | — | media |

### `rubro_66` – Farmacia (1.8.2)

Términos que lo activan: botica, farmacia

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | obligatorio | **Nota:** La modalidad exprés no aplica a este rubro | alta |
| 2 | [Habilitación de establecimiento farmacéutico](https://www.argentina.gob.ar/servicio/habilitar-un-establecimiento-farmaceutico) | obligatorio | Requiere la disposición de habilitación de la Ciudad (QR) como paso previo | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | media |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: farmacias](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Farmacias%20OK003.pdf) | referencia | **Nota:** Guía oficial no leída: relevar contenido | pendiente_verificacion |

### `rubro_102` – Alimentación en general y gastronomía (1.5)

Términos que lo activan: bar, cafe, cafeteria, cerveceria, confiteria, gastronomia, heladeria, local gastronomico, parrilla, pizzeria, restaurante

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 5 | [Curso de manipulación higiénica de alimentos (carnet de manipulador)](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | obligatorio | — | alta |
| 6 | [Certificado de limpieza de campanas y conductos](https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/certificado-de-limpieza-de-campanas) | condicional | Solo si el local tiene campana, chimenea o conducto de evacuación | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: establecimientos gastronómicos](https://static.buenosaires.gob.ar/sites/default/files/2026-03/establec_gastronomicos%202025%20OK003.pdf) | referencia | — | alta |

### `rubro_104` – Consultorio veterinario (5.1.1)

Términos que lo activan: consultorio veterinario, medico veterinario, veterinaria, veterinario

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés **Nota:** Verificar si aplica: la guía exige director médico veterinario matriculado (normativa específica) | media |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 6 | [Certificado de limpieza de campanas y conductos](https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/certificado-de-limpieza-de-campanas) | condicional | Solo si el local tiene campana, chimenea o conducto de evacuación | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: veterinarias](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Veterinarias%202025%20OK003.pdf) | referencia | **Nota:** La guía se titula 'Veterinarias'; confirmar que cubre el rubro 'Consultorio veterinario' | alta |

### `rubro_136` – Local de venta de animales domésticos (1.8.9)

Términos que lo activan: animales domesticos, mascotas, pet shop, venta de animales, venta de mascotas

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | referencia | **Nota:** Rubro con normativa específica no relevada; ver pendientes | media |

### `rubro_137` – Supermercado (1.6.1)

Términos que lo activan: autoservicio, mercado, supermercado

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 5 | [Curso de manipulación higiénica de alimentos (carnet de manipulador)](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | condicional | Personal que manipule alimentos | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | referencia | — | media |

### `rubro_169` – Maxikiosco (1.4.3)

Términos que lo activan: maxi kiosco, maxikiosco, maxikiosko

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 5 | [Curso de manipulación higiénica de alimentos (carnet de manipulador)](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | condicional | Personal que manipule alimentos | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: kiosco y maxikiosco](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Kiosco%20y%20Maxikiosco%20OK003.pdf) | referencia | — | alta |

### `rubro_245` – Local de venta de golosinas envasadas (kiosco) (1.4.2)

Términos que lo activan: kiosco, kiosko, quiosco

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 5 | [Curso de manipulación higiénica de alimentos (carnet de manipulador)](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | condicional | Personal que manipule alimentos | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: kiosco y maxikiosco](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Kiosco%20y%20Maxikiosco%20OK003.pdf) | referencia | — | alta |

### `rubro_309` – Ferretería industrial, máquinas, herramientas, motores industriales y agrícolas (1.8.23)

Términos que lo activan: ferreteria, ferreteria industrial, herramientas

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | referencia | **Nota:** Verificar si comercializa explosivos o inflamables: en ese caso no aplica la modalidad exprés | media |

### `rubro_315` – Salón de estética (6.1.16)

Términos que lo activan: barberia, peluqueria

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | media |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: peluquería, salón de belleza y servicios personales directos](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Peluqueria_%20Salon%20de%20Belleza_%20Servicios%20personales%20directos%202025%20OK003.pdf) | referencia | **Nota:** Guía oficial no leída: relevar contenido; incluye Decreto 861/1997 | pendiente_verificacion |

### `rubro_471` – Alimentación en general para llevar (1.5.3)

Términos que lo activan: comida al paso, comida para llevar, delivery de comida, rotiseria, take away

| # | Trámite | Aplicación | Condición | Confianza |
|---|---|---|---|---|
| 1 | [Habilitación de actividad económica (con evaluación técnica profesional)](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | alternativa | Es la vía cuando no corresponde el trámite exprés | alta |
| 1 | [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | alternativa | Solo si la superficie es de hasta 200 m2 y se cumplen las condiciones de ubicación y uso del trámite exprés | alta |
| 3 | [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | obligatorio | Se genera automáticamente en la modalidad exprés | media |
| 4 | [Sistema de Autoprotección (Ley 5920)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | obligatorio | — | media |
| 5 | [Curso de manipulación higiénica de alimentos (carnet de manipulador)](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | obligatorio | Personal que manipule alimentos | media |
| 6 | [Certificado de limpieza de campanas y conductos](https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/certificado-de-limpieza-de-campanas) | condicional | Solo si el local tiene campana, chimenea o conducto de evacuación | alta |
| 7 | [Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | condicional | Solo si instala letreros, toldos, marquesinas, sombrillas o carteles | media |
| 8 | [Libro de Inspecciones Digital](https://librodigital.agcontrol.gob.ar/) | obligatorio | Se accede una vez que el local está librado al uso | alta |
| 9 | [Guía de inspección AGC: establecimientos gastronómicos](https://static.buenosaires.gob.ar/sites/default/files/2026-03/establec_gastronomicos%202025%20OK003.pdf) | referencia | **Nota:** Se asimila a la guía de gastronómicos por analogía; confirmar con la AGC | media |

## 3. Catálogo de trámites

### Habilitación de actividad económica (con evaluación técnica profesional)

- **Organismo:** AGC - Dirección General de Habilitaciones y Permisos
- **Modalidad:** Online (SSIT / TAD con miBA nivel 3) · **Costo:** Gratuito (Ley Tarifaria vigente)
- **Fuente oficial:** https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica
- **Confianza:** alta

Autorización para desarrollar actividades comerciales en CABA; el local debe aprobar una evaluación técnica profesional.

**Requisitos:**
- Usuario y clave miBA nivel 3
- Formulario de conformación de la unidad de uso (declaración jurada de la actividad a desarrollar)
- Anexo Técnico firmado por profesional responsable matriculado (arquitecto, ingeniero o maestro mayor de obras): encomienda profesional, datos del profesional, información de la unidad de uso, mixtura o área especial, croquis de ubicación y declaración jurada de verificación del local
- Certificado de Aptitud Ambiental (CAA)
- (si corresponde) Si corresponde: certificado de sobrecarga, plano de uso de actividad económica y autorización de emplazamiento
- (si corresponde) Según la normativa de la actividad, puede solicitarse documentación específica adicional

**Pasos:**
1. **Iniciar la solicitud.** Ingresar a la plataforma SSIT de la AGC con miBA y elegir 'Nueva Autorización de Actividad Económica'.
2. **Cargar al titular o firmante.** Ingresar el CUIT de la persona solicitante (física o jurídica).
3. **Declarar la ubicación.** Cargar dirección o partida y datos catastrales; al guardar se generan número de trámite y código de seguridad que el profesional necesita para el Anexo Técnico.
4. **Solicitar el Certificado de Aptitud Ambiental.** Tramitar el CAA en la Agencia de Protección Ambiental.
5. **Evaluación de la AGC.** La Dirección General de Habilitaciones y Permisos puede librar al uso, aprobar, observar o rechazar. Si se libra al uso, se entrega oblea con QR y se accede al Libro de Inspecciones Digital.

**Notas:**
- Tipos de autorización según la página oficial: declaración responsable sin planos (hasta 500 m2, inicio inmediato con oblea QR; por encima de 500 m2 se requiere declaración responsable con plano), declaración responsable con plano, y licencia (requiere inspección previa y no permite iniciar hasta la notificación; validez de 15 años).
- Estar 'librado al uso' no equivale a tener la habilitación de la actividad comercial.
- Atención presencial: Tte. Gral. Juan Domingo Perón 2941, lunes a viernes de 9 a 13:30 h.
- Qué tipo de autorización corresponde a cada rubro surge del Anexo II de la Res. 96/AGC/25 (pendiente de relevar).

### Habilitación de actividad económica exprés

- **Organismo:** AGC
- **Modalidad:** Online (SSIT / TAD con miBA nivel 3) · **Costo:** Gratuito (Ley Tarifaria vigente)
- **Fuente oficial:** https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres
- **Confianza:** alta

Alternativa sin evaluación técnica profesional para locales de menos de 200 m2 que cumplen las condiciones de ubicación y uso.

**Requisitos:**
- Usuario y clave miBA nivel 3
- Superficie total que no supere los 200 m2
- No comercializar explosivos, inflamables ni productos medicinales sin envasar
- No estar en galerías, centros comerciales, paseos de compras, mercados, patios gastronómicos, estaciones de subte/tren, aeropuertos u otros complejos comerciales
- No estar en áreas especiales (históricas, culturales, ambientales o con usos específicos del Código Urbanístico) ni en edificios catalogados
- Cumplir las condiciones de accesibilidad y no tener entrepisos en las plantas a habilitar
- No realizar actividades que requieran normativa específica (por ejemplo farmacia, agencia de lotería o estudio profesional)

**Pasos:**
1. **Iniciar la solicitud.** Ingresar a SSIT con miBA y elegir 'Habilitación de actividad económica exprés'.
2. **Declarar ubicación y titular.** Dirección, partida o datos catastrales, y CUIT de la persona solicitante.
3. **Completar formularios.** Datos del local y conformidad de uso; declarar rubro y actividades.
4. **Confirmar.** Al completar los formularios se genera el CAA de forma automática; si no se cumple un requisito, el sistema deriva al trámite correspondiente.

**Notas:**
- Si el local no cumple las condiciones, corresponde la habilitación de actividad económica con evaluación técnica profesional.

### Certificado de Aptitud Ambiental (CAA)

- **Organismo:** Agencia de Protección Ambiental (GCBA)
- **Modalidad:** Online · **Costo:** No relevado
- **Fuente oficial:** https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa
- **Confianza:** media

Documento que verifica que las actividades del comercio cumplen la normativa ambiental vigente; se solicita dentro de la habilitación (se genera automáticamente en la modalidad exprés).

**Requisitos:**
- Solicitar el CAA durante la habilitación de actividad económica (automático en exprés)

**Notas:**
- Requisitos propios del CAA no relevados: la página del trámite está enlazada desde la habilitación pero no fue leída.

### Curso de manipulación higiénica de alimentos (carnet de manipulador)

- **Organismo:** AGC - Dirección General de Higiene y Seguridad Alimentaria
- **Modalidad:** Online, presencial o renovación online · **Costo:** Gratuito
- **Fuente oficial:** https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos
- **Confianza:** alta

Capacitación básica obligatoria para quienes manipulan alimentos; quienes aprueban reciben el Carnet de Manipulador, vigente 3 años.

**Requisitos:**
- Registrarse como alumno en el portal web de alimentos de la AGC
- Cursar y aprobar la evaluación de conocimientos básicos de manipulación higiénica de alimentos
- Todo el personal que manipule alimentos (elaboración, servicio, venta y distribución) debe contar con el carnet vigente

**Notas:**
- El carnet tiene validez de 3 años y puede renovarse online.

### Sistema de Autoprotección (Ley 5920)

- **Organismo:** GCBA (Ley 5920; disposiciones DGDCIV)
- **Modalidad:** A confirmar · **Costo:** No relevado
- **Fuente oficial:** https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007
- **Confianza:** alta

Conjunto de medidas para prevenir y controlar riesgos; la AGC verifica su cumplimiento en la inspección.

**Requisitos:**
- Plano de evacuación visible, visado y conforme a la realidad
- Roles y capacitación del personal designado en el Plan
- Informe descriptivo del Sistema de Autoprotección
- (si corresponde) Gastronómicos: declaración jurada o disposición aprobatoria del sistema, según corresponda

**Notas:**
- Las guías citan la Ley 5920 y las disposiciones 331/DGDCIV/25 (kiosco, local de atención al público) y 1358/DGDCIV/2019 y 356/DGDCIV/2023 (gastronómicos).

### Certificado de limpieza de campanas y conductos

- **Organismo:** AGC (registro de empresas de limpieza)
- **Modalidad:** A confirmar · **Costo:** No relevado
- **Fuente oficial:** https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/certificado-de-limpieza-de-campanas
- **Confianza:** alta

Exigido a todo local con campana, chimenea o conducto de evacuación de humos, gases, vapores u olores; lo emite una empresa registrada ante la AGC.

**Requisitos:**
- Certificado de limpieza emitido por empresa de limpieza de campanas, conductos y afines registrada ante la AGC

**Notas:**
- Aplica solo si el local tiene campana, chimenea o conducto de evacuación.

### Libro de Inspecciones Digital

- **Organismo:** AGC
- **Modalidad:** Online (CUIT y clave miBA) · **Costo:** No relevado
- **Fuente oficial:** https://librodigital.agcontrol.gob.ar/
- **Confianza:** alta

Una vez que la actividad está librada al uso se accede al Libro de Inspecciones Digital, que las guías de inspección listan como documentación exigible.

**Requisitos:**
- Acceder al Libro de Inspecciones Digital con CUIT y clave miBA

### Permiso de publicidad (letreros, toldos, marquesinas, sombrillas, carteles)

- **Organismo:** GCBA
- **Modalidad:** Online · **Costo:** No relevado
- **Fuente oficial:** https://buenosaires.gob.ar/tramites/permisos-de-publicidad
- **Confianza:** media

Si el local tiene letreros, toldos, marquesinas, sombrillas o carteles, la guía de inspección exige permiso vigente y seguro de responsabilidad civil.

**Requisitos:**
- Disposición de permiso vigente para la instalación y emplazamiento
- Seguro de responsabilidad civil contra terceros

**Notas:**
- Condicional: solo si el local instala letreros, toldos, marquesinas, sombrillas o carteles.

### Habilitación de establecimiento farmacéutico

- **Organismo:** Ministerio de Salud de la Nación (TAD)
- **Modalidad:** Online (TAD, clave fiscal AFIP nivel 2 o superior) · **Costo:** Gratuito (Res. Ministerial 1938/2025)
- **Fuente oficial:** https://www.argentina.gob.ar/servicio/habilitar-un-establecimiento-farmaceutico
- **Confianza:** alta

Habilitación sanitaria del establecimiento farmacéutico, que se suma a la habilitación comercial de la Ciudad.

**Requisitos:**
- Formulario de solicitud online en TAD y nota de aceptación del cargo firmada por el presentante y el Director Técnico
- Título de propiedad, contrato de locación o comodato con firmas certificadas por escribano (el comodato debe acompañarse del título de propiedad)
- Plano del establecimiento con carátula del Ministerio de Salud, escala 1:100, con ambientes y medidas, firmado y sellado por el profesional y el apoderado
- Disposición de habilitación definitiva o provisoria otorgada por GCBA (lectura de código QR)
- Certificado de libre regencia del profesional farmacéutico
- Planta física: 35 m2 de atención al público y 15 m2 de sector alopático (depósito y/u oficina), conforme a las resoluciones citadas por el organismo
- (si corresponde) Si está en propiedad horizontal: reglamento de copropiedad que indique el destino del inmueble
- (si corresponde) Personas jurídicas: estatuto social inscripto en IGJ (autenticado por escribano) y acta de directorio que designa al Director Técnico
- Clave fiscal AFIP nivel 2 o superior, o apoderamiento en TAD

**Pasos:**
1. **Obtener la habilitación de la Ciudad.** La solicitud exige la disposición de habilitación del GCBA (QR).
2. **Ingresar a TAD.** Trámite 'Habilitación de establecimiento farmacéutico', con clave fiscal y CUIT.

**Notas:**
- La constancia de trámite iniciado no habilita a funcionar.
- La habilitación exprés de la Ciudad no aplica a farmacias.

### Guía de inspección AGC: establecimientos gastronómicos

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/establec_gastronomicos%202025%20OK003.pdf
- **Confianza:** alta

Documentación y condiciones que los inspectores controlan en locales gastronómicos.

**Requisitos:**
- Certificado original de autorización con código QR, exhibido y con local librado al uso; el rubro y la superficie deben coincidir con la realidad
- (si corresponde) RNE y RNPA, de corresponder
- Libro digital o registro de inspección; chapa catastral visible en el frente
- Carteles de prohibición de fumar y de consumo de tabaco
- Extintores vigentes (1 cada 200 m2 y uno por planta), medios de salida libres, señalización y luces de emergencia
- Gas natural en todo el local y sin garrafas
- Protocolo de medición de puesta a tierra con encomienda profesional y tablero con disyuntor diferencial
- Certificado de desratización y desinfección, análisis bacteriológico del agua y limpieza de tanques
- Carnet de manipulación de alimentos del personal
- (si corresponde) Plano conforme a obra de condiciones contra incendio y certificado final, de corresponder

**Notas:**
- Es una guía orientativa: los inspectores pueden pedir más documentación.

### Guía de inspección AGC: kiosco y maxikiosco

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Kiosco%20y%20Maxikiosco%20OK003.pdf
- **Confianza:** alta

Documentación y condiciones que los inspectores controlan en kioscos y maxikioscos.

**Requisitos:**
- Certificado original de autorización con código QR, exhibido y con local librado al uso
- Libro digital o registro de inspección; identificación catastral en el frente
- Prohibición de expendio de bebidas alcohólicas, incluido el envío a domicilio
- Prohibición de fumar (Ley 1799)
- Sistema de Autoprotección conforme a la Ley 5920 y la Disp. 331/DGDCIV/25
- Extintores, medios de salida libres y protocolo de puesta a tierra
- Comprobante de desratización/desinfección, limpieza semestral de tanques de agua y análisis bacteriológico del agua
- Capacitación en manipulación de alimentos del personal involucrado
- (si corresponde) Si comparte el local con otro uso: independización con tabique de al menos 2,10 m de altura

**Notas:**
- Es una guía orientativa: los inspectores pueden pedir más documentación.

### Guía de inspección AGC: local de atención al público

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf
- **Confianza:** media

Guía general para comercios minoristas y de atención al público; se usa por analogía en los rubros sin guía propia (a confirmar con la AGC).

**Requisitos:**
- Certificado original de autorización con código QR, exhibido y con local librado al uso
- Libro digital o registro de inspección; identificación catastral en el frente
- Libro de quejas, reclamos y sugerencias a disposición del público
- Prohibición de fumar (Ley 1799)
- Sistema de Autoprotección conforme a la Ley 5920 y la Disp. 331/DGDCIV/25
- Extintores (1 cada 200 m2 o fracción), medios de salida libres y protocolo de puesta a tierra
- Comprobante de desratización/desinfección y certificados de limpieza de tanques y análisis bacteriológico del agua
- (si corresponde) Plano de habilitación conforme a la realidad e instalaciones contra incendio, de corresponder

**Notas:**
- Es una guía orientativa y genérica: su aplicación a cada rubro debe confirmarse con la AGC.

### Guía de inspección AGC: peluquería, salón de belleza y servicios personales directos

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Peluqueria_%20Salon%20de%20Belleza_%20Servicios%20personales%20directos%202025%20OK003.pdf
- **Confianza:** pendiente_verificacion

Guía oficial para el rubro. El PDF no pudo leerse en esta revisión (acceso automatizado bloqueado): hay que curar su contenido a mano.

**Requisitos:**
- Cumplir los procedimientos de desinfección y esterilización de útiles e instrumentos en peluquerías y salones de belleza (Decreto 861/1997)

**Notas:**
- Contenido de la guía pendiente de relevar.

### Guía de inspección AGC: farmacias

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Farmacias%20OK003.pdf
- **Confianza:** pendiente_verificacion

Guía oficial para el rubro; enlazada en el índice de guías pero no leída en esta revisión.

**Notas:**
- Contenido de la guía pendiente de relevar.

### Guía de inspección AGC: veterinarias

- **Organismo:** AGC - Dirección General de Fiscalización y Control
- **Modalidad:** Orientativa (no vinculante) · **Costo:** No aplica
- **Fuente oficial:** https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Veterinarias%202025%20OK003.pdf
- **Confianza:** alta

Documentación y condiciones que los inspectores controlan en veterinarias.

**Requisitos:**
- Chapa mural con indicación de clase, establecimiento y nombre del director médico veterinario
- Establecimiento a cargo de un director médico veterinario matriculado
- Certificado original de autorización con código QR, exhibido y con local librado al uso; libro digital o registro de inspección
- Prohibición de fumar (Ley 1799)
- Sistema de Autoprotección conforme a la Ley 5920 y la Disp. 331/DGDCIV/25
- Extintores (1 cada 200 m2 o fracción), medios de salida libres, tablero con disyuntor diferencial y protocolo de puesta a tierra con encomienda profesional
- Comprobante de desratización/desinfección, certificado semestral de limpieza de tanques de agua potable y análisis bacteriológico del agua
- Sanitarios en condiciones de uso, con revestimiento impermeable y que cumplan la Ley 962 de accesibilidad
- (si corresponde) Laboratorio con pisos y paredes impermeables (friso de 1,50 m), local de curaciones u operaciones con paredes impermeables hasta 2 m y sector de baño de animales con agua fría y caliente
- (si corresponde) Equipos de rayos X, resonancia magnética, láser o IPL: deben estar habilitados ante el Ministerio de Salud
- (si corresponde) Área de internación con celdas o jaulas con puerta de seguridad

**Notas:**
- Es una guía orientativa: los inspectores pueden pedir más documentación.
- La guía enuncia las exigencias de laboratorio e internación para veterinarias en general; hay que confirmar cuáles aplican a un consultorio.

## 4. Pendientes por verificar

- **`rubro_136`:** Venta de animales domésticos: no se encontró un trámite oficial específico. Una nota periodística menciona la prohibición de exhibir animales en vidrieras (Ley 451, art. 1.2.9, y ley de 2019). → Confirmar con la AGC o en el Digesto de la Ciudad y, si corresponde, sumar el trámite o la restricción. ([fuente](https://www.derechoenzapatillas.com/amp/2021/vidrieras-no-podran-exhibir-animales/))
- **`rubro_315`:** La guía de inspección de peluquerías no pudo leerse (acceso automatizado bloqueado). → Leer el PDF a mano y completar sus requisitos. ([fuente](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Peluqueria_%20Salon%20de%20Belleza_%20Servicios%20personales%20directos%202025%20OK003.pdf))
- **`rubro_66`:** La guía de inspección de farmacias está enlazada pero no se leyó. → Leer el PDF y completar sus requisitos. ([fuente](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Farmacias%20OK003.pdf))
- **`rubro_66`:** La página oficial indica que el Ministerio de Salud de la Nación habilita farmacias en CABA; una norma de 2014 asignaba la habilitación técnica al Ministerio de Salud porteño. → Confirmar qué jurisdicción aplica hoy antes de publicar el trámite. ([fuente](https://www.argentina.gob.ar/servicio/habilitar-un-establecimiento-farmaceutico))
- **General:** El tipo de autorización por rubro (declaración responsable sin planos, con planos o licencia) surge del Anexo II de la Res. 96/AGC/25. → Relevar el Anexo II y cruzarlo con los rubros del catálogo. ([fuente](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/781370))
- **General:** Varias páginas enlazadas (CAA, campanas, libro digital, publicidad, Ley 5920) no se leyeron; solo se usó lo que dicen las guías de inspección. → Leer cada página y completar requisitos, costos y plazos. ([fuente](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa))
- **`rubro_104`:** No está confirmado si la habilitación exprés aplica a veterinarias (exigen director médico veterinario matriculado) ni cuáles exigencias de la guía (laboratorio, internación) aplican a un consultorio. → Consultar a la AGC antes de publicar la vía de habilitación del rubro. ([fuente](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Veterinarias%202025%20OK003.pdf))

## 5. Fuentes

| Fuente | Organización | Revisión |
|---|---|---|
| [Habilitación de actividad económica](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica) | GCBA / AGC | leido |
| [Habilitación de actividad económica exprés](https://buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica-expres) | GCBA / AGC | leido |
| [Certificado de Aptitud Ambiental (CAA)](https://buenosaires.gob.ar/tramites/impacto-ambiental-certificado-de-aptitud-ambiental-caa) | GCBA / Agencia de Protección Ambiental | enlazado_no_leido |
| [Curso de manipulación higiénica de los alimentos](https://buenosaires.gob.ar/tramites/curso-de-manipulacion-higienica-de-los-alimentos) | GCBA / AGC | leido_parcial |
| [Dirección General de Higiene y Seguridad Alimentaria](https://buenosaires.gob.ar/agc/direcciongeneralhigieneyseguridadalimentaria) | GCBA / AGC | leido_parcial |
| [Guías orientativas para la inspección (índice)](https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/guias-orientativas-para-la-inspeccion) | GCBA / AGC | leido |
| [Guía de inspección: establecimientos gastronómicos](https://static.buenosaires.gob.ar/sites/default/files/2026-03/establec_gastronomicos%202025%20OK003.pdf) | GCBA / AGC | leido |
| [Guía de inspección: kiosco y maxikiosco](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Kiosco%20y%20Maxikiosco%20OK003.pdf) | GCBA / AGC | leido |
| [Guía de inspección: local de atención al público](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Local%20de%20atencion%20al%20publico%20OK003.pdf) | GCBA / AGC | leido |
| [Guía de inspección: peluquería, salón de belleza, servicios personales directos](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Peluqueria_%20Salon%20de%20Belleza_%20Servicios%20personales%20directos%202025%20OK003.pdf) | GCBA / AGC | no_leido_acceso_bloqueado |
| [Guía de inspección: farmacias](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Farmacias%20OK003.pdf) | GCBA / AGC | enlazado_no_leido |
| [Habilitar un establecimiento farmacéutico](https://www.argentina.gob.ar/servicio/habilitar-un-establecimiento-farmaceutico) | Ministerio de Salud de la Nación / argentina.gob.ar | leido |
| [Certificado de libre regencia y/o actuación profesional](https://www.argentina.gob.ar/servicio/certificado-de-libre-regencia-yo-actuacion-profesional) | Ministerio de Salud de la Nación / argentina.gob.ar | enlazado_no_leido |
| [Ley 5920 - Sistema de Autoprotección (norma en Boletín Oficial CABA)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/394007) | GCBA / Boletín Oficial | enlazado_no_leido |
| [Certificado de limpieza de campanas](https://buenosaires.gob.ar/gcaba_historico/guia-para-administrar-tu-local-comercial/certificado-de-limpieza-de-campanas) | GCBA / AGC | enlazado_no_leido |
| [Libro de Inspecciones Digital (portal)](https://librodigital.agcontrol.gob.ar/) | GCBA / AGC | enlazado_no_leido |
| [Permisos de publicidad](https://buenosaires.gob.ar/tramites/permisos-de-publicidad) | GCBA | enlazado_no_leido |
| [Decreto 861/1997 - desinfección y esterilización en peluquerías y salones de belleza](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/50039) | GCBA / Boletín Oficial | leido_parcial |
| [Anexo II Res. 96/AGC/25 - usos de actividad económica y tipos de trámite](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/781370) | GCBA / Boletín Oficial | enlazado_no_leido |
| [Vidrieras no podrán exhibir animales (nota sobre Ley 451 art. 1.2.9 y ley 2019)](https://www.derechoenzapatillas.com/amp/2021/vidrieras-no-podran-exhibir-animales/) | Derecho en Zapatillas (nota periodística) | leido_parcial |
| [Guía de inspección: veterinarias](https://static.buenosaires.gob.ar/sites/default/files/2026-03/Guia%20Veterinarias%202025%20OK003.pdf) | GCBA / AGC | leido |
