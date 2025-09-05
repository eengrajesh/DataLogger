document.addEventListener('DOMContentLoaded', function() {
    const SENSOR_TOGGLES_CONTAINER = document.getElementById('sensor-toggles-container');
    const SENSOR_TILES_CONTAINER = document.getElementById('sensor-tiles-container');
    const AVG_TEMP_CALLOUT = document.querySelector('#average-temp-callout p');
    const AVG_TEMP_BAR_CHART_CANVAS = document.getElementById('average-temp-bar-chart');
    const HISTORICAL_CHART_CANVAS = document.getElementById('temperature-chart');
    const DOWNLOAD_BUTTON = document.getElementById('download-data');
    const CONNECT_BUTTON = document.getElementById('connect-btn');
    const DISCONNECT_BUTTON = document.getElementById('disconnect-btn');
    const START_LOGGING_BUTTON = document.getElementById('start-logging-btn');
    const STOP_LOGGING_BUTTON = document.getElementById('stop-logging-btn');
    const RESTART_PI_BUTTON = document.getElementById('restart-pi-btn');
    const RESET_BOARD_BUTTON = document.getElementById('reset-board-btn');
    const CLEAR_DATA_BUTTON = document.getElementById('clear-data-btn');
    const LOGGING_STATUS_ELEMENT = document.getElementById('logging-status');
    const STORAGE_STATUS_ELEMENT = document.querySelector('#storage-status span');
    const CPU_TEMP_STATUS_ELEMENT = document.querySelector('#cpu-temp-status span');
    const CORRECTION_FACTOR_INPUT = document.getElementById('correction-factor');

    const NUMBER_OF_CHANNELS = 8;
    let historicalChart, avgTempBarChart;
    let activeSensors = {};

    function initializeUI() {
        for (let i = 1; i <= NUMBER_OF_CHANNELS; i++) {
            // Create activation toggle
            const toggleContainer = document.createElement('div');
            toggleContainer.className = 'sensor-toggle';
            toggleContainer.innerHTML = `
                <label for="sensor-active-${i}">Channel ${i}</label>
                <label class="switch">
                    <input type="checkbox" id="sensor-active-${i}" data-channel="${i}">
                    <span class="slider"></span>
                </label>
                <div class="channel-config">
                    <select id="sampling-interval-${i}" data-channel="${i}" class="sampling-interval-select">
                        <option value="1">1s</option>
                        <option value="5" selected>5s</option>
                        <option value="10">10s</option>
                        <option value="15">15s</option>
                        <option value="30">30s</option>
                        <option value="60">1m</option>
                        <option value="300">5m</option>
                        <option value="900">15m</option>
                    </select>
                </div>
            `;
            SENSOR_TOGGLES_CONTAINER.appendChild(toggleContainer);

            // Create sensor tile
            const tile = document.createElement('div');
            tile.className = 'sensor-tile';
            tile.id = `sensor-tile-${i}`;
            tile.innerHTML = `
                <div class="connectivity-indicator"></div>
                <h3>Channel ${i}</h3>
                <p class="temperature">--.- °C</p>
                <p class="avg-temp">Avg: --.- °C</p>
            `;
            SENSOR_TILES_CONTAINER.appendChild(tile);
        }

        initializeCharts();
    }

    function initializeCharts() {
        const historicalCtx = HISTORICAL_CHART_CANVAS.getContext('2d');
        historicalChart = new Chart(historicalCtx, {
            type: 'line',
            data: { datasets: [] },
            options: chartOptions('Time', 'Temperature (°C)', true)
        });

        const avgBarCtx = AVG_TEMP_BAR_CHART_CANVAS.getContext('2d');
        avgTempBarChart = new Chart(avgBarCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Average Temperature',
                    data: [],
                    backgroundColor: 'rgba(0, 82, 155, 0.6)',
                    borderColor: 'rgba(0, 82, 155, 1)',
                    borderWidth: 1
                }]
            },
            options: chartOptions('Sensor Channel', 'Avg. Temperature (°C)', false)
        });
    }

    function chartOptions(xLabel, yLabel, isTime) {
        return {
            scales: {
                x: {
                    type: isTime ? 'time' : 'category',
                    time: {
                        displayFormats: {
                            second: 'HH:mm:ss',
                            minute: 'HH:mm:ss',
                            hour: 'HH:mm:ss'
                        }
                    },
                    title: { display: true, text: xLabel, color: '#333' },
                    ticks: { color: '#333' },
                    grid: { color: '#ddd' }
                },
                y: {
                    title: { display: true, text: yLabel, color: '#333' },
                    ticks: { color: '#333' },
                    grid: { color: '#ddd' }
                }
            },
            plugins: { legend: { labels: { color: '#333' } } },
            responsive: true,
            maintainAspectRatio: false
        };
    }

    function setupEventListeners() {
        SENSOR_TOGGLES_CONTAINER.addEventListener('change', (event) => {
            if (event.target.type === 'checkbox') {
                const channel = parseInt(event.target.dataset.channel);
                const status = event.target.checked;
                postData(`/api/sensor_status/${channel}`, { status });
            } else if (event.target.classList.contains('sampling-interval-select')) {
                const channel = parseInt(event.target.dataset.channel);
                const interval = parseInt(event.target.value);
                postData(`/api/sensor_interval/${channel}`, { interval });
            }
        });

        document.getElementById('time-unit-select').addEventListener('change', () => {
            fetchData(); // Re-fetch and re-draw the chart with the new time unit
        });

        CONNECT_BUTTON.addEventListener('click', () => postData('/api/connect'));
        DISCONNECT_BUTTON.addEventListener('click', () => postData('/api/disconnect'));
        START_LOGGING_BUTTON.addEventListener('click', () => postData('/api/logging/start'));
        STOP_LOGGING_BUTTON.addEventListener('click', () => postData('/api/logging/stop'));
        RESTART_PI_BUTTON.addEventListener('click', () => {
            if(confirm('Are you sure you want to restart the Raspberry Pi?')) {
                postData('/api/system/restart');
            }
        });
        RESET_BOARD_BUTTON.addEventListener('click', () => {
            if(confirm('Are you sure you want to reset the sensor board?')) {
                postData('/api/sensor/reset');
            }
        });
        CLEAR_DATA_BUTTON.addEventListener('click', () => {
            if(confirm('Are you sure you want to clear all historical data?')) {
                postData('/api/data/clear');
            }
        });

        DOWNLOAD_BUTTON.addEventListener('click', () => {
            window.location.href = '/api/data/download/csv';
        });

        CORRECTION_FACTOR_INPUT.addEventListener('change', (event) => {
            const channel = 1; // Assuming a single correction factor for now, will need to update for per-channel
            const factor = parseFloat(event.target.value);
            postData(`/api/calibration/${channel}`, { factor });
        });
    }

    async function postData(url, body = {}) {
        try {
            const response = await fetch(url, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const result = await response.json();
            console.log(result.message);
            fetchData(); // Refresh data after action
        } catch (error) {
            console.error(`Error posting to ${url}:`, error);
        }
    }

    async function fetchData() {
        try {
            const [live, historical, average, boardInfo, sensorStatus, storageStatus, sensorIntervals, cpuTemp, calibrationFactors] = await Promise.all([
                Promise.all([...Array(NUMBER_OF_CHANNELS).keys()].map(i => fetch(`/api/data/live/${i+1}`).then(res => res.ok ? res.json() : null))),
                fetch('/api/data/historical').then(res => res.json()),
                fetch('/api/data/average').then(res => res.json()),
                fetch('/api/board_info').then(res => res.json()),
                fetch('/api/sensor_status').then(res => res.json()),
                fetch('/api/storage_status').then(res => res.json()),
                fetch('/api/sensor_intervals').then(res => res.json()),
                fetch('/api/cpu_temp').then(res => res.json()),
                fetch('/api/calibration').then(res => res.json())
            ]);

            activeSensors = sensorStatus;
            updateLiveReadings(live, average, boardInfo);
            updateAnalytics(average);
            updateHistoricalChart(historical);
            updateSensorToggles(sensorIntervals);
            updateHeaderStatus(storageStatus, boardInfo, cpuTemp);
            updateCalibrationFactor(calibrationFactors);

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }
    
    function updateHeaderStatus(storage, board, cpu) {
        const freeSpaceGB = (storage.free / (1024 * 1024 * 1024)).toFixed(2);
        STORAGE_STATUS_ELEMENT.textContent = `${freeSpaceGB} GB Free`;

        if (cpu && cpu.cpu_temp > 0) {
            CPU_TEMP_STATUS_ELEMENT.textContent = `${cpu.cpu_temp.toFixed(1)} °C`;
        } else {
            CPU_TEMP_STATUS_ELEMENT.textContent = '--.- °C';
        }

        // This is a simple check. A more robust solution would be a dedicated logging status endpoint.
        if (board.board_info.connected) {
            LOGGING_STATUS_ELEMENT.classList.add('logging');
            LOGGING_STATUS_ELEMENT.querySelector('.text').textContent = 'Logging';
        } else {
            LOGGING_STATUS_ELEMENT.classList.remove('logging');
            LOGGING_STATUS_ELEMENT.querySelector('.text').textContent = 'Idle';
        }
    }

    function updateSensorToggles(intervals) {
        for (let i = 1; i <= NUMBER_OF_CHANNELS; i++) {
            const toggle = document.getElementById(`sensor-active-${i}`);
            toggle.checked = activeSensors[i];
            document.getElementById(`sensor-tile-${i}`).style.display = activeSensors[i] ? '' : 'none';
            
            const intervalSelect = document.getElementById(`sampling-interval-${i}`);
            if (intervals && intervals[i]) {
                intervalSelect.value = intervals[i];
            }
        }
    }

    function updateLiveReadings(data, averageData, boardInfo) {
        data.forEach((reading, index) => {
            const channel = index + 1;
            const tile = document.getElementById(`sensor-tile-${channel}`);
            const indicator = tile.querySelector('.connectivity-indicator');
            const avgTempElement = tile.querySelector('.avg-temp');
            const avgReading = averageData.find(d => d.thermocouple_id === channel);

            if (activeSensors[channel]) {
                if (boardInfo.board_info.connected && reading && reading.temperature !== undefined) {
                    tile.querySelector('.temperature').textContent = `${reading.temperature.toFixed(1)} °C`;
                    indicator.classList.add('connected');
                    // This was causing an error because the sensor-type select was removed.
                    // A more robust solution would be to fetch the sensor type from the backend.
                    /* if (document.getElementById(`sensor-type-${channel}`).value === 'K') {
                        tile.classList.add('k-type');
                    } */
                } else {
                    tile.querySelector('.temperature').textContent = '--.- °C';
                    indicator.classList.remove('connected');
                }
                if (avgReading) {
                    avgTempElement.textContent = `Avg: ${avgReading.avg_temp.toFixed(1)} °C`;
                }
            }
        });
    }

    function updateAnalytics(data) {
        const activeAvgData = data.filter(d => activeSensors[d.thermocouple_id]);
        const totalAvg = activeAvgData.reduce((sum, d) => sum + d.avg_temp, 0) / (activeAvgData.length || 1);
        AVG_TEMP_CALLOUT.textContent = `${totalAvg.toFixed(1)} °C`;

        avgTempBarChart.data.labels = activeAvgData.map(d => `Channel ${d.thermocouple_id}`);
        avgTempBarChart.data.datasets[0].data = activeAvgData.map(d => d.avg_temp);
        avgTempBarChart.update();
    }

    function updateHistoricalChart(data) {
        if (data.length === 0) {
            historicalChart.data.datasets = [];
            historicalChart.update();
            return;
        }

        const colors = ['#00529B', '#6c757d', '#ffc107', '#28a745', '#17a2b8', '#6f42c1', '#fd7e14', '#6610f2'];
        historicalChart.data.datasets = Object.keys(activeSensors).map(i => {
            if (!activeSensors[i]) return null;
            const channelData = data.filter(d => d.thermocouple_id == i);
            return {
                label: `Channel ${i}`,
                data: channelData.map(d => ({ x: new Date(d.timestamp), y: d.temperature })),
                borderColor: colors[i - 1],
                fill: false,
                tension: 0.1
            };
        }).filter(Boolean);

        // Dynamically adjust the time unit on the x-axis
        const timeUnitSelect = document.getElementById('time-unit-select');
        let unit = timeUnitSelect.value;

        if (unit === 'auto') {
            const timestamps = data.map(d => new Date(d.timestamp));
            const timeRange = timestamps[timestamps.length - 1] - timestamps[0]; // in milliseconds

            if (timeRange < 5 * 60 * 1000) { // Less than 5 minutes
                unit = 'second';
            } else if (timeRange > 3 * 60 * 60 * 1000) { // More than 3 hours
                unit = 'hour';
            } else {
                unit = 'minute';
            }
        }

        historicalChart.options.scales.x.time.unit = unit;
        historicalChart.update();
    }

    function updateCalibrationFactor(factors) {
        const channel = 1; // Assuming a single correction factor for now
        if (factors && factors[channel]) {
            CORRECTION_FACTOR_INPUT.value = factors[channel];
        }
    }

    // Initial Load
    initializeUI();
    setupEventListeners();
    fetchData();
    setInterval(fetchData, 5000); // Refresh data every 5 seconds
});