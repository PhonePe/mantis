function fetchDataAndRenderBarChart(apiUrl, Eid, title, XAxisName, YAxisName, noData) {
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
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of Occurrences',
                        data: values,
                        backgroundColor: '#818cf8',
                        borderColor: '#818cf8',
                        borderWidth: 1,
                        borderRadius: 4,
                    }]
                },
                options: {
                        plugins: {
                            title: {
                                display: true,
                                text: `${title}`
                            }
                        },
                        responsive: true, // Make the chart fully responsive
                        maintainAspectRatio: false, // Ensure the aspect ratio is not enforced
                        scales: {
                        x: {
                            display: false, // Remove X axis grid lines
                            grid: {
                                display: true // Remove X axis grid lines
                            },
                            title: {
                                display: true,
                                text: `${XAxisName}`
                            }
                        },
                        y: {
                            grid: {
                                display: true // Remove X axis grid lines
                            },
                            title: {
                                display: true,
                                text: `${YAxisName}`
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
