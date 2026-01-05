<script>
  import { onMount } from 'svelte';
  import { assignmentsAPI, teachersAPI, subjectsAPI, classesAPI, termsAPI } from '../adminAPI.js';
  
  let assignments = [];
  let teachers = [];
  let subjects = [];
  let classes = [];
  let terms = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let showDetailsModal = false;
  let selectedAssignment = null;
  
  let formData = {
    teacher_id: null,
    subject_id: null,
    class_id: null,
    term_id: null
  };
  
  // Filters
  let filterTeacherId = null;
  let filterClassId = null;
  let filterTermId = null;
  let searchTerm = '';
  
  // Stats
  let stats = {
    totalAssignments: 0,
    uniqueTeachers: 0,
    uniqueClasses: 0,
    uniqueSubjects: 0
  };
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      const [assignmentsData, teachersData, subjectsData, classesData, termsData] = await Promise.all([
        assignmentsAPI.getAll(),
        teachersAPI.getAll(),
        subjectsAPI.getAll(),
        classesAPI.getAll(),
        termsAPI.getAll()
      ]);
      
      assignments = assignmentsData || [];
      teachers = teachersData || [];
      subjects = subjectsData || [];
      classes = classesData || [];
      terms = termsData || [];
      
      calculateStats();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
      assignments = [];
      teachers = [];
      subjects = [];
      classes = [];
      terms = [];
    } finally {
      loading = false;
    }
  }
  
  function calculateStats() {
    stats = {
      totalAssignments: assignments.length,
      uniqueTeachers: new Set(assignments.map(a => a.teacher_id)).size,
      uniqueClasses: new Set(assignments.map(a => a.class_id)).size,
      uniqueSubjects: new Set(assignments.map(a => a.subject_id)).size
    };
  }
  
  async function loadAssignments() {
    try {
      error = '';
      const filters = {};
      if (filterTeacherId) filters.teacher_id = filterTeacherId;
      if (filterClassId) filters.class_id = filterClassId;
      if (filterTermId) filters.term_id = filterTermId;
      
      assignments = await assignmentsAPI.getAll(filters) || [];
      calculateStats();
    } catch (err) {
      error = 'Failed to load assignments';
      console.error(err);
      assignments = [];
    }
  }
  
  function openCreateForm() {
    showForm = true;
    formData = {
      teacher_id: null,
      subject_id: null,
      class_id: null,
      term_id: null
    };
  }
  
  function closeForm() {
    showForm = false;
  }
  
  function openDetailsModal(assignment) {
    selectedAssignment = assignment;
    showDetailsModal = true;
  }
  
  function closeDetailsModal() {
    showDetailsModal = false;
    selectedAssignment = null;
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      const createData = {
        teacher_id: parseInt(formData.teacher_id),
        subject_id: parseInt(formData.subject_id),
        class_id: parseInt(formData.class_id),
        term_id: parseInt(formData.term_id)
      };
      
      await assignmentsAPI.create(createData);
      success = 'Assignment created successfully!';
      
      closeForm();
      await loadData();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, description) {
    if (!confirm(`Are you sure you want to delete this assignment?\n\n${description}`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await assignmentsAPI.delete(id);
      success = 'Assignment deleted successfully!';
      await loadData();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
  
  function clearFilters() {
    filterTeacherId = null;
    filterClassId = null;
    filterTermId = null;
    searchTerm = '';
    loadData();
  }
  
  function getFilteredAssignments() {
    if (!assignments || !Array.isArray(assignments)) return [];
    
    let filtered = [...assignments];
    
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(a => 
        a.teacher_name?.toLowerCase().includes(term) ||
        a.subject_name?.toLowerCase().includes(term) ||
        a.class_name?.toLowerCase().includes(term) ||
        a.term_name?.toLowerCase().includes(term)
      );
    }
    
    return filtered;
  }
  
  function getTeacherAssignments(teacherId) {
    return assignments.filter(a => a.teacher_id === teacherId);
  }
  
  function handleModalOverlayClick(event) {
    if (event.target.classList.contains('modal-overlay')) {
      closeForm();
      closeDetailsModal();
    }
  }
  
  $: filteredAssignments = getFilteredAssignments();
  $: hasActiveFilters = filterTeacherId || filterClassId || filterTermId || searchTerm;
</script>

<div class="page-container">
  <!-- Header -->
  <div class="page-header">
    <div class="header-content">
      <div class="header-title-section">
        <h1 class="page-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
          </svg>
          Teacher Assignments
        </h1>
        <p class="page-subtitle">Manage teacher-subject-class assignments</p>
      </div>
      <button class="btn-primary" on:click={openCreateForm}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Add Assignment
      </button>
    </div>
  </div>

  <div class="container">
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-primary">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{stats.totalAssignments}</div>
          <div class="stat-label">Total Assignments</div>
        </div>
      </div>

      <div class="stat-card stat-success">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{stats.uniqueTeachers}</div>
          <div class="stat-label">Active Teachers</div>
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
          <div class="stat-value">{stats.uniqueSubjects}</div>
          <div class="stat-label">Subjects Assigned</div>
        </div>
      </div>

      <div class="stat-card stat-warning">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{stats.uniqueClasses}</div>
          <div class="stat-label">Classes Covered</div>
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

    <!-- Search & Filters -->
    <div class="filters-card">
      <div class="search-section">
        <div class="search-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Search assignments..."
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

      <div class="filters-section">
        <div class="filters-grid">
          <div class="filter-group">
            <label for="filter-teacher">Teacher</label>
            <select id="filter-teacher" bind:value={filterTeacherId} on:change={loadAssignments}>
              <option value={null}>All Teachers</option>
              {#each teachers as teacher}
                <option value={teacher.id}>{teacher.first_name} {teacher.last_name}</option>
              {/each}
            </select>
          </div>
          
          <div class="filter-group">
            <label for="filter-class">Class</label>
            <select id="filter-class" bind:value={filterClassId} on:change={loadAssignments}>
              <option value={null}>All Classes</option>
              {#each classes as cls}
                <option value={cls.id}>{cls.name}</option>
              {/each}
            </select>
          </div>
          
          <div class="filter-group">
            <label for="filter-term">Term</label>
            <select id="filter-term" bind:value={filterTermId} on:change={loadAssignments}>
              <option value={null}>All Terms</option>
              {#each terms as term}
                <option value={term.id}>{term.name}</option>
              {/each}
            </select>
          </div>
        </div>
        
        {#if hasActiveFilters}
          <button class="btn-secondary clear-filters" on:click={clearFilters}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Clear All Filters
          </button>
        {/if}
      </div>
    </div>

    <!-- Content -->
    {#if loading}
      <div class="loading-card">
        <div class="spinner"></div>
        <p>Loading assignments...</p>
      </div>
    {:else if filteredAssignments.length === 0}
      <div class="empty-state">
        <div class="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
          </svg>
        </div>
        <h3>{hasActiveFilters ? 'No Matching Assignments' : 'No Assignments Yet'}</h3>
        <p>
          {hasActiveFilters 
            ? 'Try adjusting your filters or search terms' 
            : 'Create your first assignment to get started'}
        </p>
        {#if hasActiveFilters}
          <button class="btn-secondary" on:click={clearFilters}>Clear Filters</button>
        {:else}
          <button class="btn-primary" on:click={openCreateForm}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Create First Assignment
          </button>
        {/if}
      </div>
    {:else}
      <div class="content-card">
        <div class="card-header">
          <h2 class="card-title">
            {#if hasActiveFilters}
              Filtered Results ({filteredAssignments.length})
            {:else}
              All Assignments ({filteredAssignments.length})
            {/if}
          </h2>
        </div>

        <!-- Assignments Grid -->
        <div class="assignments-grid">
          {#each filteredAssignments as assignment (assignment.id)}
            <div class="assignment-card">
              <div class="assignment-header">
                <div class="teacher-info">
                  <div class="teacher-avatar">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <div>
                    <button 
                      class="teacher-name-btn" 
                      on:click={() => openDetailsModal(assignment)}
                    >
                      {assignment.teacher_name}
                    </button>
                    <div class="assignment-id">Assignment #{assignment.id}</div>
                  </div>
                </div>
              </div>

              <div class="assignment-body">
                <div class="assignment-detail">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                  </svg>
                  <div>
                    <span class="detail-label">Subject</span>
                    <span class="detail-value">{assignment.subject_name}</span>
                  </div>
                </div>

                <div class="assignment-detail">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                    <polyline points="9 22 9 12 15 12 15 22"/>
                  </svg>
                  <div>
                    <span class="detail-label">Class</span>
                    <span class="detail-value">{assignment.class_name}</span>
                  </div>
                </div>

                <div class="assignment-detail">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  <div>
                    <span class="detail-label">Term</span>
                    <span class="detail-value">{assignment.term_name}</span>
                  </div>
                </div>
              </div>

              <div class="assignment-actions">
                <button class="btn-action btn-view" on:click={() => openDetailsModal(assignment)}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  View Details
                </button>
                <button 
                  class="btn-action btn-delete" 
                  on:click={() => handleDelete(assignment.id, `${assignment.teacher_name} - ${assignment.subject_name} - ${assignment.class_name}`)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Create Assignment Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={handleModalOverlayClick}>
    <div class="modal-content">
      <div class="modal-header">
        <h2>Create New Assignment</h2>
        <button class="btn-close" on:click={closeForm}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <p class="modal-subtitle">
        Assign a teacher to teach a subject in a specific class for a term.
      </p>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="teacher_id">Teacher *</label>
          <select id="teacher_id" bind:value={formData.teacher_id} required>
            <option value={null}>Select Teacher</option>
            {#each teachers as teacher}
              <option value={teacher.id}>{teacher.first_name} {teacher.last_name}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-group">
          <label for="subject_id">Subject *</label>
          <select id="subject_id" bind:value={formData.subject_id} required>
            <option value={null}>Select Subject</option>
            {#each subjects as subject}
              <option value={subject.id}>{subject.name}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-group">
          <label for="class_id">Class *</label>
          <select id="class_id" bind:value={formData.class_id} required>
            <option value={null}>Select Class</option>
            {#each classes as cls}
              <option value={cls.id}>{cls.name}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-group">
          <label for="term_id">Term *</label>
          <select id="term_id" bind:value={formData.term_id} required>
            <option value={null}>Select Term</option>
            {#each terms as term}
              <option value={term.id}>{term.name}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={closeForm}>
            Cancel
          </button>
          <button type="submit" class="btn-primary">
            Create Assignment
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Assignment Details Modal -->
{#if showDetailsModal && selectedAssignment}
  <div class="modal-overlay" on:click={handleModalOverlayClick}>
    <div class="modal-content details-modal">
      <div class="modal-header">
        <h2>Assignment Details</h2>
        <button class="btn-close" on:click={closeDetailsModal}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="details-content">
        <div class="details-section">
          <div class="section-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <h3>Teacher Information</h3>
          </div>
          <div class="details-grid">
            <div class="detail-item">
              <span class="item-label">Name</span>
              <span class="item-value">{selectedAssignment.teacher_name}</span>
            </div>
            <div class="detail-item">
              <span class="item-label">Teacher ID</span>
              <span class="item-value">#{selectedAssignment.teacher_id}</span>
            </div>
            <div class="detail-item full-width">
              <span class="item-label">Total Assignments</span>
              <span class="item-value">{getTeacherAssignments(selectedAssignment.teacher_id).length}</span>
            </div>
          </div>
        </div>

        <div class="details-section">
          <div class="section-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <h3>Assignment Details</h3>
          </div>
          <div class="details-grid">
            <div class="detail-item">
              <span class="item-label">Subject</span>
              <span class="item-value">{selectedAssignment.subject_name}</span>
            </div>
            <div class="detail-item">
              <span class="item-label">Class</span>
              <span class="item-value">{selectedAssignment.class_name}</span>
            </div>
            <div class="detail-item">
              <span class="item-label">Term</span>
              <span class="item-value">{selectedAssignment.term_name}</span>
            </div>
            <div class="detail-item">
              <span class="item-label">Assignment ID</span>
              <span class="item-value">#{selectedAssignment.id}</span>
            </div>
          </div>
        </div>

        <div class="details-section">
          <div class="section-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            <h3>Other Assignments by {selectedAssignment.teacher_name}</h3>
          </div>
          {#if getTeacherAssignments(selectedAssignment.teacher_id).length > 1}
            <div class="other-assignments">
              {#each getTeacherAssignments(selectedAssignment.teacher_id) as otherAssignment}
                {#if otherAssignment.id !== selectedAssignment.id}
                  <div class="other-assignment-item">
                    <div class="assignment-pill">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                      </svg>
                      {otherAssignment.subject_name}
                    </div>
                    <span class="assignment-pill-secondary">{otherAssignment.class_name}</span>
                    <span class="assignment-pill-tertiary">{otherAssignment.term_name}</span>
                  </div>
                {/if}
              {/each}
            </div>
          {:else}
            <p class="no-other-assignments">This is the only assignment for this teacher.</p>
          {/if}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeDetailsModal}>
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
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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

  .stat-warning .stat-icon {
    background: #fef3c7;
    color: #f59e0b;
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

  /* Filters */
  .filters-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .search-section {
    margin-bottom: 1.5rem;
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

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .filter-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #1e293b;
    font-size: 0.875rem;
  }

  .filter-group select {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.875rem;
    transition: all 0.3s;
  }

  .filter-group select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .clear-filters {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
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

  /* Assignments Grid */
  .assignments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  .assignment-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s;
  }

  .assignment-card:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    transform: translateY(-4px);
  }

  .assignment-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f1f5f9;
  }

  .teacher-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .teacher-avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .teacher-name-btn {
    background: none;
    border: none;
    color: #667eea;
    font-size: 1.125rem;
    font-weight: 700;
    cursor: pointer;
    text-align: left;
    padding: 0;
    transition: color 0.2s;
  }

  .teacher-name-btn:hover {
    color: #764ba2;
    text-decoration: underline;
  }

  .assignment-id {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 0.25rem;
  }

  .assignment-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .assignment-detail {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .assignment-detail svg {
    color: #94a3b8;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .detail-label {
    display: block;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 0.25rem;
  }

  .detail-value {
    display: block;
    font-size: 0.95rem;
    color: #1e293b;
    font-weight: 600;
  }

  .assignment-actions {
    display: flex;
    gap: 0.75rem;
  }

  .btn-action {
    flex: 1;
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

  .btn-delete {
    background: #fee2e2;
    color: #dc2626;
  }

  .btn-delete:hover {
    background: #dc2626;
    color: white;
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

  /* Empty State */
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

  .details-modal {
    max-width: 700px;
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
    margin-bottom: 1.5rem;
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

  .modal-subtitle {
    color: #64748b;
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
  }

  /* Form */
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

  .form-group select {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s;
  }

  .form-group select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

  /* Details Modal */
  .details-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .details-section {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.5rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .section-header svg {
    color: #667eea;
  }

  .section-header h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: #1e293b;
  }

  .details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detail-item.full-width {
    grid-column: span 2;
  }

  .item-label {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .item-value {
    font-size: 1rem;
    color: #1e293b;
    font-weight: 600;
  }

  .other-assignments {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .other-assignment-item {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: white;
    border-radius: 8px;
  }

  .assignment-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #dbeafe;
    color: #3b82f6;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .assignment-pill-secondary {
    padding: 0.5rem 1rem;
    background: #d1fae5;
    color: #059669;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .assignment-pill-tertiary {
    padding: 0.5rem 1rem;
    background: #fef3c7;
    color: #d97706;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .no-other-assignments {
    color: #64748b;
    font-style: italic;
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

    .filters-grid {
      grid-template-columns: 1fr;
    }

    .assignments-grid {
      grid-template-columns: 1fr;
    }

    .assignment-actions {
      flex-direction: column;
    }

    .details-grid {
      grid-template-columns: 1fr;
    }

    .detail-item.full-width {
      grid-column: span 1;
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