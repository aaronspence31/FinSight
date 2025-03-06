// API service for interacting with the Athena endpoint
class APIService {
  constructor(config) {
    this.apiUrl = config.apiUrl;
  }

  // Send a query to the API Gateway Lambda function
  async queryAthena(queryType, params = {}) {
    try {
      const connectionStatus = document.getElementById("connection-status");
      connectionStatus.textContent = "Querying...";
      connectionStatus.className = "status";

      const response = await fetch(this.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          queryType: queryType,
          params: params,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `API request failed: ${response.status} - ${errorText}`
        );
      }

      const data = await response.json();

      connectionStatus.textContent = "Connected";
      connectionStatus.className = "status connected";

      return data;
    } catch (error) {
      console.error("Error querying Athena:", error);

      const connectionStatus = document.getElementById("connection-status");
      connectionStatus.textContent = `Error: ${error.message}`;
      connectionStatus.className = "status error";

      throw error;
    }
  }

  // Get stock time series data by year and month (using partitions)
  async getStockTimeSeriesByPartition(symbol, year, month) {
    // If symbol is ANY, use a different query type
    if (symbol === "ANY") {
      return this.queryAthena("allStocksTimeSeriesByPartition", {
        year: year,
        month: month,
      });
    }

    return this.queryAthena("stockTimeSeriesByPartition", {
      symbol: symbol,
      year: year,
      month: month,
    });
  }

  // Get volume analysis data by year and month
  async getVolumeAnalysisByPartition(symbol, year, month) {
    // If symbol is ANY, use a different query type
    if (symbol === "ANY") {
      return this.queryAthena("allStocksVolumeAnalysisByPartition", {
        year: year,
        month: month,
      });
    }

    return this.queryAthena("volumeAnalysisByPartition", {
      symbol: symbol,
      year: year,
      month: month,
    });
  }
}

// Create global API service instance
const api = new APIService(CONFIG);
