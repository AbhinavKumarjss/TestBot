// Configuration for different environments
const config = {
  development: {
    wsUrl: "ws://localhost:8000/api/user/ws",
    apiBase: "http://localhost:8000/api"
  },
  production: {
    wsUrl: "wss://yourdomain.com/api/user/ws", // Replace with your actual domain
    apiBase: "https://yourdomain.com/api" // Replace with your actual domain
  }
};

// Get current environment
const environment = import.meta.env.MODE || 'development';

// Export the appropriate configuration
export const currentConfig = config[environment as keyof typeof config] || config.development;

// For backward compatibility
export const wsUrl = currentConfig.wsUrl;
export const apiBase = currentConfig.apiBase; 