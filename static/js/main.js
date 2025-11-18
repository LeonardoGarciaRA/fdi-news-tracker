let allNews = [];
let currentPage = 1;
const perPage = 10;

// DOM Elements
const searchBtn = document.getElementById('searchBtn');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const searchInput = document.getElementById('searchInput');
const newsContainer = document.getElementById('newsContainer');
const loading = document.getElementById('loading');
const totalNews = document.getElementById('totalNews');
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
            allNews = data.news;
            currentPage = 1;
            displayNews();
            updateStats();
            updatePagination();
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
            allNews = [...allNews, ...data.news];
            currentPage = 1;
            displayNews();
            updateStats();
            updatePagination();
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
            allNews = [...allNews, ...data.news];
            currentPage = 1;
            displayNews();
            updateStats();
            updatePagination();
            
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
                displayNews();
                updateStats();
                updatePagination();
                // Reload latest news
                loadLatestNews();
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

// Display news with pagination
function displayNews() {
    if (allNews.length === 0) {
        newsContainer.innerHTML = '<p class="empty-state">No news collected yet.</p>';
        return;
    }
    
    // Calculate pagination
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;
    const paginatedNews = allNews.slice(start, end);
    
    newsContainer.innerHTML = paginatedNews.map((item, index) => `
        <div class="news-card">
            <h3>${escapeHtml(item.title || 'No title')}</h3>
            <div class="meta">
                <span>Source: ${escapeHtml(item.source || 'Unknown')}</span>
                ${item.published ? `<span>Published: ${item.published}</span>` : ''}
                ${item.search_date ? `<span>Search Date: ${item.search_date}</span>` : ''}
                ${item.collected_at ? `<span>Collected: ${item.collected_at}</span>` : ''}
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
    const totalPages = Math.ceil(allNews.length / perPage);
    
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
    const totalPages = Math.ceil(allNews.length / perPage);
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
    if (allNews.length > 0) {
        const lastItem = allNews[0]; // Most recent
        lastUpdate.textContent = lastItem.collected_at || 'Just now';
    } else {
        lastUpdate.textContent = '-';
    }
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

// Load latest news on page load
loadLatestNews();
