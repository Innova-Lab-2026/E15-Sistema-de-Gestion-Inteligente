export const resultsData = {
    title: "Abrir una cafetería en Av. Corrientes 2500",

    activity: "Cafetería",
    location: "Av. Corrientes 2500",

    summary: {
        title: "1 - Verificar la ubicación (Consulta de Uso)",
        description: "La actividad gastronomica es compatible con la ubicación. Vas a necesitar realizar 2 tramites principales, cumplir con normativas de locales de manipulación de alimentos e inscripcion en AFIP y AGIP, ademas de considerar el contexto de alta circulación peatonal de la zona."
    },

    procedures: [
        {
            id: 1,
            title: "Habilitación del local gastronómico",
            description: "Autorización obligatoria para operar con venta de alimentos."
        },
        {
            id: 2,
            title: "Inscripción en AFIP y AGIP (Ingresos Brutos)",
            description: "Alta impositiva jurisdiccional requerida previa a la apertura."
        }
    ],

    requirements: [
        {
            id: 1,
            title: "Documentación Legal y del Local",
            items: [
                { id: 1, description: "DNI del titular o estatuto societario si es persona juridica." },
                { id: 2, description: "Contrato de alquiler o escritura y boleta de ABL." }
            ]
        },
        {
            id: 2,
            title: "Documentación Técnica",
            items: [
                { id: 1, description: "Intervencion de un profesional matriculado (arquitecto, ingeniero o mmaestro mayor de obras) para confeccionar la encomienda profesional, el anexo técnico y los planos del local." }
            ]
        },
        {
            id: 3,
            title: "Documentación de Autoprotección",
            items: [
                { id: 1, description: "Presentacion requerida según las caracteristicas de evaluación del local." }
            ]
        },
        {
            id: 4,
            title: "Condiciones Bromatológicas y de Seguridad",
            items: [
                { id: 1, description: "Cumplir con ventilación adecuada para cocinas, áreas diferenciadas de munipulación de alimentos y elementos contra incendios (matafuegos, luces de emergencia)." }
            ]
        }
    ]
};