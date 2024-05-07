function fetchDataAndRenderDoughnutChart(apiUrl, title) {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data)
            if (data.length === 0) {
                document.getElementById('doughnut-no-data').classList.remove('hidden');
                return;
            }
            const labels = data.map(item => item.x);
            const values = data.map(item => item.y);

            const ctx = document.getElementById('doughnut-chart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of Occurrences',
                        data: values,
                        backgroundColor: [
                            '#818cf8',
                            '#ff6384',
                            '#ff9f40',
                            '#ffcd56',
                            '#4bc0c0'
                        ],
                        borderColor: [
                            '#818cf8',
                            '#ff6384',
                            '#ff9f40',
                            '#ffcd56',
                            '#4bc0c0'
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
