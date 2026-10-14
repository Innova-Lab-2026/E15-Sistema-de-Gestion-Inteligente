import type { LatLngExpression } from "leaflet";
import MapLocation from "@/components/MapLocation";

function App() {
  const position: LatLngExpression = [-34.6035512473822, -58.381626261539125];

  return (
    <>
      <MapLocation position={position} />
    </>
  );
}

export default App;
