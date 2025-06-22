document.addEventListener('DOMContentLoaded', function() {
    // Only initialize filters if the filter controls exist (user is logged in)
    const filterControls = document.querySelector('.filter-controls');
    if (!filterControls) return;

    const toggleFiltersBtn = document.getElementById('toggle-filters');
    const sortBySelect = document.getElementById('sort-by');
    const stanceFilter = document.getElementById('stance-filter');
    const userFilter = document.getElementById('user-filter');
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');
    const popularityFilter = document.getElementById('popularity-filter');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');

    // Store initial filter values
    let currentFilters = {
        sortBy: 'newest',
        stance: 'all',
        user: '',
        dateFrom: '',
        dateTo: '',
        popularity: 'all'
    };

    // Toggle filters visibility
    toggleFiltersBtn.addEventListener('click', function() {
        if (filterControls.style.display === 'none') {
            filterControls.style.display = 'block';
            filterControls.classList.add('show');
        } else {
            filterControls.style.display = 'none';
            filterControls.classList.remove('show');
        }
    });

    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        if (unsafe == null) return '';
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Function to update the topic list in the UI
    function updateTopicList(topics) {
        const topicList = document.querySelector('.topic-list');
        if (!topics.length) {
            topicList.innerHTML = `
                <div class="topic-card">
                    <div class="topic-header">
                        <h2 class="topic-title">No topics found</h2>
                        <p class="topic-content mt-2">Try adjusting your filters to see more results.</p>
                    </div>
                </div>
            `;
            return;
        }

        topicList.innerHTML = topics.map(topic => `
            <a href="/topic/${topic.topicID}" class="topic-card-link">
                <div class="topic-card">
                    <div class="topic-header">
                        <h2 class="topic-title">${escapeHtml(topic.title)}</h2>
                        <div class="topic-meta">
                            <span>Posted by <a href="/profile/${escapeHtml(topic.userName)}" class="user-link">${escapeHtml(topic.userName)}</a></span>
                            <span>${escapeHtml(topic.creationTime)}</span>
                        </div>
                    </div>
                    ${topic.content ? `
                        <div class="topic-content mt-2">
                            ${escapeHtml(topic.content.substring(0, 200))}${topic.content.length > 200 ? '...' : ''}
                        </div>
                    ` : ''}
                    <div class="topic-stats">
                        <div class="topic-stat">
                            <span>${topic.commentCount} comments</span>
                        </div>
                        <div class="topic-stat">
                            <button class="like-button ${topic.userLiked ? 'liked' : ''}" 
                                    data-topic-id="${topic.topicID}"
                                    onclick="event.stopPropagation(); toggleLike('topic', this.dataset.topicId, this)">
                                <span class="like-icon">♥</span>
                                <span class="like-count">${topic.likeCount}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </a>
        `).join('');
    }

    // Function to apply filters
    function applyFilters() {
        const formData = new FormData();
        formData.append('sortBy', sortBySelect.value);
        formData.append('stance', stanceFilter.value);
        formData.append('user', userFilter.value);
        formData.append('dateFrom', dateFrom.value);
        formData.append('dateTo', dateTo.value);
        formData.append('popularity', popularityFilter.value);

        // Show loading state
        const topicList = document.querySelector('.topic-list');
        if (topicList) {
            topicList.style.opacity = '0.5';
        }

        fetch('/apply_filters', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTopicList(data.topics);
            } else {
                console.error('Error applying filters:', data.error);
                topicList.innerHTML = `
                    <div class="topic-card">
                        <div class="topic-header">
                            <h2 class="topic-title">Error</h2>
                            <p class="topic-content mt-2">Failed to apply filters. Please try again.</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            topicList.innerHTML = `
                <div class="topic-card">
                    <div class="topic-header">
                        <h2 class="topic-title">Error</h2>
                        <p class="topic-content mt-2">An error occurred while applying filters.</p>
                    </div>
                </div>
            `;
        })
        .finally(() => {
            // Remove loading state
            if (topicList) {
                topicList.style.opacity = '1';
            }
        });
    }

    // Function to reset filters
    function resetFilters() {
        sortBySelect.value = 'newest';
        stanceFilter.value = 'all';
        userFilter.value = '';
        dateFrom.value = '';
        dateTo.value = '';
        popularityFilter.value = 'all';

        // Apply the reset filters
        applyFilters();
    }

    // Add event listeners
    applyFiltersBtn.addEventListener('click', applyFilters);
    resetFiltersBtn.addEventListener('click', resetFilters);

    // Optional: Apply filters on select/input change
    if (sortBySelect) {
        sortBySelect.addEventListener('change', applyFilters);
    }
}); 