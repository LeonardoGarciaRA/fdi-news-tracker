let allNews = [];

// DOM Elements
const searchBtn = document.getElementById('searchBtn');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const searchInput = document.getElementById('searchInput');
const numResults = document.getElementById('numResults');
const newsContainer = document.getElementById('newsContainer');
const loading = document.getElementById('loading');
const totalNews = document.getElementById('totalNews');
const lastUpdate = document.getElementById('lastUpdate');

// Date search elements
const dateSearchBtn = document.getElementById('dateSearchBtn');
const dateInput = document.getElementById('dateInput');
const dateNumResults = document.getElementById('dateNumResults');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Set max date to today
dateInput.max = new Date().toISOString().split('T')[0];

// Search for news
searchBtn.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    const num = parseInt(numResults.value) || 10;
    
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
                num_results: num
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            allNews = [...allNews, ...data.news];
            displayNews(allNews);
            updateStats();
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
                displayNews([]);
                updateStats();
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

// Display news
function displayNews(news) {
    if (news.length === 0) {
        newsContainer.innerHTML = '<p class="empty-state">No news collected yet. Click "Search News" to start.</p>';
        return;
    }
    
    newsContainer.innerHTML = news.map((item, index) => `
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

// Update statistics
function updateStats() {
    totalNews.textContent = allNews.length;
    if (allNews.length > 0) {
        const lastItem = allNews[allNews.length - 1];
        lastUpdate.textContent = lastItem.collected_at || 'Just now';
    } else {
        lastUpdate.textContent = '-';
    }
}

// Load existing news on page load
async function loadNews() {
    try {
        const response = await fetch('/api/news');
        const data = await response.json();
        if (data.success) {
            allNews = data.news;
            displayNews(allNews);
            updateStats();
        }
    } catch (error) {
        console.error('Error loading news:', error);
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

// Date-based search
dateSearchBtn.addEventListener('click', async () => {
    const selectedDate = dateInput.value;
    const num = parseInt(dateNumResults.value) || 10;
    
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
                num_results: num
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            allNews = [...allNews, ...data.news];
            displayNews(allNews);
            updateStats();
            
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

// Load news on page load
loadNews();

