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
          <h1>Recommended for you</h1>
          {recs.map((r) => (
            <div key={r.item_id} style={{ padding: "8px 0" }}>
              {r.title} — {r.match}%
            </div>
          ))}
        </>
      )}
    </div>
  );
}