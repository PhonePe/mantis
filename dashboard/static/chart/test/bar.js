// bar.js

function fetchDataAndRenderBarChart(apiUrl) {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const categories = data.map(item => item.x);
            const seriesData = data.map(item => item.y);

            const parentHeight = document.querySelector('.chart1').clientHeight;

            const chartOptions = {
                chart: {
                    type: 'bar',
                    height: parentHeight, // Increase the height for better visualization
                },
                xaxis: {
                    categories: categories,
                    title: {
                        text: 'Vulnerability Title'
                    }
                },
                yaxis: {
                    title: {
                        text: 'Number of Occurrences'
                    }
                },
                series: [{
                    name: 'Number of Occurrences',
                    data: seriesData,
                }],
            };

            const chart = new ApexCharts(document.querySelector('#bar-chart'), chartOptions);
            chart.render();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
