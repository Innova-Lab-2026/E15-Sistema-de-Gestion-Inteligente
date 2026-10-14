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
      zoom={17}
      className="m-auto"
      scrollWheelZoom={false}
      style={{ height: "500px", width: "500px" }}
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
