/**
 * Background Service Worker
 * Handles timers, notifications, and sync
 */

const API_URL = 'http://localhost:8000/api';
let clockedInState = {
  isClockedIn: false,
  startTime: null,
  employeeId: null
};

// Initialize
chrome.runtime.onInstalled.addListener(() => {
  console.log('WorkingTracker Extension installed');
  
  // Load saved state
  chrome.storage.local.get(['clockState'], (result) => {
    if (result.clockState) {
      clockedInState = result.clockState;
    }
  });
  
  // Set up periodic sync alarm (every minute)
  chrome.alarms.create('sync', { periodInMinutes: 1 });
});

// Handle alarm for elapsed time updates
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'sync' && clockedInState.isClockedIn) {
    updateElapsedTime();
  }
});

// API Helper
async function apiRequest(endpoint, options = {}) {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

async function getAuthToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken'], (result) => {
      resolve(result.authToken);
    });
  });
}

// Clock In
async function clockIn() {
  try {
    const response = await apiRequest('/time/clock-in', {
      method: 'POST',
      body: JSON.stringify({ location: 'Browser Extension' })
    });
    
    clockedInState = {
      isClockedIn: true,
      startTime: new Date().toISOString(),
      employeeId: response.employee_id
    };
    
    await saveState();
    
    // Show notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Clocked In',
      message: 'You are now clocked in!'
    });
    
    return response;
  } catch (error) {
    console.error('Clock in failed:', error);
    throw error;
  }
}

// Clock Out
async function clockOut() {
  try {
    const response = await apiRequest('/time/clock-out', {
      method: 'POST',
      body: JSON.stringify({ location: 'Browser Extension' })
    });
    
    const duration = getElapsedTime();
    
    clockedInState = {
      isClockedIn: false,
      startTime: null,
      employeeId: null
    };
    
    await saveState();
    
    // Show notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Clocked Out',
      message: `Total time: ${duration}`
    });
    
    return response;
  } catch (error) {
    console.error('Clock out failed:', error);
    throw error;
  }
}

function getElapsedTime() {
  if (!clockedInState.isClockedIn || !clockedInState.startTime) {
    return '00:00:00';
  }
  
  const start = new Date(clockedInState.startTime);
  const now = new Date();
  const elapsed = now - start;
  
  const hours = Math.floor(elapsed / 1000 / 60 / 60);
  const minutes = Math.floor((elapsed / 1000 / 60) % 60);
  const seconds = Math.floor((elapsed / 1000) % 60);
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function updateElapsedTime() {
  // Send message to popup to update display
  chrome.runtime.sendMessage({
    type: 'ELAPSED_UPDATE',
    elapsed: getElapsedTime()
  });
}

async function saveState() {
  await chrome.storage.local.set({ clockState: clockedInState });
}

// Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'CLOCK_IN') {
    clockIn().then(sendResponse).catch((error) => sendResponse({ error: error.message }));
    return true;
  }
  
  if (request.type === 'CLOCK_OUT') {
    clockOut().then(sendResponse).catch((error) => sendResponse({ error: error.message }));
    return true;
  }
  
  if (request.type === 'GET_STATE') {
    sendResponse({
      state: clockedInState,
      elapsed: getElapsedTime()
    });
    return true;
  }
  
  if (request.type === 'SET_TOKEN') {
    chrome.storage.local.set({ authToken: request.token });
    sendResponse({ success: true });
    return true;
  }
});
