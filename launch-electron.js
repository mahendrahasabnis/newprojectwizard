#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Launching Project Wizard Desktop App...');

// Check if we need to build first
const fs = require('fs');
const buildDir = path.join(__dirname, '.next');

if (!fs.existsSync(buildDir)) {
  console.log('📦 Building Next.js app first...');
  const buildProcess = spawn('npm', ['run', 'build'], {
    stdio: 'inherit',
    cwd: __dirname
  });

  buildProcess.on('close', (code) => {
    if (code === 0) {
      console.log('✅ Build completed! Starting Electron...');
      startElectron();
    } else {
      console.error('❌ Build failed!');
      process.exit(1);
    }
  });
} else {
  console.log('✅ Build already exists! Starting Electron...');
  startElectron();
}

function startElectron() {
  const electronProcess = spawn('npm', ['run', 'electron'], {
    stdio: 'inherit',
    cwd: __dirname
  });

  electronProcess.on('close', (code) => {
    console.log(`🎯 Electron app closed with code ${code}`);
  });
} 