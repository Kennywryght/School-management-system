<script>
  import { onMount } from 'svelte';
  import { studentsAPI, classesAPI } from '../adminAPI.js';
  
  let students = [];
  let classes = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let editingStudent = null;
  let formData = {
    first_name: '',
    last_name: '',
    admission_number: '',
    email: '',
    password: '',
    date_of_birth: '',
    gender: '',
    class_id: null
  };
  
  // Filter state
  let filterClassId = null;
  
  // Student counts per class
  let studentCounts = {};
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      
      // Load both students and classes
      const [studentsData, classesData] = await Promise.all([
        studentsAPI.getAll(),
        classesAPI.getAll()
      ]);
      
      students = studentsData;
      classes = classesData;
      
      // Calculate student counts per class
      calculateStudentCounts();
    } catch (err) {
      error = 'Failed to load data';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function calculateStudentCounts() {
    // Reset counts
    studentCounts = {};
    
    // Initialize all classes with 0
    classes.forEach(cls => {
      studentCounts[cls.id] = 0;
    });
    
    // Count students per class
    students.forEach(student => {
      if (student.class_id) {
        studentCounts[student.class_id] = (studentCounts[student.class_id] || 0) + 1;
      }
    });
    
    // Add "Not Assigned" count
    const notAssignedCount = students.filter(s => !s.class_id).length;
    studentCounts['not_assigned'] = notAssignedCount;
  }
  
  async function loadStudents() {
    try {
      loading = true;
      error = '';
      students = await studentsAPI.getAll();
      calculateStudentCounts();
    } catch (err) {
      error = 'Failed to load students';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function openCreateForm() {
    showForm = true;
    editingStudent = null;
    formData = {
      first_name: '',
      last_name: '',
      admission_number: '',
      email: '',
      password: '',
      date_of_birth: '',
      gender: '',
      class_id: null
    };
  }
  
  function openEditForm(student) {
    showForm = true;
    editingStudent = student;
    formData = {
      first_name: student.first_name,
      last_name: student.last_name,
      admission_number: student.admission_number,
      email: student.email,
      password: '',
      date_of_birth: student.date_of_birth || '',
      gender: student.gender || '',
      class_id: student.class_id
    };
  }
  
  function closeForm() {
    showForm = false;
    editingStudent = null;
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      if (editingStudent) {
        const updateData = {};
        if (formData.first_name) updateData.first_name = formData.first_name;
        if (formData.last_name) updateData.last_name = formData.last_name;
        if (formData.admission_number) updateData.admission_number = formData.admission_number;
        if (formData.date_of_birth) updateData.date_of_birth = formData.date_of_birth;
        if (formData.gender) updateData.gender = formData.gender;
        if (formData.class_id) updateData.class_id = parseInt(formData.class_id);
        
        await studentsAPI.update(editingStudent.id, updateData);
        success = 'Student updated successfully!';
      } else {
        const createData = {
          ...formData,
          class_id: formData.class_id ? parseInt(formData.class_id) : null
        };
        await studentsAPI.create(createData);
        success = 'Student created successfully!';
      }
      
      closeForm();
      await loadStudents();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
    if (!confirm(`Are you sure you want to delete student "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await studentsAPI.delete(id);
      success = 'Student deleted successfully!';
      await loadStudents();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
  
  function filterByClass(classId) {
    filterClassId = classId === filterClassId ? null : classId;
  }
  
  function clearFilter() {
    filterClassId = null;
  }
  
  function getFilteredStudents() {
    if (!filterClassId) return students;
    
    if (filterClassId === 'not_assigned') {
      return students.filter(s => !s.class_id);
    }
    
    return students.filter(s => s.class_id === filterClassId);
  }
  
  function getClassName(classId) {
    if (classId === 'not_assigned') return 'Not Assigned';
    const cls = classes.find(c => c.id === classId);
    return cls ? cls.name : 'Unknown Class';
  }
</script>

<div class="page-container">
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1>Manage Students</h1>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{students.length}</div>
            <div class="stat-label">Total Students</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{classes.length}</div>
            <div class="stat-label">Classes</div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" on:click={openCreateForm}>
          <span class="btn-icon">+</span>
          <span class="btn-text">Add Student</span>
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
    
    <!-- Class Statistics Section -->
    {#if classes.length > 0}
      <div class="card statistics-card">
        <h3 class="card-title">Student Distribution by Class</h3>
        <div class="stats-grid">
          <!-- Not Assigned -->
          <div 
            class="class-stat {filterClassId === 'not_assigned' ? 'active' : ''}" 
            on:click={() => filterByClass('not_assigned')}
          >
            <div class="class-stat-header">
              <span class="class-name">Not Assigned</span>
              <span class="student-count">{studentCounts['not_assigned'] || 0}</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                style={`width: ${(studentCounts['not_assigned'] / students.length * 100) || 0}%`}
              ></div>
            </div>
            <div class="percentage">
              {((studentCounts['not_assigned'] / students.length * 100) || 0).toFixed(1)}%
            </div>
          </div>
          
          <!-- Each Class -->
          {#each classes as cls}
            <div 
              class="class-stat {filterClassId === cls.id ? 'active' : ''}" 
              on:click={() => filterByClass(cls.id)}
            >
              <div class="class-stat-header">
                <span class="class-name">{cls.name}</span>
                <span class="student-count">{studentCounts[cls.id] || 0}</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  style={`width: ${(studentCounts[cls.id] / students.length * 100) || 0}%`}
                ></div>
              </div>
              <div class="percentage">
                {((studentCounts[cls.id] / students.length * 100) || 0).toFixed(1)}%
              </div>
            </div>
          {/each}
        </div>
        
        {#if filterClassId}
          <div class="filter-active">
            <span>Showing students from: <strong>{getClassName(filterClassId)}</strong></span>
            <button class="btn btn-secondary btn-sm" on:click={clearFilter}>
              Clear Filter
            </button>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Loading State -->
    {#if loading}
      <div class="card text-center loading-container">
        <div class="spinner"></div>
        <p>Loading students...</p>
      </div>
      
    <!-- Empty State -->
    {:else if students.length === 0}
      <div class="card text-center empty-state">
        <div class="empty-icon">👨‍🎓</div>
        <h3>No Students Found</h3>
        <p>Start by adding your first student to the system.</p>
        <button class="btn btn-primary" on:click={openCreateForm}>
          Add First Student
        </button>
      </div>
      
    <!-- Students List -->
    {:else}
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {#if filterClassId}
              Students in {getClassName(filterClassId)} ({getFilteredStudents().length})
            {:else}
              All Students ({students.length})
            {/if}
          </h3>
        </div>
        
        <!-- Mobile Card View -->
        <div class="mobile-cards-view">
          {#each getFilteredStudents() as student}
            <div class="student-card">
              <div class="student-card-header">
                <div class="student-id">#{student.id}</div>
                <div class="student-admission">{student.admission_number}</div>
              </div>
              <div class="student-card-body">
                <h3 class="student-name">{student.first_name} {student.last_name}</h3>
                <div class="student-info">
                  <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{student.email}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Class:</span>
                    <span class="info-value">
                      {student.class_name || 'Not assigned'}
                      {#if student.class_id}
                        <span class="class-student-count">
                          ({studentCounts[student.class_id] || 0} students)
                        </span>
                      {/if}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Gender:</span>
                    <span class="info-value gender-badge {student.gender?.toLowerCase()}">
                      {student.gender || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <div class="student-card-actions">
                <button 
                  class="btn btn-secondary btn-block" 
                  on:click={() => openEditForm(student)}
                >
                  Edit
                </button>
                <button 
                  class="btn btn-danger btn-block" 
                  on:click={() => handleDelete(student.id, `${student.first_name} ${student.last_name}`)}
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
            <table class="students-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Admission #</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Class</th>
                  <th>Students in Class</th>
                  <th>Gender</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each getFilteredStudents() as student}
                  <tr>
                    <td>{student.id}</td>
                    <td><strong>{student.admission_number}</strong></td>
                    <td>{student.first_name} {student.last_name}</td>
                    <td>{student.email}</td>
                    <td>
                      <span class="class-badge">
                        {student.class_name || 'Not assigned'}
                      </span>
                    </td>
                    <td>
                      {#if student.class_id}
                        <div class="class-count-display">
                          <span class="count-number">{studentCounts[student.class_id] || 0}</span>
                          <span class="count-label">students</span>
                        </div>
                      {:else}
                        <span class="text-muted">-</span>
                      {/if}
                    </td>
                    <td>
                      <span class="gender-badge {student.gender?.toLowerCase()}">
                        {student.gender || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          class="btn btn-secondary btn-sm" 
                          on:click={() => openEditForm(student)}
                        >
                          Edit
                        </button>
                        <button 
                          class="btn btn-danger btn-sm" 
                          on:click={() => handleDelete(student.id, `${student.first_name} ${student.last_name}`)}
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
      </div>
    {/if}
  </div>
</div>

<!-- Student Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{editingStudent ? 'Edit Student' : 'Create New Student'}</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close">×</button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-grid">
          <div class="form-group">
            <label for="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              bind:value={formData.first_name}
              placeholder="Chisomo"
              required={!editingStudent}
              autocomplete="given-name"
            />
          </div>
          
          <div class="form-group">
            <label for="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              bind:value={formData.last_name}
              placeholder="Nkhoma"
              required={!editingStudent}
              autocomplete="family-name"
            />
          </div>
          
          <div class="form-group">
            <label for="admission_number">Admission Number *</label>
            <input
              type="text"
              id="admission_number"
              bind:value={formData.admission_number}
              placeholder="STU001"
              required={!editingStudent}
              autocomplete="off"
            />
          </div>
          
          <div class="form-group">
            <label for="class_id">Class</label>
            <select id="class_id" bind:value={formData.class_id}>
              <option value={null}>Select Class</option>
              {#each classes as cls}
                <option value={cls.id}>
                  {cls.name} ({studentCounts[cls.id] || 0} students)
                </option>
              {/each}
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label for="email">Email *</label>
          <input
            type="email"
            id="email"
            bind:value={formData.email}
            placeholder="student@school.com"
            required={!editingStudent}
            disabled={editingStudent}
            autocomplete="email"
          />
          {#if editingStudent}
            <div class="field-note">Email cannot be changed</div>
          {/if}
        </div>
        
        {#if !editingStudent}
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
        
        <div class="form-grid">
          <div class="form-group">
            <label for="date_of_birth">Date of Birth</label>
            <input
              type="date"
              id="date_of_birth"
              bind:value={formData.date_of_birth}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
          
          <div class="form-group">
            <label for="gender">Gender</label>
            <select id="gender" bind:value={formData.gender}>
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-submit">
            {editingStudent ? 'Update Student' : 'Create Student'}
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
  
  .btn-primary:hover {
    background: #218838;
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
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .class-stat {
    background: rgba(255, 255, 255, 0.1);
    padding: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
  }
  
  .class-stat:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
  
  .class-stat.active {
    background: rgba(255, 255, 255, 0.2);
    border-color: white;
  }
  
  .class-stat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .class-name {
    font-weight: 600;
    font-size: 0.95rem;
  }
  
  .student-count {
    font-weight: 700;
    font-size: 1.2rem;
  }
  
  .progress-bar {
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
  }
  
  .progress-fill {
    height: 100%;
    background: white;
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  
  .percentage {
    text-align: right;
    font-size: 0.875rem;
    opacity: 0.8;
  }
  
  .filter-active {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  /* Student Cards (Mobile) */
  .mobile-cards-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .student-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e0e0e0;
  }
  
  .student-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .student-id {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .student-admission {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .student-card-body {
    margin-bottom: 16px;
  }
  
  .student-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
  }
  
  .student-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
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
  
  .class-student-count {
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-top: 2px;
  }
  
  /* Desktop Table View */
  .desktop-table-view {
    display: none;
  }
  
  .table-container {
    width: 100%;
    overflow-x: auto;
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
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .students-table td {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .students-table tr:last-child td {
    border-bottom: none;
  }
  
  .students-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .class-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
  }
  
  .gender-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
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
  
  .class-count-display {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  
  .count-number {
    font-weight: 700;
    color: #28a745;
    font-size: 1.1rem;
  }
  
  .count-label {
    color: #666;
    font-size: 0.875rem;
  }
  
  .text-muted {
    color: #999;
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
  input[type="password"],
  input[type="date"],
  select {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
  }
  
  input:focus,
  select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
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
      grid-template-columns: repeat(2, 150px);
      gap: 16px;
    }
    
    .stats-grid {
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px;
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
    
    .stats-grid {
      grid-template-columns: 1fr;
    }
    
    .student-card {
      padding: 16px;
    }
    
    .student-name {
      font-size: 1.1rem;
    }
    
    .student-card-actions {
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