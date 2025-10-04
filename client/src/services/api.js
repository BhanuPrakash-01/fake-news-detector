import axios from "axios";

// Base API URL - use environment variable or default to proxy
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor (for adding auth tokens later if needed)
apiClient.interceptors.request.use(
  (config) => {
    // You can add authorization headers here
    // config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for handling errors globally)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error("API Error:", error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error("Network Error:", error.request);
    } else {
      // Something else happened
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Analyze text for fake news detection
 * @param {string} text - The news text to analyze
 * @returns {Promise} - Analysis results
 */
export const analyzeText = async (text) => {
  try {
    const response = await apiClient.post("/analyze", { text });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
        "Failed to analyze text. Please try again."
    );
  }
};

/**
 * Health check endpoint
 * @returns {Promise} - Server health status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    throw new Error("Server is not responding");
  }
};

export default apiClient;
