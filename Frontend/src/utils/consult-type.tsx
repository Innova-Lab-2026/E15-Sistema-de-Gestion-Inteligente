export interface ConsultResponse {
  consultation_id: string;
  status?: StatusConsult;
  interpretation: Interpretation;
  location: Location;
  summary: string;
  requirements: Requirement[];
  documents: Document[];
  steps: Step[];
  territorial_information: TerritorialInformation[];
  online_procedures: OnlineProcedure[];
  physical_offices: PhysicalOffice[];
  map_layers: MapLayer[];
  sources: Source[];
  data_status: DataStatus;
  message: string;
}

type StatusConsult =
  | "needs_clarification"
  | "complete"
  | "activity_unknown"
  | "location_not_found"
  | "partial"
  | "needs_location_confirmation"
  | "out_of_scope";

export interface StatusFeedback {
  type: "error" | "warning" | "info";
  title: string;
  message: string;
  suggestion?: string;
  candidates?: Candidate[];
  warnings?: string[];
  missing?: string[];
}

export function getConsultationStatusFeedback(
  consult: ConsultResponse | null | undefined,
): StatusFeedback | null {
  if (!consult || !consult.status || consult.status === "complete") {
    return null;
  }

  switch (consult.status) {
    case "activity_unknown":
      return {
        type: "warning",
        title: "Actividad no identificada",
        message:
          consult.message ||
          "No pudimos identificar con claridad el rubro o tipo de actividad comercial que deseas realizar.",
        suggestion:
          "Intentá detallar el tipo específico de local o trámite (por ejemplo: 'cafetería', 'farmacia' o 'restaurante').",
      };

    case "location_not_found":
      return {
        type: "error",
        title: "Ubicación no encontrada",
        message:
          consult.message ||
          consult.location?.message ||
          "No pudimos localizar la dirección ingresada dentro de la Ciudad Autónoma de Buenos Aires.",
        suggestion:
          "Verificá que la dirección pertenezca a CABA e incluya la calle y altura catastral (ej.: 'Av. Corrientes 2500') o una intersección ('Av. Santa Fe y Callao').",
      };

    case "needs_location_confirmation":
      return {
        type: "warning",
        title: "Confirmación de ubicación requerida",
        message:
          consult.message ||
          consult.location?.message ||
          "Se encontraron varias posibles ubicaciones que coinciden con tu búsqueda.",
        suggestion:
          "Por favor, seleccioná una de las opciones sugeridas o especificá la altura o barrio exacto:",
        candidates: consult.location?.candidates ?? [],
      };

    case "needs_clarification":
      return {
        type: "warning",
        title: "Información insuficiente",
        message:
          consult.message ||
          "La consulta necesita más detalles para determinar los requisitos y la normativa aplicable.",
        suggestion:
          "Describí tanto la actividad que querés iniciar como la ubicación donde planificás hacerlo (ejemplo: 'Quiero abrir una cafetería en Av. Corrientes 2500').",
      };

    case "out_of_scope":
      return {
        type: "warning",
        title: "Consulta fuera de alcance",
        message:
          consult.message ||
          "La actividad o consulta solicitada no corresponde al régimen de habilitaciones comerciales ni al ámbito de la Ciudad Autónoma de Buenos Aires.",
        suggestion:
          "Este servicio brinda información para habilitaciones comerciales, obras y trámites en el ámbito oficial de CABA.",
      };

    case "partial":
      return {
        type: "info",
        title: "Información parcial",
        message:
          consult.message ||
          "Se obtuvo información preliminar sobre tu consulta, aunque ciertos datos normativos o territoriales podrían estar incompletos.",
        warnings: consult.data_status?.warnings ?? [],
        missing: consult.data_status?.missing ?? [],
      };

    default:
      return {
        type: "warning",
        title: "Estado de la consulta",
        message:
          consult.message ||
          "No se pudo completar la consulta con los datos provistos.",
        suggestion:
          "Por favor revisá los términos de tu búsqueda e intentá nuevamente.",
      };
  }
}

export interface Interpretation {
  intent: string;
  activity: Activity;
  original_query: string;
}

export interface Activity {
  normalized_category: string;
  display_name: string;
  confidence: number;
  raw_text: string;
}

export interface Location {
  normalized_address: string;
  commune: string;
  neighborhood: string;
  city: string;
  latitude: number;
  longitude: number;
  precision: string;
  status: string;
  candidates: Candidate[];
  message: string;
}

export interface Candidate {
  normalized_address: string;
  city: string;
  commune: string;
  neighborhood: string;
  latitude: number;
  longitude: number;
  precision: string;
}

export interface Requirement {
  id: string;
  title: string;
  description: string;
  status: string;
  source_ids: string[];
  documents: Document[];
}

export interface Document {
  name: string;
  details: string;
  url_fuente: string;
  source_ids: string[];
}

export interface Step {
  order: number;
  title: string;
  description: string;
  url_fuente: string;
  source_ids: string[];
}

export interface TerritorialInformation {
  title: string;
  description: string;
  source_ids: string[];
}

export interface OnlineProcedure {
  id: string;
  name: string;
  organization: string;
  type: string;
  address: string;
  opening_hours: string;
  url: string;
  latitude: number;
  longitude: number;
  commune: string;
  neighborhood: string;
  distance_meters: number;
  status: string;
  source_ids: string[];
}

export interface PhysicalOffice {
  id: string;
  name: string;
  organization: string;
  type: string;
  address: string;
  opening_hours: string;
  url: string;
  latitude: number;
  longitude: number;
  commune: string;
  neighborhood: string;
  distance_meters: number;
  status: string;
  source_ids: string[];
}

export interface MapLayer {
  id: string;
  name: string;
  description: string;
  layer_type: string;
  url: string;
  status: string;
  source_ids: string[];
}

export interface Source {
  id: string;
  name: string;
  organization: string;
  url: string;
  source_type: string;
  validity_status: string;
  ingested_at: string;
}

export interface DataStatus {
  overall: string;
  missing: string[];
  warnings: string[];
}
