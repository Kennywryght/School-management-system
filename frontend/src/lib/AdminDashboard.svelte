<script>
  import { user, logout } from './stores.js';
  import ManageClasses from './admin/ManageClasses.svelte';
  import ManageSubjects from './admin/ManageSubjects.svelte';
  import ManageTerms from './admin/ManageTerms.svelte';
  import ManageTeachers from './admin/ManageTeachers.svelte';
  import ManageStudents from'./admin/ManageStudents.svelte';
  import ManageAssignments from './admin/ManageAssignments.svelte';
  
  let currentPage = 'dashboard';
  
  function handleLogout() {
    logout();
  }
  
  function navigate(page) {
    currentPage = page;
  }
</script>

<div>
  <nav>
    <div class="container flex-between">
      <h2 style="color: white; margin: 0;">School Management System</h2>
      <div>
        <span style="color: white; margin-right: 20px;">
          {$user?.email || 'Admin'}
        </span>
        <button class="btn btn-danger" on:click={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  </nav>
  
  <!-- Sidebar Navigation -->
  <div style="display: flex;">
    <div class="sidebar">
      <button 
        class="sidebar-btn {currentPage === 'dashboard' ? 'active' : ''}"
        on:click={() => navigate('dashboard')}
      >
        Dashboard
      </button>
      <button 
        class="sidebar-btn {currentPage === 'classes' ? 'active' : ''}"
        on:click={() => navigate('classes')}
      >
        Classes
      </button>
      <button 
        class="sidebar-btn {currentPage === 'subjects' ? 'active' : ''}"
        on:click={() => navigate('subjects')}
      >
        Subjects
      </button>
      <button 
        class="sidebar-btn {currentPage === 'terms' ? 'active' : ''}"
        on:click={() => navigate('terms')}
      >
        Terms
      </button>
      <button 
        class="sidebar-btn {currentPage === 'teachers' ? 'active' : ''}"
        on:click={() => navigate('teachers')}
      >
        Teachers
      </button>
      <button 
        class="sidebar-btn {currentPage === 'students' ? 'active' : ''}"
        on:click={() => navigate('students')}
      >
        Students
      </button>
      <button 
        class="sidebar-btn {currentPage === 'assignments' ? 'active' : ''}"
        on:click={() => navigate('assignments')}
      >
        Assignments
      </button>
    </div>
    
    <!-- Main Content -->
    <div style="flex: 1; padding: 20px;">
      {#if currentPage === 'dashboard'}
        <div class="container">
          <h1>Welcome, Admin!</h1>
          <p>Select an option from the sidebar to manage the school system.</p>
          
          <div class="grid grid-3 mt-20">
            <div class="card" style="background: #4CAF50; color: white; cursor: pointer;" on:click={() => navigate('classes')}>
              <h3>Manage Classes</h3>
              <p>Add, edit, or delete classes</p>
            </div>
            
            <div class="card" style="background: #2196F3; color: white; cursor: pointer;" on:click={() => navigate('teachers')}>
              <h3>Manage Teachers</h3>
              <p>Add, edit, or delete teachers</p>
            </div>
            
            <div class="card" style="background: #FF9800; color: white; cursor: pointer;" on:click={() => navigate('students')}>
              <h3>Manage Students</h3>
              <p>Add, edit, or delete students</p>
            </div>
          </div>
        </div>
      {:else if currentPage === 'classes'}
        <ManageClasses />
      {:else if currentPage === 'subjects'}
        <ManageSubjects />
      {:else if currentPage === 'terms'}
        <ManageTerms />
      {:else if currentPage === 'teachers'}
        <ManageTeachers />
      {:else if currentPage === 'students'}
        <ManageStudents />
      {:else if currentPage === 'assignments'}
        <ManageAssignments />
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