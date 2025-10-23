import React from "react";
export default function DashboardCards({missions, loading}) {
  const total = missions.length;
  const active = missions.filter(m=>m.status==="active").length;
  const done = missions.filter(m=>m.status==="done").length;
  const critical = missions.filter(m=>m.status==="planned" && (m.title||"").toLowerCase().includes("critical")).length;
  return (
    <div className="cards">
      <div className="card"><div>Active Missions</div><div style={{fontSize:20,fontWeight:700,marginTop:6}}>{active}</div></div>
      <div className="card"><div>Critical Operations</div><div style={{fontSize:20,fontWeight:700,marginTop:6}}>{critical}</div></div>
      <div className="card"><div>Completed</div><div style={{fontSize:20,fontWeight:700,marginTop:6}}>{done}</div></div>
      <div className="card"><div>Total Missions</div><div style={{fontSize:20,fontWeight:700,marginTop:6}}>{total}</div></div>
    </div>
  );
}
