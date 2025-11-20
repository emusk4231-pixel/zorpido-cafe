/**
 * ZORPIDO POS - Advanced Overview JavaScript
 * Enhanced with modern UI/UX features
 */

document.addEventListener('DOMContentLoaded', function () {
  const apiUrl = '/pos/api/overview-data/';
  const labelsBtn = {
    day: document.getElementById('range-day'),
    week: document.getElementById('range-week'),
    month: document.getElementById('range-month')
  };

  let currentRange = 'week';
  let charts = {
    sales: null,
    expenses: null,
    profit: null
  };

  // Initialize
  init();

  function init() {
    setupEventListeners();
    setActiveButton();
    fetchData(currentRange);
  }

  function setupEventListeners() {
    Object.keys(labelsBtn).forEach(key => {
      labelsBtn[key].addEventListener('click', function () {
        if (currentRange !== key) {
          currentRange = key;
          setActiveButton();
          fetchData(key);
        }
      });
    });
  }

  function setActiveButton() {
    Object.keys(labelsBtn).forEach(key => {
      if (labelsBtn[key]) {
        labelsBtn[key].classList.toggle('active', key === currentRange);
      }
    });
  }

  function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
      overlay.classList.add('active');
    }
  }

  function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
      overlay.classList.remove('active');
    }
  }

  function fetchData(range) {
    showLoading();
    
    fetch(apiUrl + '?range=' + range, { 
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        renderSummary(data.summary);
        renderCharts(data.series);
        hideLoading();
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        hideLoading();
        showErrorMessage('Failed to load data. Please try again.');
      });
  }

  function renderSummary(summary) {
    const container = document.getElementById('summary-cards');
    if (!container) return;
    
    container.innerHTML = '';
    
    const cards = [
      {
        key: 'total_sales',
        title: 'Total Sales',
        icon: 'bi-graph-up',
        class: 'sales',
        value: summary.total_sales,
        format: 'currency'
      },
      {
        key: 'total_expenses',
        title: 'Total Expenses',
        icon: 'bi-cash-stack',
        class: 'expenses',
        value: summary.total_expenses,
        format: 'currency'
      },
      {
        key: 'net_profit',
        title: 'Net Profit',
        icon: 'bi-piggy-bank',
        class: 'profit',
        value: summary.net_profit,
        format: 'currency'
      },
      {
        key: 'total_payables',
        title: 'Total Payables',
        icon: 'bi-wallet2',
        class: 'payables',
        value: summary.total_payables,
        format: 'currency'
      },
      {
        key: 'total_receivables',
        title: 'Total Receivables',
        icon: 'bi-credit-card',
        class: 'receivables',
        value: summary.total_receivables,
        format: 'currency'
      },
      {
        key: 'active_customers',
        title: 'Active Customers',
        icon: 'bi-people',
        class: 'customers',
        value: summary.active_customers,
        format: 'number'
      },
      {
        key: 'inventory_value',
        title: 'Inventory Value',
        icon: 'bi-box-seam',
        class: 'inventory',
        value: summary.inventory_value,
        format: 'currency'
      }
    ];

    cards.forEach(card => {
      const col = document.createElement('div');
      col.className = 'col-6 col-md-4 col-lg-3';
      
      const formattedValue = formatValue(card.value, card.format);
      
      col.innerHTML = `
        <div class="stat-card ${card.class}">
          <div class="stat-card-icon">
            <i class="bi ${card.icon}"></i>
          </div>
          <div class="stat-card-title">${card.title}</div>
          <h3 class="stat-card-value">${formattedValue}</h3>
        </div>
      `;
      
      container.appendChild(col);
    });
  }

  function formatValue(value, format) {
    if (value === null || value === undefined) {
      return format === 'currency' ? 'NPR 0.00' : '0';
    }
    
    if (format === 'currency') {
      const num = parseFloat(value);
      return 'NPR ' + num.toLocaleString('en-NP', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    } else if (format === 'number') {
      return parseInt(value).toLocaleString('en-NP');
    }
    
    return value.toString();
  }

  function renderCharts(series) {
    const labels = series.labels || [];
    const salesData = series.sales || [];
    const expensesData = series.expenses || [];
    
    renderSalesChart(labels, salesData);
    renderExpensesChart(labels, expensesData);
    renderProfitChart(labels, salesData, expensesData);
  }

  function renderSalesChart(labels, salesData) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;

    if (charts.sales) {
      charts.sales.destroy();
    }

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(220, 38, 38, 0.3)');
    gradient.addColorStop(1, 'rgba(220, 38, 38, 0.05)');

    charts.sales = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Sales',
          data: salesData,
          borderColor: '#DC2626',
          backgroundColor: gradient,
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#DC2626',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 2,
          pointHoverBackgroundColor: '#FBBF24',
          pointHoverBorderColor: '#DC2626'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#1F2937',
            titleColor: '#FFFFFF',
            bodyColor: '#FFFFFF',
            borderColor: '#DC2626',
            borderWidth: 2,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function(context) {
                return 'NPR ' + context.parsed.y.toLocaleString('en-NP', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                });
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#E5E7EB',
              drawBorder: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 12
              },
              callback: function(value) {
                return 'NPR ' + value.toLocaleString('en-NP');
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 12
              }
            }
          }
        }
      }
    });
  }

  function renderExpensesChart(labels, expensesData) {
    const ctx = document.getElementById('expensesChart');
    if (!ctx) return;

    if (charts.expenses) {
      charts.expenses.destroy();
    }

    charts.expenses = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Expenses',
          data: expensesData,
          backgroundColor: '#DC2626',
          borderRadius: 8,
          borderSkipped: false,
          hoverBackgroundColor: '#991B1B'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#1F2937',
            titleColor: '#FFFFFF',
            bodyColor: '#FFFFFF',
            borderColor: '#DC2626',
            borderWidth: 2,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function(context) {
                return 'NPR ' + context.parsed.y.toLocaleString('en-NP', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                });
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#E5E7EB',
              drawBorder: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 11
              },
              callback: function(value) {
                return 'NPR ' + value.toLocaleString('en-NP');
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 11
              }
            }
          }
        }
      }
    });
  }

  function renderProfitChart(labels, salesData, expensesData) {
    const ctx = document.getElementById('profitChart');
    if (!ctx) return;

    if (charts.profit) {
      charts.profit.destroy();
    }

    const profitData = labels.map((label, index) => {
      const sales = salesData[index] || 0;
      const expenses = expensesData[index] || 0;
      return sales - expenses;
    });

    const backgroundColors = profitData.map(value => 
      value >= 0 ? '#10B981' : '#DC2626'
    );

    charts.profit = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Profit/Loss',
          data: profitData,
          backgroundColor: backgroundColors,
          borderRadius: 8,
          borderSkipped: false,
          hoverBackgroundColor: profitData.map(value => 
            value >= 0 ? '#059669' : '#991B1B'
          )
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#1F2937',
            titleColor: '#FFFFFF',
            bodyColor: '#FFFFFF',
            borderColor: '#FBBF24',
            borderWidth: 2,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function(context) {
                const value = context.parsed.y;
                const prefix = value >= 0 ? '+' : '';
                return prefix + 'NPR ' + value.toLocaleString('en-NP', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                });
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#E5E7EB',
              drawBorder: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 11
              },
              callback: function(value) {
                return 'NPR ' + value.toLocaleString('en-NP');
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#6B7280',
              font: {
                size: 11
              }
            }
          }
        }
      }
    });
  }

  function showErrorMessage(message) {
    const container = document.getElementById('summary-cards');
    if (container) {
      container.innerHTML = `
        <div class="col-12">
          <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
          </div>
        </div>
      `;
    }
  }

  // Cleanup on page unload
  window.addEventListener('beforeunload', function() {
    Object.values(charts).forEach(chart => {
      if (chart) {
        chart.destroy();
      }
    });
  });
});