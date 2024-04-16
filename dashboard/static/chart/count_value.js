// fetchAndUpdateCount.js

function fetchAndUpdateCount(apiUrl, elementId) {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const countElement = document.getElementById(elementId);
            if (countElement) {
                countElement.textContent = data.count;
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
