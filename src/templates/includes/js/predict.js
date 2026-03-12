import { mc_sim, outcomeToResult } from '/static/js/simulation.js';

  const BASE_URL = 'https://api.csapi.de';
  let selectedA = null, selectedB = null, bestOf = 3;
  let useRankings = true, alpha = 0.3, tau = 0.2, nSim = 10000;


  // --- Team search ---
  function setupInput(inputId, dropdownId, onSelect) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    input.addEventListener('input', async () => {
      const q = input.value.trim();
      onSelect(null);
      if (!q) { dropdown.classList.remove('open'); return; }
      const res = await fetch(`${BASE_URL}/teams/?name=${encodeURIComponent(q)}&limit=6`);
      const teams = await res.json();
      if (!teams.length) { dropdown.classList.remove('open'); return; }
      dropdown.innerHTML = teams.map(t =>
        `<div class="dropdown-item" data-id="${t.id}" data-name="${t.name}">${t.name}</div>`
      ).join('');
      dropdown.classList.add('open');
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

  // --- Format ---
  document.querySelectorAll('.fmt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.fmt-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      bestOf = parseInt(btn.dataset.bo);
    });
  });

  // --- Rankings toggle ---
  document.getElementById('rankingsToggle').addEventListener('click', () => {
    useRankings = !useRankings;
    document.getElementById('rankingsToggle').classList.toggle('active', useRankings);
  });

  // --- Advanced ---
  document.getElementById('advToggle').addEventListener('click', () => {
    const panel = document.getElementById('advPanel');
    const open = panel.classList.toggle('open');
    document.getElementById('advToggle').textContent = (open ? '▲' : '▼') + ' Advanced settings';
  });

  document.getElementById('alphaSlider').addEventListener('input', (e) => {
    alpha = parseFloat(e.target.value);
    document.getElementById('alphaVal').textContent = alpha.toFixed(2);
  });

  document.getElementById('tauSlider').addEventListener('input', (e) => {
    tau = parseFloat(e.target.value);
    document.getElementById('tauVal').textContent = tau.toFixed(2);
  });


document.getElementById('nSimInput').addEventListener('input', (e) => {
    nSim = parseInt(e.target.value) || 10000;
});

  // --- Predict ---
  function updateBtn() {
    document.getElementById('predictBtn').disabled =
      !(selectedA && selectedB && selectedA.id !== selectedB?.id);
  }

  document.getElementById('predictBtn').addEventListener('click', async () => {
    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.textContent = 'Loading...';

    const res = await fetch(`${BASE_URL}/predict/${selectedA.id}/${selectedB.id}`);
    const { map_win_probs, ranking_win_prob } = await res.json();

    const combined = map_win_probs.map(p =>
      useRankings ? alpha * ranking_win_prob + (1 - alpha) * p : p
    );

    const outcomes = mc_sim(combined, bestOf, nSim, tau);
    const result = outcomeToResult(outcomes, bestOf);
    renderResult(result);

    btn.textContent = 'Predict';
    updateBtn();
  });

  // --- Render ---
  function renderResult(res) {
    const mapsToWin = { 1: 1, 3: 2, 5: 3 };
    const target = mapsToWin[bestOf];

    document.getElementById('resultEmpty').style.display = 'none';
    document.getElementById('nameA').textContent = selectedA.name;
    document.getElementById('nameB').textContent = selectedB.name;
    document.getElementById('valA').textContent = (res.winA * 100).toFixed(1) + '%';
    document.getElementById('valB').textContent = (res.winB * 100).toFixed(1) + '%';

    document.getElementById('bars').innerHTML = res.dist.map((d, i) => {
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

    document.getElementById('result').classList.add('visible');

    const maxP = Math.max(...res.dist.map(d => d.p));

    res.dist.forEach((d, i) => {
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const bar = document.getElementById(`bar${i}`);
                if (bar) bar.style.width = (d.p / maxP * 100) + '%';
            });
        });
    });
  }