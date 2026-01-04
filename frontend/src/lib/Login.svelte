<script>
  import { authAPI } from './api.js';
  import { login } from './stores.js';
  
  let email = '';
  let password = '';
  let passwordVisible = '';
  let error = '';
  let loading = false;
  let showPassword = false;
  
  $: passwordVisible = password;
  
  async function handleLogin() {
  if (!email || !password) {
    error = 'Please enter email and password';
    return;
  }
  
  loading = true;
  error = '';
  
  try {
    console.log('Attempting login with:', email);
    
    // Step 1: Login and get token
    const data = await authAPI.login(email, password);
    console.log('Login successful, token received');
    
    // Step 2: Save token first
    localStorage.setItem('token', data.access_token);
    
    // Step 3: Get user info with the token
    const userData = await authAPI.getCurrentUser(data.access_token);
    console.log('User data:', userData);
    
    // Step 4: Save to store
    login(userData, data.access_token);
    
  } catch (err) {
    console.error('Full error:', err);
    console.error('Error response:', err.response);
    
    if (err.response?.status === 401) {
      error = 'Invalid email or password';
    } else {
      error = `Login failed: ${err.response?.data?.detail || err.message}`;
    }
  } finally {
    loading = false;
  }
}
</script>

<div class="login-container">
  <div class="background-shapes">
    <div class="shape shape-1"></div>
    <div class="shape shape-2"></div>
    <div class="shape shape-3"></div>
  </div>
  
  <div class="login-card card">
    <div class="logo-section">
      <div class="logo-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
          <path d="M6 12v5c3 3 9 3 12 0v-5"/>
        </svg>
      </div>
      <h1 class="title">School Management System</h1>
      <p class="subtitle">Welcome back! Please login to your account</p>
    </div>
    
    {#if error}
      <div class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {error}
      </div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="email">Email Address</label>
        <div class="input-wrapper">
          <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
            <polyline points="22,6 12,13 2,6"/>
          </svg>
          <input
            type="email"
            id="email"
            bind:value={email}
            placeholder="Enter your email"
            disabled={loading}
            required
          />
        </div>
      </div>
      
      <div class="form-group">
        <label for="password">Password</label>
        <div class="input-wrapper">
          <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          {#if showPassword}
            <input
              type="text"
              id="password"
              bind:value={password}
              placeholder="Enter your password"
              disabled={loading}
              required
            />
          {:else}
            <input
              type="password"
              id="password"
              bind:value={password}
              placeholder="Enter your password"
              disabled={loading}
              required
            />
          {/if}
          <button 
            type="button" 
            class="toggle-password"
            on:click={() => showPassword = !showPassword}
            disabled={loading}
          >
            {#if showPassword}
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            {/if}
          </button>
        </div>
      </div>
      
      <button 
        type="submit" 
        class="btn btn-primary" 
        disabled={loading}
      >
        {#if loading}
          <svg class="spinner" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="2" x2="12" y2="6"/>
            <line x1="12" y1="18" x2="12" y2="22"/>
            <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
            <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
            <line x1="2" y1="12" x2="6" y2="12"/>
            <line x1="18" y1="12" x2="22" y2="12"/>
            <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
            <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
          </svg>
          Logging in...
        {:else}
          Login
        {/if}
      </button>
    </form>
    
    <div class="footer-text">
      <p>Protected by advanced security measures</p>
    </div>
  </div>
</div>

<style>
  * {
    box-sizing: border-box;
  }
  
  .login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    position: relative;
    overflow: hidden;
  }
  
  .background-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
    overflow: hidden;
    z-index: 0;
  }
  
  .shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 20s infinite ease-in-out;
  }
  
  .shape-1 {
    width: 300px;
    height: 300px;
    top: -150px;
    left: -150px;
    animation-delay: 0s;
  }
  
  .shape-2 {
    width: 200px;
    height: 200px;
    bottom: -100px;
    right: -100px;
    animation-delay: 5s;
  }
  
  .shape-3 {
    width: 150px;
    height: 150px;
    top: 50%;
    right: 10%;
    animation-delay: 10s;
  }
  
  @keyframes float {
    0%, 100% {
      transform: translateY(0) rotate(0deg);
    }
    50% {
      transform: translateY(-30px) rotate(180deg);
    }
  }
  
  .login-card {
    max-width: 440px;
    width: 100%;
    background: white;
    border-radius: 24px;
    padding: 48px 40px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 1;
    animation: slideUp 0.6s ease-out;
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .logo-section {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .logo-circle {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
    color: white;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  }
  
  .title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 12px 0;
    line-height: 1.2;
  }
  
  .subtitle {
    font-size: 0.95rem;
    color: #718096;
    margin: 0;
  }
  
  .alert {
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: shake 0.4s ease-in-out;
  }
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    75% { transform: translateX(10px); }
  }
  
  .alert-error {
    background: #fee;
    color: #c53030;
    border: 1px solid #feb2b2;
  }
  
  .alert svg {
    flex-shrink: 0;
  }
  
  .form-group {
    margin-bottom: 24px;
  }
  
  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 8px;
  }
  
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .input-icon {
    position: absolute;
    left: 16px;
    color: #a0aec0;
    pointer-events: none;
  }
  
  input {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #f7fafc;
  }
  
  input:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .toggle-password {
    position: absolute;
    right: 16px;
    background: none;
    border: none;
    color: #a0aec0;
    cursor: pointer;
    padding: 4px;
    display: flex;
    align-items: center;
    transition: color 0.2s;
  }
  
  .toggle-password:hover:not(:disabled) {
    color: #667eea;
  }
  
  .toggle-password:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
  
  .btn {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 8px;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  }
  
  .btn-primary:active:not(:disabled) {
    transform: translateY(0);
  }
  
  .btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none !important;
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .footer-text {
    margin-top: 32px;
    text-align: center;
  }
  
  .footer-text p {
    font-size: 0.8rem;
    color: #a0aec0;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
  
  .footer-text p::before {
    content: "🔒";
    font-size: 0.9rem;
  }

  @media (max-width: 768px) {
    .login-card {
      padding: 32px 24px;
      border-radius: 20px;
    }
    
    .title {
      font-size: 1.5rem;
    }
    
    .subtitle {
      font-size: 0.875rem;
    }
    
    .logo-circle {
      width: 70px;
      height: 70px;
    }
    
    .logo-circle svg {
      width: 40px;
      height: 40px;
    }
  }
  
  @media (max-width: 480px) {
    .login-container {
      padding: 16px;
    }
    
    .login-card {
      padding: 28px 20px;
    }
    
    .title {
      font-size: 1.35rem;
    }
  }
</style>