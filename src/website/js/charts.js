// Chart rendering utilities
class ChartService {
  constructor(config) {
    this.colors = config.colors;
  }

  // Render stock price history chart
  renderStockChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext("2d");

    // Extract dates and prices from the data
    const dates = data.data.map((item) => item.date);
    const prices = data.data.map((item) => parseFloat(item.close));

    // Destroy existing chart if it exists
    if (window.stockChart && typeof window.stockChart.destroy === "function") {
      window.stockChart.destroy();
    }

    // Create new chart
    window.stockChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Close Price",
            data: prices,
            borderColor: this.colors.primary,
            backgroundColor: "rgba(26, 35, 126, 0.1)",
            borderWidth: 2,
            tension: 0.1,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${data.data[0]?.symbol || "Stock"} Price History`,
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Date",
            },
          },
          y: {
            title: {
              display: true,
              text: "Price ($)",
            },
            beginAtZero: false,
          },
        },
      },
    });
  }

  // Render volume chart
  renderVolumeChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext("2d");

    // Extract dates and volumes from the data
    const dates = data.data.map((item) => item.date);
    const volumes = data.data.map((item) => parseInt(item.volume));

    // Destroy existing chart if it exists
    if (
      window.volumeChart &&
      typeof window.volumeChart.destroy === "function"
    ) {
      window.volumeChart.destroy();
    }

    // Create new chart
    window.volumeChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Trading Volume",
            data: volumes,
            backgroundColor: this.colors.volume,
            borderColor: this.colors.primary,
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${data.data[0]?.symbol || "Stock"} Trading Volume`,
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Date",
            },
          },
          y: {
            title: {
              display: true,
              text: "Volume",
            },
            beginAtZero: true,
          },
        },
      },
    });
  }
}

// Create global chart service instance
const charts = new ChartService(CONFIG);
