document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('#song-search-input');
    const trackIdInput = document.querySelector('#track-id');
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'autocomplete-results';
    document.body.appendChild(resultsContainer);

    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        if (query.length > 2) {
            fetch(`/song_search?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    resultsContainer.innerHTML = '';
                    data.forEach(item => {
                        const resultItem = document.createElement('div');
                        resultItem.className = 'autocomplete-item';
                        resultItem.textContent = `${item.artists} - ${item.name}`;
                        resultItem.addEventListener('click', function () {
                            searchInput.value = `${item.artists} - ${item.name}`;
                            trackIdInput.value = item.id;  // Set the hidden input value
                            console.log(`Track ID set to: ${item.id}`);  // Debugging print statement
                            resultsContainer.innerHTML = '';
                            resultsContainer.style.display = 'none'; // Hide the dropdown
                        });
                        resultsContainer.appendChild(resultItem);
                    });
                    const rect = searchInput.getBoundingClientRect();
                    resultsContainer.style.left = `${rect.left}px`;
                    resultsContainer.style.top = `${rect.bottom}px`;
                    resultsContainer.style.width = `${rect.width}px`;
                    resultsContainer.style.display = 'block'; // Show the dropdown
                });
        } else {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none'; // Hide the dropdown if query is empty
        }
    });

    // Hide the dropdown when clicking outside of it
    document.addEventListener('click', function (e) {
        if (!resultsContainer.contains(e.target) && !searchInput.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });

    const form = document.querySelector('#song-search-form');
    const loadingSpinner = document.querySelector('#loading-spinner');
    form.addEventListener('submit', function () {
        loadingSpinner.style.display = 'block';
    });
});

let currentAudio = null;

function playPreview(previewUrl) {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    } else {
        currentAudio = new Audio(previewUrl);
        currentAudio.play();
    }
}
