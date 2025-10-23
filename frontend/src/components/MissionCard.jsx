import React from "react";
export default function MissionCard({mission}){
  const color = mission.status === "active" ? "#16a34a" : mission.status === "done" ? "#2563eb" : "#f59e0b";
  return (
    <article className="mission-card" style={{borderLeftColor: color}}>
      <div className="mission-title">{mission.title}</div>
      <div className="small">{mission.description || ""}</div>
      <div style={{marginTop:10,display:"flex",justifyContent:"space-between",alignItems:"center"}}>
        <div className="small">{mission.date ? new Date(mission.date).toLocaleString() : "—"}</div>
        <div style={{background:"#0f2740",padding:"6px 8px",borderRadius:8,color:"#cfe5ff",fontSize:12}}>{mission.status}</div>
      </div>
    </article>
  );
}
