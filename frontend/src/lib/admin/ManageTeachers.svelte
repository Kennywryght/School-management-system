<script>
  import { onMount } from 'svelte';
  import { teachersAPI, assignmentsAPI, subjectsAPI, classesAPI } from '../adminAPI.js';
  
  let teachers = [];
  let assignments = [];
  let subjects = [];
  let classes = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let editingTeacher = null;
  let formData = {
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    password: ''
  };
  
  // Statistics
  let teacherStats = {
    totalTeachers: 0,
    activeTeachers: 0,
    teachersWithAssignments: [],
    totalAssignments: 0
  };
  
  // Filter
  let searchTerm = '';
  
  // Modal state
  let showAssignmentsModal = false;
  let selectedTeacher = null;
  let teacherAssignments = [];
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load all data in parallel
      const [teachersData, assignmentsData, subjectsData, classesData] = await Promise.all([
        teachersAPI.getAll(),
        assignmentsAPI.getAll(),
        subjectsAPI.getAll(),
        classesAPI.getAll()
      ]);
      
      teachers = teachersData || [];
      assignments = assignmentsData || [];
      subjects = subjectsData || [];
      classes = classesData || [];
      
      // Calculate statistics
      calculateTeacherStats();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
      teachers = [];
      assignments = [];
      subjects = [];
      classes = [];
    } finally {
      loading = false;
    }
  }
  
  async function loadTeachers() {
    try {
      loading = true;
      error = '';
      const data = await teachersAPI.getAll();
      teachers = data || [];
      calculateTeacherStats();
    } catch (err) {
      error = 'Failed to load teachers';
      console.error(err);
      teachers = [];
    } finally {
      loading = false;
    }
  }
  
  function calculateTeacherStats() {
    const stats = {
      totalTeachers: teachers?.length || 0,
      activeTeachers: teachers?.length || 0,
      teachersWithAssignments: [],
      totalAssignments: 0
    };
    
    // Calculate assignments per teacher
    if (teachers && Array.isArray(teachers)) {
      teachers.forEach(teacher => {
        const teacherAssignments = assignments?.filter(a => a.teacher_id === teacher.id) || [];
        if (teacherAssignments.length > 0) {
          stats.teachersWithAssignments.push({
            id: teacher.id,
            name: `${teacher.first_name} ${teacher.last_name}`,
            assignmentCount: teacherAssignments.length
          });
        }
        stats.totalAssignments += teacherAssignments.length;
      });
    }
    
    teacherStats = stats;
  }
  
  function openCreateForm() {
    showForm = true;
    editingTeacher = null;
    formData = {
      first_name: '',
      last_name: '',
      phone: '',
      email: '',
      password: ''
    };
  }
  
  function openEditForm(teacher) {
    showForm = true;
    editingTeacher = teacher;
    formData = {
      first_name: teacher.first_name,
      last_name: teacher.last_name,
      phone: teacher.phone || '',
      email: teacher.email,
      password: ''
    };
  }
  
  function closeForm() {
    showForm = false;
    editingTeacher = null;
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      if (editingTeacher) {
        const updateData = {};
        if (formData.first_name.trim()) updateData.first_name = formData.first_name.trim();
        if (formData.last_name.trim()) updateData.last_name = formData.last_name.trim();
        if (formData.phone.trim()) updateData.phone = formData.phone.trim();
        
        await teachersAPI.update(editingTeacher.id, updateData);
        success = 'Teacher updated successfully!';
      } else {
        const createData = {
          first_name: formData.first_name.trim(),
          last_name: formData.last_name.trim(),
          phone: formData.phone.trim() || null,
          email: formData.email.trim(),
          password: formData.password
        };
        await teachersAPI.create(createData);
        success = 'Teacher created successfully!';
      }
      
      closeForm();
      await loadData();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
    // Check if teacher has assignments
    const hasAssignments = assignments?.some(a => a.teacher_id === id) || false;
    
    if (hasAssignments) {
      error = `Cannot delete teacher "${name}" because they have assignments.`;
      setTimeout(() => { error = ''; }, 5000);
      return;
    }
    
    if (!confirm(`Are you sure you want to delete teacher "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await teachersAPI.delete(id);
      success = 'Teacher deleted successfully!';
      await loadData();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
  
  // Open assignments modal for a teacher
  function openAssignmentsModal(teacher) {
    selectedTeacher = teacher;
    teacherAssignments = assignments?.filter(a => a.teacher_id === teacher.id) || [];
    showAssignmentsModal = true;
  }
  
  function closeAssignmentsModal() {
    showAssignmentsModal = false;
    selectedTeacher = null;
    teacherAssignments = [];
  }
  
  function getTeacherAssignmentCount(teacherId) {
    return assignments?.filter(a => a.teacher_id === teacherId).length || 0;
  }
  
  function getFilteredTeachers() {
    if (!teachers || !Array.isArray(teachers)) return [];
    if (!searchTerm.trim()) return teachers;
    
    const term = searchTerm.toLowerCase();
    return teachers.filter(teacher => 
      teacher.first_name.toLowerCase().includes(term) ||
      teacher.last_name.toLowerCase().includes(term) ||
      teacher.email.toLowerCase().includes(term) ||
      (teacher.phone && teacher.phone.toLowerCase().includes(term))
    );
  }
  
  // Handle modal overlay click
  function handleModalOverlayClick(event) {
    if (event.target.classList.contains('modal-overlay')) {
      closeForm();
    }
  }
  
  // Handle assignments modal overlay click
  function handleAssignmentsModalOverlayClick(event) {
    if (event.target.classList.contains('modal-overlay')) {
      closeAssignmentsModal();
    }
  }
  
  $: filteredTeachers = getFilteredTeachers();
</script>

<div class="page-container">
  <!-- Header -->
  <div class="page-header">
    <div class="header-content">
      <div class="header-title-section">
        <h1 class="page-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          Manage Teachers
        </h1>
        <p class="page-subtitle">Add, edit, and manage your teaching staff</p>
      </div>
      <button class="btn-primary" on:click={openCreateForm}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Add Teacher
      </button>
    </div>
  </div>

  <div class="container">
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-primary">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{teacherStats.totalTeachers}</div>
          <div class="stat-label">Total Teachers</div>
        </div>
      </div>

      <div class="stat-card stat-success">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{teacherStats.teachersWithAssignments.length}</div>
          <div class="stat-label">With Assignments</div>
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
          <div class="stat-value">{teacherStats.totalAssignments}</div>
          <div class="stat-label">Total Assignments</div>
        </div>
      </div>
    </div>
    
    <!-- Alerts -->
    {#if success}
      <div class="alert alert-success">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>{success}</span>
      </div>
    {/if}
    
    {#if error}
      <div class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>{error}</span>
      </div>
    {/if}
    
    <!-- Search Bar -->
    <div class="search-card">
      <div class="search-wrapper">
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          type="text"
          bind:value={searchTerm}
          placeholder="Search by name, email, or phone..."
          class="search-input"
        />
        {#if searchTerm}
          <button class="clear-btn" on:click={() => searchTerm = ''}>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        {/if}
      </div>
    </div>
    
    <!-- Main Content -->
    {#if loading}
      <div class="loading-card">
        <div class="spinner"></div>
        <p>Loading teachers...</p>
      </div>
      
    {:else if !teachers || teachers.length === 0}
      <div class="empty-state">
        <div class="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <h3>No Teachers Yet</h3>
        <p>Get started by adding your first teacher to the system</p>
        <button class="btn-primary" on:click={openCreateForm}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Create First Teacher
        </button>
      </div>
      
    {:else}
      <div class="content-card">
        <div class="card-header">
          <h2 class="card-title">
            {#if searchTerm}
              Search Results ({filteredTeachers.length})
            {:else}
              All Teachers ({teachers.length})
            {/if}
          </h2>
        </div>
        
        {#if filteredTeachers.length === 0}
          <div class="no-results">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <p>No teachers found for "<strong>{searchTerm}</strong>"</p>
            <button class="btn-secondary" on:click={() => searchTerm = ''}>Clear Search</button>
          </div>
        {:else}
          <!-- Teachers Grid -->
          <div class="teachers-grid">
            {#each filteredTeachers as teacher (teacher.id)}
              <div class="teacher-card">
                <div class="teacher-avatar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="teacher-info">
                  <h3 class="teacher-name">{teacher.first_name} {teacher.last_name}</h3>
                  <div class="teacher-details">
                    <div class="detail-row">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="4" width="20" height="16" rx="2"/>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                      </svg>
                      <span>{teacher.email}</span>
                    </div>
                    {#if teacher.phone}
                      <div class="detail-row">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                        </svg>
                        <span>{teacher.phone}</span>
                      </div>
                    {/if}
                    <div class="detail-row">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                        <line x1="16" y1="2" x2="16" y2="6"/>
                        <line x1="8" y1="2" x2="8" y2="6"/>
                        <line x1="3" y1="10" x2="21" y2="10"/>
                      </svg>
                      <span>Joined {new Date(teacher.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  {#if getTeacherAssignmentCount(teacher.id) > 0}
                    <div class="assignments-badge">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                      </svg>
                      {getTeacherAssignmentCount(teacher.id)} Assignment{getTeacherAssignmentCount(teacher.id) > 1 ? 's' : ''}
                    </div>
                  {/if}
                </div>
                
                <div class="teacher-actions">
                  {#if getTeacherAssignmentCount(teacher.id) > 0}
                    <button class="btn-action btn-view" on:click={() => openAssignmentsModal(teacher)}>
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                      View Assignments
                    </button>
                  {/if}
                  <button class="btn-action btn-edit" on:click={() => openEditForm(teacher)}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                    </svg>
                    Edit
                  </button>
                  <button 
                    class="btn-action btn-delete" 
                    on:click={() => handleDelete(teacher.id, `${teacher.first_name} ${teacher.last_name}`)}
                    disabled={getTeacherAssignmentCount(teacher.id) > 0}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                    {getTeacherAssignmentCount(teacher.id) > 0 ? 'Has Assignments' : 'Delete'}
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<!-- Teacher Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={handleModalOverlayClick}>
    <div class="modal-content">
      <div class="modal-header">
        <h2>{editingTeacher ? 'Edit Teacher' : 'Create New Teacher'}</h2>
        <button class="btn-close" on:click={closeForm}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-grid">
          <div class="form-group">
            <label for="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              bind:value={formData.first_name}
              placeholder="John"
              required={!editingTeacher}
            />
          </div>
          
          <div class="form-group">
            <label for="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              bind:value={formData.last_name}
              placeholder="Banda"
              required={!editingTeacher}
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="email">Email Address *</label>
          <input
            type="email"
            id="email"
            bind:value={formData.email}
            placeholder="teacher@school.com"
            required={!editingTeacher}
            disabled={editingTeacher}
          />
          {#if editingTeacher}
            <span class="field-hint">Email cannot be changed</span>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="phone">Phone Number</label>
          <input
            type="tel"
            id="phone"
            bind:value={formData.phone}
            placeholder="+265888123456"
          />
        </div>
        
        {#if !editingTeacher}
          <div class="form-group">
            <label for="password">Password *</label>
            <input
              type="password"
              id="password"
              bind:value={formData.password}
              placeholder="Minimum 6 characters"
              required
            />
          </div>
        {/if}
        
        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={closeForm}>
            Cancel
          </button>
          <button type="submit" class="btn-primary">
            {editingTeacher ? 'Update Teacher' : 'Create Teacher'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Assignments Modal -->
{#if showAssignmentsModal && selectedTeacher}
  <div class="modal-overlay" on:click={handleAssignmentsModalOverlayClick}>
    <div class="modal-content">
      <div class="modal-header">
        <h2>{selectedTeacher.first_name}'s Assignments</h2>
        <button class="btn-close" on:click={closeAssignmentsModal}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <div class="teacher-summary">
        <div class="summary-item">
          <span class="summary-label">Teacher:</span>
          <span class="summary-value">{selectedTeacher.first_name} {selectedTeacher.last_name}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Email:</span>
          <span class="summary-value">{selectedTeacher.email}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Assignments:</span>
          <span class="summary-value">{teacherAssignments.length}</span>
        </div>
      </div>
      
      {#if teacherAssignments.length === 0}
        <div class="empty-assignments">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <p>This teacher has no assignments yet.</p>
        </div>
      {:else}
        <div class="assignments-list">
          {#each teacherAssignments as assignment (assignment.id)}
            <div class="assignment-item">
              <div class="assignment-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div class="assignment-details">
                <h4>{assignment.subject_name}</h4>
                <div class="assignment-meta">
                  <span>Class: {assignment.class_name}</span>
                  <span>•</span>
                  <span>Term: {assignment.term_name}</span>
                </div>
              </div>
              <div class="assignment-id">#{assignment.id}</div>
            </div>
          {/each}
        </div>
      {/if}
      
      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeAssignmentsModal}>
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  .page-container {
    min-height: 100vh;
    background: #f8fafc;
  }

  /* Header */
  .page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
  }

  .header-title-section {
    flex: 1;
  }

  .page-title {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.5rem;
  }

  .page-subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1rem;
  }

  /* Container */
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }

  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s, box-shadow 0.3s;
  }

  .stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .stat-primary .stat-icon {
    background: #dbeafe;
    color: #3b82f6;
  }

  .stat-success .stat-icon {
    background: #d1fae5;
    color: #10b981;
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
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #64748b;
  }

  /* Alerts */
  .alert {
    padding: 1rem 1.25rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .alert-success {
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #10b981;
  }

  .alert-error {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #ef4444;
  }

  /* Search */
  .search-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    color: #94a3b8;
  }

  .search-input {
    width: 100%;
    padding: 14px 3rem 14px 3rem;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.3s;
  }

  .search-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .clear-btn {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .clear-btn:hover {
    background: #f1f5f9;
    color: #667eea;
  }

  /* Content Card */
  .content-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    margin-bottom: 2rem;
  }

  .card-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
  }

  /* Teachers Grid */
  .teachers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  .teacher-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s;
  }

  .teacher-card:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    transform: translateY(-4px);
  }

  .teacher-avatar {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-bottom: 1rem;
  }

  .teacher-info {
    margin-bottom: 1.5rem;
  }

  .teacher-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .teacher-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .detail-row svg {
    flex-shrink: 0;
    color: #94a3b8;
  }

  .assignments-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #dbeafe;
    color: #3b82f6;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
    margin-top: 1rem;
  }

  /* Teacher Actions */
  .teacher-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .btn-action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-view {
    background: #dbeafe;
    color: #3b82f6;
  }

  .btn-view:hover {
    background: #3b82f6;
    color: white;
  }

  .btn-edit {
    background: #f3f4f6;
    color: #4b5563;
  }

  .btn-edit:hover {
    background: #6b7280;
    color: white;
  }

  .btn-delete {
    background: #fee2e2;
    color: #dc2626;
  }

  .btn-delete:hover:not(:disabled) {
    background: #dc2626;
    color: white;
  }

  .btn-delete:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Buttons */
  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 12px 24px;
    background: white;
    color: #667eea;
    border: 2px solid white;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-primary:hover {
    background: rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 12px 24px;
    background: #f1f5f9;
    color: #475569;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
  }

  .btn-secondary:hover {
    background: #e2e8f0;
  }

  /* Loading */
  .loading-card {
    background: white;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #e2e8f0;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Empty States */
  .empty-state {
    background: white;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .empty-icon {
    margin-bottom: 1.5rem;
    color: #cbd5e1;
  }

  .empty-state h3 {
    font-size: 1.5rem;
    color: #1e293b;
    margin-bottom: 0.5rem;
  }

  .empty-state p {
    color: #64748b;
    margin-bottom: 2rem;
  }

  .no-results {
    padding: 3rem 2rem;
    text-align: center;
  }

  .no-results svg {
    color: #cbd5e1;
    margin-bottom: 1rem;
  }

  .no-results p {
    color: #64748b;
    margin-bottom: 1.5rem;
  }

  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
    backdrop-filter: blur(4px);
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: modalSlide 0.3s ease-out;
  }

  @keyframes modalSlide {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .modal-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
  }

  .btn-close {
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .btn-close:hover {
    background: #f1f5f9;
    color: #667eea;
  }

  /* Form */
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #1e293b;
    font-size: 0.875rem;
  }

  .form-group input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s;
  }

  .form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .form-group input:disabled {
    background: #f1f5f9;
    cursor: not-allowed;
  }

  .field-hint {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .form-actions .btn-primary {
    flex: 2;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  }

  .form-actions .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .form-actions .btn-secondary {
    flex: 1;
    justify-content: center;
  }

  /* Teacher Summary */
  .teacher-summary {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .summary-item:last-child {
    margin-bottom: 0;
  }

  .summary-label {
    font-weight: 600;
    color: #64748b;
  }

  .summary-value {
    font-weight: 600;
    color: #1e293b;
  }

  /* Assignments List */
  .assignments-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 2rem;
  }

  .assignment-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s;
  }

  .assignment-item:hover {
    background: #f1f5f9;
  }

  .assignment-icon {
    width: 48px;
    height: 48px;
    background: #dbeafe;
    color: #3b82f6;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .assignment-details {
    flex: 1;
  }

  .assignment-details h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .assignment-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .assignment-id {
    font-size: 0.875rem;
    color: #94a3b8;
    font-weight: 600;
  }

  .empty-assignments {
    text-align: center;
    padding: 3rem 2rem;
  }

  .empty-assignments svg {
    color: #cbd5e1;
    margin-bottom: 1rem;
  }

  .empty-assignments p {
    color: #64748b;
  }

  .modal-footer {
    margin-top: 2rem;
    text-align: right;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .page-header {
      padding: 1.5rem 1rem;
    }

    .header-content {
      flex-direction: column;
      align-items: flex-start;
    }

    .page-title {
      font-size: 1.5rem;
    }

    .container {
      padding: 1rem;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .teachers-grid {
      grid-template-columns: 1fr;
    }

    .form-grid {
      grid-template-columns: 1fr;
    }

    .form-actions {
      flex-direction: column;
    }

    .form-actions .btn-primary,
    .form-actions .btn-secondary {
      flex: 1;
    }
  }

  @media (max-width: 480px) {
    .page-title {
      font-size: 1.25rem;
    }

    .page-subtitle {
      font-size: 0.875rem;
    }

    .stat-value {
      font-size: 1.5rem;
    }

    .modal-content {
      padding: 1.5rem;
    }
  }
</style>