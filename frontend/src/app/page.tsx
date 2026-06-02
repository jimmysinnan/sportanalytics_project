export default function Home() {
  return (
    <main
      className="flex flex-1 flex-col items-center justify-center min-h-screen"
      style={{ background: "var(--bg)" }}
    >
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold text-grad">La Soccer Machine</h1>
        <p style={{ color: "var(--muted)" }} className="text-lg">
          Plateforme analytics football pro — bientôt disponible
        </p>
        <div
          className="inline-block px-6 py-2 rounded-full text-sm font-medium pulse-green"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            color: "var(--green)",
          }}
        >
          Backend en cours de connexion...
        </div>
      </div>
    </main>
  );
}
