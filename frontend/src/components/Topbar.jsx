import React from "react";
export default function Topbar(){
  return (
    <header className="topbar">
      <div style={{display:"flex",alignItems:"center",gap:12}}>
        <input placeholder="Search missions, personnel, resources..." style={{padding:10,borderRadius:8,background:"#071b30",border:"1px solid rgba(255,255,255,0.03)",color:"white",minWidth:420}}/>
      </div>
      <div style={{display:"flex",gap:12,alignItems:"center"}}>
        <div style={{fontSize:14,color:"#bcd3ff"}}>{new Date().toLocaleString()}</div>
        <div style={{width:36,height:36,borderRadius:18,background:"#123147",display:"flex",alignItems:"center",justifyContent:"center"}}>OP</div>
      </div>
    </header>
  );
}
