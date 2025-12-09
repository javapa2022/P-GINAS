// ==================== ANIMATED COUNTERS ====================
function animateCounter(element) {
    const target = parseInt(element.dataset.target);
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const prefix = element.textContent.includes('$') ? '$' : '';
    const suffix = element.textContent.includes('%') ? '%' : '';

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = prefix + target.toLocaleString() + suffix;
            clearInterval(timer);
        } else {
            element.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
        }
    }, 16);
}

// ==================== SALES CHART ====================
function createSalesChart() {
    const canvas = document.getElementById('salesChart');
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 300 * 2;
    ctx.scale(2, 2);

    const data = [42, 58, 45, 72, 68, 85];
    const labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
    const max = Math.max(...data);
    const padding = 40;
    const chartWidth = canvas.width / 2 - padding * 2;
    const chartHeight = canvas.height / 2 - padding * 2;

    // Draw grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width / 2 - padding, y);
        ctx.stroke();
    }

    // Draw bars
    const barWidth = chartWidth / data.length - 10;
    data.forEach((value, index) => {
        const x = padding + (chartWidth / data.length) * index + 5;
        const barHeight = (value / max) * chartHeight;
        const y = padding + chartHeight - barHeight;

        // Gradient
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#6366f1');
        gradient.addColorStop(1, '#ec4899');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);

        // Label
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(labels[index], x + barWidth / 2, canvas.height / 2 - 10);

        // Value
        ctx.fillStyle = '#f1f5f9';
        ctx.fillText(value + 'K', x + barWidth / 2, y - 5);
    });
}

// ==================== CATEGORY CHART (PIE) ====================
function createCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 300 * 2;
    ctx.scale(2, 2);

    const data = [
        { label: 'Electrónica', value: 35, color: '#6366f1' },
        { label: 'Ropa', value: 25, color: '#ec4899' },
        { label: 'Hogar', value: 20, color: '#14b8a6' },
        { label: 'Deportes', value: 12, color: '#f59e0b' },
        { label: 'Otros', value: 8, color: '#8b5cf6' }
    ];

    const total = data.reduce((sum, item) => sum + item.value, 0);
    const centerX = canvas.width / 4;
    const centerY = canvas.height / 4;
    const radius = 80;

    let currentAngle = -Math.PI / 2;

    data.forEach(item => {
        const sliceAngle = (item.value / total) * 2 * Math.PI;

        // Draw slice
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();

        // Draw label
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius + 30);
        const labelY = centerY + Math.sin(labelAngle) * (radius + 30);

        ctx.fillStyle = '#f1f5f9';
        ctx.font = '11px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, labelX, labelY);
        ctx.fillText(item.value + '%', labelX, labelY + 15);

        currentAngle += sliceAngle;
    });
}

// ==================== TRAFFIC CHART (LINE) ====================
let trafficData = Array(20).fill(0).map(() => Math.random() * 100);

function createTrafficChart() {
    const canvas = document.getElementById('trafficChart');
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 200 * 2;
    ctx.scale(2, 2);

    const padding = 40;
    const chartWidth = canvas.width / 2 - padding * 2;
    const chartHeight = canvas.height / 2 - padding * 2;
    const max = Math.max(...trafficData);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height / 2);

    // Draw grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding + (chartHeight / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width / 2 - padding, y);
        ctx.stroke();
    }

    // Draw line
    ctx.beginPath();
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';

    trafficData.forEach((value, index) => {
        const x = padding + (chartWidth / (trafficData.length - 1)) * index;
        const y = padding + chartHeight - (value / max) * chartHeight;

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    ctx.stroke();

    // Draw area
    ctx.lineTo(canvas.width / 2 - padding, padding + chartHeight);
    ctx.lineTo(padding, padding + chartHeight);
    ctx.closePath();

    const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
    ctx.fillStyle = gradient;
    ctx.fill();
}

function updateTrafficChart() {
    trafficData.shift();
    trafficData.push(Math.random() * 100);
    createTrafficChart();
}

// ==================== DATA TABLE ====================
const tableData = [
    { product: 'Laptop Pro 15"', category: 'Electrónica', sales: 1245, revenue: 1245000, trend: 'up' },
    { product: 'Auriculares Bluetooth', category: 'Electrónica', sales: 2341, revenue: 234100, trend: 'up' },
    { product: 'Camiseta Deportiva', category: 'Ropa', sales: 3421, revenue: 102630, trend: 'down' },
    { product: 'Zapatillas Running', category: 'Deportes', sales: 1876, revenue: 281400, trend: 'up' },
    { product: 'Cafetera Automática', category: 'Hogar', sales: 987, revenue: 148050, trend: 'up' },
    { product: 'Mochila Urbana', category: 'Accesorios', sales: 1543, revenue: 77150, trend: 'down' },
    { product: 'Smartwatch', category: 'Electrónica', sales: 2109, revenue: 632700, trend: 'up' },
    { product: 'Pantalón Jeans', category: 'Ropa', sales: 1654, revenue: 82700, trend: 'up' }
];

function renderTable(data = tableData) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = data.map(item => `
        <tr>
            <td><strong>${item.product}</strong></td>
            <td>${item.category}</td>
            <td>${item.sales.toLocaleString()}</td>
            <td>$${item.revenue.toLocaleString()}</td>
            <td class="trend-${item.trend}">
                ${item.trend === 'up' ? '↗' : '↘'} ${item.trend === 'up' ? '+' : '-'}${Math.floor(Math.random() * 15 + 5)}%
            </td>
        </tr>
    `).join('');
}

// Search functionality
document.getElementById('tableSearch').addEventListener('input', (e) => {
    const search = e.target.value.toLowerCase();
    const filtered = tableData.filter(item =>
        item.product.toLowerCase().includes(search) ||
        item.category.toLowerCase().includes(search)
    );
    renderTable(filtered);
});

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    // Animate counters
    document.querySelectorAll('.stat-value').forEach(element => {
        animateCounter(element);
    });

    // Create charts
    setTimeout(() => {
        createSalesChart();
        createCategoryChart();
        createTrafficChart();
    }, 500);

    // Update traffic chart every 2 seconds
    setInterval(updateTrafficChart, 2000);

    // Render table
    renderTable();

    // Add entrance animations
    const cards = document.querySelectorAll('.stat-card, .chart-card, .table-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// ==================== RESPONSIVE CHARTS ====================
window.addEventListener('resize', () => {
    createSalesChart();
    createCategoryChart();
    createTrafficChart();
});

// ==================== CONSOLE MESSAGE ====================
console.log('%c📊 Dashboard de Datos', 'color: #6366f1; font-size: 20px; font-weight: bold;');
console.log('%cCaracterísticas:', 'color: #ec4899; font-size: 14px; font-weight: bold;');
console.log('✓ Gráficos dibujados con Canvas API');
console.log('✓ Animaciones de contadores');
console.log('✓ Actualización en tiempo real');
console.log('✓ Tabla de datos con búsqueda');
console.log('✓ Diseño responsive y adaptable');
