// Main application logic
document.addEventListener("DOMContentLoaded", function () {
  // Set default values for year and month
  setDefaultValues();

  // Set up event listeners
  setupEventListeners();

  // Initial data load
  loadStockData();
});

// Set default values for selectors
function setDefaultValues() {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1; // JavaScript months are 0-indexed

  // Set year dropdown to current year if available
  const yearSelect = document.getElementById("yearSelect");
  const yearOptions = Array.from(yearSelect.options).map((opt) => opt.value);
  if (yearOptions.includes(currentYear.toString())) {
    yearSelect.value = currentYear.toString();
  } else {
    yearSelect.value = CONFIG.defaultYear;
  }

  // Set month dropdown to current month
  const monthSelect = document.getElementById("monthSelect");
  monthSelect.value = currentMonth.toString();

  // Set default stock
  document.getElementById("stockSymbol").value = CONFIG.defaultStock;
}

// Set up event listeners
function setupEventListeners() {
  // Update button click
  document
    .getElementById("updateChart")
    .addEventListener("click", loadStockData);
}

// Load stock data based on selected parameters
async function loadStockData() {
  const symbol = document.getElementById("stockSymbol").value;
  const year = document.getElementById("yearSelect").value;
  const month = document.getElementById("monthSelect").value;

  try {
    // Clear any previous error messages
    clearErrorMessages();

    // Load stock price data
    const priceData = await api.getStockTimeSeriesByPartition(
      symbol,
      year,
      month
    );
    if (priceData.data.length === 0) {
      const symbolDisplay = symbol === "ANY" ? "Market Average" : symbol;
      showError(
        `No price data available for ${symbolDisplay} in ${getMonthName(
          month
        )} ${year}`
      );
      return;
    }
    charts.renderStockChart("stockPriceChart", priceData);

    // Load volume data
    const volumeData = await api.getVolumeAnalysisByPartition(
      symbol,
      year,
      month
    );
    charts.renderVolumeChart("volumeChart", volumeData);
  } catch (error) {
    showError(`Error loading stock data: ${error.message}`);
  }
}

// Display an error message
function showError(message) {
  clearErrorMessages();

  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.innerHTML = `<h4>Error</h4><p>${message}</p>`;

  // Insert after the filters
  const filters = document.querySelector(".filters");
  filters.parentNode.insertBefore(errorDiv, filters.nextSibling);
}

// Clear all error messages
function clearErrorMessages() {
  const errorMessages = document.querySelectorAll(".error-message");
  errorMessages.forEach((el) => el.remove());
}

// Helper function to get month name
function getMonthName(monthNumber) {
  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  return monthNames[parseInt(monthNumber) - 1];
}
