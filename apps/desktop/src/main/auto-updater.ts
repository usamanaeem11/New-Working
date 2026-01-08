// Auto-updater for Working Tracker Desktop
// Checks for updates on startup and periodically

import { autoUpdater } from 'electron-updater';
import { BrowserWindow, dialog } from 'electron';
import log from 'electron-log';

export class AutoUpdater {
  private mainWindow: BrowserWindow;
  
  constructor(mainWindow: BrowserWindow) {
    this.mainWindow = mainWindow;
    this.configure();
  }
  
  configure() {
    // Configure auto-updater
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;
    autoUpdater.logger = log;
    
    // Set update feed URL
    autoUpdater.setFeedURL({
      provider: 'generic',
      url: 'https://downloads.workingtracker.com/desktop/',
      channel: 'latest'
    });
    
    // Event handlers
    autoUpdater.on('checking-for-update', () => {
      log.info('Checking for updates...');
    });
    
    autoUpdater.on('update-available', (info) => {
      log.info('Update available:', info);
      this.promptUpdate(info);
    });
    
    autoUpdater.on('update-not-available', () => {
      log.info('No updates available');
    });
    
    autoUpdater.on('error', (err) => {
      log.error('Update error:', err);
    });
    
    autoUpdater.on('download-progress', (progress) => {
      log.info(`Download progress: ${progress.percent}%`);
      this.mainWindow.webContents.send('update-progress', progress);
    });
    
    autoUpdater.on('update-downloaded', (info) => {
      log.info('Update downloaded:', info);
      this.promptInstall();
    });
  }
  
  checkForUpdates() {
    autoUpdater.checkForUpdates();
  }
  
  private promptUpdate(info: any) {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `Version ${info.version} is available!`,
      detail: 'Would you like to download it now?',
      buttons: ['Download', 'Later']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.downloadUpdate();
      }
    });
  }
  
  private promptInstall() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update downloaded. Restart to install?',
      buttons: ['Restart Now', 'Later']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  }
}
