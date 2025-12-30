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
  let teacherStats = {};
  
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
      
      teachers = teachersData;
      assignments = assignmentsData;
      subjects = subjectsData;
      classes = classesData;
      
      // Calculate statistics
      calculateTeacherStats();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function loadTeachers() {
    try {
      loading = true;
      error = '';
      teachers = await teachersAPI.getAll();
      calculateTeacherStats();
    } catch (err) {
      error = 'Failed to load teachers';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function calculateTeacherStats() {
    const stats = {
      totalTeachers: teachers.length,
      activeTeachers: teachers.length,
      teachersWithAssignments: [],
      totalAssignments: 0
    };
    
    // Calculate assignments per teacher
    teachers.forEach(teacher => {
      const teacherAssignments = assignments.filter(a => a.teacher_id === teacher.id);
      if (teacherAssignments.length > 0) {
        stats.teachersWithAssignments.push({
          id: teacher.id,
          name: `${teacher.first_name} ${teacher.last_name}`,
          assignmentCount: teacherAssignments.length
        });
      }
      stats.totalAssignments += teacherAssignments.length;
    });
    
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
    const hasAssignments = assignments.some(a => a.teacher_id === id);
    
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
    teacherAssignments = assignments.filter(a => a.teacher_id === teacher.id);
    showAssignmentsModal = true;
  }
  
  function closeAssignmentsModal() {
    showAssignmentsModal = false;
    selectedTeacher = null;
    teacherAssignments = [];
  }
  
  function getTeacherAssignmentCount(teacherId) {
    return assignments.filter(a => a.teacher_id === teacherId).length;
  }
  
  function getFilteredTeachers() {
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
</script>

<div class="page-container">
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1>Manage Teachers</h1>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{teacherStats.totalTeachers}</div>
            <div class="stat-label">Total Teachers</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{teacherStats.teachersWithAssignments.length}</div>
            <div class="stat-label">With Assignments</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{teacherStats.totalAssignments}</div>
            <div class="stat-label">Total Assignments</div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" on:click={openCreateForm}>
          <span class="btn-icon">+</span>
          <span class="btn-text">Add Teacher</span>
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
          placeholder="Search teachers by name, email, or phone..."
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
        <p>Loading teachers...</p>
      </div>
      
    <!-- Empty State -->
    {:else if teachers.length === 0}
      <div class="card text-center empty-state">
        <div class="empty-icon">👨‍🏫</div>
        <h3>No Teachers Found</h3>
        <p>Create your first teacher to get started!</p>
        <button class="btn btn-primary" on:click={openCreateForm}>
          Create First Teacher
        </button>
      </div>
      
    <!-- Teachers List -->
    {:else}
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {#if searchTerm}
              Search Results ({getFilteredTeachers().length})
            {:else}
              All Teachers ({teachers.length})
            {/if}
          </h3>
        </div>
        
        <!-- Mobile Card View -->
        <div class="mobile-cards-view">
          {#each getFilteredTeachers() as teacher (teacher.id)}
            <div class="teacher-card">
              <div class="teacher-card-header">
                <div class="teacher-id">#{teacher.id}</div>
                {#if getTeacherAssignmentCount(teacher.id) > 0}
                  <div class="teacher-assignments">
                    {getTeacherAssignmentCount(teacher.id)} assignment(s)
                  </div>
                {/if}
              </div>
              <div class="teacher-card-body">
                <h3 class="teacher-name">{teacher.first_name} {teacher.last_name}</h3>
                <div class="teacher-info">
                  <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{teacher.email}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Phone:</span>
                    <span class="info-value">{teacher.phone || 'N/A'}</span>
                  </div>
                </div>
                <div class="teacher-meta">
                  <span class="meta-item">
                    <span class="meta-icon">📅</span>
                    Joined: {new Date(teacher.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div class="teacher-card-actions">
                {#if getTeacherAssignmentCount(teacher.id) > 0}
                  <button 
                    class="btn btn-info btn-block" 
                    on:click={() => openAssignmentsModal(teacher)}
                  >
                    View Assignments
                  </button>
                {/if}
                <button 
                  class="btn btn-secondary btn-block" 
                  on:click={() => openEditForm(teacher)}
                >
                  Edit
                </button>
                <button 
                  class="btn btn-danger btn-block" 
                  on:click={() => handleDelete(teacher.id, `${teacher.first_name} ${teacher.last_name}`)}
                  disabled={getTeacherAssignmentCount(teacher.id) > 0}
                  class:disabled={getTeacherAssignmentCount(teacher.id) > 0}
                >
                  {getTeacherAssignmentCount(teacher.id) > 0 ? 'Has Assignments' : 'Delete'}
                </button>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Desktop Table View -->
        <div class="desktop-table-view">
          <div class="table-container">
            <table class="teachers-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Assignments</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each getFilteredTeachers() as teacher (teacher.id)}
                  <tr>
                    <td>{teacher.id}</td>
                    <td>
                      <strong class="teacher-name-cell">{teacher.first_name} {teacher.last_name}</strong>
                    </td>
                    <td>{teacher.email}</td>
                    <td>
                      {#if teacher.phone}
                        <span class="phone-badge">{teacher.phone}</span>
                      {:else}
                        <span class="text-muted">N/A</span>
                      {/if}
                    </td>
                    <td>
                      {#if getTeacherAssignmentCount(teacher.id) > 0}
                        <button 
                          class="btn btn-info btn-sm" 
                          on:click={() => openAssignmentsModal(teacher)}
                        >
                          {getTeacherAssignmentCount(teacher.id)} assignment(s)
                        </button>
                      {:else}
                        <span class="text-muted">None</span>
                      {/if}
                    </td>
                    <td>
                      {new Date(teacher.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          class="btn btn-secondary btn-sm" 
                          on:click={() => openEditForm(teacher)}
                        >
                          Edit
                        </button>
                        <button 
                          class="btn btn-danger btn-sm" 
                          on:click={() => handleDelete(teacher.id, `${teacher.first_name} ${teacher.last_name}`)}
                          disabled={getTeacherAssignmentCount(teacher.id) > 0}
                          class:disabled={getTeacherAssignmentCount(teacher.id) > 0}
                        >
                          {getTeacherAssignmentCount(teacher.id) > 0 ? 'Has Assignments' : 'Delete'}
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
        {#if searchTerm && getFilteredTeachers().length === 0}
          <div class="empty-search-results">
            <p>No teachers found for "<strong>{searchTerm}</strong>"</p>
            <button class="btn btn-secondary btn-sm" on:click={() => searchTerm = ''}>
              Clear Search
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<!-- Teacher Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={handleModalOverlayClick}>
    <div class="modal-content card">
      <div class="modal-header">
        <h2>{editingTeacher ? 'Edit Teacher' : 'Create New Teacher'}</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close modal">×</button>
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
              autocomplete="given-name"
            />
            <div class="field-note">Enter teacher's first name</div>
          </div>
          
          <div class="form-group">
            <label for="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              bind:value={formData.last_name}
              placeholder="Banda"
              required={!editingTeacher}
              autocomplete="family-name"
            />
            <div class="field-note">Enter teacher's last name</div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="email">Email *</label>
          <input
            type="email"
            id="email"
            bind:value={formData.email}
            placeholder="teacher@school.com"
            required={!editingTeacher}
            disabled={editingTeacher}
            autocomplete="email"
          />
          {#if editingTeacher}
            <div class="field-note">Email cannot be changed</div>
          {:else}
            <div class="field-note">Teacher will use this to login</div>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="phone">Phone Number</label>
          <input
            type="tel"
            id="phone"
            bind:value={formData.phone}
            placeholder="+265888123456"
            autocomplete="tel"
          />
          <div class="field-note">Optional phone number</div>
        </div>
        
        {#if !editingTeacher}
          <div class="form-group">
            <label for="password">Password *</label>
            <input
              type="password"
              id="password"
              bind:value={formData.password}
              placeholder="Enter password"
              required
              autocomplete="new-password"
            />
            <div class="field-note">Minimum 6 characters</div>
          </div>
        {/if}
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-submit">
            {editingTeacher ? 'Update Teacher' : 'Create Teacher'}
          </button>
          <button type="button" class="btn btn-secondary" on:click={closeForm}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Assignments Modal -->
{#if showAssignmentsModal && selectedTeacher}
  <div class="modal-overlay" on:click={handleAssignmentsModalOverlayClick}>
    <div class="modal-content card">
      <div class="modal-header">
        <h2>{selectedTeacher.first_name}'s Assignments</h2>
        <button class="btn btn-close" on:click={closeAssignmentsModal} aria-label="Close modal">×</button>
      </div>
      
      <div class="teacher-info-modal">
        <div class="info-row">
          <span class="info-label">Teacher:</span>
          <span class="info-value">{selectedTeacher.first_name} {selectedTeacher.last_name}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Email:</span>
          <span class="info-value">{selectedTeacher.email}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Total Assignments:</span>
          <span class="info-value">{teacherAssignments.length}</span>
        </div>
      </div>
      
      {#if teacherAssignments.length === 0}
        <div class="empty-assignments">
          <div class="empty-icon">📝</div>
          <p>This teacher has no assignments yet.</p>
        </div>
      {:else}
        <!-- Mobile Assignments View -->
        <div class="mobile-assignments-view">
          {#each teacherAssignments as assignment (assignment.id)}
            <div class="assignment-card">
              <div class="assignment-header">
                <span class="assignment-id">Assignment #{assignment.id}</span>
              </div>
              <div class="assignment-body">
                <h4 class="subject-name">{assignment.subject_name}</h4>
                <div class="assignment-details">
                  <div class="detail">
                    <span class="detail-label">Class:</span>
                    <span class="detail-value">{assignment.class_name}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-label">Term:</span>
                    <span class="detail-value">{assignment.term_name}</span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Desktop Assignments Table -->
        <div class="desktop-assignments-table">
          <div class="table-container">
            <table class="assignments-table">
              <thead>
                <tr>
                  <th>Assignment ID</th>
                  <th>Subject</th>
                  <th>Class</th>
                  <th>Term</th>
                </tr>
              </thead>
              <tbody>
                {#each teacherAssignments as assignment (assignment.id)}
                  <tr>
                    <td>#{assignment.id}</td>
                    <td><strong>{assignment.subject_name}</strong></td>
                    <td>{assignment.class_name}</td>
                    <td>{assignment.term_name}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
      
      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={closeAssignmentsModal}>
          Close
        </button>
      </div>
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
    color: #e67e22;
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
    background: #e67e22;
    color: white;
  }
  
  .btn-primary:hover {
    background: #d35400;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
  }
  
  .btn-info {
    background: #3498db;
    color: white;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  .btn-danger:disabled {
    background: #f5c6cb;
    color: #721c24;
    cursor: not-allowed;
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
    border-color: #e67e22;
    box-shadow: 0 0 0 3px rgba(230, 126, 34, 0.2);
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
  
  /* Teacher Cards (Mobile) */
  .mobile-cards-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .teacher-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    border-left: 4px solid #e67e22;
    transition: all 0.2s;
  }
  
  .teacher-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }
  
  .teacher-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .teacher-id {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .teacher-assignments {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .teacher-card-body {
    margin-bottom: 16px;
  }
  
  .teacher-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
  }
  
  .teacher-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }
  
  .info-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
  }
  
  .info-label {
    color: #666;
    font-weight: 500;
  }
  
  .info-value {
    color: #333;
    text-align: right;
  }
  
  .teacher-meta {
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
  
  .teacher-card-actions {
    display: grid;
    grid-template-columns: 1fr;
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
  
  .teachers-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .teachers-table th {
    background: #f8f9fa;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .teachers-table td {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .teachers-table tr:last-child td {
    border-bottom: none;
  }
  
  .teachers-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .teacher-name-cell {
    color: #2c3e50;
  }
  
  .phone-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
  }
  
  .text-muted {
    color: #999;
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
    border-top: 3px solid #e67e22;
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
    max-width: 600px;
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
  
  /* Teacher Info Modal */
  .teacher-info-modal {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
  }
  
  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .info-row:last-child {
    margin-bottom: 0;
  }
  
  .info-label {
    font-weight: 500;
    color: #666;
  }
  
  .info-value {
    font-weight: 600;
    color: #2c3e50;
  }
  
  /* Assignments Modal */
  .empty-assignments {
    text-align: center;
    padding: 40px 20px;
  }
  
  .empty-assignments .empty-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }
  
  .empty-assignments p {
    color: #666;
  }
  
  .mobile-assignments-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 20px;
  }
  
  .assignment-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    border-left: 4px solid #3498db;
  }
  
  .assignment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .assignment-id {
    font-size: 0.875rem;
    color: #666;
  }
  
  .assignment-body {
    margin-bottom: 12px;
  }
  
  .subject-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
  }
  
  .assignment-details {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  
  .detail {
    display: flex;
    justify-content: space-between;
  }
  
  .detail-label {
    font-size: 0.875rem;
    color: #666;
  }
  
  .detail-value {
    font-size: 0.875rem;
    color: #333;
    font-weight: 500;
  }
  
  .desktop-assignments-table {
    display: none;
  }
  
  .assignments-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .assignments-table th {
    background: #f8f9fa;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
  }
  
  .assignments-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .assignments-table tr:last-child td {
    border-bottom: none;
  }
  
  .modal-footer {
    margin-top: 20px;
    text-align: right;
  }
  
  /* Form */
  .form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }
  
  .form-group {
    margin-bottom: 16px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.95rem;
  }
  
  input[type="text"],
  input[type="email"],
  input[type="tel"],
  input[type="password"] {
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
    border-color: #e67e22;
    box-shadow: 0 0 0 3px rgba(230, 126, 34, 0.2);
  }
  
  input:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
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
    
    .form-grid {
      grid-template-columns: 1fr 1fr;
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
    
    .mobile-assignments-view {
      display: none;
    }
    
    .desktop-assignments-table {
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
      max-width: 700px;
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
    
    .teacher-card {
      padding: 16px;
    }
    
    .teacher-name {
      font-size: 1.1rem;
    }
    
    .teacher-card-actions {
      grid-template-columns: 1fr;
    }
    
    .modal-content {
      padding: 20px;
    }
    
    .modal-header h2 {
      font-size: 1.3rem;
    }
    
    input {
      padding: 12px 14px;
    }
  }
  
  /* Touch improvements */
  button, 
  input {
    min-height: 44px; /* Minimum touch target */
  }
  
  button {
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
</style>