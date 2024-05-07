function fetchDataAndRenderRadarChart(apiUrl, Eid, title, noData)  {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                document.getElementById(`${noData}`).classList.remove('hidden');
                return;
            }
            const labels = data.map(item => item.x);
            const values = data.map(item => item.y);

            const ctx = document.getElementById(`${Eid}`).getContext('2d');
            const chart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of Occurrences',
                        data: values,
                        backgroundColor: [
                            '#36a2eb',
                            '#ff6384',
                            '#ff9f40',
                            '#ffcd56',
                            '#4bc0c0'
                        ],
                        borderColor: [
                            '#36a2eb',
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
