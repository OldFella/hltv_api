function highlightJSON(pre) {
    const text = pre.textContent;
    const highlighted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?)/g, match => {
            if (/:$/.test(match)) return `<span class="json-key">${match}</span>`;
            return `<span class="json-string">${match}</span>`;
        })
        .replace(/\b(true|false)\b/g, '<span class="json-bool">$1</span>')
        .replace(/\bnull\b/g, '<span class="json-null">null</span>')
        .replace(/\b(-?\d+\.?\d*)\b/g, '<span class="json-number">$1</span>');
    pre.innerHTML = highlighted;
}

document.querySelectorAll('pre').forEach(highlightJSON);