import React from "react";
import MissionCard from "./MissionCard";
export default function MissionsList({missions, loading}){
  if(loading) return <div className="card">Loading missions…</div>;
  if(!missions.length) return <div className="card">No missions found.</div>;
  return (
    <div>
      {missions.map(m => <MissionCard key={m.id} mission={m} />)}
    </div>
  );
}

