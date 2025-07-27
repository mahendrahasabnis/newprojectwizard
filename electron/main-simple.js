const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');
const http = require('http');

let mainWindow;
let nextProcess;

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
    console.log(`Starting Next.js server on port ${port}...`);
    
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
      console.log('Next.js:', output);
      
      // Check for Next.js 15 ready message
      if (output.includes('✓ Ready') && !serverReady) {
        serverReady = true;
        console.log('Next.js server is ready!');
        // Give it a moment to fully start
        setTimeout(() => {
          console.log('Resolving server startup...');
          resolve(port);
        }, 2000);
      }
    });

    nextProcess.stderr.on('data', (data) => {
      console.error('Next.js Error:', data.toString());
    });

    nextProcess.on('error', (error) => {
      console.error('Failed to start Next.js process:', error);
      reject(error);
    });

    nextProcess.on('exit', (code) => {
      console.log(`Next.js process exited with code ${code}`);
      if (!serverReady) {
        reject(new Error(`Next.js server exited with code ${code}`));
      }
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!serverReady) {
        console.error('Next.js server startup timeout');
        reject(new Error('Next.js server failed to start within 30 seconds'));
      }
    }, 30000);
  });
}

function createWindow(port) {
  console.log(`Creating window for port ${port}...`);
  
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

  console.log(`Loading app at http://localhost:${port}`);

  // Load the app
  mainWindow.loadURL(`http://localhost:${port}`);

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show, displaying...');
    mainWindow.show();
    mainWindow.focus();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    console.log('Main window closed');
    mainWindow = null;
  });

  // Handle window close button
  mainWindow.on('close', (event) => {
    console.log('Window close event triggered');
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
    console.error('Failed to load page:', errorCode, errorDescription);
  });

  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page loaded successfully');
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
    console.log('App ready, starting...');

    // Find an available port
    console.log('Finding available port...');
    const port = await findAvailablePort(3000);
    console.log(`Using port ${port}`);

    // Start Next.js server
    console.log('Starting Next.js server...');
    await startNextServer(port);

    // Health check - make sure the server is actually responding
    console.log('Performing health check...');
    await new Promise((resolve, reject) => {
      const req = http.get(`http://localhost:${port}`, (res) => {
        console.log('Health check passed!');
        resolve();
      });
      
      req.on('error', (error) => {
        console.error('Health check failed:', error);
        reject(new Error('Server is not responding after startup'));
      });
      
      req.setTimeout(5000, () => {
        req.destroy();
        reject(new Error('Health check timeout'));
      });
    });

    // Create Electron window
    console.log('Creating Electron window...');
    createWindow(port);
    createMenu(port);

    app.on('activate', () => {
      console.log('App activated');
      if (BrowserWindow.getAllWindows().length === 0) {
        console.log('No windows found, creating new window...');
        createWindow(port);
      } else {
        console.log('Showing existing window...');
        mainWindow.show();
        mainWindow.focus();
      }
    });
  } catch (error) {
    console.error('Failed to start app:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  // On macOS, keep the app running even when all windows are closed
  if (process.platform !== 'darwin') {
    console.log('Quitting app (non-macOS)');
    app.quit();
  }
});

app.on('before-quit', () => {
  console.log('App quitting...');
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