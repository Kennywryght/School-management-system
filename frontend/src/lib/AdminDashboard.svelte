<script>
  import { user, logout } from './stores.js';
  import ManageClasses from './admin/ManageClasses.svelte';
  import ManageSubjects from './admin/ManageSubjects.svelte';
  import ManageTerms from './admin/ManageTerms.svelte';
  import ManageTeachers from './admin/ManageTeachers.svelte';
  import ManageStudents from './admin/ManageStudents.svelte';
  import ManageAssignments from './admin/ManageAssignments.svelte';
  import { onMount } from 'svelte';

  
  // We'll try to import APIs, but have fallbacks
  let studentsAPI, teachersAPI, classesAPI, termsAPI, assignmentsAPI, subjectsAPI;
  
  try {
    import('./adminAPI.js').then(module => {
      studentsAPI = module.studentsAPI;
      teachersAPI = module.teachersAPI;
      classesAPI = module.classesAPI;
      termsAPI = module.termsAPI;
      assignmentsAPI = module.assignmentsAPI;
      subjectsAPI = module.subjectsAPI;
    }).catch(() => {
      console.log('API module not found, using fallbacks');
    });
  } catch (error) {
    console.log('API import failed:', error);
  }
  
  // State management
  let currentPage = 'dashboard';
  let sidebarCollapsed = false;
  let mobileMenuOpen = false;
  let isLoading = false;
  let dashboardError = '';
  
  // Dashboard stats
  let dashboardStats = {
    totalStudents: 0,
    totalTeachers: 0,
    totalClasses: 0,
    activeTerms: 0,
    totalAssignments: 0,
    totalSubjects: 0
  };
  
  let recentActivity = [];
  
  // Simple mock API functions if real APIs fail
  const mockAPI = {
    getAll: () => Promise.resolve([])
  };
  
  onMount(() => {
    // Load dashboard data
    setTimeout(() => {
      loadDashboardData();
    }, 100);
  });
  
  async function loadDashboardData() {
    try {
      isLoading = true;
      dashboardError = '';
      
      // Use mock data initially, then try to load real data
      await loadMockData();
      
      // Try to load real data if APIs are available
      if (studentsAPI && teachersAPI) {
        setTimeout(() => {
          tryLoadRealData();
        }, 500);
      }
      
    } catch (error) {
      console.log('Failed to load dashboard data:', error);
      dashboardError = 'Data loading failed, showing sample data';
    } finally {
      isLoading = false;
    }
  }
  
  async function loadMockData() {
    // Mock data for initial display
    dashboardStats = {
      totalStudents: 0,
      totalTeachers: 0,
      totalClasses: 0,
      activeTerms: 0,
      totalAssignments: 0,
      totalSubjects: 0
    };
    
    recentActivity = [
      {
        type: 'system',
        action: 'started',
        name: 'School Management System',
        time: 'Just now',
        timestamp: new Date()
      }
    ];
  }
  
  async function tryLoadRealData() {
    try {
      const api = {
        students: studentsAPI|| mockAPI,
        teachers: teachersAPI || mockAPI,
        classes: classesAPI || mockAPI,
        terms: termsAPI || mockAPI,
        assignments: assignmentsAPI || mockAPI,
        subjects: subjectsAPI || mockAPI
      };
      
      const results = await Promise.allSettled([
        api.students.getAll(),
        api.teachers.getAll(),
        api.classes.getAll(),
        api.terms.getAll(),
        api.assignments.getAll(),
        api.subjects.getAll()
      ]);
      
      const [
        studentsResult,
        teachersResult,
        classesResult,
        termsResult,
        assignmentsResult,
        subjectsResult
      ] = results;
      
      // Extract data safely
      const getData = (result) => {
        if (result.status === 'fulfilled') {
          const value = result.value;
          return Array.isArray(value) ? value : (value?.data || []);
        }
        return [];
      };
      
      const studentsData = getData(studentsResult);
      const teachersData = getData(teachersResult);
      const classesData = getData(classesResult);
      const termsData = getData(termsResult);
      const assignmentsData = getData(assignmentsResult);
      const subjectsData = getData(subjectsResult);
      
      // Update with real data
      dashboardStats = {
        totalStudents: studentsData.length || 0,
        totalTeachers: teachersData.length || 0,
        totalClasses: classesData.length || 0,
        activeTerms: termsData.filter(term => term?.is_active).length || 0,
        totalAssignments: assignmentsData.length || 0,
        totalSubjects: subjectsData.length || 0
      };
      
      // Generate recent activity
      generateRecentActivity(studentsData, teachersData, assignmentsData);
      
    } catch (error) {
      console.log('Real data loading failed:', error);
    }
  }
  
  function generateRecentActivity(students = [], teachers = [], assignments = []) {
    const activities = [];
    const now = new Date();
    
    // Add sample activity if no real data
    if (students.length === 0 && teachers.length === 0 && assignments.length === 0) {
      recentActivity = [
        {
          type: 'system',
          action: 'started',
          name: 'School Management System',
          time: 'Just now',
          timestamp: now
        }
      ];
      return;
    }
    
    // Format time helper
    function formatTimeAgo(dateString) {
      if (!dateString) return 'Recently';
      try {
        const date = new Date(dateString);
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days} day${days !== 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        return 'Just now';
      } catch {
        return 'Recently';
      }
    }
    
    // Add recent teachers
    if (teachers.length > 0) {
      teachers.slice(0, 2).forEach(teacher => {
        activities.push({
          type: 'teacher',
          action: 'added',
          name: `${teacher.first_name || ''} ${teacher.last_name || ''}`.trim() || 'New Teacher',
          time: formatTimeAgo(teacher.created_at),
          timestamp: new Date(teacher.created_at || now)
        });
      });
    }
    
    // Add recent students
    if (students.length > 0) {
      students.slice(0, 2).forEach(student => {
        activities.push({
          type: 'student',
          action: 'registered',
          name: `${student.first_name || ''} ${student.last_name || ''}`.trim() || 'New Student',
          time: formatTimeAgo(student.created_at),
          timestamp: new Date(student.created_at || now)
        });
      });
    }
    
    // Add recent assignments
    if (assignments.length > 0) {
      assignments.slice(0, 2).forEach(assignment => {
        activities.push({
          type: 'assignment',
          action: 'created',
          name: `Assignment #${assignment.id || 'New'}`,
          time: formatTimeAgo(assignment.created_at),
          timestamp: new Date(assignment.created_at || now)
        });
      });
    }
    
    // Sort and limit
    recentActivity = activities
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, 6);
  }
  
  function navigate(page) {
    currentPage = page;
    mobileMenuOpen = false;
    
    // Simple console log to verify navigation works
    console.log('Navigating to:', page);
  }
  
  function toggleSidebar() {
    sidebarCollapsed = !sidebarCollapsed;
  }
  
  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }
  
  function handleKeyDown(event, action, param = null) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (action === 'navigate') navigate(param);
      else if (action === 'logout') handleLogout();
      else if (action === 'toggleSidebar') toggleSidebar();
      else if (action === 'toggleMobileMenu') toggleMobileMenu();
    }
  }
  
  function handleLogout() {
    logout();
  }
  
  function refreshDashboard() {
    loadDashboardData();
  }
</script>

<div class="admin-container">
  <!-- Header -->
  <header class="admin-header">
    <div class="header-content">
      <!-- Mobile menu toggle -->
      <button 
        class="mobile-menu-toggle"
        on:click={toggleMobileMenu}
        on:keydown={(e) => handleKeyDown(e, 'toggleMobileMenu')}
        aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
      >
        {#if mobileMenuOpen}
          ✕
        {:else}
          ☰
        {/if}
      </button>
      
      <!-- Logo and Title -->
      <div class="header-logo">
        <div class="logo-icon">🏫</div>
        <h1>School Management System</h1>
      </div>
      
      <!-- User Info and Actions -->
      <div class="header-actions">
        <div class="user-info">
          <div class="user-avatar">
            {($user?.email || 'A').charAt(0).toUpperCase()}
          </div>
          <div class="user-details">
            <span class="user-name">{$user?.email || 'Admin'}</span>
            <span class="user-role">Administrator</span>
          </div>
        </div>
        <button 
          class="btn btn-logout"
          on:click={handleLogout}
          on:keydown={(e) => handleKeyDown(e, 'logout')}
        >
          Logout
        </button>
      </div>
    </div>
  </header>
  
  <!-- Mobile Sidebar Overlay -->
  {#if mobileMenuOpen}
    <div 
      class="mobile-sidebar-overlay"
      on:click={toggleMobileMenu}
    ></div>
  {/if}
  
  <!-- Main Layout -->
  <div class="main-layout">
    <!-- Desktop Sidebar -->
    <aside 
      class="sidebar {sidebarCollapsed ? 'collapsed' : ''} {mobileMenuOpen ? 'mobile-open' : ''}"
    >
      <div class="sidebar-header">
        {#if !sidebarCollapsed}
          <div class="sidebar-logo">
            <div class="logo-icon">🏫</div>
            <h2>School Admin</h2>
          </div>
        {:else}
          <div class="sidebar-logo-collapsed">
            <div class="logo-icon">🏫</div>
          </div>
        {/if}
        <button 
          class="sidebar-toggle"
          on:click={toggleSidebar}
          on:keydown={(e) => handleKeyDown(e, 'toggleSidebar')}
        >
          {#if sidebarCollapsed}
            →
          {:else}
            ←
          {/if}
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-label">Overview</div>
          <button 
            class="nav-item {currentPage === 'dashboard' ? 'active' : ''}"
            on:click={() => navigate('dashboard')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'dashboard')}
          >
            <span class="nav-icon">📊</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Dashboard</span>
            {/if}
          </button>
        </div>
        
        <div class="nav-section">
          <div class="nav-label">Management</div>
          <button 
            class="nav-item {currentPage === 'classes' ? 'active' : ''}"
            on:click={() => navigate('classes')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'classes')}
          >
            <span class="nav-icon">👥</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Classes</span>
            {/if}
          </button>
          
          <button 
            class="nav-item {currentPage === 'subjects' ? 'active' : ''}"
            on:click={() => navigate('subjects')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'subjects')}
          >
            <span class="nav-icon">📚</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Subjects</span>
            {/if}
          </button>
          
          <button 
            class="nav-item {currentPage === 'terms' ? 'active' : ''}"
            on:click={() => navigate('terms')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'terms')}
          >
            <span class="nav-icon">📅</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Terms</span>
            {/if}
          </button>
        </div>
        
        <div class="nav-section">
          <div class="nav-label">People</div>
          <button 
            class="nav-item {currentPage === 'teachers' ? 'active' : ''}"
            on:click={() => navigate('teachers')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'teachers')}
          >
            <span class="nav-icon">👨‍🏫</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Teachers</span>
            {/if}
          </button>
          
          <button 
            class="nav-item {currentPage === 'students' ? 'active' : ''}"
            on:click={() => navigate('students')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'students')}
          >
            <span class="nav-icon">🎓</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Students</span>
            {/if}
          </button>
        </div>
        
        <div class="nav-section">
          <div class="nav-label">Academic</div>
          <button 
            class="nav-item {currentPage === 'assignments' ? 'active' : ''}"
            on:click={() => navigate('assignments')}
            on:keydown={(e) => handleKeyDown(e, 'navigate', 'assignments')}
          >
            <span class="nav-icon">📝</span>
            {#if !sidebarCollapsed}
              <span class="nav-text">Assignments</span>
            {/if}
          </button>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        {#if !sidebarCollapsed}
          <div class="system-status">
            <span class="status-indicator active"></span>
            <span class="status-text">System Online</span>
          </div>
        {/if}
      </div>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- Page Header -->
        <div class="page-header">
          <h2 class="page-title">
            {#if currentPage === 'dashboard'}
              Dashboard
            {:else if currentPage === 'classes'}
              Manage Classes
            {:else if currentPage === 'subjects'}
              Manage Subjects
            {:else if currentPage === 'terms'}
              Manage Terms
            {:else if currentPage === 'teachers'}
              Manage Teachers
            {:else if currentPage === 'students'}
              Manage Students
            {:else if currentPage === 'assignments'}
              Manage Assignments
            {:else}
              Dashboard
            {/if}
          </h2>
          <div class="breadcrumb">
            <span class="breadcrumb-item">Admin</span>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-item active">
              {#if currentPage === 'dashboard'}
                Dashboard
              {:else if currentPage === 'classes'}
                Classes
              {:else if currentPage === 'subjects'}
                Subjects
              {:else if currentPage === 'terms'}
                Terms
              {:else if currentPage === 'teachers'}
                Teachers
              {:else if currentPage === 'students'}
                Students
              {:else if currentPage === 'assignments'}
                Assignments
              {/if}
            </span>
          </div>
        </div>
        
        <!-- ============ PAGE CONTENT - FIXED SECTION ============ -->
        <div class="page-content">
          {#if currentPage === 'dashboard'}
            <!-- Dashboard Content -->
            <div class="dashboard-container">
              <!-- Error Alert -->
              {#if dashboardError}
                <div class="alert alert-error">
                  <div class="alert-content">
                    <strong>Note:</strong> {dashboardError}
                  </div>
                  <button class="btn btn-sm" on:click={refreshDashboard}>
                    Retry
                  </button>
                </div>
              {/if}
              
              <!-- Dashboard Header -->
              <div class="dashboard-header">
                <div class="header-left">
                  <h3>Overview</h3>
                  <p>School management dashboard</p>
                </div>
                <div class="header-right">
                  <button 
                    class="btn btn-secondary btn-sm" 
                    on:click={refreshDashboard}
                    disabled={isLoading}
                  >
                    {#if isLoading}
                      Loading...
                    {:else}
                      Refresh
                    {/if}
                  </button>
                </div>
              </div>
              
              <!-- Quick Stats -->
              <div class="stats-grid">
                {#if isLoading}
                  <!-- Loading -->
                  {#each [1, 2, 3, 4, 5, 6] as i}
                    <div class="stat-card loading">
                      <div class="stat-icon"></div>
                      <div class="stat-info">
                        <div class="stat-number">--</div>
                        <div class="stat-label">Loading...</div>
                      </div>
                    </div>
                  {/each}
                {:else}
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #4CAF50;">👥</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.totalStudents}</div>
                      <div class="stat-label">Total Students</div>
                    </div>
                  </div>
                  
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #2196F3;">👨‍🏫</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.totalTeachers}</div>
                      <div class="stat-label">Total Teachers</div>
                    </div>
                  </div>
                  
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #FF9800;">🎒</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.totalClasses}</div>
                      <div class="stat-label">Classes</div>
                    </div>
                  </div>
                  
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #9C27B0;">📅</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.activeTerms}</div>
                      <div class="stat-label">Active Terms</div>
                    </div>
                  </div>
                  
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #00BCD4;">📝</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.totalAssignments}</div>
                      <div class="stat-label">Assignments</div>
                    </div>
                  </div>
                  
                  <div class="stat-card">
                    <div class="stat-icon" style="background-color: #673AB7;">📚</div>
                    <div class="stat-info">
                      <div class="stat-number">{dashboardStats.totalSubjects}</div>
                      <div class="stat-label">Subjects</div>
                    </div>
                  </div>
                {/if}
              </div>
              
              <!-- Quick Actions -->
              <div class="dashboard-section">
                <h3 class="section-title">Quick Actions</h3>
                <div class="actions-grid">
                  <button 
                    class="action-card"
                    on:click={() => navigate('teachers')}
                    on:keydown={(e) => handleKeyDown(e, 'navigate', 'teachers')}
                  >
                    <div class="action-icon">👨‍🏫</div>
                    <h4>Add Teacher</h4>
                    <p>Register a new teacher</p>
                  </button>
                  
                  <button 
                    class="action-card"
                    on:click={() => navigate('students')}
                    on:keydown={(e) => handleKeyDown(e, 'navigate', 'students')}
                  >
                    <div class="action-icon">🎓</div>
                    <h4>Add Student</h4>
                    <p>Register a new student</p>
                  </button>
                  
                  <button 
                    class="action-card"
                    on:click={() => navigate('assignments')}
                    on:keydown={(e) => handleKeyDown(e, 'navigate', 'assignments')}
                  >
                    <div class="action-icon">📝</div>
                    <h4>Create Assignment</h4>
                    <p>Assign teacher to class</p>
                  </button>
                  
                  <button 
                    class="action-card"
                    on:click={() => navigate('classes')}
                    on:keydown={(e) => handleKeyDown(e, 'navigate', 'classes')}
                  >
                    <div class="action-icon">👥</div>
                    <h4>Manage Classes</h4>
                    <p>View all classes</p>
                  </button>
                </div>
              </div>
              
              <!-- Recent Activity -->
              <div class="dashboard-section">
                <div class="section-header">
                  <h3 class="section-title">Recent Activity</h3>
                  {#if recentActivity.length > 0}
                    <span class="section-badge">{recentActivity.length} activities</span>
                  {/if}
                </div>
                <div class="activity-list">
                  {#if recentActivity.length === 0}
                    <div class="empty-state">
                      <div class="empty-icon">📊</div>
                      <p>No recent activity found</p>
                      <p class="empty-subtext">Start using the system to see activities here</p>
                    </div>
                  {:else}
                    {#each recentActivity as activity}
                      <div class="activity-item">
                        <div class="activity-icon">
                          {#if activity.type === 'teacher'}
                            👨‍🏫
                          {:else if activity.type === 'student'}
                            🎓
                          {:else if activity.type === 'assignment'}
                            📝
                          {:else}
                            👥
                          {/if}
                        </div>
                        <div class="activity-content">
                          <div class="activity-title">
                            <strong>{activity.name}</strong> was {activity.action}
                          </div>
                          <div class="activity-time">{activity.time}</div>
                        </div>
                      </div>
                    {/each}
                  {/if}
                </div>
              </div>
            </div>
            <!-- ============ END DASHBOARD CONTENT ============ -->
            
          {:else if currentPage === 'classes'}
            <!-- Load Classes Component -->
            <ManageClasses />
            
          {:else if currentPage === 'subjects'}
            <!-- Load Subjects Component -->
            <ManageSubjects />
            
          {:else if currentPage === 'terms'}
            <!-- Load Terms Component -->
            <ManageTerms />
            
          {:else if currentPage === 'teachers'}
            <!-- Load Teachers Component -->
            <ManageTeachers />
            
          {:else if currentPage === 'students'}
            <!-- Load Students Component -->
            <ManageStudents />
            
          {:else if currentPage === 'assignments'}
            <!-- Load Assignments Component -->
            <ManageAssignments />
            
          {:else}
            <!-- Fallback (should never happen) -->
            <div class="coming-soon">
              <div class="coming-soon-icon">🚧</div>
              <h3>Page Not Found</h3>
              <p>The requested page could not be loaded.</p>
              <button class="btn btn-primary" on:click={() => navigate('dashboard')}>
                Back to Dashboard
              </button>
            </div>
          {/if}
        </div>
        <!-- ============ END PAGE CONTENT ============ -->
        
      </div>
    </main>
  </div>
</div>

<style>
  /* Reset and Base */
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  }
  
  .admin-container {
    min-height: 100vh;
    background: #f5f7fa;
  }
  
  /* Header */
  .admin-header {
    background: #2c3e50;
    color: white;
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    height: 64px;
    max-width: 100%;
  }
  
  .mobile-menu-toggle {
    display: none;
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
  }
  
  .mobile-menu-toggle:hover {
    background: rgba(255,255,255,0.1);
  }
  
  .header-logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .logo-icon {
    font-size: 32px;
  }
  
  .header-logo h1 {
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 20px;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .user-avatar {
    width: 40px;
    height: 40px;
    background: #3498db;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    font-size: 18px;
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
  }
  
  .user-name {
    font-weight: 500;
    font-size: 0.95rem;
  }
  
  .user-role {
    font-size: 0.85rem;
    opacity: 0.8;
  }
  
  .btn-logout {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.95rem;
    transition: background 0.2s;
  }
  
  .btn-logout:hover {
    background: rgba(255,255,255,0.2);
  }
  
  /* Mobile Overlay */
  .mobile-sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  }
  
  /* Main Layout */
  .main-layout {
    display: flex;
    min-height: calc(100vh - 64px);
  }
  
  /* Sidebar */
  .sidebar {
    width: 250px;
    background: white;
    border-right: 1px solid #e1e5e9;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
  }
  
  .sidebar.collapsed {
    width: 70px;
  }
  
  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid #e1e5e9;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .sidebar-logo h2 {
    font-size: 1.2rem;
    color: #2c3e50;
    margin: 0;
  }
  
  .sidebar-toggle {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    font-size: 18px;
    padding: 4px;
    border-radius: 4px;
  }
  
  .sidebar-toggle:hover {
    background: #f0f0f0;
  }
  
  .sidebar-nav {
    flex: 1;
    padding: 20px 0;
    overflow-y: auto;
  }
  
  .nav-section {
    margin-bottom: 20px;
  }
  
  .nav-label {
    font-size: 0.8rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 0 20px 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid #eee;
  }
  
  .sidebar.collapsed .nav-label {
    display: none;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 12px 20px;
    background: none;
    border: none;
    color: #555;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
  }
  
  .nav-item:hover {
    background: #f8f9fa;
    color: #2c3e50;
  }
  
  .nav-item.active {
    background: #3498db;
    color: white;
    border-right: 4px solid #2980b9;
  }
  
  .nav-icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
  }
  
  .sidebar.collapsed .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  .sidebar-footer {
    padding: 20px;
    border-top: 1px solid #e1e5e9;
  }
  
  .system-status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2ecc71;
  }
  
  .status-text {
    font-size: 0.9rem;
    color: #666;
  }
  
  /* Main Content */
  .main-content {
    flex: 1;
    overflow-y: auto;
    background: #f5f7fa;
  }
  
  .content-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
  }
  
  .page-header {
    margin-bottom: 30px;
  }
  
  .page-title {
    font-size: 1.8rem;
    color: #2c3e50;
    margin: 0 0 8px 0;
  }
  
  .breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #666;
  }
  
  .breadcrumb-item.active {
    color: #3498db;
    font-weight: 500;
  }
  
  /* Dashboard */
  .dashboard-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
  }
  
  .stat-card {
    background: white;
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.2s;
  }
  
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }
  
  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
  }
  
  .stat-info {
    flex: 1;
  }
  
  .stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1;
  }
  
  .stat-label {
    font-size: 0.95rem;
    color: #666;
    margin-top: 4px;
  }
  
  .dashboard-section {
    background: white;
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  
  .section-title {
    font-size: 1.3rem;
    color: #2c3e50;
    margin: 0 0 20px 0;
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
  }
  
  .action-card {
    background: #f8f9fa;
    border: 2px solid transparent;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .action-card:hover {
    background: white;
    border-color: #3498db;
    transform: translateY(-2px);
  }
  
  .action-icon {
    font-size: 32px;
    margin-bottom: 12px;
  }
  
  .action-card h4 {
    font-size: 1.1rem;
    color: #2c3e50;
    margin: 0 0 8px 0;
  }
  
  .action-card p {
    font-size: 0.9rem;
    color: #666;
    margin: 0;
  }
  
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .activity-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #3498db;
  }
  
  .activity-icon {
    font-size: 20px;
  }
  
  .activity-title {
    font-size: 0.95rem;
    color: #2c3e50;
    margin-bottom: 4px;
  }
  
  .activity-time {
    font-size: 0.85rem;
    color: #666;
  }
  
  /* Alert */
  .alert {
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
  }
  
  .alert-content {
    flex: 1;
  }
  
  .btn-sm {
    padding: 6px 12px;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
  }
  
  .btn-sm:hover {
    background: #5a6268;
  }
  
  /* Dashboard Header */
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  .dashboard-header h3 {
    font-size: 1.5rem;
    color: #2c3e50;
    margin: 0 0 4px 0;
  }
  
  .dashboard-header p {
    color: #666;
    margin: 0;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: #5a6268;
  }
  
  .btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Coming Soon */
  .coming-soon {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  
  .coming-soon-icon {
    font-size: 48px;
    margin-bottom: 20px;
  }
  
  .coming-soon h3 {
    color: #2c3e50;
    margin-bottom: 12px;
  }
  
  .coming-soon p {
    color: #666;
    margin-bottom: 8px;
  }
  
  .btn-primary {
    background: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    margin-top: 20px;
  }
  
  .btn-primary:hover {
    background: #2980b9;
  }
  
  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 40px 20px;
  }
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  .empty-state p {
    color: #666;
    margin: 0 0 8px 0;
  }
  
  .empty-subtext {
    font-size: 0.9rem;
    opacity: 0.7;
  }
  
  /* Section Header */
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
  }
  
  .section-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .mobile-menu-toggle {
      display: block;
    }
    
    .header-logo h1 {
      font-size: 1.2rem;
    }
    
    .user-details {
      display: none;
    }
    
    .sidebar {
      position: fixed;
      top: 64px;
      left: 0;
      bottom: 0;
      width: 280px;
      transform: translateX(-100%);
      z-index: 1000;
      box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    
    .sidebar.mobile-open {
      transform: translateX(0);
    }
    
    .content-wrapper {
      padding: 16px;
    }
    
    .stats-grid {
      grid-template-columns: 1fr;
    }
    
    .actions-grid {
      grid-template-columns: 1fr;
    }
    
    .page-title {
      font-size: 1.5rem;
    }
  }
  
  @media (max-width: 480px) {
    .header-content {
      padding: 0 12px;
    }
    
    .header-logo h1 {
      font-size: 1.1rem;
    }
    
    .content-wrapper {
      padding: 12px;
    }
  }
</style>