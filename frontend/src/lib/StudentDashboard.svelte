<script>
  import { onMount } from 'svelte';
  import { user, logout } from './stores.js';
  import { studentAPI } from './studentAPI.js';
  
  let profile = null;
  let summary = null;
  let loading = true;
  let error = '';
  
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
      } catch (err) {
        console.log('No results available yet');
        summary = null;
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
</script>

<div>
  <nav>
    <div class="container flex-between">
      <h2 style="color: white; margin: 0;">Student Portal</h2>
      <div>
        <span style="color: white; margin-right: 20px;">
          {profile?.first_name || 'Student'}
        </span>
        <button class="btn btn-danger" on:click={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  </nav>
  
  <div class="container" style="padding: 30px;">
    {#if loading}
      <div class="card text-center">
        <p>Loading your results...</p>
      </div>
    {:else if error}
      <div class="alert alert-error">{error}</div>
    {:else}
      <!-- Profile Card -->
      <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-bottom: 30px;">
        <h1 style="margin: 0 0 10px 0;">Welcome, {profile.first_name} {profile.last_name}!</h1>
        <p style="margin: 5px 0;"><strong>Admission Number:</strong> {profile.admission_number}</p>
        <p style="margin: 5px 0;"><strong>Class:</strong> {profile.class_name || 'Not assigned'}</p>
        <p style="margin: 5px 0;"><strong>Email:</strong> {profile.email}</p>
        {#if profile.date_of_birth}
          <p style="margin: 5px 0;"><strong>Date of Birth:</strong> {new Date(profile.date_of_birth).toLocaleDateString()}</p>
        {/if}
        {#if profile.gender}
          <p style="margin: 5px 0;"><strong>Gender:</strong> {profile.gender}</p>
        {/if}
      </div>
      
      {#if summary && summary.results && summary.results.length > 0}
        <!-- Position Card -->
        <div class="grid grid-3 mb-20">
          <div class="card text-center" style="background: #4CAF50; color: white;">
            <h2 style="margin: 0 0 10px 0; font-size: 48px;">{summary.position}</h2>
            <p style="font-size: 18px;">Position in Class</p>
            <small>Out of {summary.total_students} students</small>
          </div>
          
          <div class="card text-center" style="background: #2196F3; color: white;">
            <h2 style="margin: 0 0 10px 0; font-size: 48px;">{summary.total_marks}</h2>
            <p style="font-size: 18px;">Total Marks</p>
          </div>
          
          <div class="card text-center" style="background: #FF9800; color: white;">
            <h2 style="margin: 0 0 10px 0; font-size: 48px;">{summary.average_marks}%</h2>
            <p style="font-size: 18px;">Average</p>
          </div>
        </div>
        
        <!-- Results Table -->
        <div class="card">
          <h2>Your Results - {summary.term_name}</h2>
          <table style="margin-top: 20px;">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Marks</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              {#each summary.results as result}
                <tr>
                  <td><strong>{result.subject_name}</strong></td>
                  <td style="font-size: 18px;">{result.marks}</td>
                  <td>
                    <span style="padding: 8px 20px; border-radius: 5px; font-weight: bold; font-size: 18px;
                      background: {result.grade === 'A' ? '#4CAF50' : 
                                   result.grade === 'B' ? '#2196F3' : 
                                   result.grade === 'C' ? '#FF9800' : 
                                   result.grade === 'D' ? '#FFC107' : '#f44336'};
                      color: white;">
                      {result.grade}
                    </span>
                  </td>
                </tr>
              {/each}
              <tr style="background: #f5f5f5; font-weight: bold;">
                <td>TOTAL</td>
                <td style="font-size: 20px;">{summary.total_marks}</td>
                <td>Average: {summary.average_marks}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      {:else}
        <div class="card text-center">
          <h2>No Results Available</h2>
          <p style="color: #999; margin-top: 10px; font-size: 18px;">
            Your results haven't been uploaded yet.
          </p>
          <p style="color: #999;">Please check back later.</p>
        </div>
      {/if}
    {/if}
  </div>
</div>