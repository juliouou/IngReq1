import { Outlet } from "react-router-dom";
import { Topbar } from "./Topbar";
import { ChatWidget } from "../ui/ChatWidget";

export function AppLayout() {
  return (
    <div className="app-shell-top">
      {/* Global Watermark */}
      <div className="global-watermark">
        <img src="/logo.png" alt="" />
      </div>

      <Topbar />
      <main className="main-area-top">
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <Outlet />
        </div>
      </main>

      <ChatWidget />
    </div>
  );
}
