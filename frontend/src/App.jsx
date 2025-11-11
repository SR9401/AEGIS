import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import MissionsPage from "./pages/Missions";
import ResourcesPage from "./pages/Resources.jsx";
import Landing from "./pages/Landing";




function Protected({ children }) {
  const t = localStorage.getItem("access_token");
  return t ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
		<Route path="/landing" element={<Landing />} />
        <Route path="/login" element={<Login/>} />
        <Route path="/dashboard" element={<Protected><Dashboard/></Protected>} />
		<Route path="/missions" element={<Protected><MissionsPage/></Protected>} />
        <Route path="/missions"  element={<Protected><Dashboard/></Protected>} />
        <Route path="/resources" element={<Protected><ResourcesPage/></Protected>} />
        <Route path="/users"     element={<Protected><Dashboard/></Protected>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
