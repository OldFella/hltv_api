import { mc_sim, outcomeToResult } from '/static/js/simulation.js';

const BASE_URL = 'https://api.csapi.de';

// ===== STATE =====
let selectedA = null, selectedB = null, bestOf = 3;
let useRankings = true, alpha = 0.7, tau = 0.2, nSim = 10000;

// ===== CACHED DOM REFS =====
const predictBtn      = document.getElementById('predictBtn');
const rankingsToggle  = document.getElementById('rankingsToggle');
const advToggle       = document.getElementById('advToggle');
const advPanel        = document.getElementById('advPanel');
const alphaSlider     = document.getElementById('alphaSlider');
const alphaVal        = document.getElementById('alphaVal');
const tauSlider       = document.getElementById('tauSlider');
const tauVal          = document.getElementById('tauVal');
const nSimInput       = document.getElementById('nSimInput');
const resultEl        = document.getElementById('result');
const resultEmpty     = document.getElementById('resultEmpty');
const barsEl          = document.getElementById('bars');
const nameAEl         = document.getElementById('nameA');
const nameBEl         = document.getElementById('nameB');
const valAEl          = document.getElementById('valA');
const valBEl          = document.getElementById('valB');

// ===== UTILS =====

// Runs callback after two animation frames — ensures element is in the DOM
// and its initial style has been painted before applying a transition.
const afterPaint = (fn) => requestAnimationFrame(() => requestAnimationFrame(fn));

const setError = (message) => {
    resultEmpty.style.display = '';
    resultEmpty.querySelector('.loading-text').textContent = message;
    resultEl.classList.remove('visible');
};

// ===== TEAM SEARCH =====
function setupInput(inputId, dropdownId, onSelect) {
    const input    = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    input.addEventListener('input', async () => {
        const q = input.value.trim();
        onSelect(null);
        if (!q) { dropdown.classList.remove('open'); return; }

        try {
            const res   = await fetch(`${BASE_URL}/teams/?name=${encodeURIComponent(q)}&limit=6`);
            const teams = await res.json();
            if (!teams.length) { dropdown.classList.remove('open'); return; }
            dropdown.innerHTML = teams.map(t =>
                `<div class="dropdown-item" data-id="${t.id}" data-name="${t.name}">${t.name}</div>`
            ).join('');
            dropdown.classList.add('open');
        } catch {
            dropdown.classList.remove('open');
        }
    });

    dropdown.addEventListener('mousedown', (e) => {
        const item = e.target.closest('.dropdown-item');
        if (!item) return;
        input.value = item.dataset.name;
        input.classList.add('selected');
        dropdown.classList.remove('open');
        onSelect({ id: parseInt(item.dataset.id), name: item.dataset.name });
        updateBtn();
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target))
            dropdown.classList.remove('open');
    });
}

setupInput('inputA', 'dropdownA', (t) => { selectedA = t; updateBtn(); });
setupInput('inputB', 'dropdownB', (t) => { selectedB = t; updateBtn(); });

// ===== FORMAT =====
document.querySelectorAll('.fmt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.fmt-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        bestOf = parseInt(btn.dataset.bo);
    });
});

// ===== RANKINGS TOGGLE =====
rankingsToggle.addEventListener('click', () => {
    useRankings = !useRankings;
    rankingsToggle.classList.toggle('active', useRankings);
});

// ===== ADVANCED PANEL =====
// Read the open/close prefix from the element itself so JS doesn't
// need to know the label text — it's owned by the YAML/template.
const advBaseLabel = advToggle.textContent.replace(/^[▲▼]\s*/, '').trim();

advToggle.addEventListener('click', () => {
    const open = advPanel.classList.toggle('open');
    advToggle.textContent = (open ? '▲' : '▼') + ' ' + advBaseLabel;
});

alphaSlider.addEventListener('input', (e) => {
    alpha = parseFloat(e.target.value);
    alphaVal.textContent = alpha.toFixed(2);
});

tauSlider.addEventListener('input', (e) => {
    tau = parseFloat(e.target.value);
    tauVal.textContent = tau.toFixed(2);
});

nSimInput.addEventListener('input', (e) => {
    nSim = parseInt(e.target.value) || 10000;
});

// ===== PREDICT =====
function updateBtn() {
    predictBtn.disabled = !(selectedA && selectedB && selectedA.id !== selectedB?.id);
}

predictBtn.addEventListener('click', async () => {
    predictBtn.disabled = true;
    predictBtn.textContent = 'Loading...';

    try {
        const res = await fetch(`${BASE_URL}/predict/${selectedA.id}/${selectedB.id}`);
        if (!res.ok) throw new Error(`API error ${res.status}`);

        const { map_win_probs, ranking_win_prob } = await res.json();

        const combined = map_win_probs.map(p =>
            useRankings ? alpha * ranking_win_prob + (1 - alpha) * p : p
        );

        const outcomes = mc_sim(combined, bestOf, nSim, tau);
        const result   = outcomeToResult(outcomes, bestOf);
        renderResult(result);

    } catch (err) {
        console.error('Predict failed:', err);
        setError('Could not load prediction. Try again.');
    } finally {
        predictBtn.textContent = 'Predict';
        updateBtn();
    }
});

// ===== RENDER =====
function renderResult(res) {
    const target = { 1: 1, 3: 2, 5: 3 }[bestOf];

    resultEmpty.style.display = 'none';
    nameAEl.textContent = selectedA.name;
    nameBEl.textContent = selectedB.name;
    valAEl.textContent  = (res.winA * 100).toFixed(1) + '%';
    valBEl.textContent  = (res.winB * 100).toFixed(1) + '%';

    const maxP = Math.max(...res.dist.map(d => d.p));

    barsEl.innerHTML = res.dist.map((d, i) => {
        const isWin = d.o.startsWith(String(target));
        return `
            <div class="bar-row">
                <span class="outcome">${d.o}</span>
                <div class="bar-track">
                    <div class="bar-fill ${isWin ? 'win' : 'lose'}" id="bar${i}"></div>
                </div>
                <span class="pct ${isWin ? 'win' : 'lose'}">${(d.p * 100).toFixed(1)}%</span>
            </div>`;
    }).join('');

    resultEl.classList.add('visible');

    afterPaint(() => {
        res.dist.forEach((d, i) => {
            const bar = document.getElementById(`bar${i}`);
            if (bar) bar.style.width = (d.p / maxP * 100) + '%';
        });
    });
}