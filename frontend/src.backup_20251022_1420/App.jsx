import React from "react";

export default function App(){
  return (
    <div style={{minHeight:"100vh", display:"grid", placeItems:"center", background:"#07103a", color:"#eaf4ff"}}>
      <div style={{padding:30, borderRadius:12, background:"#08162a", boxShadow:"0 8px 30px rgba(0,0,0,0.6)"}}>
        <h1 style={{margin:0}}>AEGIS — Front: rendu OK</h1>
        <p style={{marginTop:8, color:"#9fb4d6"}}>Si tu vois ceci, React monte correctement.</p>
      </div>
    </div>
  );
}
