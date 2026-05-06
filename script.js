/**
 * script.js - Task Management System Landing Page
 * Handles mobile menu toggle and basic syntax highlighting for Python code blocks.
 */

document.addEventListener('DOMContentLoaded', () => {
 // Mobile Menu Toggle
 const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
 const navLinks = document.querySelector('.nav-links');

 if (mobileMenuBtn && navLinks) {
 mobileMenuBtn.addEventListener('click', () => {
 navLinks.classList.toggle('active');
 });

 // Close menu when a link is clicked
 navLinks.querySelectorAll('a').forEach(link => {
 link.addEventListener('click', () => {
 navLinks.classList.remove('active');
 });
 });
 }

 // Basic Python Syntax Highlighting
 highlightCodeBlocks();
});

/**
 * Very basic syntax highlighter for Python code blocks
 */
function highlightCodeBlocks() {
 const codeBlocks = document.querySelectorAll('pre code');
 
 const patterns = [
 // Comments
 { regex: /#.*/g, class: 'comment' },
 // Strings
 { regex: /"(?:[^"\\\\]|\\.)*"|'(?:[^'\\\\]|\\.)*'/g, class: 'string' },
 // Keywords
 { regex: /\b(def|class|from|import|return|if|else|elif|not|and|or|print|raise|while|for|in|try|except|finally|with|as|lambda|yield|True|False|None)\b/g, class: 'keyword' },
 // Numbers
 { regex: /\b\d+\b/g, class: 'number' },
 // Functions
 { regex: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\()/g, class: 'function' },
 // Operators
 { regex: /[-+*/%={<>!&|^~]/g, class: 'operator' }
 ];

 codeBlocks.forEach(block => {
 let html = block.textContent;
 
 // Escape HTML
 html = html.replace(/&/g, '&amp;')
 .replace(/</g, '&lt;')
 .replace(/>/g, '&gt;');

 // Apply highlighting
 const matches = [];
 patterns.forEach(p => {
 let match;
 while ((match = p.regex.exec(html)) !== null) {
 matches.push({
 start: match.index,
 end: match.index + match[0].length,
 text: match[0],
 className: p.class
 });
 }
 });

 // Sort matches by start position, then length (descending)
 matches.sort((a, b) => a.start - b.start || b.end - a.end);

 // Filter out overlapping matches (keep the first/longest)
 const cleanMatches = [];
 let lastEnd = 0;
 matches.forEach(m => {
 if (m.start >= lastEnd) {
 cleanMatches.push(m);
 lastEnd = m.end;
 }
 });

 // Build the HTML
 let result = '';
 let currentIndex = 0;
 cleanMatches.forEach(m => {
 result += html.substring(currentIndex, m.start);
 result += `<span class="token ${m.className}">${m.text}</span>`;
 currentIndex = m.end;
 });
 result += html.substring(currentIndex);

 block.innerHTML = result;
 });
}
