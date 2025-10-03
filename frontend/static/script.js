document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileInfoText = document.getElementById('file-info-text');
    const processBtn = document.getElementById('process-btn');
    const uploadView = document.getElementById('upload-view');
    const resultsView = document.getElementById('results-view');
    const statusMessage = document.getElementById('status-message');
    const previewTable = document.getElementById('preview-table');
    const loadingSpinner = document.getElementById('loading-spinner');
    const spinnertext = document.getElementById('spinner-text');
    const resetBtn = document.getElementById('reset-btn');
    const mapTabBtn = document.getElementById('map-tab-btn');
    const generateReportBtn = document.getElementById('generate-report-btn'); // <-- New button

    let uploadedFile = null;

    // --- Drag and Drop ---
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        uploadedFile = file;
        fileInfoText.textContent = `Selected file: ${file.name}`;
        processBtn.disabled = false;
    }

    processBtn.addEventListener('click', async () => {
        if (!uploadedFile) return;

        showSpinner('Uploading and analyzing...');

        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('File upload failed.');
            }

            const uploadData = await uploadResponse.json();

            // *** FIX: Check for coordinates and enable map tab ***
            const columns = uploadData.columns.map(c => c.toLowerCase());
            if (columns.includes('latitude') && columns.includes('longitude')) {
                mapTabBtn.disabled = false;
                mapTabBtn.title = "View geospatial map";
            } else {
                mapTabBtn.disabled = true;
                mapTabBtn.title = "Map not available: Your data must contain 'Latitude' and 'Longitude' columns.";
            }

            statusMessage.textContent = `${uploadData.rows} rows of data uploaded successfully. Now calculating HMPI...`;

            showSpinner('Calculating HMPI...');
            const calculateResponse = await fetch('/calculate', {
                method: 'POST'
            });

            if (!calculateResponse.ok) {
                throw new Error('HMPI calculation failed.');
            }

            const calculateData = await calculateResponse.json();
            displayResults(calculateData);
            switchToResultsView();
        } catch (error) {
            console.error('Error:', error);
            statusMessage.textContent = `An error occurred: ${error.message}`;
        } finally {
            hideSpinner();
        }
    });

    // --- Start of Report Generation Logic ---
    generateReportBtn.addEventListener('click', async () => {
        showSpinner('Generating your report...');

        const reportData = {
            title: document.getElementById('report-title').value,
            date: document.getElementById('report-date').value,
            org: document.getElementById('report-org').value,
            author: document.getElementById('report-author').value,
            recommendations: document.getElementById('include-recs').checked,
            sections: {
                exec: document.getElementById('section-exec').checked,
                results: document.getElementById('section-results').checked,
                quality: document.getElementById('section-quality').checked,
                conc: document.getElementById('section-conc').checked
            }
        };

        try {
            const response = await fetch('/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reportData)
            });

            if (!response.ok) {
                throw new Error('Report generation failed.');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'hmpi_report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Report Error:', error);
            alert('Failed to generate report.');
        } finally {
            hideSpinner();
        }
    });
    // --- End of Report Generation Logic ---


    function displayResults(data) {
        const {
            columns,
            preview
        } = data;
        let tableHtml = '<table><thead><tr>';
        columns.forEach(col => {
            if (col !== 'Pollution_Color') { // Don't show the color column
                tableHtml += `<th>${col}</th>`;
            }
        });
        tableHtml += '</tr></thead><tbody>';

        preview.forEach(row => {
            const pollutionLevel = row['Pollution Level'] ? row['Pollution Level'].replace(/\s+/g, '-').toLowerCase() : '';
            const pollutionColor = row['Pollution_Color'] || '#ffffff';
            tableHtml += `<tr class="${pollutionLevel}">`;
            columns.forEach(col => {
                if (col !== 'Pollution_Color') {
                    let cellValue = row[col];
                    if (typeof cellValue === 'number') {
                        cellValue = cellValue.toFixed(2);
                    }
                    if (col === 'Station Name' || col === 'Location') {
                        tableHtml += `<td><span style="color: ${pollutionColor}; font-weight: bold;">${cellValue}</span></td>`;
                    } else {
                        tableHtml += `<td>${cellValue}</td>`;
                    }
                }
            });
            tableHtml += '</tr>';
        });


        tableHtml += '</tbody></table>';
        previewTable.innerHTML = tableHtml;
    }

    function switchToResultsView() {
        uploadView.classList.add('hidden');
        resultsView.classList.remove('hidden');
    }

    function showSpinner(message = 'Processing...') {
        spinnertext.textContent = message;
        loadingSpinner.classList.remove('hidden');
    }

    function hideSpinner() {
        loadingSpinner.classList.add('hidden');
    }

    resetBtn.addEventListener('click', () => {
        location.reload();
    });


    // --- Tabs ---
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (link.disabled) return;

            tabLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            const tabId = link.getAttribute('data-tab');
            tabContents.forEach(content => {
                if (content.id === tabId) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });

            if (tabId === 'map-tab' && !document.getElementById('map-container').hasChildNodes()) {
                loadMap();
            }
        });
    });

    async function loadMap() {
        const mapContainer = document.getElementById('map-container');
        mapContainer.innerHTML = '<div class="spinner"></div><p>Loading map...</p>';

        try {
            const response = await fetch('/map');
            if (response.ok) {
                const mapHtml = await response.text();
                mapContainer.innerHTML = mapHtml;
            } else {
                const errorText = await response.text();
                mapContainer.textContent = `Could not load map: ${errorText}`;
            }
        } catch (error) {
            mapContainer.textContent = 'An error occurred while loading the map.';
        }
    }

});
// --- Start of Scroll Animation Logic ---
// Select all elements you want to animate on scroll
const animatedElements = document.querySelectorAll('.info-card');

// Set up the Intersection Observer
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        // If the element is in the viewport, add the 'visible' class
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, {
    threshold: 0.1 // Trigger when 10% of the element is visible
});

// Tell the observer to watch each of the selected elements
animatedElements.forEach(el => observer.observe(el));
// --- End of Scroll Animation Logic ---