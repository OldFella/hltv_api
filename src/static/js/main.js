fetch("includes/header.html")
  .then(res => res.text())
  .then(data => {
    document.getElementById("header").innerHTML = data;
  });

fetch("includes/footer.html")
    .then(res => res.text())
    .then(data => {
    document.getElementById("footer").innerHTML = data;
});


fetch("/results/latest")
  .then(r => r.json())
  .then(data => {
    const el = document.getElementById("results");

    if (!data.length) {
      el.textContent = "No results available.";
      return;
    }

    el.innerHTML = "";

    data.forEach(m => {
      const row = document.createElement("div");
      row.className = "match";

      const teamColor =
        m.score > m.score_opponent ? "green-score" :
        m.score < m.score_opponent ? "red-score" :
        "neutral-score";

      const oppColor =
        m.score_opponent > m.score ? "green-score" :
        m.score_opponent < m.score ? "red-score" :
        "neutral-score";

      row.innerHTML = `
        <div class="match-left">
          <div class="match-scores">
            <div class="team team-left">${m.team}</div>

            <div class="score-center">
              <span class="${teamColor}">${m.score}</span>
              <span>-</span>
              <span class="${oppColor}">${m.score_opponent}</span>
            </div>

            <div class="team team-right">${m.opponent}</div>
          </div>

          <div class="match-event-date">
            <span>${m.event}</span>
            <span>${m.date}</span>
          </div>
        </div>
      `;

      el.appendChild(row);
    });
  })
  .catch(err => {
    console.error("Failed to fetch results:", err);
    document.getElementById("results").textContent =
      "Could not load results.";
  });