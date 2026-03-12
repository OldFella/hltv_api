function softmax_t(x,tau){
    const e = x.map((el) => Math.exp(el/tau));
    const sum = e.reduce((acc,value) => acc + value, 0);
    return e.map((el) => el/sum);
};

function choose(array, weights){
    const cumulative  = [];
    weights.reduce((acc, w, i) => {
        cumulative[i] = acc + w;
        return cumulative[i]
    }, 0);
    const r = Math.random();
    return array[cumulative.findIndex(c => r <= c)];
};

function do_ban(tau, mapWinProbs, worst = true){
    const banProbs = worst ? mapWinProbs.map((el) => 1-el) : mapWinProbs;
    const weights = softmax_t(banProbs,tau);
    const indices = Array.from({length:mapWinProbs.length}, (_,i) => i);
    return choose(indices, weights);
};

function do_pick(tau, mapWinProbs, best = true){
    const pickProbs = best ? mapWinProbs: mapWinProbs.map((el) => 1-el);
    const weights = softmax_t(pickProbs,tau);
    const indices = Array.from({length:mapWinProbs.length}, (_,i) => i);
    return choose(indices, weights);
};

function remove(mapWinProbs, idx){
    return mapWinProbs.filter((_,i) => i !== idx);
};

function pick_and_remove(picks, tau, mapWinProbs, best=true){
    const idx = do_pick(tau, mapWinProbs, best);
    const val = mapWinProbs[idx];
    picks.push(val);
    return remove(mapWinProbs, idx);
};

function ban_and_remove(tau, mapWinProbs, worst){
    const idx = do_ban(tau, mapWinProbs, worst);
    return remove(mapWinProbs, idx);
};

function simulate_series(mapWinProbs, best_of = 3 ,tau = 0.2){
    let p = mapWinProbs.slice();
    let picks = [];

    // First ban rotation (shared across all formats)
    p = ban_and_remove(tau, p, true);
    p = ban_and_remove(tau, p, false);

    if (best_of == 1){
        p = ban_and_remove(tau, p, true);
        p = ban_and_remove(tau, p, false);
        p = ban_and_remove(tau, p, true);
        p = ban_and_remove(tau, p, false);
    }
    else if (best_of ==3){
        p = pick_and_remove(picks, tau, p, true);
        p = pick_and_remove(picks, tau, p, false);
        p = ban_and_remove(tau, p, false);
        p = ban_and_remove(tau, p, true);
    }
    else if (best_of == 5){
        p = pick_and_remove(picks, tau, p, true);
        p = pick_and_remove(picks, tau, p, false);
        p = pick_and_remove(picks, tau, p, true);
        p = pick_and_remove(picks, tau, p, false);
    }

    // Decider
    picks.push(p[0]);
    return picks
};

function mc_sim(mapWinProbs, best_of = 3, N = 10000, tau = 0.2){
    const mapsToWin = {1:1, 3:2, 5:3};
    const target = mapsToWin[best_of];
    let outcomes = {};

    for (let i=0; i< N; i++){
        let picks = simulate_series(mapWinProbs, best_of, tau);
        let score_a = 0;
        let score_b = 0;

        for(let j =0; j < picks.length; j++) {
            let r = Math.random();
            if (r < picks[j]){
                score_a++;
            }
            else{
                score_b--;
            }
            if (Math.abs(score_a)==target || Math.abs(score_b) == target){ break;
            } 
        }
        let score = score_a + score_b;
        outcomes[score] = (outcomes[score] || 0) + 1;
    }
    return outcomes;
};

function scoreToLabel(score, target){
    if (score > 0) return `${target} - ${target - score}`;
    return `${target+score} - ${target}`
};

function outcomeToResult(outcomes, best_of) {
    const mapsToWin = {1: 1, 3: 2, 5: 3};
    const target = mapsToWin[best_of];
    const total = Object.values(outcomes).reduce((a, b) => a + b, 0);

    const sortedOutcomes = Object.entries(outcomes)
        .sort(([a], [b]) => parseInt(b) - parseInt(a));

    const winA = sortedOutcomes
        .filter(([k]) => parseInt(k) > 0)
        .reduce((sum, [, v]) => sum + v, 0) / total;

    const dist = sortedOutcomes.map(([score, n]) => ({
        o: scoreToLabel(parseInt(score), target),
        p: n / total,
    }));

    return { winA, winB: 1 - winA, dist };
}

export {simulate_series, mc_sim, outcomeToResult };