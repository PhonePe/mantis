function fetchDataAndRenderLineChart(apiUrl, Eid, title, XAxisName, YAxisName, noData) {
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

            // Create the gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, 350); // Adjust coordinates for desired gradient direction
            gradient.addColorStop(1, 'rgba(75, 192, 192, 0.2)'); // Set starting color with transparency (optional)
            gradient.addColorStop(0, 'rgba(75, 192, 192, 1)'); // Set ending color

            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of Occurrences',
                        data: values,
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4, // Enable fill for gradient effect
                        backgroundColor: gradient // Set background color to the created gradient
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
                            display: false, // Changed to display X-axis grid lines
                            grid: {
                                display: false
                            },
                            title: {
                                display: false,
                                text: `${XAxisName}`
                            }
                        },
                        y: {
                            grid: {
                                display: true,
                                color: 'rgba(0, 0, 0, 0.1)'
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
