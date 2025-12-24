import { writable } from 'svelte/store';

// User store
export const user = writable(null);

// Loading store
export const loading = writable(false);

// Check if user is logged in on app load
export function initAuth() {
  const token = localStorage.getItem('token');
  const userData = localStorage.getItem('user');
  
  if (token && userData) {
    user.set(JSON.parse(userData));
  }
}

// Login function
export function login(userData, token) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(userData));
  user.set(userData);
}

// Logout function
export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  user.set(null);
}