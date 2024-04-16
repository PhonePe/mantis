function fetchDataAndRenderphishingDoughnutChart(apiUrl, title) {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const total_count = data.length; // Extract total count from the API response
            console.log('total_count', total_count)
            if (total_count === 0) {
                document.getElementById('doughnut_count-no-data').classList.remove('hidden');
                return;
            }

            const ctx = document.getElementById('doughnut_count-chart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Total Count'], // Label for the single data point
                    datasets: [{
                        label: 'Number of Occurrences',
                        data: [total_count], // Single data point
                        backgroundColor: [
                            '#818cf8',
                            '#ffcd56',
                            '#4bc0c0',
                            '#36a2eb',
                            '#ff6384'                            
                        ],
                        borderColor: [
                            '#4F46E5',
                            '#ffcd56',
                            '#4bc0c0',
                            '#36a2eb',
                            '#ff6384' 
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: `${title}`
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
