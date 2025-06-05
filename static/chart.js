let markersStore = {}; // Store markers for each symbol

async function fetchCandlestickData() {
    try {
        const chartContainer = document.getElementById('charts');
        if (!chartContainer) {
            console.error('Chart container element not found.');
            return;
        }

        const response = await fetch('/history');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        // console.log('Fetched Data:', data); // Debugging line

        if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
            throw new Error('Invalid or empty data received from API.');
        }

        const symbols = Object.keys(data);

        // Process only first 20 symbols for demo
        const visibleSymbols = symbols.slice(0, 100);

        const totalCharts = symbols.length;
        const remainingCharts = totalCharts % 3;

        for (const symbol of visibleSymbols) {
            const symbolData = data[symbol];
            if (!Array.isArray(symbolData) || symbolData.length === 0) {
                console.error(`No valid data available for symbol: ${symbol}`, data[symbol]);
                continue;
            }

            const chartData = symbolData ? symbolData.map(item => ({
                time: item.time,
                open: parseFloat(item.open),
                high: parseFloat(item.high),
                low: parseFloat(item.low),
                close: parseFloat(item.close),
            })) : [];

            const container = document.createElement('div');
            const name = document.createElement('div');
            container.className = 'chart-container';
            name.className = 'chart-name';
            container.id = `chart-${symbol}`;

            container.appendChild(name).innerHTML = `
                <a target="_blank" class="crypto_url" href="https://www.binance.com/en/futures/${symbol}">${symbol}</a>`;
            chartContainer.appendChild(container);

            try {
                const chart = LightweightCharts.createChart(container, {
                    width: container.clientWidth,
                    height: 500,
                    layout: {
                        background: { type: 'solid', color: '#000000' },
                        textColor: 'rgba(255, 255, 255, 0.9)',
                    },
                    grid: {
                        vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
                        horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
                    },
                    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
                    rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
                    timeScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
                });

                const candleSeries = chart.addCandlestickSeries({
                    upColor: 'rgb(0, 255, 94)',
                    downColor: 'rgb(190, 0, 0)',
                    borderDownColor: 'rgb(190, 0, 0)',
                    borderUpColor: 'rgb(0, 255, 94)',
                    wickDownColor: 'rgb(190, 0, 0)',
                    wickUpColor: 'rgb(0, 255, 94)',
                });

                candleSeries.setData(chartData);

                markersStore[symbol] = []; // Initialize storage
                // addCandlestickPatternMarkers(chartData, candleSeries, symbol);

                setupWebSocket(symbol.toLowerCase(), candleSeries, symbol);
            } catch (error) {
                console.error(`Error creating chart for ${symbol}:`, error);
            }
        }

        if (remainingCharts !== 0) {
            for (let i = 0; i < 3 - remainingCharts; i++) {
                const placeholder = document.createElement('div');
                placeholder.className = 'chart-container placeholder';
                chartContainer.appendChild(placeholder);
            }
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function setupWebSocket(symbol, candleSeries, originalSymbol) {
    const binanceSocket = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol}@kline_5m`);

    binanceSocket.onmessage = function (event) {
        const message = JSON.parse(event.data);
        const candleStick = message.k;

        var newCandle = {
            time: candleStick.t / 1000,
            open: parseFloat(candleStick.o),
            high: parseFloat(candleStick.h),
            low: parseFloat(candleStick.l),
            close: parseFloat(candleStick.c)
        };

        candleSeries.update(newCandle);

        // Add markers without removing existing ones
        addCandlestickPatternMarkers([newCandle], candleSeries, originalSymbol); // Use originalSymbol here

        // Ensure markersStore exists for the symbol
        if (!markersStore[originalSymbol]) {
            markersStore[originalSymbol] = [];
        }

        // Add new markers
        addCandlestickPatternMarkers([newCandle], candleSeries, originalSymbol);

        
    };

    binanceSocket.onerror = function (error) {
        console.error(`WebSocket error for ${symbol}:`, error);
    };

    binanceSocket.onclose = function () {
        console.log(`WebSocket closed for ${symbol}. Reconnecting...`);
        setTimeout(() => setupWebSocket(symbol, candleSeries), 5000);
    };
}

function addCandlestickPatternMarkers(data, candleSeries, symbol) {
    if (!markersStore[symbol]) markersStore[symbol] = []; // Initialize if empty
    let newMarkers = [];

    data.forEach((candle) => {
        let bodySize = Math.abs(candle.open - candle.close);
        let upperWick = candle.high - Math.max(candle.open, candle.close);
        let lowerWick = Math.min(candle.open, candle.close) - candle.low;

        let marker = null;

        // Hammer (Small body, long lower wick)
        if (bodySize > 0 && lowerWick >= bodySize * 2 && upperWick <= bodySize) {
            marker = {
                // time: candle.time,
                // position: 'belowBar',
                // color: 'green',
                // shape: 'arrowUp',
                // text: 'Hammer'
            };
        }

        // Inverted Hammer (Small body, long upper wick)
        if (bodySize > 0 && upperWick >= bodySize * 2 && lowerWick <= bodySize) {
            marker = {
                // time: candle.time,
                // position: 'aboveBar',
                // color: 'red',
                // shape: 'arrowDown',
                // text: 'Inv Hammer'
            };
        }

        if (marker) {
            // Prevent duplicate markers
            const exists = markersStore[symbol].some(m => m.time === marker.time);
            if (!exists) {
                markersStore[symbol].push(marker);
                newMarkers.push(marker);
            }
        }
    });

    // Reapply all markers to the chart
    candleSeries.setMarkers(markersStore[symbol]);
}

function filterCharts(chartValue) {
    const chartContainers = document.querySelectorAll('.chart-container:not(.placeholder)');
    chartContainers.forEach(container => {
        const symbol = container.id.replace('chart-', '');
        const markers = markersStore[symbol] || [];
        let shouldShow = false;

        switch (chartValue) {
            case 'all':
                shouldShow = true;
                break;
            case 'hammer':
                shouldShow = markers.some(marker => marker.text === 'Hammer');
                break;
            case 'invHammer':
                shouldShow = markers.some(marker => marker.text === 'Inv Hammer');
                break;
        }

        container.style.display = shouldShow ? 'block' : 'none';
    });
}

window.onload = fetchCandlestickData;