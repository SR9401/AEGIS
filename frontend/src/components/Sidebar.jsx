import React from "react";
export default function Sidebar(){
  return (
    <aside className="sidebar">
      <div className="logo">AEGIS</div>
      <nav>
        <a className="menu-item" href="#">Dashboard</a>
        <a className="menu-item" href="#">Missions</a>
        <a className="menu-item" href="#">Resources</a>
        <a className="menu-item" href="#">Personnel</a>
      </nav>
    </aside>
  );
}
