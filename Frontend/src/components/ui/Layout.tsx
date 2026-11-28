import { useState } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  const [showNewQuery, setShowNewQuery] = useState(false);

  return (
    <div className="min-h-screen w-full flex flex-col bg-background-white-2">
      <Navbar showNewQuery={showNewQuery} />
      <main className="flex-1 w-full">
        <Outlet context={{ setShowNewQuery }} />
      </main>
    </div>
  );
}
