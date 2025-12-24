<script>
  import { onMount } from 'svelte';
  import { teachersAPI } from '../adminAPI.js';
  
  let teachers = [];
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
  
  onMount(() => {
    loadTeachers();
  });
  
  async function loadTeachers() {
    try {
      loading = true;
      error = '';
      teachers = await teachersAPI.getAll();
    } catch (err) {
      error = 'Failed to load teachers';
      console.error(err);
    } finally {
      loading = false;
    }
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
      phone: teacher.phone,
      email: teacher.email,
      password: '' // Don't show password
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
        // Only send fields that are not empty for update
        const updateData = {};
        if (formData.first_name) updateData.first_name = formData.first_name;
        if (formData.last_name) updateData.last_name = formData.last_name;
        if (formData.phone) updateData.phone = formData.phone;
        
        await teachersAPI.update(editingTeacher.id, updateData);
        success = 'Teacher updated successfully!';
      } else {
        await teachersAPI.create(formData);
        success = 'Teacher created successfully!';
      }
      
      closeForm();
      await loadTeachers();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
    if (!confirm(`Are you sure you want to delete teacher "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await teachersAPI.delete(id);
      success = 'Teacher deleted successfully!';
      await loadTeachers();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
</script>

<div class="container">
  <div class="flex-between mb-20">
    <h2>Manage Teachers</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Teacher
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
      <p>Loading teachers...</p>
    </div>
  {:else if teachers.length === 0}
    <div class="card text-center">
      <p>No teachers found. Create your first teacher!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each teachers as teacher}
            <tr>
              <td>{teacher.id}</td>
              <td><strong>{teacher.first_name} {teacher.last_name}</strong></td>
              <td>{teacher.email}</td>
              <td>{teacher.phone || 'N/A'}</td>
              <td>{new Date(teacher.created_at).toLocaleDateString()}</td>
              <td>
                <div class="flex gap-10">
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => openEditForm(teacher)}
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-danger" 
                    style="padding: 5px 15px;"
                    on:click={() => handleDelete(teacher.id, `${teacher.first_name} ${teacher.last_name}`)}
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
      <h2>{editingTeacher ? 'Edit Teacher' : 'Create New Teacher'}</h2>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="grid grid-2">
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
          <label for="email">Email *</label>
          <input
            type="email"
            id="email"
            bind:value={formData.email}
            placeholder="teacher@school.com"
            required={!editingTeacher}
            disabled={editingTeacher}
          />
          {#if editingTeacher}
            <small style="color: #999;">Email cannot be changed</small>
          {/if}
        </div>
        
        <div class="form-group">
          <label for="phone">Phone</label>
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
              placeholder="Enter password"
              required
            />
          </div>
        {/if}
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            {editingTeacher ? 'Update' : 'Create'}
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