/**
 * Enhanced Climate Data Visualization
 * Interactive features: dataset toggles, time range selection, trend analysis, exports
 */

class ClimateVisualization {
  constructor() {
    this.chart = null;
    this.rawData = {};
    this.filteredData = {};
    this.datasets = {
      giss: { 
        label: 'NASA GISTEMP', 
        color: 'rgb(255, 99, 132)',
        visible: true 
      },
      ghcn: { 
        label: 'GHCN Raw (Simple)', 
        color: 'rgb(54, 162, 235)',
        visible: true 
      },
      crutem: { 
        label: 'CRUTEM5', 
        color: 'rgb(75, 192, 192)',
        visible: true 
      }
    };
    
    this.init();
  }

  async init() {
    try {
      this.showLoading(true);
      this.initializeDarkMode();
      this.setupEventListeners();
      await this.loadData();
      this.createChart();
      this.showLoading(false);
      this.updateStatistics();
    } catch (error) {
      console.error('Initialization failed:', error);
      this.showLoading(false);
      this.showStatus(`Initialization failed: ${error.message}`, 'error');
    }
  }

  initializeDarkMode() {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('darkMode');
    
    // Use saved preference, or fall back to system preference
    const shouldUseDark = savedTheme !== null ? savedTheme === 'true' : prefersDark;
    
    this.setDarkMode(shouldUseDark);
    document.getElementById('darkModeToggle').checked = shouldUseDark;
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem('darkMode') === null) {
        this.setDarkMode(e.matches);
        document.getElementById('darkModeToggle').checked = e.matches;
      }
    });
  }

  setDarkMode(isDark) {
    const html = document.documentElement;
    const icon = document.getElementById('darkModeIcon');
    
    if (isDark) {
      html.setAttribute('data-bs-theme', 'dark');
      icon.className = 'fas fa-sun';
    } else {
      html.setAttribute('data-bs-theme', 'light');
      icon.className = 'fas fa-moon';
    }
    
    // Update chart colors if chart exists
    if (this.chart) {
      this.updateChartTheme(isDark);
    }
  }

  updateChartTheme(isDark) {
    const textColor = isDark ? '#ffffff' : '#333333';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
    
    this.chart.options.scales.x.title.color = textColor;
    this.chart.options.scales.x.ticks.color = textColor;
    this.chart.options.scales.x.grid.color = gridColor;
    
    this.chart.options.scales.y.title.color = textColor;
    this.chart.options.scales.y.ticks.color = textColor;
    this.chart.options.scales.y.grid.color = gridColor;
    
    this.chart.options.plugins.title.color = textColor;
    this.chart.options.plugins.legend.labels.color = textColor;
    
    this.chart.update();
  }

  showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const chartCanvas = document.getElementById('myChart');
    
    if (show) {
      loadingIndicator.style.display = 'block';
      chartCanvas.style.display = 'none';
    } else {
      loadingIndicator.style.display = 'none';
      chartCanvas.style.display = 'block';
    }
  }

  showStatus(message, type = 'info') {
    const statusIndicator = document.getElementById('statusIndicator');
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 'alert-info';
    
    statusIndicator.innerHTML = `
      <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    `;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      statusIndicator.innerHTML = '';
    }, 5000);
  }

  async loadData() {
    try {
      const response = await fetch('/data');
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Validate data structure
      if (!data.years || data.years.length === 0) {
        throw new Error('No year data found');
      }
      
      this.rawData = data;
      this.filteredData = { ...data };
      
      // Set initial year range
      if (data.years && data.years.length > 0) {
        const startYear = Math.min(...data.years);
        const endYear = Math.max(...data.years);
        
        document.getElementById('startYear').value = startYear;
        document.getElementById('endYear').value = endYear;
      }
      
      this.showStatus(`Data loaded successfully: ${data.years.length} years`, 'success');
    } catch (error) {
      console.error('Failed to load data:', error);
      this.showStatus(`Failed to load data: ${error.message}`, 'error');
      throw error; // Re-throw to prevent chart creation
    }
  }

  setupEventListeners() {
    // Dataset toggles
    document.getElementById('toggleGISS').addEventListener('change', (e) => {
      this.datasets.giss.visible = e.target.checked;
      this.updateChart();
    });
    
    document.getElementById('toggleGHCN').addEventListener('change', (e) => {
      this.datasets.ghcn.visible = e.target.checked;
      this.updateChart();
    });
    
    document.getElementById('toggleCRUTEM').addEventListener('change', (e) => {
      this.datasets.crutem.visible = e.target.checked;
      this.updateChart();
    });

    // Time range controls
    document.getElementById('applyTimeRange').addEventListener('click', () => {
      this.applyTimeFilter();
    });
    
    document.getElementById('resetTimeRange').addEventListener('click', () => {
      this.resetTimeFilter();
    });

    // Trend analysis controls
    document.getElementById('showDataSeries').addEventListener('change', () => {
      this.updateChart();
    });
    
    document.getElementById('showLinearTrend').addEventListener('change', () => {
      this.updateChart();
    });
    
    document.getElementById('showMovingAverage').addEventListener('change', (e) => {
      const controls = document.getElementById('movingAverageControls');
      controls.style.display = e.target.checked ? 'block' : 'none';
      this.updateChart();
    });
    
    document.getElementById('movingAverageYears').addEventListener('change', () => {
      if (document.getElementById('showMovingAverage').checked) {
        this.updateChart();
      }
    });

    // Dark mode toggle
    document.getElementById('darkModeToggle').addEventListener('change', (e) => {
      this.setDarkMode(e.target.checked);
      localStorage.setItem('darkMode', e.target.checked.toString());
    });

    // Export controls
    document.getElementById('exportCSV').addEventListener('click', () => {
      this.exportToCSV();
    });
    
    document.getElementById('exportPNG').addEventListener('click', () => {
      this.exportToPNG();
    });

    // Advanced analysis
    document.getElementById('advancedAnalysis').addEventListener('click', () => {
      this.showAdvancedAnalysis();
    });
  }

  applyTimeFilter() {
    const startYear = parseInt(document.getElementById('startYear').value);
    const endYear = parseInt(document.getElementById('endYear').value);
    
    if (startYear >= endYear) {
      this.showStatus('Start year must be less than end year', 'error');
      return;
    }
    
    // Filter data by year range
    const filteredYears = [];
    const filteredData = {};
    
    this.rawData.years.forEach((year, index) => {
      if (year >= startYear && year <= endYear) {
        filteredYears.push(year);
        Object.keys(this.datasets).forEach(dataset => {
          if (!filteredData[dataset]) filteredData[dataset] = [];
          filteredData[dataset].push(this.rawData[dataset][index]);
        });
      }
    });
    
    this.filteredData = {
      years: filteredYears,
      ...filteredData
    };
    
    this.updateChart();
    this.updateStatistics();
    this.showStatus(`Filtered to ${startYear}-${endYear}`, 'success');
  }

  resetTimeFilter() {
    this.filteredData = { ...this.rawData };
    
    if (this.rawData.years && this.rawData.years.length > 0) {
      document.getElementById('startYear').value = Math.min(...this.rawData.years);
      document.getElementById('endYear').value = Math.max(...this.rawData.years);
    }
    
    this.updateChart();
    this.updateStatistics();
    this.showStatus('Time filter reset', 'success');
  }

  createChart() {
    const canvas = document.getElementById('myChart');
    const ctx = canvas.getContext('2d');
    
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDark ? '#ffffff' : '#333333';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
    
    const chartData = {
      labels: this.filteredData.years,
      datasets: this.buildChartDatasets()
    };

    this.chart = new Chart(ctx, {
      type: 'line',
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Global Temperature Anomalies (°C relative to 1951-1980)',
            font: { size: 16 },
            color: textColor
          },
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: textColor
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Year',
              color: textColor
            },
            ticks: {
              color: textColor
            },
            grid: {
              display: true,
              color: gridColor
            }
          },
          y: {
            title: {
              display: true,
              text: 'Temperature Anomaly (°C)',
              color: textColor
            },
            ticks: {
              color: textColor
            },
            grid: {
              display: true,
              color: gridColor
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }

  buildChartDatasets() {
    const datasets = [];
    const showDataSeries = document.getElementById('showDataSeries').checked;
    const showMovingAverage = document.getElementById('showMovingAverage').checked;
    
    // Determine line thickness based on what's displayed
    const seriesLineWidth = (showMovingAverage || document.getElementById('showLinearTrend').checked) ? 1.5 : 2;
    const movingAvgLineWidth = 3;
    
    // Add main datasets (only if showDataSeries is checked)
    if (showDataSeries) {
      Object.keys(this.datasets).forEach(key => {
        if (this.datasets[key].visible && this.filteredData[key]) {
          
          datasets.push({
            label: this.datasets[key].label,
            data: this.filteredData[key],
            borderColor: this.datasets[key].color,
            backgroundColor: this.datasets[key].color + '20',
            borderWidth: seriesLineWidth,
            fill: false,
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 4
          });
        }
      });
    }
    
    // Add trend lines
    if (document.getElementById('showLinearTrend').checked) {
      this.addLinearTrendLines(datasets);
    }
    
    if (document.getElementById('showMovingAverage').checked) {
      this.addMovingAverages(datasets);
    }
    
    return datasets;
  }

  addLinearTrendLines(datasets) {
    const trendSlopes = [];
    
    Object.keys(this.datasets).forEach(key => {
      if (this.datasets[key].visible && this.filteredData[key]) {
        const trendResult = this.calculateLinearTrend(this.filteredData.years, this.filteredData[key]);
        if (trendResult && trendResult.data) {
          datasets.push({
            label: `${this.datasets[key].label} Trend`,
            data: trendResult.data,
            borderColor: this.datasets[key].color,
            backgroundColor: this.datasets[key].color,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
            tension: 0
          });
          
          // Store slope information for display
          trendSlopes.push({
            dataset: this.datasets[key].label,
            color: this.datasets[key].color,
            slope: trendResult.slope,
            rSquared: trendResult.rSquared
          });
        }
      }
    });
    
    // Update trend slopes display
    this.updateTrendSlopesDisplay(trendSlopes);
  }

  addMovingAverages(datasets) {
    const years = parseInt(document.getElementById('movingAverageYears').value);
    const movingAvgLineWidth = 3;
    
    Object.keys(this.datasets).forEach(key => {
      if (this.datasets[key].visible && this.filteredData[key]) {
        const movingAvg = this.calculateMovingAverage(this.filteredData[key], years);
        if (movingAvg) {
          datasets.push({
            label: `${this.datasets[key].label} (${years}yr avg)`,
            data: movingAvg,
            borderColor: this.datasets[key].color,
            backgroundColor: this.datasets[key].color + '40',
            borderWidth: movingAvgLineWidth,
            fill: false,
            pointRadius: 0,
            tension: 0.3
          });
        }
      }
    });
  }

  calculateLinearTrend(years, values) {
    // Filter out null values
    const validData = years.map((year, i) => ({ x: year, y: values[i] }))
                           .filter(point => point.y !== null && point.y !== undefined);
    
    if (validData.length < 2) return null;
    
    const n = validData.length;
    const sumX = validData.reduce((sum, point) => sum + point.x, 0);
    const sumY = validData.reduce((sum, point) => sum + point.y, 0);
    const sumXY = validData.reduce((sum, point) => sum + point.x * point.y, 0);
    const sumXX = validData.reduce((sum, point) => sum + point.x * point.x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Calculate R-squared
    const yMean = sumY / n;
    const trendValues = validData.map(point => slope * point.x + intercept);
    const ssRes = validData.reduce((sum, point, i) => sum + Math.pow(point.y - trendValues[i], 2), 0);
    const ssTot = validData.reduce((sum, point) => sum + Math.pow(point.y - yMean, 2), 0);
    const rSquared = ssTot !== 0 ? 1 - (ssRes / ssTot) : 0;
    
    return {
      data: years.map(year => slope * year + intercept),
      slope: slope,
      rSquared: rSquared
    };
  }

  calculateMovingAverage(values, windowSize) {
    if (values.length < windowSize) return null;
    
    const result = [];
    const halfWindow = Math.floor(windowSize / 2);
    
    for (let i = 0; i < values.length; i++) {
      if (i < halfWindow || i >= values.length - halfWindow) {
        result.push(null);
      } else {
        const window = values.slice(i - halfWindow, i + halfWindow + 1);
        const validValues = window.filter(v => v !== null && v !== undefined);
        if (validValues.length > 0) {
          const avg = validValues.reduce((sum, val) => sum + val, 0) / validValues.length;
          result.push(avg);
        } else {
          result.push(null);
        }
      }
    }
    
    return result;
  }

  updateChart() {
    if (this.chart) {
      this.chart.data.labels = this.filteredData.years;
      this.chart.data.datasets = this.buildChartDatasets();
      this.chart.update();
      this.updateStatistics();
      
      // Hide trend slopes if linear trend is not shown
      const showLinearTrend = document.getElementById('showLinearTrend').checked;
      const trendSlopesDisplay = document.getElementById('trendSlopesDisplay');
      if (!showLinearTrend) {
        trendSlopesDisplay.style.display = 'none';
      }
    }
  }

  updateTrendSlopesDisplay(trendSlopes) {
    const trendSlopesDisplay = document.getElementById('trendSlopesDisplay');
    const trendSlopesContent = document.getElementById('trendSlopesContent');
    
    if (trendSlopes.length === 0) {
      trendSlopesDisplay.style.display = 'none';
      return;
    }
    
    let html = '<div class="row">';
    
    trendSlopes.forEach(trend => {
      const slopePerDecade = trend.slope * 10;
      
      html += `
        <div class="col-md-4 mb-2">
          <div class="border rounded p-2">
            <strong style="color: ${trend.color}">${trend.dataset}</strong><br>
            <small>
              <strong>${slopePerDecade > 0 ? '+' : ''}${slopePerDecade.toFixed(2)}°C/decade</strong><br>
              <span class="text-muted">R² = ${trend.rSquared.toFixed(4)}</span>
            </small>
          </div>
        </div>
      `;
    });
    
    html += '</div>';
    trendSlopesContent.innerHTML = html;
    trendSlopesDisplay.style.display = 'block';
  }

  updateStatistics() {
    const statsContent = document.getElementById('statisticsContent');
    const advancedButton = document.getElementById('advancedAnalysis');
    const visibleDatasets = Object.keys(this.datasets).filter(key => this.datasets[key].visible);
    
    if (visibleDatasets.length === 0 || !this.filteredData.years) {
      statsContent.innerHTML = '<small class="text-muted">Select datasets to view statistics</small>';
      advancedButton.style.display = 'none';
      return;
    }
    
    let html = '';
    
    visibleDatasets.forEach(key => {
      if (this.filteredData[key]) {
        const stats = this.calculateStatistics(this.filteredData[key]);
        html += `
          <div class="mb-2">
            <strong style="color: ${this.datasets[key].color}">${this.datasets[key].label}</strong><br>
            <small>
              Mean: ${stats.mean}°C<br>
              Std Dev: ${stats.stdDev}°C<br>
              Range: ${stats.min}°C to ${stats.max}°C
            </small>
          </div>
        `;
      }
    });
    
    statsContent.innerHTML = html;
    
    // Show advanced analysis button if multiple datasets are visible
    if (visibleDatasets.length > 1) {
      advancedButton.style.display = 'block';
    } else {
      advancedButton.style.display = 'none';
    }
  }

  calculateStatistics(values) {
    const validValues = values.filter(v => v !== null && v !== undefined);
    
    if (validValues.length === 0) {
      return { mean: 'N/A', stdDev: 'N/A', min: 'N/A', max: 'N/A' };
    }
    
    const mean = validValues.reduce((sum, val) => sum + val, 0) / validValues.length;
    const variance = validValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / validValues.length;
    const stdDev = Math.sqrt(variance);
    const min = Math.min(...validValues);
    const max = Math.max(...validValues);
    
    return {
      mean: mean.toFixed(3),
      stdDev: stdDev.toFixed(3),
      min: min.toFixed(3),
      max: max.toFixed(3)
    };
  }

  exportToCSV() {
    const visibleDatasets = Object.keys(this.datasets).filter(key => this.datasets[key].visible);
    
    if (visibleDatasets.length === 0) {
      this.showStatus('No datasets selected for export', 'error');
      return;
    }
    
    let csv = 'Year';
    visibleDatasets.forEach(key => {
      csv += `,${this.datasets[key].label}`;
    });
    csv += '\n';
    
    this.filteredData.years.forEach((year, index) => {
      csv += year;
      visibleDatasets.forEach(key => {
        const value = this.filteredData[key][index];
        csv += `,${value !== null && value !== undefined ? value : ''}`;
      });
      csv += '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `climate_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    this.showStatus('CSV exported successfully', 'success');
  }

  exportToPNG() {
    if (this.chart) {
      const url = this.chart.toBase64Image();
      const a = document.createElement('a');
      a.href = url;
      a.download = `climate_chart_${new Date().toISOString().split('T')[0]}.png`;
      a.click();
      
      this.showStatus('Chart exported as PNG', 'success');
    }
  }

  async showAdvancedAnalysis() {
    const modal = new bootstrap.Modal(document.getElementById('advancedStatsModal'));
    const modalContent = document.getElementById('advancedStatsContent');
    
    // Show loading spinner
    modalContent.innerHTML = `
      <div class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading analysis...</span>
        </div>
        <p class="mt-2">Calculating advanced statistics...</p>
      </div>
    `;
    
    modal.show();
    
    try {
      const visibleDatasets = Object.keys(this.datasets).filter(key => this.datasets[key].visible);
      const startYear = this.filteredData.years ? Math.min(...this.filteredData.years) : null;
      const endYear = this.filteredData.years ? Math.max(...this.filteredData.years) : null;
      
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          datasets: visibleDatasets,
          start_year: startYear,
          end_year: endYear
        })
      });
      
      const analysis = await response.json();
      
      if (analysis.error) {
        throw new Error(analysis.error);
      }
      
      this.displayAdvancedAnalysis(analysis);
      
    } catch (error) {
      modalContent.innerHTML = `
        <div class="alert alert-danger">
          <h6><i class="fas fa-exclamation-triangle"></i> Analysis Error</h6>
          <p>${error.message}</p>
        </div>
      `;
    }
  }
  
  displayAdvancedAnalysis(analysis) {
    const modalContent = document.getElementById('advancedStatsContent');
    
    let html = `
      <div class="row">
        <div class="col-12">
          <h6><i class="fas fa-info-circle"></i> Analysis Period: ${analysis.period} (${analysis.total_years} years)</h6>
        </div>
      </div>
    `;
    
    // Correlation Matrix
    if (analysis.correlations && Object.keys(analysis.correlations).length > 0) {
      html += `
        <div class="row mt-3">
          <div class="col-12">
            <h6><i class="fas fa-link"></i> Dataset Correlations</h6>
            <div class="table-responsive">
              <table class="table table-sm table-bordered">
                <thead>
                  <tr>
                    <th>Dataset Pair</th>
                    <th>Correlation</th>
                    <th>P-value</th>
                    <th>Samples</th>
                  </tr>
                </thead>
                <tbody>
      `;
      
      Object.keys(analysis.correlations).forEach(dataset1 => {
        Object.keys(analysis.correlations[dataset1]).forEach(dataset2 => {
          const corr = analysis.correlations[dataset1][dataset2];
          const corrValue = corr.correlation !== null ? corr.correlation.toFixed(4) : 'N/A';
          const pValue = corr.p_value !== null ? corr.p_value.toFixed(6) : 'N/A';
          
          html += `
            <tr>
              <td><strong>${this.datasets[dataset1].label}</strong> vs <strong>${this.datasets[dataset2].label}</strong></td>
              <td><span class="badge ${this.getCorrelationBadgeClass(corr.correlation)}">${corrValue}</span></td>
              <td>${pValue}</td>
              <td>${corr.n_samples}</td>
            </tr>
          `;
        });
      });
      
      html += `
                </tbody>
              </table>
            </div>
            <small class="text-muted">
              Correlation: -1 = perfect negative, 0 = no correlation, +1 = perfect positive<br>
              P-value: < 0.05 typically indicates statistical significance
            </small>
          </div>
        </div>
      `;
    }
    
    // Trend Analysis
    if (analysis.trends && Object.keys(analysis.trends).length > 0) {
      html += `
        <div class="row mt-4">
          <div class="col-12">
            <h6><i class="fas fa-chart-line"></i> Linear Trend Analysis</h6>
            <div class="table-responsive">
              <table class="table table-sm table-striped">
                <thead>
                  <tr>
                    <th>Dataset</th>
                    <th>Trend (°C/decade)</th>
                    <th>R-squared</th>
                    <th>Period</th>
                    <th>Samples</th>
                  </tr>
                </thead>
                <tbody>
      `;
      
      Object.keys(analysis.trends).forEach(dataset => {
        const trend = analysis.trends[dataset];
        html += `
          <tr>
            <td><strong style="color: ${this.datasets[dataset].color}">${this.datasets[dataset].label}</strong></td>
            <td><span class="badge ${this.getTrendBadgeClass(trend.slope_per_decade)}">${trend.slope_per_decade > 0 ? '+' : ''}${trend.slope_per_decade}°C</span></td>
            <td>${trend.r_squared}</td>
            <td>${trend.period}</td>
            <td>${trend.n_samples}</td>
          </tr>
        `;
      });
      
      html += `
                </tbody>
              </table>
            </div>
            <small class="text-muted">
              Trend shows temperature change per decade. R-squared indicates how well the linear trend fits the data (0-1).
            </small>
          </div>
        </div>
      `;
    }
    
    modalContent.innerHTML = html;
  }
  
  getCorrelationBadgeClass(correlation) {
    if (correlation === null) return 'bg-secondary';
    const abs = Math.abs(correlation);
    if (abs >= 0.9) return 'bg-success';
    if (abs >= 0.7) return 'bg-info';
    if (abs >= 0.5) return 'bg-warning';
    return 'bg-light text-dark';
  }
  
  getTrendBadgeClass(slope) {
    if (slope > 0.15) return 'bg-danger';
    if (slope > 0.05) return 'bg-warning';
    if (slope > -0.05) return 'bg-info';
    return 'bg-primary';
  }
}

// Initialize the visualization when the page loads
document.addEventListener('DOMContentLoaded', () => {
  new ClimateVisualization();
});