<script>
  import { onMount } from 'svelte';
  import { user, logout } from './stores.js';
  import { studentAPI } from './studentAPI.js';
  
  let profile = null;
  let summary = null;
  let loading = true;
  let error = '';
  let activeTab = 'overview';
  let selectedTerm = 'current';
  
  // Mock data for terms - replace with actual API calls
  let termsData = [];
  
  onMount(async () => {
    await loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load profile
      profile = await studentAPI.getProfile();
      
      // Try to load summary (will be null if no results)
      try {
        summary = await studentAPI.getResultsSummary();
        // For demonstration, create terms data from summary
        if (summary) {
          termsData = [{
            id: 'current',
            name: summary.term_name || 'Current Term',
            results: summary.results || [],
            total_marks: summary.total_marks || 0,
            average_marks: summary.average_marks || 0,
            position: summary.position || 0,
            total_students: summary.total_students || 0
          }];
        }
      } catch (err) {
        console.log('No results available yet');
        summary = null;
        termsData = [];
      }
      
    } catch (err) {
      console.error('Failed to load data:', err);
      error = 'Failed to load profile data';
    } finally {
      loading = false;
    }
  }
  
  function handleLogout() {
    logout();
  }
  
  function getGradeColor(grade) {
    const colors = {
      'A': '#10b981',
      'B': '#3b82f6',
      'C': '#f59e0b',
      'D': '#fbbf24',
      'F': '#ef4444'
    };
    return colors[grade] || '#6b7280';
  }
  
  function getPerformanceLevel(average) {
    if (average >= 80) return { text: 'Excellent', color: '#10b981' };
    if (average >= 70) return { text: 'Very Good', color: '#3b82f6' };
    if (average >= 60) return { text: 'Good', color: '#f59e0b' };
    if (average >= 50) return { text: 'Average', color: '#fbbf24' };
    return { text: 'Needs Improvement', color: '#ef4444' };
  }
  
  $: currentTermData = termsData.find(t => t.id === selectedTerm) || termsData[0];
  $: performanceLevel = currentTermData ? getPerformanceLevel(currentTermData.average_marks) : null;
</script>

<div class="dashboard">
  <!-- Header Navigation -->
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="brand-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <span class="brand-text">Student Portal</span>
      </div>
      <div class="nav-actions">
        <span class="user-name">
          {profile?.first_name || 'Student'}
        </span>
        <button class="btn-logout" on:click={handleLogout}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Logout
        </button>
      </div>
    </div>
  </nav>

  <div class="main-container">
    {#if loading}
      <div class="loading-container">
        <div class="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    {:else if error}
      <div class="error-card">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3>Error Loading Data</h3>
        <p>{error}</p>
        <button class="btn-primary" on:click={loadData}>Retry</button>
      </div>
    {:else}
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="profile-avatar">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div class="profile-info">
          <h1 class="profile-name">{profile.first_name} {profile.last_name}</h1>
          <p class="profile-subtitle">Student • {profile.class_name || 'Not assigned'}</p>
        </div>
        <div class="profile-details">
          <div class="detail-item">
            <span class="detail-label">Admission No.</span>
            <span class="detail-value">{profile.admission_number}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Email</span>
            <span class="detail-value">{profile.email}</span>
          </div>
          {#if profile.date_of_birth}
            <div class="detail-item">
              <span class="detail-label">Date of Birth</span>
              <span class="detail-value">{new Date(profile.date_of_birth).toLocaleDateString()}</span>
            </div>
          {/if}
          {#if profile.gender}
            <div class="detail-item">
              <span class="detail-label">Gender</span>
              <span class="detail-value">{profile.gender}</span>
            </div>
          {/if}
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="tabs-container">
        <button 
          class="tab-button {activeTab === 'overview' ? 'active' : ''}"
          on:click={() => activeTab = 'overview'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
          Overview
        </button>
        <button 
          class="tab-button {activeTab === 'results' ? 'active' : ''}"
          on:click={() => activeTab = 'results'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="20" x2="12" y2="10"/>
            <line x1="18" y1="20" x2="18" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="16"/>
          </svg>
          Academic Results
        </button>
        <button 
          class="tab-button {activeTab === 'progress' ? 'active' : ''}"
          on:click={() => activeTab = 'progress'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          Progress Chart
        </button>
      </div>

      <!-- Tab Content -->
      {#if activeTab === 'overview'}
        {#if summary && summary.results && summary.results.length > 0}
          <!-- Stats Cards -->
          <div class="stats-grid">
            <div class="stat-card stat-primary">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="8.5" cy="7" r="4"/>
                  <polyline points="17 11 19 13 23 9"/>
                </svg>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{summary.position}</h3>
                <p class="stat-label">Class Position</p>
                <span class="stat-meta">Out of {summary.total_students} students</span>
              </div>
            </div>

            <div class="stat-card stat-success">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{summary.total_marks}</h3>
                <p class="stat-label">Total Marks</p>
                <span class="stat-meta">{summary.term_name}</span>
              </div>
            </div>

            <div class="stat-card stat-warning">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{summary.average_marks}%</h3>
                <p class="stat-label">Average Score</p>
                <span class="stat-meta" style="color: {performanceLevel?.color}">{performanceLevel?.text}</span>
              </div>
            </div>

            <div class="stat-card stat-info">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div class="stat-content">
                <h3 class="stat-value">{summary.results?.length || 0}</h3>
                <p class="stat-label">Subjects</p>
                <span class="stat-meta">Total enrolled</span>
              </div>
            </div>
          </div>

          <!-- Recent Results -->
          <div class="content-card">
            <div class="card-header">
              <h2 class="card-title">Recent Performance</h2>
              <span class="badge">{summary.term_name}</span>
            </div>
            <div class="results-grid">
              {#each summary.results as result}
                <div class="result-item">
                  <div class="result-subject">
                    <div class="subject-icon" style="background: {getGradeColor(result.grade)}20; color: {getGradeColor(result.grade)}">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                      </svg>
                    </div>
                    <div>
                      <h4 class="subject-name">{result.subject_name}</h4>
                      <p class="subject-marks">{result.marks} marks</p>
                    </div>
                  </div>
                  <div class="result-grade" style="background: {getGradeColor(result.grade)}; color: white;">
                    {result.grade}
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {:else}
          <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <h3>No Results Available</h3>
            <p>Your academic results haven't been uploaded yet. Please check back later.</p>
          </div>
        {/if}

      {:else if activeTab === 'results'}
        {#if termsData.length > 0}
          <!-- Term Selector -->
          <div class="term-selector">
            <label for="term-select">Select Term:</label>
            <select id="term-select" bind:value={selectedTerm} class="term-select">
              {#each termsData as term}
                <option value={term.id}>{term.name}</option>
              {/each}
            </select>
          </div>

          {#if currentTermData}
            <!-- Results Table -->
            <div class="content-card">
              <div class="card-header">
                <h2 class="card-title">Detailed Results - {currentTermData.name}</h2>
                <button class="btn-secondary">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Download Report
                </button>
              </div>
              <div class="table-container">
                <table class="results-table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Marks Obtained</th>
                      <th>Grade</th>
                      <th>Performance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each currentTermData.results as result}
                      <tr>
                        <td>
                          <div class="table-subject">
                            <div class="table-subject-icon" style="background: {getGradeColor(result.grade)}20; color: {getGradeColor(result.grade)}">
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                              </svg>
                            </div>
                            <strong>{result.subject_name}</strong>
                          </div>
                        </td>
                        <td><strong>{result.marks}</strong></td>
                        <td>
                          <span class="grade-badge" style="background: {getGradeColor(result.grade)}">
                            {result.grade}
                          </span>
                        </td>
                        <td>
                          <div class="progress-bar-container">
                            <div class="progress-bar" style="width: {result.marks}%; background: {getGradeColor(result.grade)}"></div>
                          </div>
                          <span class="progress-text">{result.marks}%</span>
                        </td>
                      </tr>
                    {/each}
                    <tr class="total-row">
                      <td><strong>TOTAL</strong></td>
                      <td><strong>{currentTermData.total_marks}</strong></td>
                      <td colspan="2">
                        <strong>Average: {currentTermData.average_marks}%</strong>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          {/if}
        {:else}
          <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <h3>No Results Available</h3>
            <p>Your academic results haven't been uploaded yet.</p>
          </div>
        {/if}

      {:else if activeTab === 'progress'}
        {#if currentTermData && currentTermData.results.length > 0}
          <div class="content-card">
            <div class="card-header">
              <h2 class="card-title">Performance Analysis</h2>
            </div>
            
            <!-- Visual Chart -->
            <div class="chart-container">
              <div class="chart-bars">
                {#each currentTermData.results as result}
                  <div class="chart-bar-wrapper">
                    <div class="chart-bar-container">
                      <div 
                        class="chart-bar" 
                        style="height: {result.marks}%; background: {getGradeColor(result.grade)}"
                      >
                        <span class="chart-bar-value">{result.marks}</span>
                      </div>
                    </div>
                    <div class="chart-label">
                      <span class="chart-subject">{result.subject_name}</span>
                      <span class="chart-grade" style="color: {getGradeColor(result.grade)}">{result.grade}</span>
                    </div>
                  </div>
                {/each}
              </div>
              <div class="chart-average-line" style="bottom: {currentTermData.average_marks}%">
                <span class="chart-average-label">Average: {currentTermData.average_marks}%</span>
              </div>
            </div>

            <!-- Performance Insights -->
            <div class="insights-grid">
              <div class="insight-card insight-success">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <div>
                  <h4>Strongest Subject</h4>
                  <p>{currentTermData.results.reduce((a, b) => a.marks > b.marks ? a : b).subject_name}</p>
                </div>
              </div>
              <div class="insight-card insight-warning">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <div>
                  <h4>Needs Improvement</h4>
                  <p>{currentTermData.results.reduce((a, b) => a.marks < b.marks ? a : b).subject_name}</p>
                </div>
              </div>
              <div class="insight-card insight-info">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <div>
                  <h4>Overall Performance</h4>
                  <p style="color: {performanceLevel?.color}">{performanceLevel?.text}</p>
                </div>
              </div>
            </div>
          </div>
        {:else}
          <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
            <h3>No Data Available</h3>
            <p>Progress charts will appear once your results are uploaded.</p>
          </div>
        {/if}
      {/if}
    {/if}
  </div>
</div>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  .dashboard {
    min-height: 100vh;
    background: #f8fafc;
  }

  /* Navbar */
  .navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .brand-icon {
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .brand-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: white;
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .user-name {
    color: white;
    font-weight: 500;
  }

  .btn-logout {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-logout:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  /* Main Container */
  .main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }

  /* Loading */
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 1rem;
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #e2e8f0;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Error Card */
  .error-card {
    background: white;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .error-card svg {
    color: #ef4444;
    margin-bottom: 1rem;
  }

  .error-card h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: #1e293b;
  }

  .error-card p {
    color: #64748b;
    margin-bottom: 1.5rem;
  }

  /* Profile Header */
  .profile-header {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 2rem;
    align-items: center;
  }

  .profile-avatar {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .profile-info {
    flex: 1;
  }

  .profile-name {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .profile-subtitle {
    color: #64748b;
    font-size: 1rem;
  }

  .profile-details {
    display: flex;
    gap: 2rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detail-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .detail-value {
    font-size: 0.95rem;
    color: #1e293b;
    font-weight: 500;
  }

  /* Tabs */
  .tabs-container {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    background: white;
    padding: 0.5rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .tab-button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    background: transparent;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    transition: all 0.3s;
  }

  .tab-button:hover {
    background: #f8fafc;
    color: #667eea;
  }

  .tab-button.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    gap: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
  }

  .stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-primary .stat-icon {
    background: #dbeafe;
    color: #3b82f6;
  }

  .stat-success .stat-icon {
    background: #d1fae5;
    color: #10b981;
  }

  .stat-warning .stat-icon {
    background: #fef3c7;
    color: #f59e0b;
  }

  .stat-info .stat-icon {
    background: #e0e7ff;
    color: #667eea;
  }

  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }

  .stat-meta {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  /* Content Card */
  .content-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .card-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
  }

  .badge {
    padding: 6px 16px;
    background: #e0e7ff;
    color: #667eea;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
  }

  /* Results Grid */
  .results-grid {
    display: grid;
    gap: 1rem;
  }

  .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    transition: all 0.3s;
  }

  .result-item:hover {
    background: #f1f5f9;
    transform: translateX(4px);
  }

  .result-subject {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .subject-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .subject-name {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .subject-marks {
    font-size: 0.875rem;
    color: #64748b;
  }

  .result-grade {
    padding: 8px 20px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.25rem;
  }

  /* Term Selector */
  .term-selector {
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .term-selector label {
    font-weight: 600;
    color: #1e293b;
  }

  .term-select {
    padding: 10px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    background: white;
    cursor: pointer;
  }

  .term-select:focus {
    outline: none;
    border-color: #667eea;
  }

  /* Table */
  .table-container {
    overflow-x: auto;
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
  }

  .results-table th {
    text-align: left;
    padding: 1rem;
    background: #f8fafc;
    color: #64748b;
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .results-table td {
    padding: 1rem;
    border-top: 1px solid #e2e8f0;
  }

  .results-table tbody tr:hover {
    background: #f8fafc;
  }

  .table-subject {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .table-subject-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .grade-badge {
    padding: 6px 16px;
    border-radius: 6px;
    color: white;
    font-weight: 700;
    display: inline-block;
  }

  .progress-bar-container {
    width: 200px;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 4px;
  }

  .progress-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
  }

  .progress-text {
    font-size: 0.875rem;
    color: #64748b;
  }

  .total-row {
    background: #f8fafc;
    font-weight: 700;
  }

  .total-row td {
    padding: 1.25rem 1rem;
  }

  /* Chart */
  .chart-container {
    position: relative;
    height: 400px;
    padding: 2rem 1rem;
    background: #f8fafc;
    border-radius: 12px;
    margin-bottom: 2rem;
  }

  .chart-bars {
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    height: 100%;
    gap: 1rem;
  }

  .chart-bar-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
  }

  .chart-bar-container {
    flex: 1;
    width: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    position: relative;
  }

  .chart-bar {
    width: 60%;
    max-width: 60px;
    border-radius: 8px 8px 0 0;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 8px;
    transition: all 0.3s;
  }

  .chart-bar:hover {
    filter: brightness(1.1);
    transform: scaleX(1.1);
  }

  .chart-bar-value {
    color: white;
    font-weight: 700;
    font-size: 0.875rem;
  }

  .chart-label {
    margin-top: 1rem;
    text-align: center;
  }

  .chart-subject {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }

  .chart-grade {
    display: block;
    font-weight: 700;
    font-size: 1rem;
  }

  .chart-average-line {
    position: absolute;
    left: 0;
    right: 0;
    height: 2px;
    background: #ef4444;
    opacity: 0.5;
  }

  .chart-average-label {
    position: absolute;
    right: 1rem;
    top: -24px;
    background: #ef4444;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  /* Insights */
  .insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .insight-card {
    padding: 1.5rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .insight-success {
    background: #d1fae5;
    color: #065f46;
  }

  .insight-warning {
    background: #fef3c7;
    color: #92400e;
  }

  .insight-info {
    background: #dbeafe;
    color: #1e40af;
  }

  .insight-card h4 {
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }

  .insight-card p {
    font-size: 1rem;
    font-weight: 700;
  }

  /* Buttons */
  .btn-primary {
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    color: #1e293b;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-secondary:hover {
    border-color: #667eea;
    color: #667eea;
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .empty-state svg {
    color: #cbd5e1;
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    font-size: 1.5rem;
    color: #1e293b;
    margin-bottom: 0.5rem;
  }

  .empty-state p {
    color: #64748b;
  }

  /* Responsive */
  @media (max-width: 1024px) {
    .profile-header {
      grid-template-columns: 1fr;
      text-align: center;
    }

    .profile-avatar {
      margin: 0 auto;
    }

    .profile-details {
      justify-content: center;
      flex-wrap: wrap;
    }
  }

  @media (max-width: 768px) {
    .main-container {
      padding: 1rem;
    }

    .nav-container {
      padding: 0 1rem;
    }

    .brand-text {
      display: none;
    }

    .user-name {
      display: none;
    }

    .tabs-container {
      flex-direction: column;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .profile-details {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .detail-item {
      text-align: center;
    }

    .card-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .chart-container {
      height: 300px;
    }

    .chart-bar-wrapper {
      min-width: 60px;
    }

    .chart-subject {
      font-size: 0.65rem;
    }

    .progress-bar-container {
      width: 100px;
    }
  }

  @media (max-width: 480px) {
    .profile-name {
      font-size: 1.5rem;
    }

    .stat-value {
      font-size: 1.5rem;
    }

    .card-title {
      font-size: 1.25rem;
    }

    .result-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .insights-grid {
      grid-template-columns: 1fr;
    }
  }
</style>