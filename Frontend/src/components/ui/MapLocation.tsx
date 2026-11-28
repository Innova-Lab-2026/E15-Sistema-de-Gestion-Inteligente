import { type LatLngExpression } from "leaflet";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

export default function MapLocation({
  position,
}: {
  position: LatLngExpression;
}) {
  return (
    <MapContainer
      center={position}
      zoom={16}
      className="m-auto font-sans z-10 w-full h-56 rounded-lg"
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={position}>
        <Popup>Ubicación del establecimiento</Popup>
      </Marker>
    </MapContainer>
  );
}
