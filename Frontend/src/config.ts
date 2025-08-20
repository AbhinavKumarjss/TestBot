// Configuration for different environments
const config = {
  development: {
    wsUrl: "ws://localhost:8000/api/user/ws",
    apiBase: "http://localhost:8000/api"
  },
  production: {
    // Use same domain as the app (served by Nginx) and proxy to backend via /api
    get wsUrl() {
      const wsProto = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws';
      const host = typeof window !== 'undefined' ? window.location.host : '';
      return `${wsProto}://${host}/api/user/ws`;
    },
    get apiBase() {
      const origin = typeof window !== 'undefined' ? window.location.origin : '';
      return `${origin}/api`;
    }
  }
};

// Get current environment
const environment = import.meta.env.MODE || 'development';

// Export the appropriate configuration
export const currentConfig = config[environment as keyof typeof config] || config.development;

// For backward compatibility
export const wsUrl = (currentConfig as any).wsUrl instanceof Function ? (currentConfig as any).wsUrl() : (currentConfig as any).wsUrl;
export const apiBase = (currentConfig as any).apiBase instanceof Function ? (currentConfig as any).apiBase() : (currentConfig as any).apiBase; 