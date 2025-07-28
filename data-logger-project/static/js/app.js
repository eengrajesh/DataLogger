document.addEventListener('DOMContentLoaded', function() {
    const STATUS_ELEMENT = document.getElementById('status');
    const CARDS_CONTAINER = document.getElementById('cards-container');
    const CHART_CANVAS = document.getElementById('temperature-chart');
    const NUMBER_OF_CHANNELS = 8;

    let temperatureChart;

    // --- Initialize UI ---
    function initializeUI() {
        // Create placeholder cards
        for (let i = 1; i <= NUMBER_OF_CHANNELS; i++) {
            const card = document.createElement('div');
            card.className = 'card';
            card.id = `card-${i}`;
            card.innerHTML = `
                <h3>Thermocouple ${i}</h3>
                <p class="temperature">--.- °C</p>
                <p class="timestamp">Waiting for data...</p>
            `;
            CARDS_CONTAINER.appendChild(card);
        }
        initializeChart();
    }

    // --- Chart.js Initialization ---
    function initializeChart() {
        const ctx = CHART_CANVAS.getContext('2d');
        temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [] // Datasets will be added dynamically
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute'
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // --- Data Fetching and UI Updates ---
    async function fetchLatestData() {
        try {
            const response = await fetch('/api/data/latest');
            if (!response.ok) throw new Error('Network response was not ok.');
            
            const data = await response.json();
            STATUS_ELEMENT.textContent = 'Running';
            STATUS_ELEMENT.style.color = '#28a745';

            updateCards(data);

        } catch (error) {
            console.error('Error fetching latest data:', error);
            STATUS_ELEMENT.textContent = 'Error';
            STATUS_ELEMENT.style.color = '#dc3545';
        }
    }

    async function fetchHistoricalData() {
        try {
            const response = await fetch('/api/data/historical');
            if (!response.ok) throw new Error('Network response was not ok.');
            
            const data = await response.json();
            updateChart(data);

        } catch (error) {
            console.error('Error fetching historical data:', error);
        }
    }

    function updateCards(data) {
        data.forEach(reading => {
            const card = document.getElementById(`card-${reading.thermocouple_id}`);
            if (card) {
                card.querySelector('.temperature').textContent = `${reading.temperature.toFixed(1)} °C`;
                card.querySelector('.timestamp').textContent = new Date(reading.timestamp).toLocaleTimeString();
            }
        });
    }

    function updateChart(data) {
        const datasets = [];
        const colors = ['#007bff', '#dc3545', '#ffc107', '#28a745', '#17a2b8', '#6f42c1', '#fd7e14', '#6610f2'];

        for (let i = 1; i <= NUMBER_OF_CHANNELS; i++) {
            const thermocoupleData = data.filter(d => d.thermocouple_id === i);
            if (thermocoupleData.length > 0) {
                datasets.push({
                    label: `TC ${i}`,
                    data: thermocoupleData.map(d => ({ x: new Date(d.timestamp), y: d.temperature })),
                    borderColor: colors[i - 1],
                    fill: false,
                    tension: 0.1
                });
            }
        }
        temperatureChart.data.datasets = datasets;
        temperatureChart.update();
    }

    // --- Initial Load and Periodic Updates ---
    initializeUI();
    fetchLatestData();
    fetchHistoricalData();

    setInterval(fetchLatestData, 5000); // Update latest readings every 5 seconds
    setInterval(fetchHistoricalData, 60000); // Update chart every minute
});