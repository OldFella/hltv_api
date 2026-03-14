const input        = document.getElementById('searchInput');
const allItems     = Array.from(document.querySelectorAll('#folderList li'));
const emptyMessage = document.getElementById('emptyMessage');
const visibleCount = document.getElementById('visibleCount');
const pagination   = document.getElementById('pagination');

const PER_PAGE = 5;
let currentPage = 1;
let filtered = allItems; // items currently matching the search

// ===== FILTER =====
input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    filtered = allItems.filter(li =>
        li.textContent.toLowerCase().includes(q)
    );
    currentPage = 1;
    render();
});

// ===== RENDER =====
function render() {
    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));
    currentPage = Math.min(currentPage, totalPages);

    const start = (currentPage - 1) * PER_PAGE;
    const pageItems = filtered.slice(start, start + PER_PAGE);

    // Hide all, show only current page slice
    allItems.forEach(li => li.style.display = 'none');

    pageItems.forEach((li, i) => {
        li.style.display = '';
        // Update index number to reflect global position
        const num = li.querySelector('.fantasy-num');
        if (num) num.textContent = start + i + 1;
        // Stagger
        const item = li.querySelector('.fantasy-item');
        if (item) {
            item.style.opacity = '0';
            item.style.setProperty('--stagger-delay', `${i * 50}ms`);
            // Re-trigger animation by forcing reflow
            item.classList.remove('animate');
            void item.offsetWidth;
            item.classList.add('animate');
        }
    });

    if (visibleCount) visibleCount.textContent = total;
    emptyMessage.style.display = total === 0 ? '' : 'none';

    renderPagination(totalPages);
}

// ===== PAGINATION =====
function renderPagination(totalPages) {
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    const pages = buildPageRange(currentPage, totalPages);

    pagination.innerHTML = pages.map(p => {
        if (p === '…') return `<span class="page-gap">…</span>`;
        return `<button
            class="page-btn${p === currentPage ? ' active' : ''}"
            data-page="${p}">${p}</button>`;
    }).join('');

    // Prev / next
    pagination.insertAdjacentHTML('afterbegin',
        `<button class="page-btn page-nav" data-page="${currentPage - 1}"
            ${currentPage === 1 ? 'disabled' : ''}>←</button>`
    );
    pagination.insertAdjacentHTML('beforeend',
        `<button class="page-btn page-nav" data-page="${currentPage + 1}"
            ${currentPage === totalPages ? 'disabled' : ''}>→</button>`
    );

    pagination.querySelectorAll('.page-btn[data-page]').forEach(btn => {
        btn.addEventListener('click', () => {
            const p = parseInt(btn.dataset.page);
            if (!isNaN(p) && p >= 1 && p <= totalPages) {
                currentPage = p;
                render();
            }
        });
    });
}

// Returns array of page numbers + '…' gaps e.g. [1, '…', 4, 5, 6, '…', 10]
function buildPageRange(current, total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages = new Set([1, total, current, current - 1, current + 1]
        .filter(p => p >= 1 && p <= total));
    const sorted = Array.from(pages).sort((a, b) => a - b);
    const result = [];
    for (let i = 0; i < sorted.length; i++) {
        if (i > 0 && sorted[i] - sorted[i - 1] > 1) result.push('…');
        result.push(sorted[i]);
    }
    return result;
}

// ===== INIT =====
render();