import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [genres, setGenres] = useState([]);
  const [step, setStep] = useState("genre");
  const [films, setFilms] = useState([]);
  const [ratings, setRatings] = useState({});
  const [recs, setRecs] = useState([]);
  
  useEffect(() => {
    fetch(API + "/genres")
      .then((res) => res.json())
      .then((data) => setGenres(data.filter((g) => g !== "unknown")));
  }, []);

  const pickGenre = (g) => {
    fetch(`${API}/genres/${g}/popular`)
      .then((res) => res.json())
      .then((data) => { setFilms(data); setStep("rate"); });
  };

  const setRating = (id, val) => setRatings({ ...ratings, [id]: val });
  const getRecs = () => {
  const payload = Object.entries(ratings).map(([id, r]) => ({
    item_id: Number(id),
    rating: r,
  }));
  fetch(`${API}/recommend?limit=10`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((data) => { setRecs(data); setStep("results"); });
};

  return (
    <div style={{ maxWidth: 680, margin: "2rem auto", fontFamily: "system-ui", padding: "0 1rem" }}>
      {step === "genre" && (
        <>
          <h1>Pick a genre</h1>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}>
            {genres.map((g) => (
              <button key={g} onClick={() => pickGenre(g)} style={{ padding: "12px" }}>
                {g}
              </button>
            ))}
          </div>
        </>
      )}

      {step === "rate" && (
        <>
          <h1>Rate a few films</h1>
          {films.map((f) => (
            <div key={f.item_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 0" }}>
              <span style={{ flex: 1 }}>{f.title}</span>
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onClick={() => setRating(f.item_id, n)}
                  style={{
                    padding: "6px 10px",
                    background: ratings[f.item_id] === n ? "#333" : "transparent",
                    color: ratings[f.item_id] === n ? "#fff" : "inherit",
                  }}
                >
                  {n}
                </button>
              ))}
            </div>
          ))}
<button onClick={getRecs} style={{ marginTop: 12, padding: "8px 16px" }}>
            Get Recommendations
          </button>
        </>
      )}

{step === "results" && (
  <>
    <h1 style={{ marginBottom: 4 }}>Recommended for you</h1>
    <p style={{ color: "#666", marginTop: 0, marginBottom: 20 }}>
      Based on {Object.keys(ratings).length} films you rated
    </p>
    <div style={{ border: "1px solid #e5e5e5", borderRadius: 12, overflow: "hidden" }}>
      {recs.map((r, i) => (
        <div
          key={r.item_id}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            padding: "14px 18px",
            borderBottom: i < recs.length - 1 ? "1px solid #eee" : "none",
          }}
        >
          <div style={{ color: "#999", minWidth: 18, fontSize: 13 }}>{i + 1}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 500 }}>{r.title}</div>
            <div style={{ color: "#666", fontSize: 13 }}>
              {r.year} · {r.genres.join(", ")} · {r.n_ratings} ratings
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontWeight: 500, color: "#2563eb" }}>{Math.round(r.match)}%</div>
            <div style={{ fontSize: 11, color: "#999" }}>match</div>
          </div>
        </div>
      ))}
    </div>
    <button
      onClick={() => { setStep("genre"); setRatings({}); }}
      style={{ marginTop: 16, padding: "10px 16px" }}
    >
      Start over
    </button>
</>
)}
    </div>
  );
}