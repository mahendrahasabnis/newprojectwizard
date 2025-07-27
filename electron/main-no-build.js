const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');
const http = require('http');
const fs = require('fs');

let mainWindow;
let nextProcess;

// Safe logging function that won't crash the app
function safeLog(message, type = 'log') {
  try {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    
    // Try to write to a log file instead of console
    fs.appendFileSync(path.join(__dirname, '../app.log'), logMessage);
    
    // Only try console if it's available
    if (process.stdout && !process.stdout.destroyed) {
      if (type === 'error') {
        console.error(message);
      } else {
        console.log(message);
      }
    }
  } catch (error) {
    // Silently fail if logging fails
  }
}

// Check if a port is available
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => {
        resolve(true);
      });
      server.close();
    });
    server.on('error', () => {
      resolve(false);
    });
  });
}

// Find an available port starting from 3000
async function findAvailablePort(startPort = 3000) {
  for (let port = startPort; port < startPort + 100; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error('No available ports found');
}

function startNextServer(port) {
  return new Promise((resolve, reject) => {
    safeLog(`Starting Next.js server on port ${port}...`);
    
    // Start Next.js server on the specified port
    nextProcess = spawn('npm', ['run', 'start'], {
      cwd: path.join(__dirname, '..'),
      stdio: 'pipe',
      env: { ...process.env, PORT: port.toString() }
    });

    let serverReady = false;

    // Wait for server to be ready
    nextProcess.stdout.on('data', (data) => {
      const output = data.toString();
      safeLog('Next.js: ' + output);
      
      // Check for Next.js 15 ready message
      if (output.includes('✓ Ready') && !serverReady) {
        serverReady = true;
        safeLog('Next.js server is ready!');
        // Give it a moment to fully start
        setTimeout(() => {
          safeLog('Resolving server startup...');
          resolve(port);
        }, 2000);
      }
    });

    nextProcess.stderr.on('data', (data) => {
      safeLog('Next.js Error: ' + data.toString(), 'error');
    });

    nextProcess.on('error', (error) => {
      safeLog('Failed to start Next.js process: ' + error.message, 'error');
      reject(error);
    });

    nextProcess.on('exit', (code) => {
      safeLog(`Next.js process exited with code ${code}`);
      if (!serverReady) {
        reject(new Error(`Next.js server exited with code ${code}`));
      }
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!serverReady) {
        safeLog('Next.js server startup timeout', 'error');
        reject(new Error('Next.js server failed to start within 30 seconds'));
      }
    }, 30000);
  });
}

function createWindow(port) {
  safeLog(`Creating window for port ${port}...`);
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
    icon: path.join(__dirname, '../public/favicon.ico'),
    title: 'NewProjWiz',
    show: false, // Don't show until ready
  });

  safeLog(`Loading app at http://localhost:${port}`);

  // Load the app
  mainWindow.loadURL(`http://localhost:${port}`);

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    safeLog('Window ready to show, displaying...');
    mainWindow.show();
    mainWindow.focus();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    safeLog('Main window closed');
    mainWindow = null;
  });

  // Handle window close button
  mainWindow.on('close', (event) => {
    safeLog('Window close event triggered');
    // On macOS, just hide the window instead of closing
    if (process.platform === 'darwin') {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });

  // Add error handling for page load
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    safeLog(`Failed to load page: ${errorCode} - ${errorDescription}`, 'error');
  });

  mainWindow.webContents.on('did-finish-load', () => {
    safeLog('Page loaded successfully');
  });
}

// Create menu
function createMenu(port) {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Project',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            if (mainWindow) {
              mainWindow.loadURL(`http://localhost:${port}/new`);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ];

  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideothers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(async () => {
  try {
    safeLog('App ready, starting...');

    // Check if build exists
    if (!fs.existsSync(path.join(__dirname, '../.next'))) {
      safeLog('Build not found, please run: npm run build', 'error');
      app.quit();
      return;
    }

    // Find an available port
    safeLog('Finding available port...');
    const port = await findAvailablePort(3000);
    safeLog(`Using port ${port}`);

    // Start Next.js server
    safeLog('Starting Next.js server...');
    await startNextServer(port);

    // Health check - make sure the server is actually responding
    safeLog('Performing health check...');
    await new Promise((resolve, reject) => {
      const req = http.get(`http://localhost:${port}`, (res) => {
        safeLog('Health check passed!');
        resolve();
      });
      
      req.on('error', (error) => {
        safeLog('Health check failed: ' + error.message, 'error');
        reject(new Error('Server is not responding after startup'));
      });
      
      req.setTimeout(5000, () => {
        req.destroy();
        reject(new Error('Health check timeout'));
      });
    });

    // Create Electron window
    safeLog('Creating Electron window...');
    createWindow(port);
    createMenu(port);

    app.on('activate', () => {
      safeLog('App activated');
      if (BrowserWindow.getAllWindows().length === 0) {
        safeLog('No windows found, creating new window...');
        createWindow(port);
      } else {
        safeLog('Showing existing window...');
        mainWindow.show();
        mainWindow.focus();
      }
    });
  } catch (error) {
    safeLog('Failed to start app: ' + error.message, 'error');
    app.quit();
  }
});

app.on('window-all-closed', () => {
  safeLog('All windows closed');
  // On macOS, keep the app running even when all windows are closed
  if (process.platform !== 'darwin') {
    safeLog('Quitting app (non-macOS)');
    app.quit();
  }
});

app.on('before-quit', () => {
  safeLog('App quitting...');
  // Kill Next.js server when app quits
  if (nextProcess) {
    nextProcess.kill();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    require('electron').shell.openExternal(navigationUrl);
  });
}); 