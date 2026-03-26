const fs = require('fs');
const path = require('path');

const targetFile = 'c:\\Users\\aniru\\.gemini\\antigravity\\scratch\\research-paper-analyzer\\frontend\\src\\app\\components\\chat\\chat.component.css';
let content = fs.readFileSync(targetFile, 'utf8');

const replacements = [
    [/#6C63FF/gi, "var(--accent)"],
    [/#E8E6F0/gi, "var(--text-primary)"],
    [/#D4D2E0/gi, "var(--text-primary)"],
    [/#B8B5CC/gi, "var(--text-secondary)"],
    [/#9B97B0/gi, "var(--text-secondary)"],
    [/#C8C6D8/gi, "var(--text-secondary)"],
    [/#6B6880/gi, "var(--text-muted)"],
    [/#4A4760/gi, "var(--text-dim)"],
    [/#4ADE80/gi, "var(--success)"],
    [/#FBBF24/gi, "var(--warning)"],
    [/#FF5252/gi, "var(--error)"],
    [/rgba\(\s*22\s*,\s*20\s*,\s*35\s*,\s*[0-9.]+\s*\)/gi, "var(--bg-card)"],
    [/rgba\(\s*12\s*,\s*10\s*,\s*22\s*,\s*[0-9.]+\s*\)/gi, "var(--bg-secondary)"]
];

for (const [regex, replacement] of replacements) {
    content = content.replace(regex, replacement);
}

content = content.replace(/rgba\(\s*108\s*,\s*99\s*,\s*255\s*,\s*([0-9.]+)\s*\)/gi, (match, p1) => {
    return `color-mix(in srgb, var(--accent) ${Math.round(parseFloat(p1) * 100)}%, transparent)`;
});
content = content.replace(/rgba\(\s*74\s*,\s*222\s*,\s*128\s*,\s*([0-9.]+)\s*\)/gi, (match, p1) => {
    return `color-mix(in srgb, var(--success) ${Math.round(parseFloat(p1) * 100)}%, transparent)`;
});
content = content.replace(/rgba\(\s*251\s*,\s*191\s*,\s*36\s*,\s*([0-9.]+)\s*\)/gi, (match, p1) => {
    return `color-mix(in srgb, var(--warning) ${Math.round(parseFloat(p1) * 100)}%, transparent)`;
});
content = content.replace(/rgba\(\s*255\s*,\s*82\s*,\s*82\s*,\s*([0-9.]+)\s*\)/gi, (match, p1) => {
    return `color-mix(in srgb, var(--error) ${Math.round(parseFloat(p1) * 100)}%, transparent)`;
});

fs.writeFileSync(targetFile, content, 'utf8');
console.log('Success');
