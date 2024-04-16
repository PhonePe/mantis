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
  
        // Check if chartjs-plugin-gradient is available
        const gradientPlugin = window['chartjs-plugin-gradient'];
        if (gradientPlugin) {
          Chart.register(gradientPlugin); // Register the plugin if available
        } else {
          console.warn('chartjs-plugin-gradient not found. Gradient effect might not work.');
        }
  
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
              backgroundColor: (context) => {
                // Define a single gradient for both background and border
                const gradient = ctx.createLinearGradient(100, 100, 100, 350); // Adjust coordinates for desired gradient direction
            gradient.addColorStop(1, '#594aa3'); // Set starting color with transparency (optional)
            gradient.addColorStop(0, '#12c99b'); // Set ending color
                return gradient;
              }
            }]
          },
          options: {
            plugins: {
              gradient: gradientPlugin, // Use the plugin if registered
              title: {
                display: false,
                text: `${title}`
              }
            },
            responsive: true, // Make the chart fully responsive
            maintainAspectRatio: false, // Ensure the aspect ratio is not enforced
            scales: {
              x: {
                display: true, // Show X-axis grid lines again
                grid: {
                  display: false
                },
                title: {
                  display: true,
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
  