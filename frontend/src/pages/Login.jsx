import { useState } from "react";
import api from "../api/client";

export default function Login() {
  const [email, setEmail] = useState("operator@aegis.mil");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "/dashboard";
    } catch (error) {
      const msg = error?.response?.data?.message || "Login failed.";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F182D] via-blue-600 to-[#0F182D] flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-md rounded-2xl shadow-2xl border border-white/10 p-8">
        {/* Icon */}
		<div className="flex justify-center mb-6">
		<div className="w-22 h-22 rounded-2xl bg-indigo-600/10 border border-indigo-400/30 flex items-center justify-center overflow-hidden">
			<img
			src="img/logo-aegis.png"
			alt="AEGIS"
			className="w-22 h-22 object-contain"
			draggable="false"
			/>
		</div>
		</div>

        <h1 className='flex justify-center mb-6 text-slate-200 font-["Cinzel",serif] text-4xl tracking-wider'>AEGIS</h1>
        <p className="text-slate-300 text-center mt-1">Mission Management System</p>

        <form onSubmit={onSubmit} className="mt-8 space-y-4">
          {/* Email */}
          <label className="block">
            <span className="text-slate-200 text-sm">Email Address</span>
            <div className="mt-1 flex items-center gap-2 bg-slate-800/60 border border-white/10 rounded-xl px-3">
              <span className="text-slate-400">
                <svg width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M12 13L2 6.76V18h20V6.76zM12 11L2 4h20z"/></svg>
              </span>
              <input
                className="w-full bg-transparent py-3 outline-none text-slate-100 placeholder:text-slate-500"
                type="email"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                placeholder="operator@aegis.mil"
                required
                autoFocus
              />
            </div>
          </label>

          {/* Password */}
          <label className="block">
            <span className="text-slate-200 text-sm">Password</span>
            <div className="mt-1 flex items-center gap-2 bg-slate-800/60 border border-white/10 rounded-xl px-3">
              <span className="text-slate-400">
                <svg width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M12 17a2 2 0 1 0 0-4a2 2 0 0 0 0 4m6-6h-1V9a5 5 0 1 0-10 0v2H6a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2m-3 0H9V9a3 3 0 1 1 6 0z"/></svg>
              </span>
              <input
                className="w-full bg-transparent py-3 outline-none text-slate-100 placeholder:text-slate-500"
                type="password"
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          </label>

          {/* Error */}
          {err && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">{err}</div>}

          {/* Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 transition text-white font-semibold shadow-lg shadow-blue-900/30 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Accessing…" : "Access System"}
          </button>
        </form>

        <p className="text-center text-slate-400 text-xs mt-6">
          Authorized Personnel Only • Classification Level: RESTRICTED
        </p>
      </div>
    </div>
  );
}
