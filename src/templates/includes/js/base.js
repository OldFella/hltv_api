const themes = [
    { key: null, label: 'DEFAULT' },
    { key: 'cb',  label: 'CB'  },
];

const toggle = document.getElementById('theme-toggle');

function applyTheme(key) {
    if (key) {
        document.documentElement.setAttribute('data-theme', key);
    } else {
        document.documentElement.removeAttribute('data-theme');
    }

    const isAlt = key !== null;
    toggle.classList.toggle('is-active', isAlt);
    toggle.textContent = '🎨 ' + (themes.find(t => t.key === key)?.label ?? 'DEFAULT');
}

// Restore saved theme on load
const saved = localStorage.getItem('theme') || null;
applyTheme(saved);

toggle.addEventListener('click', () => {
    const currentKey = document.documentElement.getAttribute('data-theme') || null;
    const currentIndex = themes.findIndex(t => t.key === currentKey);
    const next = themes[(currentIndex + 1) % themes.length];

    if (next.key) {
        localStorage.setItem('theme', next.key);
    } else {
        localStorage.removeItem('theme');
    }

    applyTheme(next.key);
});

// Last updated fetch
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

const burgerBtn = document.getElementById('burgerBtn');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sidebarClose = document.getElementById('sidebarClose');

function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');
    document.body.style.overflow = '';
}

burgerBtn.addEventListener('click', openSidebar);
sidebarClose.addEventListener('click', closeSidebar);
sidebarOverlay.addEventListener('click', closeSidebar);