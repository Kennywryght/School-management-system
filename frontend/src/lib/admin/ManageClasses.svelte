<script>
  import { onMount } from 'svelte';
  import { classesAPI, studentsAPI } from '../adminAPI.js';
  
  let classes = [];
  let allStudents = [];
  let loading = true;
  let error = '';
  let success = '';
  
  // Form state
  let showForm = false;
  let editingClass = null;
  let formData = {
    name: '',
    level: 1
  };
  
  // Student display state
  let selectedClass = null;
  let classStudents = [];
  let showStudentsModal = false;
  
  // Student counts
  let studentCounts = {};
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load classes and students in parallel
      const [classesData, studentsData] = await Promise.all([
        classesAPI.getAll(),
        studentsAPI.getAll()
      ]);
      
      classes = classesData;
      allStudents = studentsData;
      
      // Calculate student counts
      calculateStudentCounts();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function calculateStudentCounts() {
    studentCounts = {};
    
    // Initialize all classes with 0
    classes.forEach(cls => {
      studentCounts[cls.id] = 0;
    });
    
    // Count students per class
    allStudents.forEach(student => {
      if (student.class_id) {
        studentCounts[student.class_id] = (studentCounts[student.class_id] || 0) + 1;
      }
    });
  }
  
  async function loadClasses() {
    try {
      loading = true;
      error = '';
      classes = await classesAPI.getAll();
      calculateStudentCounts();
    } catch (err) {
      error = 'Failed to load classes';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function loadStudentsForClass(classId) {
    try {
      selectedClass = classes.find(c => c.id === classId);
      classStudents = allStudents.filter(student => student.class_id === classId);
      showStudentsModal = true;
    } catch (err) {
      error = 'Failed to load students for class';
      console.error(err);
    }
  }
  
  function openCreateForm() {
    showForm = true;
    editingClass = null;
    formData = { name: '', level: 1 };
  }
  
  function openEditForm(cls) {
    showForm = true;
    editingClass = cls;
    formData = { name: cls.name, level: cls.level };
  }
  
  function closeForm() {
    showForm = false;
    editingClass = null;
    formData = { name: '', level: 1 };
  }
  
  function closeStudentsModal() {
    showStudentsModal = false;
    selectedClass = null;
    classStudents = [];
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      if (editingClass) {
        await classesAPI.update(editingClass.id, formData);
        success = 'Class updated successfully!';
      } else {
        await classesAPI.create(formData);
        success = 'Class created successfully!';
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
    // Check if class has students
    const studentCount = studentCounts[id] || 0;
    
    if (studentCount > 0) {
      error = `Cannot delete class "${name}" because it has ${studentCount} student(s).`;
      setTimeout(() => { error = ''; }, 5000);
      return;
    }
    
    if (!confirm(`Are you sure you want to delete class "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await classesAPI.delete(id);
      success = 'Class deleted successfully!';
      await loadClasses();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
</script>

<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <h1>Manage Classes</h1>
      <div class="header-stats">
        <div class="stat-card">
          <div class="stat-number">{classes.length}</div>
          <div class="stat-label">Total Classes</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{allStudents.length}</div>
          <div class="stat-label">Total Students</div>
        </div>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn btn-primary" on:click={openCreateForm}>
        <span class="btn-icon">+</span>
        <span class="btn-text">Add Class</span>
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
  
  <!-- Class Statistics -->
  {#if classes.length > 0}
    <div class="card statistics-card">
      <h3 class="card-title">Class Statistics</h3>
      <div class="stats-summary">
        <div class="summary-item">
          <span class="summary-label">Classes with Students:</span>
          <span class="summary-value">
            {classes.filter(c => studentCounts[c.id] > 0).length} / {classes.length}
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Total Students Assigned:</span>
          <span class="summary-value">
            {Object.values(studentCounts).reduce((a, b) => a + b, 0)}
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">Unassigned Students:</span>
          <span class="summary-value">
            {allStudents.filter(s => !s.class_id).length}
          </span>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Main Content -->
  {#if loading}
    <div class="card text-center loading-container">
      <div class="spinner"></div>
      <p>Loading classes...</p>
    </div>
    
  <!-- Empty State -->
  {:else if classes.length === 0}
    <div class="card text-center empty-state">
      <div class="empty-icon">🏫</div>
      <h3>No Classes Found</h3>
      <p>Create your first class to get started!</p>
      <button class="btn btn-primary" on:click={openCreateForm}>
        Create First Class
      </button>
    </div>
    
  <!-- Classes List -->
  {:else}
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Classes List ({classes.length})</h3>
      </div>
      
      <!-- Mobile Card View -->
      <div class="mobile-cards-view">
        {#each classes as cls}
          <div 
            class="class-card {studentCounts[cls.id] > 0 ? 'has-students' : ''}" 
            on:click={() => studentCounts[cls.id] > 0 && loadStudentsForClass(cls.id)}
            class:clickable={studentCounts[cls.id] > 0}
          >
            <div class="class-card-header">
              <div class="class-id">#{cls.id}</div>
              <div class="class-level">Level {cls.level}</div>
            </div>
            <div class="class-card-body">
              <h3 class="class-name">{cls.name}</h3>
              <div class="student-count-display">
                <div class="student-count-badge">
                  <span class="count-number">{studentCounts[cls.id] || 0}</span>
                  <span class="count-label">
                    {studentCounts[cls.id] === 1 ? 'student' : 'students'}
                  </span>
                </div>
                {#if studentCounts[cls.id] > 0}
                  <span class="view-students">View students →</span>
                {/if}
              </div>
              <p class="class-date">
                Created: {new Date(cls.created_at).toLocaleDateString()}
              </p>
            </div>
            <div class="class-card-actions">
              <button 
                class="btn btn-secondary btn-block" 
                on:click={() => openEditForm(cls)}
              >
                Edit
              </button>
              <button 
                class="btn btn-danger btn-block" 
                on:click={() => handleDelete(cls.id, cls.name)}
                disabled={studentCounts[cls.id] > 0}
                class:disabled={studentCounts[cls.id] > 0}
              >
                {studentCounts[cls.id] > 0 ? 'Has Students' : 'Delete'}
              </button>
            </div>
          </div>
        {/each}
      </div>
      
      <!-- Desktop Table View -->
      <div class="desktop-table-view">
        <div class="table-container">
          <table class="classes-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Class Name</th>
                <th>Level</th>
                <th>Students</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each classes as cls}
                <tr class:has-students={studentCounts[cls.id] > 0}>
                  <td>{cls.id}</td>
                  <td>
                    <strong>{cls.name}</strong>
                  </td>
                  <td>
                    <span class="level-badge">Level {cls.level}</span>
                  </td>
                  <td>
                    <div 
                      class="student-count-cell {studentCounts[cls.id] > 0 ? 'clickable' : ''}" 
                      on:click={() => studentCounts[cls.id] > 0 && loadStudentsForClass(cls.id)}
                    >
                      <div class="student-count-display">
                        <div class="student-count-badge">
                          <span class="count-number">{studentCounts[cls.id] || 0}</span>
                          <span class="count-label">
                            {studentCounts[cls.id] === 1 ? 'student' : 'students'}
                          </span>
                        </div>
                        {#if studentCounts[cls.id] > 0}
                          <span class="view-students">View →</span>
                        {/if}
                      </div>
                    </div>
                  </td>
                  <td>
                    {new Date(cls.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button 
                        class="btn btn-secondary btn-sm" 
                        on:click={() => openEditForm(cls)}
                      >
                        Edit
                      </button>
                      <button 
                        class="btn btn-danger btn-sm" 
                        on:click={() => handleDelete(cls.id, cls.name)}
                        disabled={studentCounts[cls.id] > 0}
                        class:disabled={studentCounts[cls.id] > 0}
                      >
                        {studentCounts[cls.id] > 0 ? 'Has Students' : 'Delete'}
                      </button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Class Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingClass ? 'Edit Class' : 'Create New Class'}</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close">×</button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Class Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Form 1, Grade 10, Class A"
            required
            autocomplete="off"
          />
          <div class="field-note">Enter the class name</div>
        </div>
        
        <div class="form-group">
          <label for="level">Level *</label>
          <input
            type="number"
            id="level"
            bind:value={formData.level}
            min="1"
            max="12"
            required
            class="level-input"
          />
          <div class="field-note">Enter level between 1-12</div>
        </div>
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-submit">
            {editingClass ? 'Update Class' : 'Create Class'}
          </button>
          <button type="button" class="btn btn-secondary" on:click={closeForm}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Students in Class Modal -->
{#if showStudentsModal && selectedClass}
  <div class="modal-overlay" on:click={closeStudentsModal}>
    <div class="modal-content card" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Students in {selectedClass.name}</h2>
        <button class="btn btn-close" on:click={closeStudentsModal} aria-label="Close">×</button>
      </div>
      
      <div class="class-info">
        <div class="info-row">
          <span class="info-label">Class:</span>
          <span class="info-value">{selectedClass.name}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Level:</span>
          <span class="info-value">Level {selectedClass.level}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Total Students:</span>
          <span class="info-value">{classStudents.length}</span>
        </div>
      </div>
      
      {#if classStudents.length === 0}
        <div class="empty-students">
          <div class="empty-icon">👨‍🎓</div>
          <p>No students assigned to this class yet.</p>
        </div>
      {:else}
        <!-- Mobile Students View -->
        <div class="mobile-students-view">
          {#each classStudents as student}
            <div class="student-item">
              <div class="student-item-header">
                <span class="student-id">#{student.id}</span>
                <span class="student-admission">{student.admission_number}</span>
              </div>
              <div class="student-item-body">
                <h4 class="student-name">{student.first_name} {student.last_name}</h4>
                <div class="student-details">
                  <span class="detail">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{student.email}</span>
                  </span>
                  <span class="detail">
                    <span class="detail-label">Gender:</span>
                    <span class="detail-value gender-badge {student.gender?.toLowerCase()}">
                      {student.gender || 'N/A'}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Desktop Students Table -->
        <div class="desktop-students-table">
          <div class="table-container">
            <table class="students-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Admission #</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Gender</th>
                </tr>
              </thead>
              <tbody>
                {#each classStudents as student}
                  <tr>
                    <td>{student.id}</td>
                    <td>{student.admission_number}</td>
                    <td>{student.first_name} {student.last_name}</td>
                    <td>{student.email}</td>
                    <td>
                      <span class="gender-badge {student.gender?.toLowerCase()}">
                        {student.gender || 'N/A'}
                      </span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
      
      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={closeStudentsModal}>
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
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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
    font-size: 2rem;
    font-weight: 700;
    color: #3498db;
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
    background: #28a745;
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
  
  /* Statistics Card */
  .statistics-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .statistics-card .card-title {
    color: white;
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 16px;
  }
  
  .stats-summary {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .summary-item:last-child {
    border-bottom: none;
  }
  
  .summary-label {
    font-size: 0.95rem;
    opacity: 0.9;
  }
  
  .summary-value {
    font-weight: 700;
    font-size: 1.1rem;
  }
  
  /* Class Cards (Mobile) */
  .mobile-cards-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .class-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    transition: all 0.2s;
  }
  
  .class-card.has-students {
    border-color: #e8f4fc;
  }
  
  .class-card.clickable {
    cursor: pointer;
  }
  
  .class-card.clickable:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    border-color: #3498db;
  }
  
  .class-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .class-id {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .class-level {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .class-card-body {
    margin-bottom: 16px;
  }
  
  .class-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
  }
  
  .student-count-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .student-count-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #e8f4fc;
    color: #2980b9;
    padding: 6px 12px;
    border-radius: 20px;
  }
  
  .count-number {
    font-weight: 700;
    font-size: 1.2rem;
  }
  
  .count-label {
    font-size: 0.875rem;
  }
  
  .view-students {
    font-size: 0.875rem;
    color: #3498db;
    font-weight: 500;
  }
  
  .class-date {
    font-size: 0.875rem;
    color: #666;
  }
  
  .class-card-actions {
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
  
  .classes-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .classes-table th {
    background: #f8f9fa;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .classes-table td {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .classes-table tr:last-child td {
    border-bottom: none;
  }
  
  .classes-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .classes-table tr.has-students:hover {
    background-color: #e8f4fc;
  }
  
  .level-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
  }
  
  .student-count-cell {
    cursor: default;
  }
  
  .student-count-cell.clickable {
    cursor: pointer;
  }
  
  .student-count-cell.clickable:hover .student-count-badge {
    background: #3498db;
    color: white;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
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
    border-top: 3px solid #3498db;
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
  
  /* Class Info */
  .class-info {
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
  
  /* Students in Class */
  .empty-students {
    text-align: center;
    padding: 40px 20px;
  }
  
  .empty-students .empty-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }
  
  .empty-students p {
    color: #666;
  }
  
  .mobile-students-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;
  }
  
  .student-item {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    border-left: 4px solid #3498db;
  }
  
  .student-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .student-id {
    font-size: 0.875rem;
    color: #666;
  }
  
  .student-admission {
    background: #e8f4fc;
    color: #2980b9;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
  }
  
  .student-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
  }
  
  .student-details {
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
  }
  
  .desktop-students-table {
    display: none;
  }
  
  .students-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .students-table th {
    background: #f8f9fa;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
  }
  
  .students-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .students-table tr:last-child td {
    border-bottom: none;
  }
  
  .gender-badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-block;
  }
  
  .gender-badge.male {
    background: #d4edf9;
    color: #0056b3;
  }
  
  .gender-badge.female {
    background: #f9d4ed;
    color: #b30086;
  }
  
  .modal-footer {
    margin-top: 20px;
    text-align: right;
  }
  
  /* Form */
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
  input[type="number"] {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
  }
  
  input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
  }
  
  .field-note {
    font-size: 0.875rem;
    color: #666;
    margin-top: 6px;
  }
  
  .level-input {
    width: 100%;
    max-width: 200px;
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
      grid-template-columns: repeat(2, 150px);
      gap: 16px;
    }
    
    .stats-summary {
      grid-template-columns: repeat(3, 1fr);
      gap: 0;
    }
    
    .summary-item {
      flex-direction: column;
      align-items: flex-start;
      padding: 0 20px;
      border-bottom: none;
      border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .summary-item:last-child {
      border-right: none;
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
    
    .mobile-students-view {
      display: none;
    }
    
    .desktop-students-table {
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
    
    .class-card {
      padding: 16px;
    }
    
    .class-name {
      font-size: 1.1rem;
    }
    
    .class-card-actions {
      grid-template-columns: 1fr;
    }
    
    .modal-content {
      padding: 20px;
    }
    
    .modal-header h2 {
      font-size: 1.3rem;
    }
  }
</style>