<script>
  import { onMount } from 'svelte';
  import { subjectsAPI, teachersAPI, classesAPI } from '../adminAPI.js';
  
  let subjects = [];
  let teachers = [];
  let classes = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let editingSubject = null;
  let formData = {
    name: '',
    code: ''
  };
  
  // Subject statistics
  let subjectStats = {};
  
  // Filter
  let searchTerm = '';
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load all data in parallel
      const [subjectsData, teachersData, classesData] = await Promise.all([
        subjectsAPI.getAll(),
        teachersAPI.getAll(),
        classesAPI.getAll()
      ]);
      
      subjects = subjectsData;
      teachers = teachersData;
      classes = classesData;
      
      // Calculate subject statistics
      calculateSubjectStats();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function loadSubjects() {
    try {
      loading = true;
      error = '';
      subjects = await subjectsAPI.getAll();
      calculateSubjectStats();
    } catch (err) {
      error = 'Failed to load subjects';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function calculateSubjectStats() {
    // For now, we'll just initialize with basic stats
    // In a real app, you might get these from an API endpoint
    subjectStats = {
      totalSubjects: subjects.length,
      activeSubjects: subjects.length, // Assuming all are active
      hasTeachers: Math.floor(subjects.length * 0.7), // Mock data
      hasClasses: Math.floor(subjects.length * 0.5) // Mock data
    };
  }
  
  function openCreateForm() {
    showForm = true;
    editingSubject = null;
    formData = { name: '', code: '' };
  }
  
  function openEditForm(subject) {
    showForm = true;
    editingSubject = subject;
    formData = { name: subject.name, code: subject.code };
  }
  
  function closeForm() {
    showForm = false;
    editingSubject = null;
    formData = { name: '', code: '' };
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      if (editingSubject) {
        await subjectsAPI.update(editingSubject.id, formData);
        success = 'Subject updated successfully!';
      } else {
        await subjectsAPI.create(formData);
        success = 'Subject created successfully!';
      }
      
      closeForm();
      await loadSubjects();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
    if (!confirm(`Are you sure you want to delete subject "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await subjectsAPI.delete(id);
      success = 'Subject deleted successfully!';
      await loadSubjects();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
  
  function getFilteredSubjects() {
    if (!searchTerm.trim()) return subjects;
    
    const term = searchTerm.toLowerCase();
    return subjects.filter(subject => 
      subject.name.toLowerCase().includes(term) ||
      (subject.code && subject.code.toLowerCase().includes(term))
    );
  }
</script>

<div class="page-container">
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1>Manage Subjects</h1>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{subjects.length}</div>
            <div class="stat-label">Total Subjects</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{subjectStats.hasTeachers || 0}</div>
            <div class="stat-label">With Teachers</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{subjectStats.hasClasses || 0}</div>
            <div class="stat-label">With Classes</div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" on:click={openCreateForm}>
          <span class="btn-icon">+</span>
          <span class="btn-text">Add Subject</span>
        </button>
      </div>
    </div>
    
    <!-- Alerts -->
    {#if success}
      <div class="alert alert-success">
        <span class="alert-icon">✓</span>
        <div class="alert-content">
          <strong>Success!</strong> {success}
        </div>
      </div>
    {/if}
    
    {#if error}
      <div class="alert alert-error">
        <span class="alert-icon">!</span>
        <div class="alert-content">
          <strong>Error!</strong> {error}
        </div>
      </div>
    {/if}
    
    <!-- Search and Filter -->
    <div class="card filter-card">
      <div class="search-container">
        <div class="search-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8" stroke-width="2"/>
            <path d="M21 21l-4.35-4.35" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <input
          type="text"
          bind:value={searchTerm}
          placeholder="Search subjects by name or code..."
          class="search-input"
        />
        {#if searchTerm}
          <button class="btn btn-clear-search" on:click={() => searchTerm = ''} aria-label="Clear search">
            ×
          </button>
        {/if}
      </div>
    </div>
    
    <!-- Main Content -->
    {#if loading}
      <div class="card text-center loading-container">
        <div class="spinner"></div>
        <p>Loading subjects...</p>
      </div>
      
    <!-- Empty State -->
    {:else if subjects.length === 0}
      <div class="card text-center empty-state">
        <div class="empty-icon">📚</div>
        <h3>No Subjects Found</h3>
        <p>Create your first subject to get started!</p>
        <button class="btn btn-primary" on:click={openCreateForm}>
          Create First Subject
        </button>
      </div>
      
    <!-- Subjects List -->
    {:else}
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {#if searchTerm}
              Search Results ({getFilteredSubjects().length})
            {:else}
              All Subjects ({subjects.length})
            {/if}
          </h3>
        </div>
        
        <!-- Mobile Card View -->
        <div class="mobile-cards-view">
          {#each getFilteredSubjects() as subject}
            <div class="subject-card">
              <div class="subject-card-header">
                <div class="subject-id">#{subject.id}</div>
                {#if subject.code}
                  <div class="subject-code">{subject.code}</div>
                {/if}
              </div>
              <div class="subject-card-body">
                <h3 class="subject-name">{subject.name}</h3>
                <div class="subject-meta">
                  <span class="meta-item">
                    <span class="meta-icon">📅</span>
                    {new Date(subject.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div class="subject-card-actions">
                <button 
                  class="btn btn-secondary btn-block" 
                  on:click={() => openEditForm(subject)}
                >
                  Edit
                </button>
                <button 
                  class="btn btn-danger btn-block" 
                  on:click={() => handleDelete(subject.id, subject.name)}
                >
                  Delete
                </button>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Desktop Table View -->
        <div class="desktop-table-view">
          <div class="table-container">
            <table class="subjects-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Subject Name</th>
                  <th>Code</th>
                  <th>Created At</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each getFilteredSubjects() as subject}
                  <tr>
                    <td>{subject.id}</td>
                    <td>
                      <strong class="subject-name-cell">{subject.name}</strong>
                    </td>
                    <td>
                      {#if subject.code}
                        <span class="code-badge">{subject.code}</span>
                      {:else}
                        <span class="text-muted">N/A</span>
                      {/if}
                    </td>
                    <td>
                      {new Date(subject.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <span class="status-badge active">Active</span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          class="btn btn-secondary btn-sm" 
                          on:click={() => openEditForm(subject)}
                        >
                          Edit
                        </button>
                        <button 
                          class="btn btn-danger btn-sm" 
                          on:click={() => handleDelete(subject.id, subject.name)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Empty Search Results -->
        {#if searchTerm && getFilteredSubjects().length === 0}
          <div class="empty-search-results">
            <p>No subjects found for "<strong>{searchTerm}</strong>"</p>
            <button class="btn btn-secondary btn-sm" on:click={() => searchTerm = ''}>
              Clear Search
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<!-- Subject Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingSubject ? 'Edit Subject' : 'Create New Subject'}</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close">×</button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Subject Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Mathematics, English, Science"
            required
            autocomplete="off"
          />
          <div class="field-note">Enter the full subject name</div>
        </div>
        
        <div class="form-group">
          <label for="code">Subject Code</label>
          <input
            type="text"
            id="code"
            bind:value={formData.code}
            placeholder="e.g., MATH, ENG, SCI"
            autocomplete="off"
          />
          <div class="field-note">Short code (optional, usually 2-4 letters)</div>
        </div>
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-submit">
            {editingSubject ? 'Update Subject' : 'Create Subject'}
          </button>
          <button type="button" class="btn btn-secondary" on:click={closeForm}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  /* Base responsive styles */
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  .page-container {
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px;
  }
  
  /* Header */
  .header {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .header-left h1 {
    font-size: 1.8rem;
    color: #2c3e50;
    margin: 0 0 12px 0;
  }
  
  .header-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .stat-card {
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
  }
  
  .stat-number {
    font-size: 1.8rem;
    font-weight: 700;
    color: #9b59b6;
    line-height: 1;
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: #666;
    margin-top: 4px;
  }
  
  .header-actions {
    display: flex;
    justify-content: flex-end;
  }
  
  .btn {
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 44px;
  }
  
  .btn-primary {
    background: #9b59b6;
    color: white;
  }
  
  .btn-primary:hover {
    background: #8e44ad;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  .btn-sm {
    padding: 8px 16px;
    font-size: 0.875rem;
  }
  
  .btn-block {
    width: 100%;
    justify-content: center;
  }
  
  .btn-icon {
    font-size: 1.1rem;
  }
  
  /* Alerts */
  .alert {
    padding: 14px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }
  
  .alert-success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
  }
  
  .alert-error {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
  }
  
  .alert-icon {
    font-weight: bold;
    font-size: 1.1rem;
  }
  
  .alert-content {
    flex: 1;
  }
  
  /* Search and Filter */
  .filter-card {
    margin-bottom: 20px;
  }
  
  .search-container {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .search-icon {
    position: absolute;
    left: 16px;
    color: #666;
  }
  
  .search-input {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #9b59b6;
    box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.2);
  }
  
  .btn-clear-search {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
  
  /* Cards */
  .card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 20px;
  }
  
  .card-title {
    font-size: 1.2rem;
    color: #2c3e50;
    margin: 0 0 20px 0;
  }
  
  /* Subject Cards (Mobile) */
  .mobile-cards-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .subject-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    border-left: 4px solid #9b59b6;
    transition: all 0.2s;
  }
  
  .subject-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }
  
  .subject-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .subject-id {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .subject-code {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
  }
  
  .subject-card-body {
    margin-bottom: 16px;
  }
  
  .subject-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
  }
  
  .subject-meta {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.875rem;
    color: #666;
  }
  
  .meta-icon {
    font-size: 1rem;
  }
  
  .subject-card-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  /* Desktop Table View */
  .desktop-table-view {
    display: none;
  }
  
  .table-container {
    width: 100%;
    overflow-x: auto;
  }
  
  .subjects-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .subjects-table th {
    background: #f8f9fa;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .subjects-table td {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .subjects-table tr:last-child td {
    border-bottom: none;
  }
  
  .subjects-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .subject-name-cell {
    color: #2c3e50;
  }
  
  .code-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
    display: inline-block;
  }
  
  .text-muted {
    color: #999;
  }
  
  .status-badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
  }
  
  .status-badge.active {
    background: #d4edda;
    color: #155724;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  /* Empty Search Results */
  .empty-search-results {
    text-align: center;
    padding: 30px 20px;
    border-top: 1px solid #e9ecef;
    margin-top: 20px;
  }
  
  .empty-search-results p {
    color: #666;
    margin-bottom: 16px;
  }
  
  /* Loading State */
  .loading-container {
    padding: 40px 20px;
    text-align: center;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #9b59b6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* Empty State */
  .empty-state {
    padding: 48px 24px;
    text-align: center;
  }
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-state h3 {
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 1.3rem;
  }
  
  .empty-state p {
    color: #666;
    margin-bottom: 24px;
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
    padding: 16px;
    backdrop-filter: blur(4px);
  }
  
  .modal-content {
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    animation: modalSlideIn 0.3s ease-out;
  }
  
  @keyframes modalSlideIn {
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
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h2 {
    font-size: 1.5rem;
    color: #2c3e50;
    margin: 0;
  }
  
  .btn-close {
    background: none;
    border: none;
    font-size: 28px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
  
  /* Form */
  .form-group {
    margin-bottom: 24px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.95rem;
  }
  
  input[type="text"] {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
  }
  
  input:focus {
    outline: none;
    border-color: #9b59b6;
    box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.2);
  }
  
  .field-note {
    font-size: 0.875rem;
    color: #666;
    margin-top: 6px;
  }
  
  .modal-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 32px;
  }
  
  .btn-submit {
    padding: 14px 20px;
    font-weight: 600;
    font-size: 1rem;
  }
  
  /* Media Queries */
  @media (min-width: 768px) {
    .container {
      padding: 24px;
    }
    
    .header {
      flex-direction: row;
      justify-content: space-between;
      align-items: flex-start;
    }
    
    .header-left {
      flex: 1;
    }
    
    .header-stats {
      grid-template-columns: repeat(3, 140px);
      gap: 16px;
    }
    
    .stat-number {
      font-size: 2rem;
    }
    
    .modal-actions {
      flex-direction: row;
    }
    
    .btn-submit {
      flex: 2;
    }
    
    .mobile-cards-view {
      display: none;
    }
    
    .desktop-table-view {
      display: block;
    }
  }
  
  @media (min-width: 1024px) {
    .container {
      padding: 32px;
    }
    
    .header-left h1 {
      font-size: 2rem;
    }
    
    .modal-content {
      max-width: 500px;
    }
  }
  
  @media (max-width: 480px) {
    .container {
      padding: 12px;
    }
    
    .header-left h1 {
      font-size: 1.4rem;
    }
    
    .stat-card {
      padding: 12px;
    }
    
    .stat-number {
      font-size: 1.5rem;
    }
    
    .subject-card {
      padding: 16px;
    }
    
    .subject-name {
      font-size: 1.1rem;
    }
    
    .subject-card-actions {
      grid-template-columns: 1fr;
    }
    
    .modal-content {
      padding: 20px;
    }
    
    .modal-header h2 {
      font-size: 1.3rem;
    }
    
    input[type="text"] {
      padding: 12px 14px;
    }
  }
  
  /* Touch improvements */
  button, 
  input[type="text"] {
    min-height: 44px; /* Minimum touch target */
  }
  
  button {
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  
  /* Responsive text sizing */
  @media (max-width: 320px) {
    .btn-text {
      font-size: 0.9rem;
    }
    
    .stat-number {
      font-size: 1.3rem;
    }
    
    .subject-name {
      font-size: 1rem;
    }
  }
</style>