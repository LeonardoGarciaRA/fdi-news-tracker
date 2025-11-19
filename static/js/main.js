let allNews = [];
let filteredNews = [];
let currentPage = 1;
const perPage = 9;
const filters = {
    country: 'all',
    sector: 'all',
    minScore: 0,
    text: ''
};

// DOM Elements
const searchBtn = document.getElementById('searchBtn');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const searchInput = document.getElementById('searchInput');
const newsContainer = document.getElementById('newsContainer');
const loading = document.getElementById('loading');
const totalNews = document.getElementById('totalNews');
const visibleNews = document.getElementById('visibleNews');
const lastUpdate = document.getElementById('lastUpdate');

// Date search elements
const dateSearchBtn = document.getElementById('dateSearchBtn');
const dateInput = document.getElementById('dateInput');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Pagination elements
const pagination = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

// Filter elements
const countryFilter = document.getElementById('countryFilter');
const sectorFilter = document.getElementById('sectorFilter');
const scoreFilter = document.getElementById('scoreFilter');
const scoreValue = document.getElementById('scoreValue');
const textFilter = document.getElementById('textFilter');
const resetFiltersBtn = document.getElementById('resetFilters');
const activeFilters = document.getElementById('activeFilters');

// Set max date to today
dateInput.max = new Date().toISOString().split('T')[0];

// Auto-load latest news on page load
async function loadLatestNews() {
    loading.classList.remove('hidden');
    newsContainer.innerHTML = '<p class="empty-state">Loading latest FDI news...</p>';
    
    try {
        const response = await fetch('/api/news/latest');
        const data = await response.json();
        
        if (data.success) {
            allNews = mergeNews(allNews, data.news);
            currentPage = 1;
            refreshFilters();
            applyFilters();
        } else {
            newsContainer.innerHTML = '<p class="empty-state">Error loading news: ' + data.error + '</p>';
        }
    } catch (error) {
        newsContainer.innerHTML = '<p class="empty-state">Error loading news: ' + error.message + '</p>';
    } finally {
        loading.classList.add('hidden');
    }
}

// Search for news
searchBtn.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    loading.classList.remove('hidden');
    newsContainer.innerHTML = '';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                num_results: 20
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            allNews = mergeNews(allNews, data.news);
            currentPage = 1;
            refreshFilters();
            applyFilters();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error searching for news: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
});

// Date-based search
dateSearchBtn.addEventListener('click', async () => {
    const selectedDate = dateInput.value;
    
    if (!selectedDate) {
        alert('Please select a date');
        return;
    }
    
    // Check if date is in the future
    const today = new Date().toISOString().split('T')[0];
    if (selectedDate > today) {
        alert('Please select a date that is not in the future');
        return;
    }
    
    loading.classList.remove('hidden');
    newsContainer.innerHTML = '';
    
    try {
        const response = await fetch('/api/search/date', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: selectedDate,
                num_results: 20
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            allNews = mergeNews(allNews, data.news);
            currentPage = 1;
            refreshFilters();
            applyFilters();

            // Show success message
            if (data.count > 0) {
                alert(`Found ${data.count} articles for ${selectedDate}`);
            } else {
                alert(`No articles found for ${selectedDate}. Try a different date.`);
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error searching for news: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
});

// Export to Excel
exportBtn.addEventListener('click', async () => {
    if (allNews.length === 0) {
        alert('No news to export');
        return;
    }
    
    try {
        const response = await fetch('/api/export');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `fdi_projects_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            alert('Error exporting to Excel');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Clear all news
clearBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear all collected news?')) {
        try {
            const response = await fetch('/api/clear', {
                method: 'POST'
            });
            
            if (response.ok) {
                allNews = [];
                currentPage = 1;
                refreshFilters();
                applyFilters();
                loadLatestNews();
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

// Filter change handlers
countryFilter.addEventListener('change', () => {
    filters.country = countryFilter.value;
    applyFilters();
});

sectorFilter.addEventListener('change', () => {
    filters.sector = sectorFilter.value;
    applyFilters();
});

scoreFilter.addEventListener('input', () => {
    filters.minScore = Number(scoreFilter.value);
    scoreValue.textContent = filters.minScore;
    applyFilters();
});

textFilter.addEventListener('input', (event) => {
    filters.text = event.target.value.toLowerCase();
    applyFilters();
});

resetFiltersBtn.addEventListener('click', () => {
    filters.country = 'all';
    filters.sector = 'all';
    filters.minScore = 0;
    filters.text = '';
    countryFilter.value = 'all';
    sectorFilter.value = 'all';
    scoreFilter.value = 0;
    scoreValue.textContent = '0';
    textFilter.value = '';
    applyFilters();
});

// Display news with pagination
function displayNews() {
    if (filteredNews.length === 0) {
        newsContainer.innerHTML = '<p class="empty-state">No news collected yet.</p>';
        return;
    }

    // Calculate pagination
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;
    const paginatedNews = filteredNews.slice(start, end);

    newsContainer.innerHTML = paginatedNews.map((item, index) => `
        <div class="news-card">
            <div class="card-top">
                <h3>${escapeHtml(item.title || 'No title')}</h3>
                <span class="ai-pill">Resumo IA</span>
            </div>
            <div class="meta">
                <span class="score-pill">Relevância ${(item.relevance_score ?? 0).toFixed(1)}</span>
                <span>Source: ${escapeHtml(item.source || 'Unknown')}</span>
                ${item.published ? `<span>Published: ${item.published}</span>` : ''}
                ${item.search_date ? `<span>Search Date: ${item.search_date}</span>` : ''}
                ${item.collected_at ? `<span>Collected: ${item.collected_at}</span>` : ''}
            </div>
            <div class="tag-list">
                ${renderTags(item)}
            </div>
            <div class="summary">
                ${escapeHtml(item.summary || 'No summary available')}
            </div>
            <a href="${item.url}" target="_blank" class="source-link">
                Read full article →
            </a>
        </div>
    `).join('');
}

// Update pagination controls
function updatePagination() {
    const totalPages = Math.ceil(filteredNews.length / perPage);
    
    if (totalPages <= 1) {
        pagination.classList.add('hidden');
        return;
    }
    
    pagination.classList.remove('hidden');
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;
}

// Pagination event listeners
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayNews();
        updatePagination();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

nextPageBtn.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredNews.length / perPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayNews();
        updatePagination();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

// Update statistics
function updateStats() {
    totalNews.textContent = allNews.length;
    visibleNews.textContent = filteredNews.length;
    if (allNews.length > 0) {
        const lastItem = allNews[0];
        lastUpdate.textContent = lastItem.collected_at || 'Just now';
    } else {
        lastUpdate.textContent = '-';
    }
    renderActiveFilters();
}

// Tab switching functionality
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        button.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderTags(item) {
    const tags = [];
    if (item.countries && item.countries.length) {
        tags.push(...item.countries.map(country => `<span class="tag">${escapeHtml(country)}</span>`));
    }
    if (item.sectors && item.sectors.length) {
        tags.push(...item.sectors.map(sector => `<span class="tag">${escapeHtml(sector)}</span>`));
    }
    if (item.amount) {
        tags.push(`<span class="tag">${escapeHtml(item.amount)}</span>`);
    }
    if (item.company) {
        tags.push(`<span class="tag">${escapeHtml(item.company)}</span>`);
    }
    return tags.join('');
}

function mergeNews(existing, incoming) {
    const map = new Map();
    [...incoming, ...existing].forEach(item => {
        if (item && item.url && !map.has(item.url)) {
            map.set(item.url, item);
        }
    });
    return Array.from(map.values());
}

function refreshFilters() {
    const countrySet = new Set();
    const sectorSet = new Set();
    allNews.forEach(item => {
        (item.countries || []).forEach(country => countrySet.add(country));
        (item.sectors || []).forEach(sector => sectorSet.add(sector));
    });

    populateSelect(countryFilter, Array.from(countrySet).sort());
    populateSelect(sectorFilter, Array.from(sectorSet).sort());
}

function populateSelect(selectEl, options) {
    const current = selectEl.value;
    selectEl.innerHTML = '<option value="all">Todos</option>' + options.map(option => `<option value="${option}">${option}</option>`).join('');
    if (options.includes(current)) {
        selectEl.value = current;
    } else {
        selectEl.value = 'all';
    }
}

function renderActiveFilters() {
    const pills = [];
    if (filters.country !== 'all') {
        pills.push(`País: ${filters.country}`);
    }
    if (filters.sector !== 'all') {
        pills.push(`Setor: ${filters.sector}`);
    }
    if (filters.minScore > 0) {
        pills.push(`Score ≥ ${filters.minScore}`);
    }
    if (filters.text) {
        pills.push(`Texto: ${filters.text}`);
    }
    activeFilters.innerHTML = pills.map(pill => `<span class="filter-pill">${pill}</span>`).join('');
}

function applyFilters() {
    filteredNews = allNews.filter(item => {
        if (filters.country !== 'all') {
            const countries = item.countries || [];
            if (!countries.includes(filters.country) && item.country !== filters.country) {
                return false;
            }
        }

        if (filters.sector !== 'all') {
            const sectors = item.sectors || [];
            if (!sectors.includes(filters.sector) && item.sector !== filters.sector) {
                return false;
            }
        }

        if ((item.relevance_score || 0) < filters.minScore) {
            return false;
        }

        if (filters.text) {
            const blob = `${item.title || ''} ${item.summary || ''} ${item.source || ''}`.toLowerCase();
            if (!blob.includes(filters.text)) {
                return false;
            }
        }
        return true;
    });

    currentPage = 1;
    displayNews();
    updatePagination();
    updateStats();
}

// Load latest news on page load
loadLatestNews();
