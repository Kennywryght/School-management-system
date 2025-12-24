<script>
  import { onMount } from 'svelte';
  import { classesAPI } from '../adminAPI.js';
  
  let classes = [];
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
  
  onMount(() => {
    loadClasses();
  });
  
  async function loadClasses() {
    try {
      loading = true;
      error = '';
      classes = await classesAPI.getAll();
    } catch (err) {
      error = 'Failed to load classes';
      console.error(err);
    } finally {
      loading = false;
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
      await loadClasses();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
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
  <div class="flex-between mb-20">
    <h2>Manage Classes</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Class
    </button>
  </div>
  
  {#if success}
    <div class="alert alert-success">
      {success}
    </div>
  {/if}
  
  {#if error}
    <div class="alert alert-error">
      {error}
    </div>
  {/if}
  
  {#if loading}
    <div class="card text-center">
      <p>Loading classes...</p>
    </div>
  {:else if classes.length === 0}
    <div class="card text-center">
      <p>No classes found. Create your first class!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Class Name</th>
            <th>Level</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each classes as cls}
            <tr>
              <td>{cls.id}</td>
              <td><strong>{cls.name}</strong></td>
              <td>{cls.level}</td>
              <td>{new Date(cls.created_at).toLocaleDateString()}</td>
              <td>
                <div class="flex gap-10">
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => openEditForm(cls)}
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-danger" 
                    style="padding: 5px 15px;"
                    on:click={() => handleDelete(cls.id, cls.name)}
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

<!-- Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={closeForm}>
    <div class="modal-content card" on:click|stopPropagation>
      <h2>{editingClass ? 'Edit Class' : 'Create New Class'}</h2>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Class Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Form 1, Form 2"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="level">Level *</label>
          <input
            type="number"
            id="level"
            bind:value={formData.level}
            min="1"
            max="10"
            required
          />
        </div>
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            {editingClass ? 'Update' : 'Create'}
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