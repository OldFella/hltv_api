const themes = [
    { key: null,     label: '[GRN]' },
    { key: 'orange', label: '[ORG]' },
    { key: 'light',  label: '[LGT]' },
    { key: 'cb',     label: '[HC]'  },
];

const toggle = document.getElementById('theme-toggle');
const saved = localStorage.getItem('theme');

if (saved) document.documentElement.setAttribute('data-theme', saved);

// set initial label
const current = themes.find(t => t.key === (saved || null));
if (current) toggle.textContent = current.label;

toggle.addEventListener('click', () => {
    const currentKey = document.documentElement.getAttribute('data-theme') || null;
    const currentIndex = themes.findIndex(t => t.key === currentKey);
    const next = themes[(currentIndex + 1) % themes.length];

    if (next.key) {
        document.documentElement.setAttribute('data-theme', next.key);
        localStorage.setItem('theme', next.key);
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.removeItem('theme');
    }

    toggle.textContent = next.label;
});

fetch("https://api.csapi.de/status")
.then(r => r.json())
.then(({ updated_at }) => {
    const date = new Date(updated_at);
    const formatted = date.toLocaleString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
    timeZone: "UTC", timeZoneName: "short"
    });
    document.getElementById("last-updated").textContent = `Last updated: ${formatted}`;
})
.catch(() => {
    document.getElementById("last-updated").textContent = "";
});
