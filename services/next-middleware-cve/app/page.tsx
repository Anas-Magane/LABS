export default function Home() {
  return (
    <div>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "1.1rem 2.5rem",
          background: "var(--navy-2)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontWeight: 700 }}>
          <span
            style={{
              width: 28,
              height: 28,
              borderRadius: 7,
              background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
              display: "inline-block",
            }}
          />
          Anas Education Platform
        </div>
        <nav style={{ fontSize: "0.92rem", color: "var(--text-dim)" }}>
          <span style={{ marginLeft: "1.5rem" }}>Courses</span>
          <span style={{ marginLeft: "1.5rem" }}>Students</span>
          <span style={{ marginLeft: "1.5rem" }}>About</span>
        </nav>
      </header>

      <main style={{ maxWidth: 880, margin: "0 auto", padding: "4rem 2rem" }}>
        <div
          style={{
            color: "var(--accent)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            fontSize: "0.78rem",
            fontWeight: 600,
          }}
        >
          Online Learning
        </div>
        <h1 style={{ fontSize: "2.1rem", margin: "0.6rem 0 0.8rem" }}>
          Welcome To Anas Education Platform
        </h1>
        <p style={{ color: "var(--text-dim)", fontSize: "1.05rem", maxWidth: 560, lineHeight: 1.6 }}>
          A lightweight learning portal for course materials, assignments, and
          student progress tracking.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1.1rem",
            marginTop: "2.5rem",
          }}
        >
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 10, padding: "1.4rem" }}>
            <h3 style={{ margin: "0 0 0.4rem", fontSize: "1rem" }}>Course Library</h3>
            <p style={{ margin: 0, color: "var(--text-dim)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Browse published course materials and lecture notes.
            </p>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 10, padding: "1.4rem" }}>
            <h3 style={{ margin: "0 0 0.4rem", fontSize: "1rem" }}>Assignments</h3>
            <p style={{ margin: 0, color: "var(--text-dim)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Track upcoming assignment deadlines and submissions.
            </p>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 10, padding: "1.4rem" }}>
            <h3 style={{ margin: "0 0 0.4rem", fontSize: "1rem" }}>Progress</h3>
            <p style={{ margin: 0, color: "var(--text-dim)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Review grades and completion status at a glance.
            </p>
          </div>
        </div>
      </main>

      <footer
        style={{
          textAlign: "center",
          padding: "2rem",
          color: "var(--text-dim)",
          fontSize: "0.82rem",
          borderTop: "1px solid var(--border)",
          marginTop: "3rem",
        }}
      >
        &copy; Anas Education Platform
      </footer>
    </div>
  );
}
