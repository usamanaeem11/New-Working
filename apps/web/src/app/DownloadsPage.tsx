// Working Tracker - Downloads Page
// app.workingtracker.com/downloads
// Production-ready with auto OS detection

import React, { useState, useEffect } from 'react';
import { Download, Check, Shield, Info, ExternalLink, Copy, CheckCircle } from 'lucide-react';

interface Release {
  version: string;
  date: string;
  notes: string[];
}

interface Platform {
  name: string;
  icon: string;
  downloads: {
    label: string;
    url: string;
    size: string;
    checksum?: string;
  }[];
}

const DownloadsPage: React.FC = () => {
  const [detectedOS, setDetectedOS] = useState<string>('');
  const [copied, setCopied] = useState<string>('');
  const [latestRelease, setLatestRelease] = useState<Release | null>(null);

  // Auto-detect OS
  useEffect(() => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    let os = 'windows';
    
    if (userAgent.indexOf('mac') !== -1) os = 'macos';
    else if (userAgent.indexOf('linux') !== -1) os = 'linux';
    else if (userAgent.indexOf('android') !== -1) os = 'android';
    else if (userAgent.indexOf('iphone') !== -1 || userAgent.indexOf('ipad') !== -1) os = 'ios';
    
    setDetectedOS(os);
  }, []);

  // Fetch latest release info
  useEffect(() => {
    fetch('https://downloads.workingtracker.com/api/latest')
      .then(res => res.json())
      .then(data => setLatestRelease(data))
      .catch(err => console.error('Failed to fetch release info:', err));
  }, []);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(''), 2000);
  };

  const platforms: Platform[] = [
    {
      name: 'Windows',
      icon: '🪟',
      downloads: [
        {
          label: 'Windows Installer (x64)',
          url: 'https://downloads.workingtracker.com/desktop/windows/WorkingTracker-Setup.exe',
          size: '85 MB',
          checksum: 'a1b2c3d4e5f6...'
        },
        {
          label: 'Windows Portable (x64)',
          url: 'https://downloads.workingtracker.com/desktop/windows/WorkingTracker-Portable.exe',
          size: '82 MB',
          checksum: 'f6e5d4c3b2a1...'
        }
      ]
    },
    {
      name: 'macOS',
      icon: '🍎',
      downloads: [
        {
          label: 'macOS Universal (DMG)',
          url: 'https://downloads.workingtracker.com/desktop/macos/WorkingTracker.dmg',
          size: '120 MB',
          checksum: 'b2c3d4e5f6a1...'
        },
        {
          label: 'macOS Apple Silicon',
          url: 'https://downloads.workingtracker.com/desktop/macos/WorkingTracker-arm64.dmg',
          size: '95 MB',
          checksum: 'c3d4e5f6a1b2...'
        },
        {
          label: 'macOS Intel',
          url: 'https://downloads.workingtracker.com/desktop/macos/WorkingTracker-x64.dmg',
          size: '98 MB',
          checksum: 'd4e5f6a1b2c3...'
        }
      ]
    },
    {
      name: 'Linux',
      icon: '🐧',
      downloads: [
        {
          label: 'AppImage (Universal)',
          url: 'https://downloads.workingtracker.com/desktop/linux/WorkingTracker.AppImage',
          size: '90 MB',
          checksum: 'e5f6a1b2c3d4...'
        },
        {
          label: 'Debian/Ubuntu (.deb)',
          url: 'https://downloads.workingtracker.com/desktop/linux/working-tracker_amd64.deb',
          size: '88 MB',
          checksum: 'f6a1b2c3d4e5...'
        },
        {
          label: 'RPM (Fedora/RHEL)',
          url: 'https://downloads.workingtracker.com/desktop/linux/working-tracker.x86_64.rpm',
          size: '89 MB',
          checksum: 'a1b2c3d4e5f6...'
        }
      ]
    }
  ];

  const mobileStores = [
    {
      name: 'iOS',
      icon: '📱',
      label: 'Download on the',
      store: 'App Store',
      url: 'https://apps.apple.com/app/working-tracker/id123456789',
      badge: 'https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us'
    },
    {
      name: 'Android',
      icon: '🤖',
      label: 'Get it on',
      store: 'Google Play',
      url: 'https://play.google.com/store/apps/details?id=com.workingtracker.app',
      badge: 'https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png'
    }
  ];

  const browserExtensions = [
    {
      name: 'Chrome',
      icon: '🔵',
      url: 'https://chrome.google.com/webstore/detail/working-tracker/abcdefg',
      label: 'Chrome Web Store'
    },
    {
      name: 'Firefox',
      icon: '🦊',
      url: 'https://addons.mozilla.org/en-US/firefox/addon/working-tracker/',
      label: 'Firefox Add-ons'
    },
    {
      name: 'Edge',
      icon: '🌊',
      url: 'https://microsoftedge.microsoft.com/addons/detail/working-tracker/xyz',
      label: 'Edge Add-ons'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Download Working Tracker
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Available on all your devices
          </p>
          {latestRelease && (
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              Latest Version: {latestRelease.version} • Released {latestRelease.date}
            </div>
          )}
        </div>

        {/* Recommended Download */}
        {detectedOS && (
          <div className="mb-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Recommended for Your Device</h2>
            </div>
            <p className="text-blue-100 mb-6">
              We detected you're using <span className="font-semibold capitalize">{detectedOS}</span>
            </p>
            <a
              href={
                detectedOS === 'windows' ? platforms[0].downloads[0].url :
                detectedOS === 'macos' ? platforms[1].downloads[0].url :
                detectedOS === 'linux' ? platforms[2].downloads[0].url :
                detectedOS === 'ios' ? mobileStores[0].url :
                detectedOS === 'android' ? mobileStores[1].url :
                '#'
              }
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg hover:bg-blue-50 transition-all transform hover:scale-105 shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Now
            </a>
          </div>
        )}

        {/* Desktop Downloads */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
            💻 Desktop Apps
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {platforms.map((platform) => (
              <div
                key={platform.name}
                className={`bg-white rounded-xl shadow-lg p-6 border-2 ${
                  platform.name.toLowerCase() === detectedOS
                    ? 'border-blue-500 ring-4 ring-blue-100'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-4xl">{platform.icon}</span>
                  <h3 className="text-2xl font-bold text-gray-900">{platform.name}</h3>
                </div>
                <div className="space-y-3">
                  {platform.downloads.map((download, idx) => (
                    <div key={idx} className="border-t pt-3 first:border-t-0 first:pt-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {download.label}
                        </span>
                        <span className="text-xs text-gray-500">{download.size}</span>
                      </div>
                      <a
                        href={download.url}
                        className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </a>
                      {download.checksum && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                            SHA256 Checksum
                          </summary>
                          <div className="mt-2 flex items-center gap-2 p-2 bg-gray-50 rounded text-xs font-mono">
                            <code className="flex-1 truncate">{download.checksum}</code>
                            <button
                              onClick={() => copyToClipboard(download.checksum!, `${platform.name}-${idx}`)}
                              className="p-1 hover:bg-gray-200 rounded"
                            >
                              {copied === `${platform.name}-${idx}` ? (
                                <Check className="w-3 h-3 text-green-600" />
                              ) : (
                                <Copy className="w-3 h-3 text-gray-600" />
                              )}
                            </button>
                          </div>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mobile Apps */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
            📱 Mobile Apps
          </h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
            {mobileStores.map((store) => (
              <a
                key={store.name}
                href={store.url}
                className={`bg-white rounded-xl shadow-lg p-8 border-2 hover:shadow-xl transition-all ${
                  store.name.toLowerCase() === detectedOS
                    ? 'border-blue-500 ring-4 ring-blue-100'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-4xl">{store.icon}</span>
                  <h3 className="text-2xl font-bold text-gray-900">{store.name}</h3>
                </div>
                <img
                  src={store.badge}
                  alt={`${store.label} ${store.store}`}
                  className="h-12 mx-auto"
                />
              </a>
            ))}
          </div>
        </div>

        {/* Browser Extensions */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
            🧩 Browser Extensions
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {browserExtensions.map((ext) => (
              <a
                key={ext.name}
                href={ext.url}
                className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all text-center"
              >
                <span className="text-5xl mb-4 block">{ext.icon}</span>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{ext.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{ext.label}</p>
                <div className="flex items-center justify-center gap-2 text-blue-600 font-medium">
                  Install Extension
                  <ExternalLink className="w-4 h-4" />
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* System Requirements */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Info className="w-6 h-6 text-blue-600" />
            System Requirements
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Windows</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Windows 10 or later (64-bit)</li>
                <li>• 4 GB RAM (8 GB recommended)</li>
                <li>• 500 MB free disk space</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-3">macOS</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• macOS 11 Big Sur or later</li>
                <li>• Apple Silicon or Intel</li>
                <li>• 4 GB RAM (8 GB recommended)</li>
                <li>• 500 MB free disk space</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Linux</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Ubuntu 20.04+ / Fedora 35+</li>
                <li>• 4 GB RAM (8 GB recommended)</li>
                <li>• 500 MB free disk space</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Release Notes */}
        {latestRelease && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              What's New in {latestRelease.version}
            </h2>
            <ul className="space-y-2">
              {latestRelease.notes.map((note, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{note}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DownloadsPage;
