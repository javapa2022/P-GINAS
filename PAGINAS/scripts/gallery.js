// ==================== GALLERY DATA ====================
const galleryData = [
    { id: 1, title: 'Bosque Místico', category: 'nature', icon: '🌲' },
    { id: 2, title: 'Código Futurista', category: 'tech', icon: '💻' },
    { id: 3, title: 'Geometría Espacial', category: 'abstract', icon: '🔷' },
    { id: 4, title: 'Ciudad Nocturna', category: 'urban', icon: '🌃' },
    { id: 5, title: 'Montañas Nevadas', category: 'nature', icon: '⛰️' },
    { id: 6, title: 'Circuitos Digitales', category: 'tech', icon: '⚡' },
    { id: 7, title: 'Ondas de Color', category: 'abstract', icon: '🌊' },
    { id: 8, title: 'Rascacielos', category: 'urban', icon: '🏢' },
    { id: 9, title: 'Jardín Zen', category: 'nature', icon: '🎋' },
    { id: 10, title: 'Inteligencia Artificial', category: 'tech', icon: '🤖' },
    { id: 11, title: 'Nebulosa Abstracta', category: 'abstract', icon: '🌌' },
    { id: 12, title: 'Puente Urbano', category: 'urban', icon: '🌉' },
    { id: 13, title: 'Cascada Natural', category: 'nature', icon: '💧' },
    { id: 14, title: 'Realidad Virtual', category: 'tech', icon: '🥽' },
    { id: 15, title: 'Espiral Infinita', category: 'abstract', icon: '🌀' },
    { id: 16, title: 'Metrópolis', category: 'urban', icon: '🏙️' },
    { id: 17, title: 'Aurora Boreal', category: 'nature', icon: '🌈' },
    { id: 18, title: 'Blockchain', category: 'tech', icon: '🔗' },
    { id: 19, title: 'Fractales', category: 'abstract', icon: '✨' },
    { id: 20, title: 'Calle Urbana', category: 'urban', icon: '🚦' },
];

// ==================== INITIALIZE GALLERY ====================
const galleryGrid = document.getElementById('galleryGrid');
const filterButtons = document.querySelectorAll('.filter-btn');
const searchInput = document.getElementById('searchInput');
const noResults = document.getElementById('noResults');
const lightbox = document.getElementById('lightbox');
const lightboxImage = document.getElementById('lightboxImage');
const lightboxTitle = document.getElementById('lightboxTitle');
const lightboxCategory = document.getElementById('lightboxCategory');
const lightboxCounter = document.getElementById('lightboxCounter');
const lightboxClose = document.getElementById('lightboxClose');
const lightboxPrev = document.getElementById('lightboxPrev');
const lightboxNext = document.getElementById('lightboxNext');

let currentFilter = 'all';
let currentSearch = '';
let currentLightboxIndex = 0;
let filteredItems = [...galleryData];

// ==================== RENDER GALLERY ====================
function renderGallery() {
    galleryGrid.innerHTML = '';

    filteredItems = galleryData.filter(item => {
        const matchesFilter = currentFilter === 'all' || item.category === currentFilter;
        const matchesSearch = item.title.toLowerCase().includes(currentSearch.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    if (filteredItems.length === 0) {
        noResults.style.display = 'block';
        galleryGrid.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        galleryGrid.style.display = 'grid';

        filteredItems.forEach((item, index) => {
            const galleryItem = createGalleryItem(item, index);
            galleryGrid.appendChild(galleryItem);
        });
    }

    updateStats();
}

function createGalleryItem(item, index) {
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.dataset.index = index;

    const gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    ];

    const gradient = gradients[item.id % gradients.length];

    div.innerHTML = `
        <div class="gallery-image" style="background: ${gradient}">
            <span>${item.icon}</span>
        </div>
        <div class="gallery-overlay">
            <h3 class="gallery-title">${item.title}</h3>
            <span class="gallery-category">${getCategoryName(item.category)}</span>
        </div>
        <div class="gallery-zoom">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8" stroke-width="2"/>
                <path d="M21 21l-4.35-4.35" stroke-width="2" stroke-linecap="round"/>
                <path d="M11 8v6M8 11h6" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
    `;

    div.addEventListener('click', () => openLightbox(index));

    return div;
}

function getCategoryName(category) {
    const categories = {
        nature: 'Naturaleza',
        tech: 'Tecnología',
        abstract: 'Abstracto',
        urban: 'Urbano'
    };
    return categories[category] || category;
}

// ==================== FILTER FUNCTIONALITY ====================
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        currentFilter = button.dataset.filter;
        animateFilterChange();
    });
});

function animateFilterChange() {
    const items = document.querySelectorAll('.gallery-item');
    items.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('hide');
        }, index * 30);
    });

    setTimeout(() => {
        renderGallery();
    }, items.length * 30 + 300);
}

// ==================== SEARCH FUNCTIONALITY ====================
searchInput.addEventListener('input', (e) => {
    currentSearch = e.target.value;

    // Debounce search
    clearTimeout(searchInput.debounceTimer);
    searchInput.debounceTimer = setTimeout(() => {
        renderGallery();
    }, 300);
});

// ==================== LIGHTBOX FUNCTIONALITY ====================
function openLightbox(index) {
    currentLightboxIndex = index;
    updateLightbox();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

function updateLightbox() {
    const item = filteredItems[currentLightboxIndex];

    const gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    ];

    const gradient = gradients[item.id % gradients.length];

    lightboxImage.style.background = gradient;
    lightboxImage.innerHTML = `<span>${item.icon}</span>`;
    lightboxTitle.textContent = item.title;
    lightboxCategory.textContent = getCategoryName(item.category);
    lightboxCounter.textContent = `${currentLightboxIndex + 1} / ${filteredItems.length}`;
}

function nextImage() {
    currentLightboxIndex = (currentLightboxIndex + 1) % filteredItems.length;
    updateLightbox();
}

function prevImage() {
    currentLightboxIndex = (currentLightboxIndex - 1 + filteredItems.length) % filteredItems.length;
    updateLightbox();
}

// Lightbox event listeners
lightboxClose.addEventListener('click', closeLightbox);
lightboxNext.addEventListener('click', nextImage);
lightboxPrev.addEventListener('click', prevImage);

document.querySelector('.lightbox-overlay').addEventListener('click', closeLightbox);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;

    switch (e.key) {
        case 'Escape':
            closeLightbox();
            break;
        case 'ArrowRight':
            nextImage();
            break;
        case 'ArrowLeft':
            prevImage();
            break;
    }
});

// ==================== STATS UPDATE ====================
function updateStats() {
    const totalItems = document.getElementById('totalItems');
    const visibleItems = document.getElementById('visibleItems');

    animateNumber(totalItems, galleryData.length);
    animateNumber(visibleItems, filteredItems.length);
}

function animateNumber(element, target) {
    const duration = 1000;
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// ==================== INTERSECTION OBSERVER ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '50px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// ==================== SCROLL ANIMATIONS ====================
function setupScrollAnimations() {
    const items = document.querySelectorAll('.gallery-item');
    items.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = `all 0.5s ease ${index * 0.05}s`;
        observer.observe(item);
    });
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    renderGallery();

    // Add scroll animation after initial render
    setTimeout(() => {
        setupScrollAnimations();
    }, 100);
});

// ==================== PERFORMANCE OPTIMIZATION ====================
// Lazy load gallery items as user scrolls
let lazyLoadTimeout;
window.addEventListener('scroll', () => {
    clearTimeout(lazyLoadTimeout);
    lazyLoadTimeout = setTimeout(() => {
        const items = document.querySelectorAll('.gallery-item');
        items.forEach(item => {
            const rect = item.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                item.style.willChange = 'transform';
            } else {
                item.style.willChange = 'auto';
            }
        });
    }, 100);
});

// ==================== TOUCH SUPPORT ====================
let touchStartX = 0;
let touchEndX = 0;

lightbox.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

lightbox.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            nextImage();
        } else {
            prevImage();
        }
    }
}

// ==================== CONSOLE MESSAGE ====================
console.log('%c🎨 Galería Interactiva', 'color: #6366f1; font-size: 20px; font-weight: bold;');
console.log('%cCaracterísticas:', 'color: #ec4899; font-size: 14px; font-weight: bold;');
console.log('✓ Filtrado dinámico por categorías');
console.log('✓ Búsqueda en tiempo real');
console.log('✓ Lightbox con navegación por teclado');
console.log('✓ Animaciones suaves y transiciones');
console.log('✓ Diseño responsive y touch-friendly');
console.log('✓ Intersection Observer para lazy loading');
