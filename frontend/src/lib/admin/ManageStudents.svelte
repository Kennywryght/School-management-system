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
  
  onMount(() => {
    loadStudents();
    loadClasses();
  });
  
  async function loadStudents() {
    try {
      loading = true;
      error = '';
      students = await studentsAPI.getAll();
    } catch (err) {
      error = 'Failed to load students';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function loadClasses() {
    try {
      classes = await classesAPI.getAll();
    } catch (err) {
      console.error('Failed to load classes:', err);
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
</script>

<div class="container">
  <div class="flex-between mb-20">
    <h2>Manage Students</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Student
    </button>
  </div>
  
  {#if success}
    <div class="alert alert-success">{success}</div>
  {/if}
  
  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}
  
  {#if loading}
    <div class="card text-center">
      <p>Loading students...</p>
    </div>
  {:else if students.length === 0}
    <div class="card text-center">
      <p>No students found. Create your first student!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Admission #</th>
            <th>Name</th>
            <th>Email</th>
            <th>Class</th>
            <th>Gender</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each students as student}
            <tr>
              <td>{student.id}</td>
              <td><strong>{student.admission_number}</strong></td>
              <td>{student.first_name} {student.last_name}</td>
              <td>{student.email}</td>
              <td>{student.class_name || 'Not assigned'}</td>
              <td>{student.gender || 'N/A'}</td>
              <td>
                <div class="flex gap-10">
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => openEditForm(student)}
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-danger" 
                    style="padding: 5px 15px;"
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
  {/if}
</div>

{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <h2>{editingStudent ? 'Edit Student' : 'Create New Student'}</h2>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="grid grid-2">
          <div class="form-group">
            <label for="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              bind:value={formData.first_name}
              placeholder="Chisomo"
              required={!editingStudent}
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
            />
          </div>
        </div>
        
        <div class="grid grid-2">
          <div class="form-group">
            <label for="admission_number">Admission Number *</label>
            <input
              type="text"
              id="admission_number"
              bind:value={formData.admission_number}
              placeholder="STU001"
              required={!editingStudent}
            />
          </div>
          
          <div class="form-group">
            <label for="class_id">Class</label>
            <select id="class_id" bind:value={formData.class_id}>
              <option value={null}>Select Class</option>
              {#each classes as cls}
                <option value={cls.id}>{cls.name}</option>
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
          />
          {#if editingStudent}
            <small style="color: #999;">Email cannot be changed</small>
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
            />
          </div>
        {/if}
        
        <div class="grid grid-2">
          <div class="form-group">
            <label for="date_of_birth">Date of Birth</label>
            <input
              type="date"
              id="date_of_birth"
              bind:value={formData.date_of_birth}
            />
          </div>
          
          <div class="form-group">
            <label for="gender">Gender</label>
            <select id="gender" bind:value={formData.gender}>
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            {editingStudent ? 'Update' : 'Create'}
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
    max-width: 700px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
  }
</style>