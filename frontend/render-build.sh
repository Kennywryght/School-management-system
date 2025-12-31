#!/bin/bash
set -e

echo "Cleaning node_modules..."
rm -rf node_modules package-lock.json

echo "Installing dependencies with legacy peer deps..."
npm install --legacy-peer-deps --force

echo "Building Svelte app..."
npm run build

echo "Build completed successfully!"