let products = [];
let filteredProducts = [];
let sortField = null;
let sortAsc = true;
let currentSessionId = null;

const API_URL = '/api/products/';

// Генерируем уникальный ID сессии при загрузке страницы
function generateSessionId() {
    if (!currentSessionId) {
        currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        // Сохраняем в localStorage для сохранения сессии при перезагрузке
        localStorage.setItem('wb_parser_session_id', currentSessionId);
    }
    return currentSessionId;
}

// Восстанавливаем сессию из localStorage
function restoreSession() {
    const savedSessionId = localStorage.getItem('wb_parser_session_id');
    if (savedSessionId) {
        currentSessionId = savedSessionId;
    }
}

async function fetchProducts(filters = {}) {
    const params = new URLSearchParams();
    if (currentSessionId) {
        params.append('session_id', currentSessionId);
    }
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.min_rating) params.append('min_rating', filters.min_rating);
    if (filters.min_reviews_count) params.append('min_reviews_count', filters.min_reviews_count);
    
    const url = params.toString() ? `${API_URL}?${params}` : API_URL;
    const res = await fetch(url);
    const data = await res.json();
    products = data;
    filteredProducts = [...products];
    renderTable();
    renderCharts();
    updatePriceSlider();
    updateSessionInfo();
}

// Функция для парсинга конкретного товара
async function parseProduct(url) {
    const sessionId = generateSessionId();
    try {
        const response = await fetch(`${API_URL}parse_product/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: url,
                session_id: sessionId
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult('productResult', result.message, 'success');
            // Обновляем список товаров
            await fetchProducts();
        } else {
            showResult('productResult', result.error, 'error');
        }
    } catch (error) {
        showResult('productResult', 'Ошибка при парсинге товара: ' + error.message, 'error');
    }
}

// Функция для парсинга по поисковому запросу
async function parseSearch(query) {
    const sessionId = generateSessionId();
    try {
        const response = await fetch(`${API_URL}parse_search/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: query,
                session_id: sessionId
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult('searchResult', result.message, 'success');
            // Обновляем список товаров
            await fetchProducts();
        } else {
            showResult('searchResult', result.error, 'error');
        }
    } catch (error) {
        showResult('searchResult', 'Ошибка при поиске товаров: ' + error.message, 'error');
    }
}

// Функция для очистки текущей сессии
async function clearSession() {
    if (!currentSessionId) {
        showResult('sessionResult', 'Нет активной сессии для очистки', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}clear_session/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: currentSessionId })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult('sessionResult', result.message, 'success');
            // Очищаем текущую сессию
            currentSessionId = null;
            localStorage.removeItem('wb_parser_session_id');
            // Обновляем список товаров
            await fetchProducts();
        } else {
            showResult('sessionResult', result.error, 'error');
        }
    } catch (error) {
        showResult('sessionResult', 'Ошибка при очистке сессии: ' + error.message, 'error');
    }
}

// Функция для создания новой сессии
function createNewSession() {
    currentSessionId = null;
    localStorage.removeItem('wb_parser_session_id');
    generateSessionId();
    showResult('sessionResult', 'Создана новая сессия', 'success');
    fetchProducts();
}

// Функция для отображения информации о сессии
function updateSessionInfo() {
    const sessionInfo = document.getElementById('sessionInfo');
    if (sessionInfo) {
        sessionInfo.textContent = `Текущая сессия: ${currentSessionId ? currentSessionId.substring(0, 20) + '...' : 'Нет'}`;
        sessionInfo.title = currentSessionId || 'Нет активной сессии';
    }
    
    // Обновляем счетчик товаров
    const productCount = document.getElementById('productCount');
    if (productCount) {
        const count = filteredProducts.length;
        productCount.textContent = `(${count} товаров)`;
    }
}

// Функция для отображения результатов
function showResult(elementId, message, type) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = `result ${type}`;
        
        // Скрываем сообщение через 5 секунд
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

function renderTable() {
    const tbody = document.querySelector('#productsTable tbody');
    tbody.innerHTML = '';
    
    if (filteredProducts.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="7" style="text-align: center; color: #666;">Нет товаров в текущей сессии</td>';
        tbody.appendChild(tr);
        return;
    }
    
    filteredProducts.forEach(prod => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prod.name}</td>
            <td>${prod.image_url ? `<img src="${prod.image_url}" alt="Фото" style="max-width:60px;max-height:60px;">` : ''}</td>
            <td>${prod.price}</td>
            <td>${prod.discounted_price}</td>
            <td>${prod.rating}</td>
            <td>${prod.reviews_count}</td>
            <td>${prod.wb_url ? `<a href="${prod.wb_url}" target="_blank">Открыть</a>` : ''}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateSliderTooltip(sliderId, tooltipId, captionId, captionPrefix) {
    const slider = document.getElementById(sliderId);
    const tooltip = document.getElementById(tooltipId);
    const caption = document.getElementById(captionId);
    const min = +slider.min;
    const max = +slider.max;
    const val = +slider.value;
    tooltip.textContent = val;
    // Позиция бегунка в процентах
    const percent = (val - min) / (max - min);
    tooltip.style.left = `calc(${percent * 100}% )`;
    if (caption) {
        caption.textContent = `${captionPrefix}: ${val}`;
    }
}

function applyFilters() {
    const minPrice = +document.getElementById('minPriceRange').value;
    const maxPrice = +document.getElementById('maxPriceRange').value;
    const minRating = +document.getElementById('minRating').value;
    const minReviews = +document.getElementById('minReviews').value;
    const realMin = Math.min(minPrice, maxPrice);
    const realMax = Math.max(minPrice, maxPrice);
    // Обновляем tooltips и подписи
    updateSliderTooltip('minPriceRange', 'minPriceTooltip', 'minPriceCaption', 'Мин. цена');
    updateSliderTooltip('maxPriceRange', 'maxPriceTooltip', 'maxPriceCaption', 'Макс. цена');
    filteredProducts = products.filter(p =>
        p.discounted_price >= realMin &&
        p.discounted_price <= realMax &&
        p.rating >= minRating &&
        p.reviews_count >= minReviews
    );
    if (sortField) sortTable(sortField, sortAsc, false);
    renderTable();
    renderCharts();
}

function updatePriceSlider() {
    const priceSliderBlock = document.getElementById('priceSliderBlock');
    if (products.length === 0) {
        priceSliderBlock.style.display = 'none';
        return;
    }
    priceSliderBlock.style.display = '';
    const prices = products.map(p => p.discounted_price);
    const min = Math.min(...prices, 0);
    const max = Math.max(...prices, 10000);
    const minSlider = document.getElementById('minPriceRange');
    const maxSlider = document.getElementById('maxPriceRange');
    minSlider.min = min;
    minSlider.max = max;
    maxSlider.min = min;
    maxSlider.max = max;
    if (+minSlider.value < min) minSlider.value = min;
    if (+maxSlider.value > max) maxSlider.value = max;
    updateSliderTooltip('minPriceRange', 'minPriceTooltip', 'minPriceCaption', 'Мин. цена');
    updateSliderTooltip('maxPriceRange', 'maxPriceTooltip', 'maxPriceCaption', 'Макс. цена');
}

// Обработчики событий для парсинга
document.getElementById('parseProduct').addEventListener('click', () => {
    const url = document.getElementById('productUrl').value.trim();
    if (url) {
        parseProduct(url);
    } else {
        showResult('productResult', 'Введите URL товара', 'error');
    }
});

document.getElementById('parseSearch').addEventListener('click', () => {
    const query = document.getElementById('searchQuery').value.trim();
    if (query) {
        parseSearch(query);
    } else {
        showResult('searchResult', 'Введите поисковый запрос', 'error');
    }
});

// Обработчики событий для управления сессиями
document.getElementById('clearSession').addEventListener('click', clearSession);
document.getElementById('newSession').addEventListener('click', createNewSession);

// Обработчики событий для фильтров
document.getElementById('minPriceRange').addEventListener('input', applyFilters);
document.getElementById('maxPriceRange').addEventListener('input', applyFilters);
document.getElementById('minRating').addEventListener('input', applyFilters);
document.getElementById('minReviews').addEventListener('input', applyFilters);
document.getElementById('resetFilters').addEventListener('click', () => {
    const minSlider = document.getElementById('minPriceRange');
    const maxSlider = document.getElementById('maxPriceRange');
    minSlider.value = minSlider.min;
    maxSlider.value = maxSlider.max;
    updateSliderTooltip('minPriceRange', 'minPriceTooltip', 'minPriceCaption', 'Мин. цена');
    updateSliderTooltip('maxPriceRange', 'maxPriceTooltip', 'maxPriceCaption', 'Макс. цена');
    document.getElementById('minRating').value = 0;
    document.getElementById('minReviews').value = 0;
    applyFilters();
});

// Обработчики событий для сортировки
document.querySelectorAll('#productsTable th').forEach(th => {
    th.addEventListener('click', () => {
        const field = th.getAttribute('data-sort');
        if (sortField === field) {
            sortAsc = !sortAsc;
        } else {
            sortField = field;
            sortAsc = true;
        }
        sortTable(field, sortAsc);
    });
});

function sortTable(field, asc = true, rerender = true) {
    filteredProducts.sort((a, b) => {
        if (typeof a[field] === 'string') {
            return asc ? a[field].localeCompare(b[field]) : b[field].localeCompare(a[field]);
        } else {
            return asc ? a[field] - b[field] : b[field] - a[field];
        }
    });
    if (rerender) renderTable();
}

// Chart.js
let priceChart = null;
let discountChart = null;
function renderCharts() {
    if (filteredProducts.length === 0) {
        // Очищаем графики если нет данных
        if (priceChart) {
            priceChart.destroy();
            priceChart = null;
        }
        if (discountChart) {
            discountChart.destroy();
            discountChart = null;
        }
        return;
    }
    
    // Гистограмма цен
    const prices = filteredProducts.map(p => p.discounted_price);
    const bins = [0, 1000, 2000, 3000, 4000, 5000, 7000, 10000, 20000];
    const counts = bins.map((b, i) =>
        prices.filter(p => p >= b && p < (bins[i + 1] || Infinity)).length
    );
    if (priceChart) priceChart.destroy();
    priceChart = new Chart(document.getElementById('priceHistogram'), {
        type: 'bar',
        data: {
            labels: bins.map((b, i) => `${b} - ${bins[i + 1] || '+'}`),
            datasets: [{
                label: 'Количество товаров',
                data: counts,
                backgroundColor: '#4e73df',
            }]
        },
        options: {responsive: false}
    });
    // Линейный график: скидка vs рейтинг
    const discounts = filteredProducts.map(p => p.price - p.discounted_price);
    const ratings = filteredProducts.map(p => p.rating);
    if (discountChart) discountChart.destroy();
    discountChart = new Chart(document.getElementById('discountVsRating'), {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Скидка vs Рейтинг',
                data: filteredProducts.map(p => ({x: p.rating, y: p.price - p.discounted_price})),
                backgroundColor: '#e74a3b',
            }]
        },
        options: {
            responsive: false,
            scales: {
                x: {title: {display: true, text: 'Рейтинг'}},
                y: {title: {display: true, text: 'Скидка (руб)'}}
            }
        }
    });
}

// Инициализация
restoreSession();
fetchProducts(); 