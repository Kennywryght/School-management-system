<script>
  import { authAPI } from './api.js';
  import { login } from './stores.js';
  
  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  
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
  <div class="login-card card">
    <h1 class="text-center" style="color: #4CAF50; margin-bottom: 30px;">
      School Management System
    </h1>
    
    <h2 class="text-center" style="margin-bottom: 30px;">
      Login
    </h2>
    
    {#if error}
      <div class="alert alert-error">
        {error}
      </div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          id="email"
          bind:value={email}
          placeholder="Enter your email"
          disabled={loading}
          required
        />
      </div>
      
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          bind:value={password}
          placeholder="Enter your password"
          disabled={loading}
          required
        />
      </div>
      
      <button 
        type="submit" 
        class="btn btn-primary" 
        style="width: 100%;"
        disabled={loading}
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .login-card {
    max-width: 400px;
    width: 100%;
    margin: 20px;
  }
  /* Add to existing style */

@media (max-width: 768px) {
  .login-card {
    margin: 10px;
    padding: 20px;
  }
  
  .login-container {
    padding: 20px;
  }
  
  h1 {
    font-size: 1.8rem !important;
  }
  
  h2 {
    font-size: 1.3rem !important;
  }
}
</style>