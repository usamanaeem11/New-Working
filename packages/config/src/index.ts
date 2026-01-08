export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || process.env.EXPO_PUBLIC_API_URL || process.env.ELECTRON_API_URL || 'http://localhost:8000',
    timeout: 30000,
  },
  app: {
    name: 'Working Tracker',
    version: '3.0.0',
  },
  features: {
    enableAI: process.env.ENABLE_AI_FEATURES === 'true',
    enableAdvancedML: process.env.ENABLE_ADVANCED_ML === 'true',
    enableAnalytics: process.env.ENABLE_ANALYTICS === 'true',
  },
};

export default config;
