<script>
  import { onMount } from 'svelte';
  import { user, logout } from './stores.js';
  import { teacherAPI } from './teacherAPI.js';
  import UploadResults from './teacher/UploadResults.svelte';
  import ViewResults from './teacher/ViewResults.svelte';
  
  let currentPage = 'dashboard';
  let assignments = [];
  let loading = true;
  let selectedAssignment = null;
  
  onMount(async () => {
    await loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      // Only load assignments for teachers
      assignments = await teacherAPI.getMyAssignments();
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      loading = false;
    }
  }
  
  function handleLogout() {
    logout();
  }
  
  function navigate(page) {
    currentPage = page;
    selectedAssignment = null;
  }
  
  function selectAssignment(assignment) {
    selectedAssignment = assignment;
    currentPage = 'upload-form';
  }
</script>

<div>
  <nav>
    <div class="container flex-between">
      <h2 style="color: white; margin: 0;">Teacher Portal</h2>
      <div>
        <span style="color: white; margin-right: 20px;">
          {$user?.email || 'Teacher'}
        </span>
        <button class="btn btn-danger" on:click={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  </nav>
  
  <div style="display: flex;">
    <div class="sidebar">
      <button 
        class="sidebar-btn {currentPage === 'dashboard' ? 'active' : ''}"
        on:click={() => navigate('dashboard')}
      >
        Dashboard
      </button>
      <button 
        class="sidebar-btn {currentPage === 'assignments' ? 'active' : ''}"
        on:click={() => navigate('assignments')}
      >
        My Assignments
      </button>
      <button 
        class="sidebar-btn {currentPage === 'upload' ? 'active' : ''}"
        on:click={() => navigate('upload')}
      >
        Upload Results
      </button>
      <button 
        class="sidebar-btn {currentPage === 'results' ? 'active' : ''}"
        on:click={() => navigate('results')}
      >
        View Results
      </button>
    </div>
    
    <div style="flex: 1; padding: 20px;">
      {#if loading}
        <div class="card text-center">
          <p>Loading...</p>
        </div>
      {:else if currentPage === 'dashboard'}
        <div class="container">
          <h1>Welcome, Teacher!</h1>
          <p>Use the sidebar to navigate through your teaching portal.</p>
          
          <div class="grid grid-2 mt-20">
            <div class="card" style="background: #4CAF50; color: white;">
              <h3>{assignments.length}</h3>
              <p>Total Assignments</p>
            </div>
            
            <div class="card" style="background: #2196F3; color: white; cursor: pointer;" on:click={() => navigate('upload')}>
              <h3>Upload Results</h3>
              <p>Click to upload marks</p>
            </div>
          </div>
          
          <div class="card mt-20">
            <h3>Your Current Assignments</h3>
            {#if assignments.length === 0}
              <p style="color: #999;">No assignments found. Please contact the administrator.</p>
            {:else}
              <ul style="list-style: none; padding: 0;">
                {#each assignments as assignment}
                  <li style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>{assignment.subject_name}</strong> - {assignment.class_name} ({assignment.term_name})
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      {:else if currentPage === 'assignments'}
        <div class="container">
          <h2>My Assignments</h2>
          
          {#if assignments.length === 0}
            <div class="card text-center">
              <p>You have no assignments. Please contact the administrator.</p>
            </div>
          {:else}
            <div class="card">
              <table>
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Class</th>
                    <th>Term</th>
                  </tr>
                </thead>
                <tbody>
                  {#each assignments as assignment}
                    <tr>
                      <td><strong>{assignment.subject_name}</strong></td>
                      <td>{assignment.class_name}</td>
                      <td>{assignment.term_name}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>
      {:else if currentPage === 'upload'}
        <div class="container">
          <h2>Upload Results</h2>
          <p style="margin-bottom: 20px;">Select an assignment to upload results...</p>
          
          {#if assignments.length === 0}
            <div class="card text-center">
              <p>You have no assignments to upload results for.</p>
              <p style="color: #999; margin-top: 10px;">Please contact the administrator to assign subjects to you.</p>
            </div>
          {:else}
            <div class="grid grid-2">
              {#each assignments as assignment}
                <div 
                  class="card" 
                  style="cursor: pointer; border: 2px solid #4CAF50; transition: transform 0.2s;"
                  on:click={() => selectAssignment(assignment)}
                  on:mouseenter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  on:mouseleave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  <h3>{assignment.subject_name}</h3>
                  <p><strong>Class:</strong> {assignment.class_name}</p>
                  <p><strong>Term:</strong> {assignment.term_name}</p>
                  <button class="btn btn-primary mt-20" style="width: 100%;">
                    Upload Results →
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {:else if currentPage === 'upload-form' && selectedAssignment}
        <UploadResults 
          assignment={selectedAssignment} 
          onBack={() => navigate('upload')} 
        />
      {:else if currentPage === 'results'}
        <ViewResults />
      {/if}
    </div>
  </div>
</div>

<style>
  .sidebar {
    width: 250px;
    background: #2c3e50;
    min-height: calc(100vh - 57px);
    padding: 20px 0;
  }
  
  .sidebar-btn {
    width: 100%;
    padding: 15px 20px;
    background: none;
    border: none;
    color: white;
    text-align: left;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
  }
  
  .sidebar-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  .sidebar-btn.active {
    background: #4CAF50;
    font-weight: bold;
  }
</style>