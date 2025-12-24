<script>
  import { onMount } from 'svelte';
  import { subjectsAPI } from '../adminAPI.js';
  
  let subjects = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let editingSubject = null;
  let formData = {
    name: '',
    code: ''
  };
  
  onMount(() => {
    loadSubjects();
  });
  
  async function loadSubjects() {
    try {
      loading = true;
      error = '';
      subjects = await subjectsAPI.getAll();
    } catch (err) {
      error = 'Failed to load subjects';
      console.error(err);
    } finally {
      loading = false;
    }
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
</script>

<div class="container">
  <div class="flex-between mb-20">
    <h2>Manage Subjects</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Subject
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
      <p>Loading subjects...</p>
    </div>
  {:else if subjects.length === 0}
    <div class="card text-center">
      <p>No subjects found. Create your first subject!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Subject Name</th>
            <th>Code</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each subjects as subject}
            <tr>
              <td>{subject.id}</td>
              <td><strong>{subject.name}</strong></td>
              <td>{subject.code || 'N/A'}</td>
              <td>{new Date(subject.created_at).toLocaleDateString()}</td>
              <td>
                <div class="flex gap-10">
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => openEditForm(subject)}
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-danger" 
                    style="padding: 5px 15px;"
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
  {/if}
</div>

{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <h2>{editingSubject ? 'Edit Subject' : 'Create New Subject'}</h2>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Subject Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Mathematics, English"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="code">Subject Code</label>
          <input
            type="text"
            id="code"
            bind:value={formData.code}
            placeholder="e.g., MATH, ENG"
          />
        </div>
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            {editingSubject ? 'Update' : 'Create'}
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
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
  }
</style>