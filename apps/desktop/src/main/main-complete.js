// Complete Desktop Tracker Application
// Electron-based with AI analysis, auto-categorization, and privacy features

const { app, BrowserWindow, Tray, Menu, ipcMain, screen, desktopCapturer, powerMonitor } = require('electron');
const path = require('path');
const screenshot = require('screenshot-desktop');
const activeWin = require('active-win');
const axios = require('axios');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');
const sharp = require('sharp');
const Tesseract = require('tesseract.js');
const FormData = require('form-data');
const fs = require('fs').promises;

// Configuration
const store = new Store();
const API_URL = process.env.API_URL || 'https://api.workingtracker.com';
let mainWindow = null;
let tray = null;
let screenshotInterval = null;
let activityInterval = null;
let isTracking = false;
let offlineQueue = [];

// ============================================
// APP INITIALIZATION
// ============================================

app.whenReady().then(() => {
    createWindow();
    createTray();
    setupAutoUpdater();
    setupPowerMonitoring();
    checkAuthentication();
});

app.on('window-all-closed', (e) => {
    e.preventDefault(); // Keep running in background
});

// ============================================
// WINDOW MANAGEMENT
// ============================================

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 600,
        show: false,
        frame: false,
        resizable: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('index.html');
    
    // Position window in bottom right
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    mainWindow.setPosition(width - 420, height - 620);
}

function createTray() {
    tray = new Tray(path.join(__dirname, 'assets', 'icon.png'));
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'WorkingTracker',
            enabled: false
        },
        { type: 'separator' },
        {
            label: 'Start Tracking',
            id: 'start',
            click: () => startTracking(),
            enabled: !isTracking
        },
        {
            label: 'Stop Tracking',
            id: 'stop',
            click: () => stopTracking(),
            enabled: isTracking
        },
        { type: 'separator' },
        {
            label: 'Dashboard',
            click: () => mainWindow.show()
        },
        {
            label: 'Settings',
            click: () => showSettings()
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);
    
    tray.setContextMenu(contextMenu);
    tray.setToolTip('WorkingTracker - Not tracking');
    
    tray.on('click', () => {
        mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    });
}

// ============================================
// AUTHENTICATION
// ============================================

async function checkAuthentication() {
    const token = store.get('authToken');
    const user = store.get('user');
    
    if (!token || !user) {
        mainWindow.webContents.send('auth-required');
        mainWindow.show();
        return false;
    }
    
    try {
        // Verify token
        const response = await axios.get(`${API_URL}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        store.set('user', response.data.user);
        mainWindow.webContents.send('auth-success', response.data.user);
        
        // Load settings
        loadUserSettings(response.data.user);
        
        return true;
    } catch (error) {
        store.delete('authToken');
        store.delete('user');
        mainWindow.webContents.send('auth-required');
        mainWindow.show();
        return false;
    }
}

ipcMain.handle('login', async (event, { email, password }) => {
    try {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
            email,
            password
        });
        
        store.set('authToken', response.data.token);
        store.set('user', response.data.user);
        
        loadUserSettings(response.data.user);
        
        return { success: true, user: response.data.user };
    } catch (error) {
        return { 
            success: false, 
            error: error.response?.data?.detail || 'Login failed' 
        };
    }
});

ipcMain.handle('logout', async () => {
    stopTracking();
    store.delete('authToken');
    store.delete('user');
    mainWindow.webContents.send('auth-required');
    mainWindow.show();
});

// ============================================
// TRACKING MANAGEMENT
// ============================================

async function startTracking() {
    if (isTracking) return;
    
    const user = store.get('user');
    if (!user) {
        mainWindow.webContents.send('error', 'Please login first');
        return;
    }
    
    isTracking = true;
    
    // Update tray
    tray.setToolTip('WorkingTracker - Tracking');
    updateTrayMenu();
    
    // Start time entry
    const timeEntry = await createTimeEntry();
    store.set('currentTimeEntry', timeEntry);
    
    // Start screenshot capture
    const screenshotIntervalMs = (user.screenshot_interval || 600) * 1000;
    screenshotInterval = setInterval(() => {
        captureAndProcessScreenshot();
    }, screenshotIntervalMs);
    
    // Start activity monitoring
    activityInterval = setInterval(() => {
        captureActivity();
    }, 10000); // Every 10 seconds
    
    mainWindow.webContents.send('tracking-started', timeEntry);
}

async function stopTracking() {
    if (!isTracking) return;
    
    isTracking = false;
    
    // Clear intervals
    if (screenshotInterval) clearInterval(screenshotInterval);
    if (activityInterval) clearInterval(activityInterval);
    
    // Update tray
    tray.setToolTip('WorkingTracker - Not tracking');
    updateTrayMenu();
    
    // End time entry
    const timeEntry = store.get('currentTimeEntry');
    if (timeEntry) {
        await endTimeEntry(timeEntry.id);
        store.delete('currentTimeEntry');
    }
    
    // Process offline queue
    await processOfflineQueue();
    
    mainWindow.webContents.send('tracking-stopped');
}

function updateTrayMenu() {
    const contextMenu = Menu.buildFromTemplate([
        { label: 'WorkingTracker', enabled: false },
        { type: 'separator' },
        {
            label: 'Start Tracking',
            click: () => startTracking(),
            enabled: !isTracking
        },
        {
            label: 'Stop Tracking',
            click: () => stopTracking(),
            enabled: isTracking
        },
        { type: 'separator' },
        { label: 'Dashboard', click: () => mainWindow.show() },
        { label: 'Settings', click: () => showSettings() },
        { type: 'separator' },
        { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); }}
    ]);
    tray.setContextMenu(contextMenu);
}

// ============================================
// SCREENSHOT CAPTURE & AI ANALYSIS
// ============================================

async function captureAndProcessScreenshot() {
    try {
        const user = store.get('user');
        if (!user.screenshot_enabled) return;
        
        // Capture screenshot
        const img = await screenshot({ format: 'png' });
        
        // Process with AI and privacy features
        const processed = await processScreenshot(img, user);
        
        // Upload to server
        await uploadScreenshot(processed);
        
    } catch (error) {
        console.error('Screenshot capture error:', error);
        
        // Add to offline queue
        offlineQueue.push({
            type: 'screenshot',
            timestamp: new Date().toISOString(),
            error: error.message
        });
    }
}

async function processScreenshot(buffer, user) {
    const settings = store.get('screenshotSettings', {});
    
    // Step 1: Compress image
    let processed = await sharp(buffer)
        .resize(1920, 1080, { fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: settings.quality || 80 })
        .toBuffer();
    
    // Step 2: Privacy blur (if enabled)
    if (settings.privacyBlur) {
        processed = await applyPrivacyBlur(processed, settings.blurRegions);
    }
    
    // Step 3: OCR (if enabled)
    let ocrText = null;
    if (settings.enableOCR) {
        ocrText = await performOCR(processed);
    }
    
    // Step 4: AI Analysis (if enabled)
    let aiAnalysis = null;
    if (user.ai_enabled && settings.enableAI) {
        aiAnalysis = await analyzeScreenshotWithAI(processed, ocrText);
    }
    
    // Step 5: Detect apps/URLs
    const detectedApps = await detectApps();
    const detectedURLs = await detectURLs();
    
    return {
        image: processed,
        ocrText,
        aiAnalysis,
        detectedApps,
        detectedURLs,
        capturedAt: new Date().toISOString()
    };
}

async function applyPrivacyBlur(buffer, blurRegions = []) {
    // Default blur regions (can be customized)
    const defaultRegions = [
        { top: 0, left: 0, width: 200, height: 60 }, // Top-left (file paths)
        // Add more regions as needed
    ];
    
    const regions = blurRegions.length > 0 ? blurRegions : defaultRegions;
    
    let image = sharp(buffer);
    
    for (const region of regions) {
        // Create blurred overlay
        const blurred = await sharp(buffer)
            .extract(region)
            .blur(20)
            .toBuffer();
        
        // Composite back
        image = image.composite([{
            input: blurred,
            top: region.top,
            left: region.left
        }]);
    }
    
    return await image.toBuffer();
}

async function performOCR(buffer) {
    try {
        const { data: { text } } = await Tesseract.recognize(buffer, 'eng', {
            logger: () => {} // Disable logging
        });
        return text;
    } catch (error) {
        console.error('OCR error:', error);
        return null;
    }
}

async function analyzeScreenshotWithAI(buffer, ocrText) {
    try {
        const token = store.get('authToken');
        
        // Prepare context
        const context = {
            ocr_text: ocrText?.substring(0, 500), // Limit text
            timestamp: new Date().toISOString()
        };
        
        // Call AI API
        const response = await axios.post(
            `${API_URL}/api/ai/analyze-screenshot`,
            context,
            { headers: { Authorization: `Bearer ${token}` }}
        );
        
        return response.data;
    } catch (error) {
        console.error('AI analysis error:', error);
        return null;
    }
}

async function detectApps() {
    try {
        const win = await activeWin();
        return win ? [{
            app: win.owner.name,
            title: win.title,
            bounds: win.bounds
        }] : [];
    } catch (error) {
        return [];
    }
}

async function detectURLs() {
    // TODO: Implement browser detection
    // This would require browser-specific extensions or APIs
    return [];
}

// ============================================
// ACTIVITY MONITORING
// ============================================

async function captureActivity() {
    try {
        const win = await activeWin();
        if (!win) return;
        
        const token = store.get('authToken');
        const timeEntry = store.get('currentTimeEntry');
        
        // Categorize activity
        const category = await categorizeActivity(win.owner.name, win.title);
        
        const activity = {
            time_entry_id: timeEntry?.id,
            app_name: win.owner.name,
            window_title: win.title,
            category: category.category,
            activity_type: category.activity_type,
            productivity_score: category.productivity_score,
            started_at: new Date().toISOString(),
            duration_seconds: 10
        };
        
        // Send to server
        await axios.post(
            `${API_URL}/api/activities`,
            activity,
            { headers: { Authorization: `Bearer ${token}` }}
        );
        
    } catch (error) {
        console.error('Activity capture error:', error);
    }
}

async function categorizeActivity(appName, windowTitle) {
    try {
        const token = store.get('authToken');
        
        const response = await axios.post(
            `${API_URL}/api/ai/categorize/activity`,
            { app_name: appName, window_title: windowTitle },
            { headers: { Authorization: `Bearer ${token}` }}
        );
        
        return response.data;
    } catch (error) {
        // Fallback to basic categorization
        return basicCategorization(appName);
    }
}

function basicCategorization(appName) {
    const productiveApps = ['vscode', 'sublime', 'pycharm', 'intellij', 'terminal', 'cmd'];
    const distractingApps = ['facebook', 'twitter', 'youtube', 'netflix', 'spotify'];
    
    const appLower = appName.toLowerCase();
    
    if (productiveApps.some(app => appLower.includes(app))) {
        return {
            category: 'Development',
            activity_type: 'productive',
            productivity_score: 90
        };
    } else if (distractingApps.some(app => appLower.includes(app))) {
        return {
            category: 'Entertainment',
            activity_type: 'distracting',
            productivity_score: 20
        };
    } else {
        return {
            category: 'General',
            activity_type: 'neutral',
            productivity_score: 50
        };
    }
}

// ============================================
// API COMMUNICATION
// ============================================

async function createTimeEntry() {
    try {
        const token = store.get('authToken');
        
        const response = await axios.post(
            `${API_URL}/api/time-entries`,
            {
                start_time: new Date().toISOString(),
                source: 'desktop_app'
            },
            { headers: { Authorization: `Bearer ${token}` }}
        );
        
        return response.data.time_entry;
    } catch (error) {
        console.error('Create time entry error:', error);
        throw error;
    }
}

async function endTimeEntry(entryId) {
    try {
        const token = store.get('authToken');
        
        await axios.patch(
            `${API_URL}/api/time-entries/${entryId}`,
            {
                end_time: new Date().toISOString()
            },
            { headers: { Authorization: `Bearer ${token}` }}
        );
    } catch (error) {
        console.error('End time entry error:', error);
    }
}

async function uploadScreenshot(processed) {
    try {
        const token = store.get('authToken');
        const timeEntry = store.get('currentTimeEntry');
        
        const formData = new FormData();
        formData.append('file', processed.image, 'screenshot.jpg');
        formData.append('time_entry_id', timeEntry?.id || '');
        formData.append('ocr_text', processed.ocrText || '');
        formData.append('detected_apps', JSON.stringify(processed.detectedApps));
        formData.append('ai_analysis', JSON.stringify(processed.aiAnalysis));
        formData.append('captured_at', processed.capturedAt);
        
        await axios.post(
            `${API_URL}/api/screenshots`,
            formData,
            {
                headers: {
                    ...formData.getHeaders(),
                    Authorization: `Bearer ${token}`
                }
            }
        );
    } catch (error) {
        console.error('Screenshot upload error:', error);
        
        // Add to offline queue
        offlineQueue.push({
            type: 'screenshot',
            data: processed,
            timestamp: new Date().toISOString()
        });
    }
}

async function processOfflineQueue() {
    if (offlineQueue.length === 0) return;
    
    console.log(`Processing ${offlineQueue.length} offline items...`);
    
    for (const item of offlineQueue) {
        try {
            if (item.type === 'screenshot') {
                await uploadScreenshot(item.data);
            }
        } catch (error) {
            console.error('Offline queue processing error:', error);
        }
    }
    
    offlineQueue = [];
}

// ============================================
// SETTINGS & CONFIGURATION
// ============================================

function loadUserSettings(user) {
    const defaultSettings = {
        screenshotInterval: user.screenshot_interval || 600,
        screenshotEnabled: user.screenshot_enabled ?? true,
        activityTracking: user.activity_tracking ?? true,
        enableOCR: true,
        enableAI: user.ai_enabled ?? true,
        privacyBlur: true,
        quality: 80,
        blurRegions: []
    };
    
    const settings = { ...defaultSettings, ...store.get('screenshotSettings', {}) };
    store.set('screenshotSettings', settings);
}

function showSettings() {
    mainWindow.webContents.send('show-settings');
    mainWindow.show();
}

ipcMain.handle('get-settings', () => {
    return store.get('screenshotSettings');
});

ipcMain.handle('update-settings', (event, settings) => {
    store.set('screenshotSettings', settings);
    
    // Restart tracking if active
    if (isTracking) {
        stopTracking();
        startTracking();
    }
    
    return { success: true };
});

// ============================================
// AUTO-UPDATES
// ============================================

function setupAutoUpdater() {
    autoUpdater.checkForUpdatesAndNotify();
    
    autoUpdater.on('update-available', () => {
        mainWindow.webContents.send('update-available');
    });
    
    autoUpdater.on('update-downloaded', () => {
        mainWindow.webContents.send('update-downloaded');
    });
}

ipcMain.handle('install-update', () => {
    autoUpdater.quitAndInstall();
});

// ============================================
// POWER MONITORING
// ============================================

function setupPowerMonitoring() {
    powerMonitor.on('suspend', () => {
        if (isTracking) {
            stopTracking();
            store.set('wasTrackingBeforeSleep', true);
        }
    });
    
    powerMonitor.on('resume', () => {
        if (store.get('wasTrackingBeforeSleep')) {
            startTracking();
            store.delete('wasTrackingBeforeSleep');
        }
    });
}

// ============================================
// IPC HANDLERS
// ============================================

ipcMain.handle('start-tracking', startTracking);
ipcMain.handle('stop-tracking', stopTracking);
ipcMain.handle('get-status', () => ({ isTracking }));

module.exports = { app, mainWindow, tray };
