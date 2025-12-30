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
  
  // Mobile menu state
  let showMobileFilters = false;
  
  onMount(() => {
    loadData();
    // Add viewport meta dynamically if not present
    if (!document.querySelector('meta[name="viewport"]')) {
      const meta = document.createElement('meta');
      meta.name = 'viewport';
      meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
      document.head.appendChild(meta);
    }
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load all data in parallel
      const [assignmentsData, teachersData, subjectsData, classesData, termsData] = await Promise.all([
        assignmentsAPI.getAll(),
        teachersAPI.getAll(),
        subjectsAPI.getAll(),
        classesAPI.getAll(),
        termsAPI.getAll()
      ]);
      
      assignments = assignmentsData;
      teachers = teachersData;
      subjects = subjectsData;
      classes = classesData;
      terms = termsData;
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function loadAssignments() {
    try {
      error = '';
      const filters = {};
      if (filterTeacherId) filters.teacher_id = filterTeacherId;
      if (filterClassId) filters.class_id = filterClassId;
      if (filterTermId) filters.term_id = filterTermId;
      
      assignments = await assignmentsAPI.getAll(filters);
    } catch (err) {
      error = 'Failed to load assignments';
      console.error(err);
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
      await loadAssignments();
      
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
      await loadAssignments();
      
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
    loadAssignments();
  }
  
  function toggleMobileFilters() {
    showMobileFilters = !showMobileFilters;
  }
</script>

<div class="container">
  <!-- Responsive header -->
  <div class="header-container">
    <div class="mobile-header">
      <h2 class="page-title">Manage Teacher Assignments</h2>
      <div class="mobile-actions">
        <button class="btn btn-icon" on:click={toggleMobileFilters} aria-label="Toggle filters">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
            <path d="M3 5h14M3 10h14M3 15h14" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <button class="btn btn-primary btn-mobile" on:click={openCreateForm} aria-label="Add assignment">
          <span class="btn-text">Add New</span>
          <span class="btn-icon">+</span>
        </button>
      </div>
    </div>
    
    <div class="desktop-actions">
      <button class="btn btn-primary" on:click={openCreateForm}>
        + Add New Assignment
      </button>
    </div>
  </div>
  
  {#if success}
    <div class="alert alert-success">{success}</div>
  {/if}
  
  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}
  
  <!-- Mobile Filters Toggle -->
  <div class="mobile-filters-toggle" class:active={showMobileFilters}>
    <button class="btn btn-secondary btn-block" on:click={toggleMobileFilters}>
      {showMobileFilters ? 'Hide Filters' : 'Show Filters'}
    </button>
  </div>
  
  <!-- Filters -->
  <div class="card mb-20 filters-container" class:show={showMobileFilters}>
    <h3 class="filters-title">Filter Assignments</h3>
    <div class="filter-grid">
      <div class="form-group">
        <label for="filter-teacher">Teacher</label>
        <select id="filter-teacher" bind:value={filterTeacherId} on:change={loadAssignments}>
          <option value={null}>All Teachers</option>
          {#each teachers as teacher}
            <option value={teacher.id}>{teacher.first_name} {teacher.last_name}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group">
        <label for="filter-class">Class</label>
        <select id="filter-class" bind:value={filterClassId} on:change={loadAssignments}>
          <option value={null}>All Classes</option>
          {#each classes as cls}
            <option value={cls.id}>{cls.name}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group">
        <label for="filter-term">Term</label>
        <select id="filter-term" bind:value={filterTermId} on:change={loadAssignments}>
          <option value={null}>All Terms</option>
          {#each terms as term}
            <option value={term.id}>{term.name}</option>
          {/each}
        </select>
      </div>
    </div>
    {#if filterTeacherId || filterClassId || filterTermId}
      <button class="btn btn-secondary clear-filters-btn" on:click={clearFilters}>
        Clear Filters
      </button>
    {/if}
  </div>
  
  <!-- Content -->
  {#if loading}
    <div class="card text-center loading-card">
      <div class="spinner"></div>
      <p>Loading assignments...</p>
    </div>
  {:else if assignments.length === 0}
    <div class="card text-center empty-state">
      <p>No assignments found. Create your first assignment!</p>
    </div>
  {:else}
    <div class="table-container">
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Teacher</th>
              <th>Subject</th>
              <th>Class</th>
              <th>Term</th>
              <th class="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each assignments as assignment}
              <tr>
                <td data-label="ID">{assignment.id}</td>
                <td data-label="Teacher">{assignment.teacher_name}</td>
                <td data-label="Subject"><strong>{assignment.subject_name}</strong></td>
                <td data-label="Class">{assignment.class_name}</td>
                <td data-label="Term">{assignment.term_name}</td>
                <td data-label="Actions" class="actions-col">
                  <button 
                    class="btn btn-danger btn-sm" 
                    on:click={() => handleDelete(
                      assignment.id, 
                      `${assignment.teacher_name} - ${assignment.subject_name} - ${assignment.class_name}`
                    )}
                    aria-label="Delete assignment"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Create New Assignment</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close modal">×</button>
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
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-block">
            Create Assignment
          </button>
          <button type="button" class="btn btn-secondary btn-block" on:click={closeForm}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  /* Base responsive styles */
  * {
    box-sizing: border-box;
  }
  
  body {
    font-size: 16px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
  }
  
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 15px;
  }
  
  /* Header */
  .header-container {
    margin-bottom: 20px;
  }
  
  .mobile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .page-title {
    font-size: 1.5rem;
    margin: 0;
    flex: 1;
  }
  
  .mobile-actions {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  
  .desktop-actions {
    display: none;
  }
  
  /* Buttons */
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: #007bff;
    color: white;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  .btn-block {
    width: 100%;
  }
  
  .btn-sm {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .btn-icon {
    padding: 8px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .btn-mobile .btn-text {
    display: none;
  }
  
  .btn-mobile .btn-icon {
    font-size: 20px;
  }
  
  /* Cards and Alerts */
  .card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .alert {
    padding: 12px 15px;
    border-radius: 6px;
    margin-bottom: 15px;
  }
  
  .alert-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  .alert-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  /* Filters */
  .filters-container {
    display: block;
  }
  
  .filters-title {
    margin-bottom: 15px;
    font-size: 1.2rem;
  }
  
  .filter-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .mobile-filters-toggle {
    display: block;
    margin-bottom: 10px;
  }
  
  .clear-filters-btn {
    margin-top: 15px;
    width: 100%;
  }
  
  /* Form */
  .form-group {
    margin-bottom: 15px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #333;
  }
  
  select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background: white;
  }
  
  /* Table */
  .table-container {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .data-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px;
  }
  
  .data-table th {
    background: #f8f9fa;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #dee2e6;
  }
  
  .data-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #dee2e6;
  }
  
  /* Loading */
  .loading-card {
    text-align: center;
    padding: 40px 20px;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* Empty State */
  .empty-state {
    padding: 40px 20px;
    color: #666;
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
    padding: 15px;
  }
  
  .modal-content {
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.4rem;
  }
  
  .btn-close {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
  }
  
  .modal-subtitle {
    color: #666;
    margin-bottom: 20px;
    font-size: 14px;
  }
  
  .modal-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 20px;
  }
  
  /* Media Queries */
  @media (min-width: 768px) {
    .container {
      padding: 20px;
    }
    
    .mobile-header {
      display: none;
    }
    
    .desktop-actions {
      display: block;
    }
    
    .filter-grid {
      grid-template-columns: repeat(3, 1fr);
    }
    
    .clear-filters-btn {
      width: auto;
      margin-top: 20px;
    }
    
    .modal-actions {
      flex-direction: row;
    }
    
    .btn-block {
      width: auto;
      flex: 1;
    }
    
    .mobile-filters-toggle {
      display: none;
    }
    
    .filters-container {
      display: block !important;
    }
  }
  
  @media (max-width: 767px) {
    .filters-container:not(.show) {
      display: none;
    }
    
    .btn-mobile .btn-text {
      display: inline;
    }
    
    .btn-mobile .btn-icon {
      display: none;
    }
    
    .data-table {
      display: block;
    }
    
    .data-table thead {
      display: none;
    }
    
    .data-table tbody, 
    .data-table tr, 
    .data-table td {
      display: block;
      width: 100%;
    }
    
    .data-table tr {
      margin-bottom: 15px;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 15px;
    }
    
    .data-table td {
      padding: 8px 0;
      border: none;
      position: relative;
      padding-left: 50%;
    }
    
    .data-table td:before {
      content: attr(data-label);
      position: absolute;
      left: 0;
      width: 45%;
      padding-right: 10px;
      font-weight: 600;
      color: #333;
    }
    
    .actions-col {
      text-align: center;
      padding-left: 0 !important;
    }
    
    .actions-col:before {
      display: none;
    }
  }
  
  @media (max-width: 480px) {
    .container {
      padding: 10px;
    }
    
    .page-title {
      font-size: 1.3rem;
    }
    
    .modal-content {
      padding: 15px;
    }
    
    .modal-header h2 {
      font-size: 1.2rem;
    }
    
    .btn {
      padding: 10px 15px;
    }
  }
  
  /* Touch improvements */
  select, button {
    min-height: 44px; /* Minimum touch target size */
  }
  
  .btn {
    touch-action: manipulation; /* Prevent double-tap zoom on mobile */
  }
  
  /* Prevent text overflow */
  td, th {
    word-break: break-word;
    overflow-wrap: break-word;
  }
</style>