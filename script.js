let allClusterData = [];
let allPcaData = [];
let heatmapLabels = ["Current Price", "Constant Price", "Feat 0", "Feat 1", "Feat 2", "Feat 3", "Feat 4", "Feat 5", "Feat 6", "Feat 7"];
let pcaChart = null;
let heatmapChart = null;
let heatmapChart2 = null;
let currentSearch = "";
let currentSearch2 = "";
let compareMode = false;

async function loadResults() {
    try {
        const [resRes, pcaRes] = await Promise.all([
            fetch('results.json?' + new Date().getTime()),
            fetch('pca_data.json?' + new Date().getTime())
        ]);
        allClusterData = await resRes.json();
        allPcaData = await pcaRes.json();
        populateDatalist();
        updateUI();
    } catch (error) { console.warn('Waiting for data files...'); }
}

function populateDatalist() {
    const list = document.getElementById('industries');
    if (list.children.length > 0) return;
    const industries = [...new Set(allPcaData.map(d => d.industry))];
    industries.sort().forEach(ind => {
        const opt = document.createElement('option');
        opt.value = ind;
        list.appendChild(opt);
    });
}

function updateUI() {
    renderClusters(allClusterData, currentSearch);
    updatePCAChart();
    updateHeatmapChart(1);
    if (compareMode) updateHeatmapChart(2);
    updateConclusion();
}

function renderClusters(data, filter = "") {
    const grid = document.getElementById('cluster-grid');
    grid.innerHTML = '';
    const search = filter.toLowerCase();
    const filteredData = data.filter(cluster => {
        if (!filter) return true;
        return cluster.top_industry.toLowerCase().includes(search) || 
               Object.keys(cluster.industries).some(ind => ind.toLowerCase().includes(search));
    });

    filteredData.forEach((cluster) => {
        const card = document.createElement('div');
        card.className = 'cluster-card glass fade-in';
        const industries = Object.entries(cluster.industries).sort((a, b) => b[1] - a[1]).slice(0, 3)
            .map(([name, count]) => `<li>${name} (${count})</li>`).join('');
        card.innerHTML = `
            <div class="cluster-tag">Cluster ${cluster.id}</div>
            <h3>${cluster.top_industry}</h3>
            <p style="color: #6366f1; font-weight: 600; margin: 0.5rem 0;">${cluster.size} Documents</p>
            <ul style="font-size: 0.85rem; list-style: none; color: #d1d5db;">${industries}</ul>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);"><p style="font-size: 1.2rem; font-weight: 700;">₹ ${cluster.avg_price.toLocaleString()} Cr</p></div>
        `;
        grid.appendChild(card);
    });
    document.getElementById('total-records').textContent = allPcaData.length;
}

function updatePCAChart() {
    if (!allPcaData.length) return;
    const s1 = currentSearch.toLowerCase();
    const s2 = currentSearch2.toLowerCase();
    let datasets = [];
    const colors = ['#6366f1', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6'];

    if (compareMode && (s1 || s2)) {
        datasets.push({ label: s1 || 'Primary', data: allPcaData.filter(d => s1 && d.industry.toLowerCase().includes(s1)).map(d => ({x: d.x, y: d.y})), backgroundColor: '#6366f1', pointRadius: 6, zIndex: 10 });
        datasets.push({ label: s2 || 'Secondary', data: allPcaData.filter(d => s2 && d.industry.toLowerCase().includes(s2)).map(d => ({x: d.x, y: d.y})), backgroundColor: '#f43f5e', pointRadius: 6, zIndex: 10 });
        datasets.push({ label: 'Background', data: allPcaData.filter(d => (!s1 || !d.industry.toLowerCase().includes(s1)) && (!s2 || !d.industry.toLowerCase().includes(s2))).map(d => ({x: d.x, y: d.y})), backgroundColor: 'rgba(255,255,255,0.03)', pointRadius: 2, zIndex: 0 });
    } else {
        const filtered = allPcaData.filter(d => !currentSearch || d.industry.toLowerCase().includes(s1));
        const clusters = [...new Set(filtered.map(d => d.label))];
        clusters.forEach(c => {
            datasets.push({ label: `Cluster ${c}`, data: filtered.filter(d => d.label === c).map(d => ({x: d.x, y: d.y})), backgroundColor: colors[c % colors.length], pointRadius: 4 });
        });
    }

    if (pcaChart) { pcaChart.data.datasets = datasets; pcaChart.update(); }
    else {
        const ctx = document.getElementById('pcaChart').getContext('2d');
        pcaChart = new Chart(ctx, { type: 'scatter', data: { datasets }, options: { responsive: true, maintainAspectRatio: false, scales: { x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } }, y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } } } } });
    }
}

function pearson(x, y) {
    const n = x.length;
    if (n < 2) return 0;
    let sumX=0, sumY=0, sumXY=0, sumX2=0, sumY2=0;
    for (let i=0; i<n; i++) { sumX+=x[i]; sumY+=y[i]; sumXY+=x[i]*y[i]; sumX2+=x[i]*x[i]; sumY2+=y[i]*y[i]; }
    const num = n*sumXY - sumX*sumY;
    const den = Math.sqrt((n*sumX2 - sumX*sumX) * (n*sumY2 - sumY*sumY));
    return den === 0 ? 0 : num / den;
}

function calculateCorrelation(data) {
    if (!data.length || !data[0].features) return [];
    const numFeatures = 10;
    const correlations = [];
    for (let i=0; i<numFeatures; i++) {
        for (let j=0; j<numFeatures; j++) {
            const x = data.map(d => d.features[i]);
            const y = data.map(d => d.features[j]);
            correlations.push({ x: heatmapLabels[i], y: heatmapLabels[j], v: pearson(x, y) });
        }
    }
    return correlations;
}

function updateHeatmapChart(id) {
    const filter = (id === 1 ? currentSearch : currentSearch2).toLowerCase();
    const filtered = allPcaData.filter(d => !filter || d.industry.toLowerCase().includes(filter));
    const data = calculateCorrelation(filtered);
    const canvasId = id === 1 ? 'distChart' : 'distChart2';
    const labelId = id === 1 ? 'heatmap-label-1' : 'heatmap-label-2';
    let chart = id === 1 ? heatmapChart : heatmapChart2;

    document.getElementById(labelId).textContent = (filter || 'GLOBAL').toUpperCase();
    
    if (!data.length) return;

    if (chart) {
        chart.data.datasets[0].data = data;
        chart.update();
    } else {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const newChart = new Chart(ctx, {
            type: 'matrix',
            data: {
                datasets: [{
                    data: data,
                    backgroundColor(c) {
                        if (!c.dataset.data[c.dataIndex]) return 'rgba(0,0,0,0)';
                        const v = c.dataset.data[c.dataIndex].v;
                        return `rgba(${id===1?'99, 102, 241':'244, 63, 94'}, ${(v+1)/2})`;
                    },
                    width: ({chart}) => chart.chartArea ? chart.chartArea.width/10 - 1 : 20,
                    height: ({chart}) => chart.chartArea ? chart.chartArea.height/10 - 1 : 20
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { type: 'category', labels: heatmapLabels, ticks: { display: id===1, color: '#9ca3af', font: {size:7} } },
                    y: { type: 'category', labels: heatmapLabels, ticks: { display: true, color: '#9ca3af', font: {size:7} } }
                },
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (i) => `Corr: ${i.raw.v.toFixed(2)}` } } }
            }
        });
        if (id === 1) heatmapChart = newChart; else heatmapChart2 = newChart;
    }
}

function updateConclusion() {
    const conclusionSection = document.getElementById('conclusion');
    const conclusionText = document.getElementById('conclusion-text');
    if (!currentSearch && !currentSearch2) { conclusionSection.classList.add('hidden'); return; }
    conclusionSection.classList.remove('hidden');
    let message = "";
    if (compareMode && currentSearch && currentSearch2) {
        message = `Comparison analysis reveals that <span>${currentSearch}</span> and <span>${currentSearch2}</span> have distinct structural profiles. The dual heatmaps show how feature correlations differ across these segments, providing a nexus of economic insights for e-governance planning.`;
    } else if (currentSearch) {
        message = `Detailed analysis of <span>${currentSearch}</span> shows strong internal consistency within its identified clusters. The correlation matrix suggests specific feature dependencies that are characteristic of this industry's current economic footprint.`;
    }
    conclusionText.innerHTML = message;
}

window.addEventListener('DOMContentLoaded', () => {
    loadResults();
    const s1 = document.getElementById('industry-search');
    const s2 = document.getElementById('industry-search-2');
    const toggle = document.getElementById('compare-toggle');
    const box2 = document.getElementById('compare-search-box');
    const wrapper = document.getElementById('heatmap-wrapper');
    const cell2 = document.getElementById('heatmap-cell-2');

    const jumpToCharts = () => {
        const target = document.getElementById('visuals');
        if (target) window.scrollTo({ top: target.offsetTop - 50, behavior: 'smooth' });
    };

    s1.addEventListener('change', (e) => { currentSearch = e.target.value; updateUI(); jumpToCharts(); });
    s2.addEventListener('change', (e) => { currentSearch2 = e.target.value; updateUI(); jumpToCharts(); });
    
    toggle.addEventListener('click', () => {
        compareMode = !compareMode;
        toggle.classList.toggle('active');
        box2.classList.toggle('hidden');
        cell2.classList.toggle('hidden');
        wrapper.className = compareMode ? 'heatmap-comparison' : 'heatmap-wrapper-single';
        updateUI();
        jumpToCharts(); // Added jump on compare click
    });

    setInterval(loadResults, 5000);
});
