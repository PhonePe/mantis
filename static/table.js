// Function to fetch data from API with parameters
async function fetchData(apiEndpoint, org, pageSize, pageNumber) {
    try {
        const apiUrl = `${apiEndpoint}?org=${org}&page=${pageNumber}&page_size=${pageSize}`;
        const response = await fetch(apiUrl);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return [];
    }
}

// Function to populate the table with fetched data or show a message if no data is found
async function populateTable(apiEndpoint, org, pageSize, pageNumber) {
    const data = await fetchData(apiEndpoint, org, pageSize, pageNumber);
    const tbody = document.querySelector('tbody');
    tbody.innerHTML = ''; // Clear the existing table content

    if (data.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.setAttribute('colspan', '6');
        cell.classList.add('text-center', 'font-bold', 'p-8'); 
        cell.textContent = 'No data found';
        row.appendChild(cell);
        tbody.appendChild(row);
    } else {
        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item.Host}</td>
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item.Title}</td>
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item.Severity}</td>
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item.Description}</td>
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item['Tool Source']}</td>
                <td class="px-6 py-2 whitespace-nowrap text-sm">${item.Status}</td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Call populateTable function when the DOM is fully loaded

