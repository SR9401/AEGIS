import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosInstance";

export default function Login(){
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e){
    e.preventDefault();
    setError(null);
    setLoading(true);
    try{
      const res = await api.post("/auth/login", { email: (email||"").trim().toLowerCase(), password });
      // selon ton backend le token peut être dans res.data.access_token
      const token = res.data && (res.data.access_token || res.data.token);
      if(token){
        localStorage.setItem("token", token);
      }
      // tu peux stocker snapshot user si renvoyé
      if(res.data && res.data.user) localStorage.setItem("user", JSON.stringify(res.data.user));
      navigate("/");
    }catch(err){
      console.error("login error", err);
      const msg = err?.response?.data?.message || "Erreur de connexion";
      setError(msg);
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card" role="main" aria-labelledby="login-title">
        <div className="login-logo">
          <div style={{fontSize:42, color:"#2b6ef6", marginBottom:8}}>🔰</div>
        </div>
        <div id="login-title" className="login-title">AEGIS</div>
        <div className="login-sub">Mission Management System</div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <label className="small-muted" htmlFor="email">Email Address</label>
            <input id="email" className="input" placeholder="operator@aegis.mil" value={email}
                   onChange={e=>setEmail(e.target.value)} />
          </div>

          <div className="form-row">
            <label className="small-muted" htmlFor="pw">Password</label>
            <input id="pw" className="input" type="password" placeholder="••••••••" value={password}
                   onChange={e=>setPassword(e.target.value)} />
          </div>

          {error && <div style={{color:"#ff8a8a", marginBottom:12, fontSize:13}}>{error}</div>}

          <div className="form-row">
            <button type="submit" className="button-primary" disabled={loading}>
              {loading ? "Connexion..." : "Access System"}
            </button>
          </div>
        </form>

        <div className="small-muted">Authorized Personnel Only • Classification Level: RESTRICTED</div>
      </div>
    </div>
  );
}

