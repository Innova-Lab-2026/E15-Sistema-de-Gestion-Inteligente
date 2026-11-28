import { useState } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  const [showNewQuery, setShowNewQuery] = useState(false);

  return (
    <>
      <Navbar showNewQuery={showNewQuery} />
      <main>
        <Outlet context={{ setShowNewQuery }} />
      </main>
    </>
  );
}
