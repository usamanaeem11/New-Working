/**
 * Desktop Error Recovery
 * Handles crashes and auto-recovery
 */

const { app, dialog } = require('electron');
const log = require('electron-log');
const Store = require('electron-store');

const store = new Store();

class ErrorRecovery {
  constructor() {
    this.crashCount = 0;
    this.lastCrashTime = 0;
    this.setupHandlers();
  }
  
  setupHandlers() {
    // Uncaught exception handler
    process.on('uncaughtException', (error) => {
      log.error('Uncaught exception:', error);
      this.handleCrash(error);
    });
    
    // Unhandled rejection handler
    process.on('unhandledRejection', (reason, promise) => {
      log.error('Unhandled rejection:', reason);
      this.handleCrash(new Error(String(reason)));
    });
    
    // Renderer process crash
    app.on('render-process-gone', (event, webContents, details) => {
      log.error('Renderer process gone:', details);
      this.handleRendererCrash(webContents, details);
    });
  }
  
  handleCrash(error) {
    const now = Date.now();
    
    // Reset crash count if more than 5 minutes since last crash
    if (now - this.lastCrashTime > 300000) {
      this.crashCount = 0;
    }
    
    this.crashCount++;
    this.lastCrashTime = now;
    
    // Log crash
    log.error(`Crash #${this.crashCount}:`, error);
    
    // Save crash report
    store.set('last_crash', {
      timestamp: now,
      error: error.message,
      stack: error.stack,
      count: this.crashCount
    });
    
    // If too many crashes, show dialog and quit
    if (this.crashCount >= 3) {
      dialog.showErrorBox(
        'Critical Error',
        'The application has crashed multiple times. It will now close. Please contact support.'
      );
      app.quit();
      return;
    }
    
    // Show error dialog with option to continue
    const choice = dialog.showMessageBoxSync({
      type: 'error',
      title: 'Application Error',
      message: 'An error occurred. Would you like to continue?',
      buttons: ['Continue', 'Quit'],
      defaultId: 0
    });
    
    if (choice === 1) {
      app.quit();
    }
  }
  
  handleRendererCrash(webContents, details) {
    log.error('Renderer crash details:', details);
    
    // Try to reload the page
    if (webContents && !webContents.isDestroyed()) {
      dialog.showMessageBox({
        type: 'warning',
        title: 'Page Unresponsive',
        message: 'The page became unresponsive. Reloading...',
        buttons: ['OK']
      }).then(() => {
        webContents.reload();
      });
    }
  }
  
  getLastCrash() {
    return store.get('last_crash');
  }
  
  clearCrashHistory() {
    store.delete('last_crash');
    this.crashCount = 0;
  }
}

module.exports = new ErrorRecovery();
