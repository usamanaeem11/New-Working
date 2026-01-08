/**
 * Popup UI Logic
 */

let state = {
  isAuthenticated: false,
  isClockedIn: false,
  elapsed: '00:00:00'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  
  // Update elapsed time every second
  setInterval(updateElapsed, 1000);
});

async function checkAuth() {
  const result = await chrome.storage.local.get(['authToken']);
  
  if (result.authToken) {
    state.isAuthenticated = true;
    loadState();
    renderMain();
  } else {
    renderLogin();
  }
}

function loadState() {
  chrome.runtime.sendMessage({ type: 'GET_STATE' }, (response) => {
    if (response && response.state) {
      state.isClockedIn = response.state.isClockedIn;
      state.elapsed = response.elapsed;
      renderMain();
    }
  });
}

function updateElapsed() {
  if (state.isClockedIn) {
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, (response) => {
      if (response && response.elapsed) {
        state.elapsed = response.elapsed;
        const timerEl = document.getElementById('timer');
        if (timerEl) {
          timerEl.textContent = state.elapsed;
        }
      }
    });
  }
}

function renderLogin() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="header">
      <h1>WorkingTracker</h1>
      <p>Sign in to start tracking</p>
    </div>
    <div class="login-section">
      <input type="email" id="email" placeholder="Email">
      <input type="password" id="password" placeholder="Password">
      <button class="button button-login" id="login-btn">Sign In</button>
    </div>
    <div id="message"></div>
  `;
  
  document.getElementById('login-btn').addEventListener('click', handleLogin);
}

async function handleLogin() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  const messageEl = document.getElementById('message');
  messageEl.textContent = 'Signing in...';
  messageEl.className = 'message';
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // Save token
    await chrome.runtime.sendMessage({
      type: 'SET_TOKEN',
      token: data.access_token
    });
    
    state.isAuthenticated = true;
    loadState();
    renderMain();
  } catch (error) {
    messageEl.textContent = 'Login failed. Please check credentials.';
  }
}

function renderMain() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="header">
      <h1>WorkingTracker</h1>
      <p>Time Tracking Extension</p>
    </div>
    <div class="status">
      <div>
        <span class="status-indicator ${state.isClockedIn ? '' : 'inactive'}"></span>
        <span>${state.isClockedIn ? 'Clocked In' : 'Not Clocked In'}</span>
      </div>
      ${state.isClockedIn ? `<div class="timer" id="timer">${state.elapsed}</div>` : ''}
    </div>
    <button class="button ${state.isClockedIn ? 'button-clock-out' : 'button-clock-in'}" id="clock-btn">
      ${state.isClockedIn ? 'Clock Out' : 'Clock In'}
    </button>
    <div id="message"></div>
  `;
  
  document.getElementById('clock-btn').addEventListener('click', handleClock);
}

function handleClock() {
  const messageEl = document.getElementById('message');
  messageEl.textContent = state.isClockedIn ? 'Clocking out...' : 'Clocking in...';
  messageEl.className = 'message';
  
  const type = state.isClockedIn ? 'CLOCK_OUT' : 'CLOCK_IN';
  
  chrome.runtime.sendMessage({ type }, (response) => {
    if (response && !response.error) {
      state.isClockedIn = !state.isClockedIn;
      renderMain();
    } else {
      messageEl.textContent = 'Action failed. Please try again.';
    }
  });
}
