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
  
  onMount(() => {
    loadData();
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
</script>

<div class="container">
  <div class="flex-between mb-20">
    <h2>Manage Teacher Assignments</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Assignment
    </button>
  </div>
  
  {#if success}
    <div class="alert alert-success">{success}</div>
  {/if}
  
  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}
  
  <!-- Filters -->
  <div class="card mb-20">
    <h3 style="margin-bottom: 15px;">Filter Assignments</h3>
    <div class="grid grid-3">
      <div class="form-group" style="margin-bottom: 0;">
        <label for="filter-teacher">Teacher</label>
        <select id="filter-teacher" bind:value={filterTeacherId} on:change={loadAssignments}>
          <option value={null}>All Teachers</option>
          {#each teachers as teacher}
            <option value={teacher.id}>{teacher.first_name} {teacher.last_name}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group" style="margin-bottom: 0;">
        <label for="filter-class">Class</label>
        <select id="filter-class" bind:value={filterClassId} on:change={loadAssignments}>
          <option value={null}>All Classes</option>
          {#each classes as cls}
            <option value={cls.id}>{cls.name}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group" style="margin-bottom: 0;">
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
      <button class="btn btn-secondary mt-20" style="padding: 8px 15px;" on:click={clearFilters}>
        Clear Filters
      </button>
    {/if}
  </div>
  
  {#if loading}
    <div class="card text-center">
      <p>Loading assignments...</p>
    </div>
  {:else if assignments.length === 0}
    <div class="card text-center">
      <p>No assignments found. Create your first assignment!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Teacher</th>
            <th>Subject</th>
            <th>Class</th>
            <th>Term</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each assignments as assignment}
            <tr>
              <td>{assignment.id}</td>
              <td>{assignment.teacher_name}</td>
              <td><strong>{assignment.subject_name}</strong></td>
              <td>{assignment.class_name}</td>
              <td>{assignment.term_name}</td>
              <td>
                <button 
                  class="btn btn-danger" 
                  style="padding: 5px 15px;"
                  on:click={() => handleDelete(
                    assignment.id, 
                    `${assignment.teacher_name} - ${assignment.subject_name} - ${assignment.class_name}`
                  )}
                >
                  Delete
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <h2>Create New Assignment</h2>
      <p style="color: #666; margin-bottom: 20px;">
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
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            Create Assignment
          </button>
          <button type="button" class="btn btn-secondary" style="flex: 1;" on:click={closeForm}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
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
  }
  
  .modal-content {
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
  }
</style>