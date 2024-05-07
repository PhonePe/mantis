function onOrgSelectChange(selectElement) {
    const selectedOrg = selectElement.value;
    const newUrl = `?org=${encodeURIComponent(selectedOrg)}`;
    window.location.href = newUrl;

    // Set the selected org in the header
    setHeaderOrg(selectedOrg);
}

// Function to set the selected value in the dropdown based on the URL parameter
function setSelectedOrgFromUrl() {
    const orgFromLocalStorage = localStorage.getItem('org') || '';
    if (orgFromLocalStorage) {
        const orgSelect = document.getElementById('orgSelect');
        orgSelect.value = orgFromLocalStorage;
    }
}

// Function to fetch data from the URL and populate the dropdown
function fetchDataAndPopulateDropdown() {
    fetch('org/organizations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const orgSelect = document.getElementById('orgSelect');

            // Clear existing options
            orgSelect.innerHTML = '';

            // Create and add options based on the data
            data.forEach(org => {
                const option = document.createElement('option');
                option.value = org;
                option.textContent = org;
                orgSelect.appendChild(option);
            });

            // Set the selected org from the URL
            setSelectedOrgFromUrl();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            // Handle fetch errors here
        });
}

// Function to set the organization header
function setHeaderOrg(org) {
    const headers = new Headers();
    headers.append('org', org);
    localStorage.setItem('org', org);
}

// Call the function to fetch data and populate the dropdown on page load
fetchDataAndPopulateDropdown();