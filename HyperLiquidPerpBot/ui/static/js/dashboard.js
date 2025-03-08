// Helper function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Balance chart initialization
let balanceChart = null;

function initBalanceChart(data) {
    const ctx = document.getElementById('balance-chart').getContext('2d');
    
    if (balanceChart) {
        balanceChart.destroy();
    }
    
    balanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => formatDate(item.timestamp)),
            datasets: [{
                label: 'Account Balance',
                data: data.map(item => item.balance),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Update bot status indicator
function updateStatusIndicator(status) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (status === 'RUNNING') {
        indicator.className = 'status-indicator status-active';
        statusText.textContent = 'Active';
    } else {
        indicator.className = 'status-indicator status-inactive';
        statusText.textContent = 'Inactive';
    }
}

// Fetch open positions
function fetchOpenPositions() {
    fetch('/api/open_positions')
        .then(response => response.json())
        .then(positions => {
            const tableBody = document.getElementById('positions-table');
            tableBody.innerHTML = '';
            
            if (positions.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No open positions</td></tr>';
                return;
            }
            
            positions.forEach(position => {
                const row = document.createElement('tr');
                
                const pnlClass = position.pnl >= 0 ? 'text-success' : 'text-danger';
                
                row.innerHTML = `
                    <td>${position.asset}</td>
                    <td>${position.size}</td>
                    <td>${formatCurrency(position.entryPrice)}</td>
                    <td>${formatCurrency(position.currentPrice)}</td>
                    <td class="${pnlClass}">${formatCurrency(position.pnl)}</td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching positions:', error));
}

// Fetch trade history
function fetchTradeHistory() {
    fetch('/api/trade_history')
        .then(response => response.json())
        .then(trades => {
            const tableBody = document.getElementById('trade-history');
            tableBody.innerHTML = '';
            
            if (trades.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No trade history</td></tr>';
                return;
            }
            
            document.getElementById('total-trades').textContent = trades.length;
            
            // Calculate 24h P/L
            const now = new Date();
            const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);
            
            let dailyPnl = 0;
            
            trades.forEach(trade => {
                const tradeDate = new Date(trade.timestamp);
                
                if (tradeDate >= oneDayAgo) {
                    dailyPnl += parseFloat(trade.pnl);
                }
                
                const row = document.createElement('tr');
                
                const pnlClass = parseFloat(trade.pnl) >= 0 ? 'text-success' : 'text-danger';
                
                row.innerHTML = `
                    <td>${formatDate(trade.timestamp)}</td>
                    <td>${trade.asset}</td>
                    <td>${trade.type}</td>
                    <td>${trade.size}</td>
                    <td>${formatCurrency(trade.price)}</td>
                    <td class="${pnlClass}">${formatCurrency(trade.pnl)}</td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // Update daily P/L display
            const dailyPnlElement = document.getElementById('daily-pnl');
            const pnlClass = dailyPnl >= 0 ? 'text-success' : 'text-danger';
            dailyPnlElement.className = pnlClass;
            dailyPnlElement.textContent = `${formatCurrency(dailyPnl)}`;
        })
        .catch(error => console.error('Error fetching trade history:', error));
}

// Fetch balance history
function fetchBalanceHistory() {
    fetch('/api/balance_history')
        .then(response => response.json())
        .then(history => {
            if (history.length > 0) {
                // Update current balance
                const latestBalance = history[history.length - 1].balance;
                document.getElementById('current-balance').textContent = formatCurrency(latestBalance);
                
                // Update balance chart
                initBalanceChart(history);
            }
        })
        .catch(error => console.error('Error fetching balance history:', error));
}

// Fetch bot status
function fetchBotStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data.status);
        })
        .catch(error => console.error('Error fetching bot status:', error));
}

// Start bot
document.getElementById('start-btn').addEventListener('click', function() {
    fetch('/api/start_bot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        updateStatusIndicator('RUNNING');
    })
    .catch(error => console.error('Error starting bot:', error));
});

// Stop bot
document.getElementById('stop-btn').addEventListener('click', function() {
    fetch('/api/stop_bot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        updateStatusIndicator('STOPPED');
    })
    .catch(error => console.error('Error stopping bot:', error));
});

// Initial data load
fetchBotStatus();
fetchOpenPositions();
fetchTradeHistory();
fetchBalanceHistory();

// Set up auto-refresh
setInterval(() => {
    fetchBotStatus();
    fetchOpenPositions();
    fetchTradeHistory();
    fetchBalanceHistory();
}, 30000); // Refresh every 30 seconds