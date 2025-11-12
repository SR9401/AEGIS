import { Link } from "react-router-dom";

/**
 * Remplace les URLs ci-dessous par tes vrais liens.
 */
const DEPLOY_URL = "https://ton-deploiement.exemple.app";
const GITHUB_URL = "https://github.com/SR9401/AEGIS";      // OK
//const YT_DEMO_URL = "https://youtube.com/watch?v=ton_demo";

// Liens perso (About)
const ABOUT = {
  name: "Shakib Rojas",
  //linkedin: "https://www.linkedin.com/in/ton-profil",
  github: "https://github.com/SR9401",
};

export default function Landing() {
  return (
    <div className="min-h-screen text-white bg-gradient-to-b from-[#0F182D] via-slate-900 to-[#0F182D]">
      {/* Header / Nav */}
      <header className="sticky top-0 z-20 backdrop-blur bg-black/20 border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="public/logo-aegis.png" alt="AEGIS" className="w-9 h-9 rounded-lg border border-white/15 object-cover" />
            <span className='text-xl font-semibold font-["Cinzel",serif] tracking-wider'>AEGIS</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-300">
            <a href="#features" className="hover:text-white">Features</a>
            <a href="#about" className="hover:text-white">About</a>
            <a href="#deliverables" className="hover:text-white">Deliverables</a>
          </nav>
          <div className="flex items-center gap-2">
            <a
              href={DEPLOY_URL}
              className="px-4 py-2 rounded-xl border border-white/10 bg-indigo-600 hover:bg-indigo-500 transition"
            >
              Open App
            </a>
          </div>
        </div>
      </header>

      {/* Intro / Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[40rem] h-[40rem] rounded-full bg-indigo-600/20 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-[40rem] h-[40rem] rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="mx-auto max-w-7xl px-4 py-16 md:py-24 grid lg:grid-cols-2 gap-10 items-center">
          <div>
            <h1 className='text-4xl md:text-6xl font-extrabold leading-tight font-["Cinzel",serif] tracking-wide'>
              AEGIS — Mission Management System
            </h1>
            <p className="mt-5 text-slate-300 text-lg">
              Plan, assign, and monitor operations with a secure dashboard, interactive map and local weather.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a href={DEPLOY_URL} className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 transition border border-white/10 text-white font-medium">
                Go to Application
              </a>
              <Link to="/login" className="px-5 py-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 transition border border-white/10 text-slate-100">
                Sign in (Local)
              </Link>
            </div>
            <div className="mt-6 flex flex-wrap items-center gap-3 text-[12px] text-slate-400">
              <span className="px-2 py-1 rounded-lg border border-white/10 bg-slate-900/50">JWT Auth</span>
              <span className="px-2 py-1 rounded-lg border border-white/10 bg-slate-900/50">Flask + SQLAlchemy</span>
              <span className="px-2 py-1 rounded-lg border border-white/10 bg-slate-900/50">React + Tailwind</span>
              <span className="px-2 py-1 rounded-lg border border-white/10 bg-slate-900/50">Leaflet Map</span>
              <span className="px-2 py-1 rounded-lg border border-white/10 bg-slate-900/50">OpenWeather</span>
            </div>
          </div>

          {/* Large cover image (Intro requirement) */}
          <div className="rounded-2xl border border-white/10 bg-slate-900/60 shadow-2xl overflow-hidden">
            {/* Mets une vraie capture de ton dashboard dans /public/ */}
            <img src="/logo-aegis.png" alt="AEGIS Cover" className="w-full h-full object-cover" />
          </div>
        </div>
      </section>

      {/* Feature Section (3 features, each with media) */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-16">
        <h2 className='text-2xl md:text-3xl font-bold font-["Cinzel",serif]'>Core Features</h2>
        <p className="mt-2 text-slate-400">Highlights of what you can do with AEGIS.</p>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Feature
            title="Mission Planning"
            desc="Create missions with status, schedule, and geolocation."
            media="public/missionview.png"  // TODO: ajoute une capture/gif dans public/
          />
          <Feature
            title="Resource Assignment"
            desc="Assign available assets and keep track of capacity."
            media="public/resourcesas.png" // TODO
          />
          <Feature
            title="Map & Weather"
            desc="Visualize missions on the map and display local weather."
            media="public/map&weather.png" // TODO
          />
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="mx-auto max-w-7xl px-4 py-16">
        <h2 className='text-2xl md:text-3xl font-bold font-["Cinzel",serif]'>About</h2>
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 text-slate-300 leading-relaxed">
            {/* Inspiration perso — adapte le texte */}
            <p className="mb-3">
              AEGIS was inspired by real coordination needs in field operations (logistics, NGOs, security).
              I wanted a simple, reliable tool to centralize information and speed up decision-making.
            </p>
            <p className="mb-3">
              This project is part of my Holberton Portfolio. It focuses on a clear MVP:
              authentication with roles, mission/resource CRUD, map, and local weather integration.
            </p>
            <a href={GITHUB_URL} target="_blank" className="text-indigo-300 hover:text-indigo-200 underline">
              View the GitHub repository
            </a>
          </div>
          <div className="space-y-3">
            <PersonCard name={ABOUT.name} linkedin={ABOUT.linkedin} github={ABOUT.github} twitter={ABOUT.twitter} />
            <div className="rounded-xl border border-white/10 bg-slate-900/60 p-4 text-sm text-slate-300">
              <div className="font-semibold text-white">Tech (by layer)</div>
              <ul className="mt-2 list-disc list-inside space-y-1">
                <li>Frontend: React (Vite), TailwindCSS</li>
                <li>Backend: Flask, SQLAlchemy, PyJWT, Alembic</li>
                <li>DB: SQLite (MVP), PostgreSQL (next step)</li>
                <li>Integrations: Leaflet + OSM, OpenWeatherMap</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Deliverables */}
      <section id="deliverables" className="mx-auto max-w-7xl px-4 py-16">
        <h2 className='text-2xl md:text-3xl font-bold font-["Cinzel",serif]'>Deliverables</h2>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-300">
          <CardLink label="GitHub Repository" href={GITHUB_URL} />
          {/*<CardLink label="Trello Board" href={TRELLO_URL} />*/}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto max-w-7xl px-4 text-sm text-slate-400 flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <img src="/logo-aegis.png" alt="AEGIS" className="w-6 h-6 rounded" />
            <span>AEGIS — Mission Management System</span>
          </div>
          <div className="flex items-center gap-4">
            <a href={GITHUB_URL} target="_blank" className="hover:text-white">GitHub</a>
            <a href={ABOUT.linkedin} target="_blank" className="hover:text-white">LinkedIn</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Feature({ title, desc, media }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/60 overflow-hidden">
      {/* Media */}
      <div className="aspect-video bg-slate-800/50">
        {/* image/gif/vidéo statique: */}
        <img src={media} alt={title} className="w-full h-full object-cover" />
        {/* Si tu veux une vidéo: remplace <img> par <video controls src={media} className="w-full h-full"/> */}
      </div>
      <div className="p-5">
        <div className="text-lg font-semibold text-white">{title}</div>
        <div className="mt-1 text-slate-400 text-sm">{desc}</div>
      </div>
    </div>
  );
}

function PersonCard({ name, linkedin, github, twitter }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/60 p-4 text-sm">
      <div className="text-white font-semibold">Project by</div>
      <div className="mt-1 text-slate-300">{name}</div>
      <div className="mt-3 flex items-center gap-3">
        {linkedin && <a className="hover:text-white text-slate-300 underline" href={linkedin} target="_blank">LinkedIn</a>}
        {github && <a className="hover:text-white text-slate-300 underline" href={github} target="_blank">GitHub</a>}
        {twitter && <a className="hover:text-white text-slate-300 underline" href={twitter} target="_blank">Twitter</a>}
      </div>
    </div>
  );
}

function CardLink({ label, href }) {
  return (
    <a href={href} target="_blank" className="rounded-xl border border-white/10 bg-slate-900/60 p-4 hover:bg-slate-900/70 transition">
      <div className="text-slate-300">{label}</div>
      <div className="text-indigo-300 text-sm truncate">{href}</div>
    </a>
  );
}
