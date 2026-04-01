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

// Injects --stagger-delay on each child element after they're in the DOM
const applyStagger = (selector, stepMs = 100) => {
    document.querySelectorAll(selector).forEach((el, i) => {
        el.style.setProperty('--stagger-delay', `${i * stepMs}ms`);
        el.classList.add('stagger-ready');
    });
};

const renderResults = (data) => {
    const el = document.getElementById("results");
    if (!data || !data.length) {
        el.textContent = "No results available.";
        return;
    }
    el.innerHTML = "";
    el.classList.remove("loading-text");
    data.slice(0, 3).forEach(m => el.appendChild(createMatchRow(m)));
    applyStagger("#results .match", 100);
};

// Hero stat counters from /counts/
const formatCount = (n) => {
    if (n >= 1000) return Math.floor(n / 100) * 100 + '+';
    if (n >= 100)  return Math.floor(n / 10)  * 10  + '+';
    return n.toString();
};

const animateCount = (el, target, suffix = '') => {
    const rounded = target >= 1000 ? Math.floor(target / 100) * 100
                  : target >= 100  ? Math.floor(target / 10)  * 10
                  : target;
    const duration = 1200;
    const start = performance.now();
    const update = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(eased * rounded);
        el.textContent = current.toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
};

const populateHeroStats = () => {
    fetch("https://api.csapi.de/counts/")
        .then(r => r.json())
        .then(data => {
            const matchEl  = document.getElementById('hero-matches');
            const playerEl = document.getElementById('hero-players');
            const teamEl   = document.getElementById('hero-teams');
            if (matchEl)  animateCount(matchEl,  data.matches, '+');
            if (playerEl) animateCount(playerEl, data.players, '+');
            if (teamEl)   animateCount(teamEl,   data.teams,   '+');
        })
        .catch(() => {});
};

const createRankItem = (r) => {
    const item = document.createElement("div");
    item.className = `rank-item ${r.rank <= 3 ? 'top3' : ''}`;

    // Logic: negative rank_diff = improvement (e.g. 5th to 3rd = -2)
    const isImprovement = r.rank_diff < 0;
    const isDrop = r.rank_diff > 0;
    
    const trendClass = isImprovement ? 'trend-up' : isDrop ? 'trend-down' : 'trend-flat';
    const trendIcon = isImprovement ? '▲' : isDrop ? '▼' : '•';
    const absDiff = Math.abs(r.rank_diff);

    item.innerHTML = `
        <div class="rank-num">${r.rank}</div>
        <div class="rank-team">
            ${r.name}
            <span class="rank-trend ${trendClass}">
                ${trendIcon}${absDiff !== 0 ? absDiff : ''}
            </span>
        </div>
        <div class="rank-pts">
            <span class="pts-main">${r.points.toLocaleString()}</span>
            <span class="pts-diff ${r.points_diff >= 0 ? 'pos' : 'neg'}">
                ${r.points_diff >= 0 ? '+' : ''}${r.points_diff}
            </span>
        </div>
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
        data.rankings.slice(0, 10).forEach(r => el.appendChild(createRankItem(r)));
        applyStagger("#rankings .rank-item", 50);
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
    if (rating >= 1.3)  return 'var(--win)';
    if (rating >= 1.15) return 'var(--yellow)';
    if (rating >= 1.0)  return 'var(--warning)';
    return 'var(--danger)';
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
        <div class="lb-stat">${p.swing.toFixed(2)}%</div>
        <div class="lb-stat">${p.adr.toFixed(1)}</div>
        <div class="lb-stat">${p.kast.toFixed(2)}%</div>
        <div class="lb-rating-wrap">
            <div class="lb-rating-bar">
                <div class="lb-rating-fill" style="width:0%; background:${color}; transition: width 0.6s ease ${p.rank * 0.05}s"></div>
            </div>
            <span class="lb-rating-val" style="color:${color}">${p.rating.toFixed(2)}</span>
        </div>
    `;

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            row.querySelector('.lb-rating-fill').style.width = `${barPct}%`;
        });
    });
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
                <span>Swing%</span>
                <span>ADR</span>
                <span>KAST%</span>
                <span>Rating</span>
            </div>
        `;
        el.classList.remove("loading-text");
        data.forEach(p => el.appendChild(createLeaderboardRow(p)));
        applyStagger("#leaderboard .leaderboard-row", 50);
    })
    .catch(() => {
        document.getElementById("leaderboard").textContent = "Could not load leaderboard.";
    });