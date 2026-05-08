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

 // Dashboard Initialization
 if (document.getElementById('dashboard')) {
     initDashboard();
 }
});

/**
 * Dashboard Logic
 */
let cy;
const statusColors = {
    'COMPLETED': '#10b981', // Green
    'RUNNING': '#2563eb',   // Vibrant Blue
    'RETRYING': '#f59e0b',  // Vivid Amber
    'FAILED': '#ef4444',    // Curated Red
    'PENDING': '#94a3b8',   // Muted Gray
    'CANCELLED': '#64748b'  // Muted Gray
};

async function initDashboard() {
    checkAuth();
    initGraph();
    setupEventListeners();
    await refreshData();
    startLogSimulation();
}

/**
 * Auth Logic (F-0009)
 */
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        document.getElementById('login-overlay').classList.add('hidden');
        document.getElementById('logout-item').classList.remove('hidden');
        document.getElementById('project-selector-container').classList.remove('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const errorEl = document.getElementById('login-error');
    
    // Demo auth logic
    if (username === 'admin') {
        localStorage.setItem('token', 'demo-jwt-token');
        localStorage.setItem('username', username);
        document.getElementById('login-overlay').classList.add('hidden');
        document.getElementById('logout-item').classList.remove('hidden');
        document.getElementById('project-selector-container').classList.remove('hidden');
        addLogEntry('SYSTEM', 'INFO', `User ${username} logged in`);
    } else {
        errorEl.textContent = 'Invalid credentials. Try "admin".';
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    location.reload();
}

function initGraph() {
    cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': 'data(color)',
                    'label': 'data(id)',
                    'color': '#1e293b',
                    'font-family': 'Inter, sans-serif',
                    'font-weight': 'bold',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '60px',
                    'height': '60px',
                    'border-width': 2,
                    'border-color': '#fff'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#cbd5e1',
                    'target-arrow-color': '#cbd5e1',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            },
            {
                selector: ':selected',
                style: {
                    'border-width': 4,
                    'border-color': '#2563eb'
                }
            }
        ],
        layout: { name: 'dagre' }
    });

    cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        showNodeInfo(node.data());
    });

    cy.on('tap', (evt) => {
        if (evt.target === cy) {
            hideNodeInfo();
        }
    });
}

function setupEventListeners() {
    // Auth
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    const taskForm = document.getElementById('task-form');
    taskForm.addEventListener('submit', handleFormSubmit);

    // Schedule Type toggle (F-0008)
    document.getElementById('schedule-type').addEventListener('change', (e) => {
        const container = document.getElementById('schedule-value-container');
        if (e.target.value === 'manual') {
            container.classList.add('hidden');
        } else {
            container.classList.remove('hidden');
        }
    });

    // AI Workflow Generator (F-0007)
    document.getElementById('btn-generate-ai').addEventListener('click', handleAIGeneration);
    document.getElementById('btn-ai-apply').addEventListener('click', applyAIGeneratedDAG);
    document.getElementById('btn-ai-cancel').addEventListener('click', discardAIGeneratedDAG);

    document.getElementById('refresh-graph').addEventListener('click', refreshData);
    document.getElementById('run-all').addEventListener('click', runAllTasks);
    
    document.getElementById('btn-cancel').addEventListener('click', () => handleTaskAction('cancel'));
    document.getElementById('btn-retry').addEventListener('click', () => handleTaskAction('retry'));

    // Filters
    document.getElementById('log-filter-task').addEventListener('input', applyLogFilters);
    document.getElementById('log-filter-level').addEventListener('change', applyLogFilters);
}

async function refreshData() {
    try {
        const response = await fetch('/api/tasks');
        if (!response.ok) throw new Error('API not available');
        const tasks = await response.json();
        updateGraph(tasks);
        updateDependenciesList(tasks);
        updateUpcomingRuns(tasks);
    } catch (err) {
        console.warn('Backend API not found, using demo data');
        const demoTasks = [
            { id: 'Extract', name: 'Extract Data', priority: 1, status: 'COMPLETED', result: 'Fetched 100 rows' },
            { id: 'Transform', name: 'Transform Data', priority: 5, status: 'RUNNING', result: null },
            { id: 'Load', name: 'Load Database', priority: 3, status: 'PENDING', result: null, schedule_type: 'cron', schedule_value: '0 0 * * *' },
            { id: 'Notify', name: 'Send Notification', priority: 2, status: 'PENDING', result: null }
        ];
        const demoEdges = [
            { source: 'Extract', target: 'Transform' },
            { source: 'Transform', target: 'Load' },
            { source: 'Load', target: 'Notify' }
        ];
        const tasksWithDeps = demoTasks.map(t => ({ ...t, dependencies: demoEdges.filter(e => e.target === t.id).map(e => e.source) }));
        updateGraph(tasksWithDeps);
        updateDependenciesList(demoTasks);
        updateUpcomingRuns(tasksWithDeps);
    }
}

/**
 * AI Workflow Logic (F-0007)
 */
let aiGeneratedTasks = null;

async function handleAIGeneration() {
    const prompt = document.getElementById('ai-prompt').value;
    if (!prompt) return;

    const btn = document.getElementById('btn-generate-ai');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        // Mock AI response
        await new Promise(r => setTimeout(r, 1500));
        aiGeneratedTasks = [
            { id: 'S3_Fetch', name: 'Fetch from S3', status: 'PENDING', dependencies: [] },
            { id: 'Spark_Job', name: 'Run Spark Transformation', status: 'PENDING', dependencies: ['S3_Fetch'] },
            { id: 'BQ_Load', name: 'Load BigQuery', status: 'PENDING', dependencies: ['Spark_Job'] },
            { id: 'Slack_Alert', name: 'Slack Notification', status: 'PENDING', dependencies: ['BQ_Load'] }
        ];

        updateGraph(aiGeneratedTasks);
        document.getElementById('ai-preview-controls').classList.remove('hidden');
        addLogEntry('AI', 'INFO', `Generated workflow suggestion based on: "${prompt.substring(0, 30)}..."`);
    } catch (err) {
        console.error('AI Generation failed:', err);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Draft';
    }
}

async function applyAIGeneratedDAG() {
    if (!aiGeneratedTasks) return;
    addLogEntry('SYSTEM', 'INFO', 'Applying AI-generated workflow');
    // In a real system, we would POST each task to the backend
    await refreshData();
    discardAIGeneratedDAG();
}

function discardAIGeneratedDAG() {
    aiGeneratedTasks = null;
    document.getElementById('ai-preview-controls').classList.add('hidden');
    document.getElementById('ai-prompt').value = '';
    refreshData();
}

/**
 * Advanced Scheduling Logic (F-0008)
 */
function updateUpcomingRuns(tasks) {
    const list = document.getElementById('upcoming-runs-list');
    const scheduledTasks = tasks.filter(t => t.schedule_type && t.schedule_type !== 'manual');
    
    if (scheduledTasks.length === 0) {
        list.innerHTML = '<p class="text-muted italic">No active schedules</p>';
        return;
    }

    list.innerHTML = '';
    scheduledTasks.forEach(task => {
        const item = document.createElement('div');
        item.className = 'upcoming-item';
        item.innerHTML = `
            <span class="task-id">${task.id}</span>
            <span class="next-run">Next: In 5 mins (${task.schedule_value})</span>
        `;
        list.appendChild(item);
    });
}

function updateGraph(tasks) {
    const elements = [];
    tasks.forEach(task => {
        elements.push({
            data: { 
                id: task.id, 
                name: task.name, 
                status: task.status, 
                result: task.result,
                color: statusColors[task.status] || '#94a3b8'
            }
        });
        if (task.dependencies) {
            task.dependencies.forEach(dep => {
                elements.push({ data: { source: dep, target: task.id } });
            });
        }
    });

    cy.elements().remove();
    cy.add(elements);
    cy.layout({ name: 'dagre', rankDir: 'LR' }).run();
}

function updateDependenciesList(tasks) {
    const select = document.getElementById('dependencies');
    const currentValue = Array.from(select.selectedOptions).map(o => o.value);
    select.innerHTML = '';
    tasks.forEach(task => {
        const option = document.createElement('option');
        option.value = task.id;
        option.textContent = task.name || task.id;
        if (currentValue.includes(task.id)) option.selected = true;
        select.appendChild(option);
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        priority: parseInt(formData.get('priority')),
        max_retries: parseInt(formData.get('max_retries')),
        base_delay: parseFloat(formData.get('base_delay')),
        dependencies: Array.from(document.getElementById('dependencies').selectedOptions).map(o => o.value)
    };

    const messageEl = document.getElementById('form-message');
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            messageEl.textContent = 'Task scheduled successfully!';
            messageEl.className = 'form-message success';
            e.target.reset();
            refreshData();
        } else {
            const errData = await response.json();
            throw new Error(errData.detail || 'Validation failed');
        }
    } catch (err) {
        messageEl.textContent = `Error: ${err.message}`;
        messageEl.className = 'form-message error';
    }
}

let selectedNodeData = null;

function showNodeInfo(data) {
    selectedNodeData = data;
    document.getElementById('info-name').textContent = `Task: ${data.name || data.id}`;
    document.getElementById('info-status').textContent = data.status;
    document.getElementById('info-status').style.color = statusColors[data.status];
    
    const resultEl = document.getElementById('info-result');
    if (data.result) {
        resultEl.textContent = typeof data.result === 'object' ? JSON.stringify(data.result) : data.result;
        document.getElementById('info-result-container').classList.remove('hidden');
    } else {
        document.getElementById('info-result-container').classList.add('hidden');
    }

    document.getElementById('node-info').classList.remove('hidden');
}

function hideNodeInfo() {
    selectedNodeData = null;
    document.getElementById('node-info').classList.add('hidden');
}

async function handleTaskAction(action) {
    if (!selectedNodeData) return;
    try {
        const response = await fetch(`/api/tasks/${selectedNodeData.id}/${action}`, { method: 'POST' });
        if (response.ok) {
            addLogEntry(`SYSTEM`, `INFO`, `Task ${selectedNodeData.id} ${action}ed manually`);
            refreshData();
        }
    } catch (err) {
        console.error(`Failed to ${action} task:`, err);
    }
}

async function runAllTasks() {
    try {
        const response = await fetch('/api/execute', { method: 'POST' });
        if (response.ok) {
            addLogEntry(`SYSTEM`, `INFO`, `Execution triggered`);
            refreshData();
        }
    } catch (err) {
        console.error('Failed to trigger execution:', err);
    }
}

/**
 * Log Viewer Logic
 */
function addLogEntry(taskId, level, message) {
    const container = document.getElementById('log-viewer');
    const entry = document.createElement('div');
    const now = new Date().toLocaleTimeString();
    
    entry.className = `log-entry ${level}`;
    entry.innerHTML = `
        <span class="timestamp">[${now}]</span>
        <span class="level">${level}</span>
        <span class="task-id">${taskId}</span>
        <span class="message">${message}</span>
    `;
    
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
    
    // Limit log entries
    while (container.childNodes.length > 200) {
        container.removeChild(container.firstChild);
    }
}

function applyLogFilters() {
    const taskFilter = document.getElementById('log-filter-task').value.toLowerCase();
    const levelFilter = document.getElementById('log-filter-level').value;
    
    const entries = document.querySelectorAll('.log-entry');
    entries.forEach(entry => {
        const taskId = entry.querySelector('.task-id').textContent.toLowerCase();
        const level = entry.querySelector('.level').textContent;
        
        const matchesTask = !taskFilter || taskId.includes(taskFilter);
        const matchesLevel = !levelFilter || level === levelFilter;
        
        entry.style.display = (matchesTask && matchesLevel) ? 'block' : 'none';
    });
}

function startLogSimulation() {
    const messages = [
        { taskId: 'Extract', level: 'INFO', msg: 'Connected to source API' },
        { taskId: 'Extract', level: 'INFO', msg: 'Downloaded 50MB of raw data' },
        { taskId: 'Transform', level: 'WARNING', msg: 'Missing field "email", using default' },
        { taskId: 'Transform', level: 'INFO', msg: 'Normalized timestamps' },
        { taskId: 'Load', level: 'ERROR', msg: 'Connection timeout (retry 1/3)' },
        { taskId: 'System', level: 'INFO', msg: 'Checkpointing state to SQLite' }
    ];

    setInterval(() => {
        const m = messages[Math.floor(Math.random() * messages.length)];
        addLogEntry(m.taskId, m.level, m.msg);
    }, 5000);
}

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
