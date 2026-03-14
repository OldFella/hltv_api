// =============================================
// CSAPI — BASE.JS
// Theme toggle, last-updated, sidebar.
// Loaded with defer — runs after DOM is ready.
// =============================================

// ===== THEME =====
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
    if (toggle) {
        toggle.classList.toggle('is-active', key !== null);
        toggle.textContent = '🎨 ' + (themes.find(t => t.key === key)?.label ?? 'DEFAULT');
    }
}

// Restore saved theme — also called by the inline <script> in <head>
// before defer fires, so this just keeps toggle label in sync.
applyTheme(localStorage.getItem('theme') || null);

toggle?.addEventListener('click', () => {
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

// ===== LAST UPDATED =====
fetch("https://api.csapi.de/status")
    .then(r => r.json())
    .then(({ updated_at }) => {
        const formatted = new Date(updated_at).toLocaleString("en-GB", {
            day: "2-digit", month: "short", year: "numeric",
            hour: "2-digit", minute: "2-digit",
            timeZone: "UTC", timeZoneName: "short"
        });
        const el = document.getElementById("last-updated");
        if (el) el.textContent = `Last updated: ${formatted}`;
    })
    .catch(() => {
        const el = document.getElementById("last-updated");
        if (el) el.textContent = "";
    });

// ===== SIDEBAR =====
const burgerBtn       = document.getElementById('burgerBtn');
const sidebar         = document.getElementById('sidebar');
const sidebarOverlay  = document.getElementById('sidebarOverlay');
const sidebarClose    = document.getElementById('sidebarClose');

// Guard: sidebar elements are optional (not all pages need them)
if (sidebar && sidebarOverlay) {
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

    burgerBtn?.addEventListener('click', openSidebar);
    sidebarClose?.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });
}