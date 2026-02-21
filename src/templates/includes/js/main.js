const fetchHTML = (url, id) =>
  fetch(url).then(r => r.text()).then(data => {
    document.getElementById(id).innerHTML = data;
  });

const getScoreClass = (a, b) =>
  a > b ? "green-score" : a < b ? "red-score" : "neutral-score";

const createMatchRow = (m) => {
  const row = document.createElement("div");
  row.className = "match";
  row.innerHTML = `
    <div class="match-scores">
      <div class="team team-left ${m.winner.id === m.team1.id ? 'team-winner' : ''}">${m.team1.name}</div>
      <div class="score-center">
        <span class="${getScoreClass(m.team1.score, m.team2.score)}">${m.team1.score}</span>
        <span>-</span>
        <span class="${getScoreClass(m.team2.score, m.team1.score)}">${m.team2.score}</span>
      </div>
      <div class="team team-right ${m.winner.id === m.team2.id ? 'team-winner' : ''}">${m.team2.name}</div>
    </div>
    <div class="match-event-date">
      <span>${m.event}</span>
      <span>${m.date}</span>
    </div>
  `;
  return row;
};

const renderResults = (data) => {
  const el = document.getElementById("results");
  if (!data.length) {
    el.textContent = "No results available.";
    return;
  }

  el.innerHTML = "";

  // render first row to measure it
  const firstRow = createMatchRow(data[0]);
  el.appendChild(firstRow);
  const rowHeight = firstRow.getBoundingClientRect().height;

  const cardHeight = document.querySelector('.card:not(.results-card)').getBoundingClientRect().height;
  const remainingHeight = cardHeight - rowHeight;

  const limit = Math.floor(remainingHeight / rowHeight);

  data.slice(1, limit).forEach(m => el.appendChild(createMatchRow(m)));
};

fetchHTML("includes/header.html", "header");
fetchHTML("includes/footer.html", "footer");

fetch("https://api.csapi.de/matches/")
  .then(r => r.json())
  .then(renderResults)
  .catch(err => {
    console.error("Failed to fetch results:", err);
    document.getElementById("results").textContent = "Could not load results.";
  });