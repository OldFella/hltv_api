const getScoreClass = (a, b) =>
    a > b ? "green-score" : a < b ? "red-score" : "neutral-score";

const createMatchRow = (m) => {
    const row = document.createElement("div");
    row.className = "match";

    const mapChips = (m.maps || []).map(map => {
        const t1wins = map.team1_score > map.team2_score;
        const t2wins = map.team2_score > map.team1_score;
        return `<span class="map-chip">
            <span class="map-name">${map.name}</span>
            <span class="map-score ${t1wins ? 'green-score' : 'red-score'}">${map.team1_score}</span>
            <span class="map-sep">–</span>
            <span class="map-score ${t2wins ? 'green-score' : 'red-score'}">${map.team2_score}</span>
        </span>`;
    }).join('');

    row.innerHTML = `
        <div class="match-meta">
            <span class="match-event">${m.event}</span>
            <span class="match-date">${m.date}</span>
        </div>
        <div class="match-scores">
            <div class="team team-left ${m.winner.id === m.team1.id ? 'team-winner' : ''}">
                <span class="team-name">${m.team1.name}</span>
                ${m.team1.rank ? `<span class="team-rank">#${m.team1.rank}</span>` : ''}
            </div>
            <div class="score-center">
                <div class="score-nums">
                    <span class="${getScoreClass(m.team1.score, m.team2.score)}">${m.team1.score}</span>
                    <span class="score-sep">:</span>
                    <span class="${getScoreClass(m.team2.score, m.team1.score)}">${m.team2.score}</span>
                </div>
                <div class="score-label">BEST OF ${m.best_of}</div>
            </div>
            <div class="team team-right ${m.winner.id === m.team2.id ? 'team-winner' : ''}">
                <span class="team-name">${m.team2.name}</span>
                ${m.team2.rank ? `<span class="team-rank">#${m.team2.rank}</span>` : ''}
            </div>
        </div>
        ${mapChips ? `<div class="match-maps">${mapChips}</div>` : ''}
    `;
    return row;
};

const renderResults = (data) => {
    const el = document.getElementById("results");
    if (!data || !data.length) {
        el.textContent = "No results available.";
        return;
    }
    el.innerHTML = "";
    el.classList.remove("loading-text");
    data.slice(0,3).forEach(m => el.appendChild(createMatchRow(m)));
};

// Hero stat counters from /counts/
const formatCount = (n) => {
    if (n >= 1000) return Math.floor(n / 100) * 100 + '+';
    if (n >= 100)  return Math.floor(n / 10)  * 10  + '+';
    return n.toString();
};

const populateHeroStats = () => {
    fetch("https://api.csapi.de/counts/")
        .then(r => r.json())
        .then(data => {
            const matchEl  = document.getElementById('hero-matches');
            const playerEl = document.getElementById('hero-players');
            const teamEl   = document.getElementById('hero-teams');
            if (matchEl)  matchEl.textContent  = formatCount(data.matches);
            if (playerEl) playerEl.textContent = formatCount(data.players);
            if (teamEl)   teamEl.textContent   = formatCount(data.teams);
        })
        .catch(() => {});
};

// Rankings
const createRankItem = (r) => {
    const item = document.createElement("div");
    item.className = `rank-item ${r.rank <= 3 ? 'top3' : ''}`;
    item.innerHTML = `
        <div class="rank-num">${r.rank}</div>
        <div class="rank-team">${r.name}</div>
        <div class="rank-pts">${r.points.toLocaleString()} pts</div>
    `;
    return item;
};

// Fire all fetches in parallel
populateHeroStats();

fetch("https://api.csapi.de/rankings/")
    .then(r => r.json())
    .then(data => {
        const el = document.getElementById("rankings");
        if (!data.rankings || !data.rankings.length) {
            el.textContent = "No rankings available.";
            return;
        }
        el.innerHTML = "";
        el.classList.remove("loading-text");
        data.rankings.slice(0, 12).forEach(r => el.appendChild(createRankItem(r)));
    })
    .catch(() => {
        document.getElementById("rankings").textContent = "Could not load rankings.";
    });

fetch("https://api.csapi.de/matches/latest")
    .then(r => r.json())
    .then(data => renderResults(data))
    .catch(err => {
        console.error("Failed to fetch results:", err);
        document.getElementById("results").textContent = "Could not load results.";
    });

const ratingColor = (rating) => {
    if (rating >= 1.3) return 'var(--win)';        // green
    if (rating >= 1.15) return 'var(--accent)';    // gold
    if (rating >= 1.0) return 'var(--warning)';    // orange
    return 'var(--danger)';                         // red
};


const createLeaderboardRow = (p) => {
    const row = document.createElement("div");
    row.className = `leaderboard-row ${p.rank <= 3 ? 'top3' : ''}`;
    const color = ratingColor(p.rating);
    const barPct = Math.min(100, Math.max(0, ((p.rating - 0.8) / 0.7) * 100)).toFixed(1);
    const kd = p.d > 0 ? (p.k / p.d).toFixed(2) : p.k.toFixed(2);
    row.innerHTML = `
        <div class="lb-rank">${p.rank}</div>
        <div class="lb-name">${p.name}</div>
        <div class="lb-maps">${p.N}</div>
        <div class="lb-stat">${kd}</div>
        <div class="lb-stat">${p.adr.toFixed(1)}</div>
        <div class="lb-stat">${p.kast.toFixed(2)}%</div>
        <div class="lb-rating-wrap">
            <div class="lb-rating-bar">
                <div class="lb-rating-fill" style="width:${barPct}%; background:${color}"></div>
            </div>
            <span class="lb-rating-val" style="color:${color}">${p.rating.toFixed(2)}</span>
        </div>
    `;
    return row;
};

fetch("https://api.csapi.de/players/stats?limit=10")
    .then(r => r.json())
    .then(data => {
        const el = document.getElementById("leaderboard");
        if (!data || !data.length) {
            el.textContent = "No data available.";
            return;
        }
        el.innerHTML = `
            <div class="lb-header">
                <span>#</span>
                <span>Player</span>
                <span>Maps</span>
                <span>K/D</span>
                <span>ADR</span>
                <span>KAST%</span>
                <span>Rating</span>
            </div>
        `;
        el.classList.remove("loading-text");
        data.forEach(p => el.appendChild(createLeaderboardRow(p)));
    })
    .catch(() => {
        document.getElementById("leaderboard").textContent = "Could not load leaderboard.";
    });