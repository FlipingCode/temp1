document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let uploadedFile = null;
    let resultsData = null; // Store the full results data
    let hasCoordinates = false;

    // --- DOM ELEMENT REFERENCES ---
    const uploadView = document.getElementById('upload-view');
    const resultsView = document.getElementById('results-view');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileInfoText = document.getElementById('file-info-text');
    const processBtn = document.getElementById('process-btn');
    const resetBtn = document.getElementById('reset-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const spinner = document.getElementById('loading-spinner');
    const spinnerText = document.getElementById('spinner-text');
    const previewTableContainer = document.getElementById('preview-table');
    const statusMessage = document.getElementById('status-message');
    const mapContainer = document.getElementById('map-container');
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    const mapTabBtn = document.getElementById('map-tab-btn');

    // Report Generator Elements
    const generateReportBtn = document.getElementById('generate-report-btn');
    const reportDateInput = document.getElementById('report-date');

    // Account UI Elements
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');

    // --- INITIALIZATION ---
    setCurrentDate();

    // --- EVENT LISTENERS ---
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) handleFile(fileInput.files[0]); });

    processBtn.addEventListener('click', handleProcess);
    resetBtn.addEventListener('click', handleReset);
    downloadCsvBtn.addEventListener('click', downloadCSV);
    downloadPdfBtn.addEventListener('click', downloadTablePDF);
    generateReportBtn.addEventListener('click', handleGenerateReport);

    // Mock Auth Listeners
    loginBtn.addEventListener('click', () => alert('Login functionality is not yet implemented.'));
    signupBtn.addEventListener('click', () => alert('Sign-up functionality is not yet implemented.'));

    tabLinks.forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.disabled) return;
            tabLinks.forEach(link => link.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
            if (tab.dataset.tab === 'map-tab' && mapContainer.innerHTML.trim() === '') fetchMap();
        });
    });

    // --- CORE FUNCTIONS ---
    function handleFile(file) {
        uploadedFile = file;
        fileInfoText.innerHTML = `Selected file: <b>${file.name}</b>`;
        processBtn.disabled = false;
    }

    async function handleProcess() {
        if (!uploadedFile) return;
        showSpinner('Uploading & cleaning data...');
        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            const uploadResponse = await fetch('/upload', { method: 'POST', body: formData });
            if (!uploadResponse.ok) throw new Error('File upload failed.');
            const previewData = await uploadResponse.json();
            if (previewData.error) throw new Error(previewData.error);

            const lowercasedColumns = previewData.columns.map(c => c.toLowerCase());
            hasCoordinates = lowercasedColumns.includes('latitude') && lowercasedColumns.includes('longitude');

            showSpinner('Calculating HMPI...');
            const calcResponse = await fetch('/calculate', { method: 'POST', body: formData });
            if (!calcResponse.ok) throw new Error('Calculation failed.');

            resultsData = await calcResponse.json();
            if (resultsData.error) throw new Error(resultsData.error);

            renderTable(resultsData);
            updateUIForResults();
        } catch (error) {
            console.error('Processing failed:', error);
            alert(`Error: ${error.message}`);
        } finally {
            hideSpinner();
        }
    }

    function handleReset() {
        uploadedFile = null;
        resultsData = null;
        hasCoordinates = false;

        fileInput.value = '';
        previewTableContainer.innerHTML = '';
        statusMessage.textContent = '';
        mapContainer.innerHTML = '';

        fileInfoText.innerHTML = 'Supported formats: CSV, XLSX, XLS';
        processBtn.disabled = true;
        mapTabBtn.disabled = true;

        document.querySelectorAll('.tab-link, .tab-content').forEach(el => el.classList.remove('active'));
        document.querySelector('.tab-link[data-tab="table-tab"]').classList.add('active');
        document.getElementById('table-tab').classList.add('active');

        resultsView.classList.add('hidden');
        uploadView.classList.remove('hidden');
    }

    async function fetchMap() {
        if (!hasCoordinates) {
            mapContainer.innerHTML = '<p>No coordinate data (latitude, longitude) found in file to generate a map.</p>';
            return;
        }
        mapContainer.innerHTML = '<p>Loading map...</p>';
        try {
            const response = await fetch('/map');
            if (!response.ok) throw new Error(await response.text() || 'Failed to load map data.');
            mapContainer.innerHTML = await response.text();
        } catch (error) {
            mapContainer.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
        }
    }

    // --- FEATURE FUNCTIONS ---

    function handleGenerateReport() {
        alert("Report settings noted. Generating the calculation results as a CSV file...");
        downloadCSV();
    }

    function downloadCSV() {
        if (!resultsData) {
            alert("No data available to download. Please process a file first.");
            return;
        }
        const columns = resultsData.columns;
        const rows = resultsData.preview;
        let csvContent = "data:text/csv;charset=utf-8," + columns.join(",") + "\n";

        rows.forEach(row => {
            const values = columns.map(col => {
                const val = row[col] === null || row[col] === undefined ? '' : row[col];
                return `"${String(val).replace(/"/g, '""')}"`;
            });
            csvContent += values.join(",") + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "hmpi_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function downloadTablePDF() {
        if (!resultsData) {
            alert("No data available to download. Please process a file first.");
            return;
        }
        showSpinner('Generating PDF...');
        const { jsPDF } = window.jspdf;
        const table = document.querySelector("#preview-table table");

        html2canvas(table).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({ orientation: 'landscape', unit: 'pt', format: [canvas.width + 40, canvas.height + 60] });

            pdf.setFontSize(20);
            pdf.text('HMPI Analysis Results Table', 20, 30);
            pdf.addImage(imgData, 'PNG', 20, 50, canvas.width, canvas.height);
            pdf.save("results_table.pdf");
            hideSpinner();
        }).catch(err => {
            alert('Failed to generate PDF. See console for details.');
            console.error(err);
            hideSpinner();
        });
    }

    // --- UI HELPER FUNCTIONS ---
    function setCurrentDate() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const dd = String(today.getDate()).padStart(2, '0');
        if (reportDateInput) {
            reportDateInput.value = `${yyyy}-${mm}-${dd}`;
        }
    }

    function renderTable(data) {
        statusMessage.textContent = `${data.message} (${data.rows} rows found)`;
        let tableHtml = '<table><thead><tr>' + data.columns.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
        tableHtml += data.preview.map(row => '<tr>' + data.columns.map(col => `<td>${row[col] ?? ''}</td>`).join('') + '</tr>').join('');
        tableHtml += '</tbody></table>';
        previewTableContainer.innerHTML = tableHtml;
    }

    function updateUIForResults() {
        mapTabBtn.disabled = !hasCoordinates;
        mapTabBtn.title = hasCoordinates ? "" : "Map requires 'latitude' and 'longitude' columns.";
        uploadView.classList.add('hidden');
        resultsView.classList.remove('hidden');
    }

    function showSpinner(message) {
        spinnerText.textContent = message || 'Processing...';
        spinner.classList.remove('hidden');
    }

    function hideSpinner() {
        spinner.classList.add('hidden');
    }
});