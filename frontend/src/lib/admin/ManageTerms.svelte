<script>
  import { onMount } from 'svelte';
  import { termsAPI } from '../adminAPI.js';
  
  let terms = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let showForm = false;
  let editingTerm = null;
  let formData = {
    name: '',
    year: new Date().getFullYear(),
    term_number: 1,
    start_date: '',
    end_date: '',
    is_active: false
  };
  
  onMount(() => {
    loadTerms();
  });
  
  async function loadTerms() {
    try {
      loading = true;
      error = '';
      terms = await termsAPI.getAll();
    } catch (err) {
      error = 'Failed to load terms';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function openCreateForm() {
    showForm = true;
    editingTerm = null;
    formData = {
      name: '',
      year: new Date().getFullYear(),
      term_number: 1,
      start_date: '',
      end_date: '',
      is_active: false
    };
  }
  
  function openEditForm(term) {
    showForm = true;
    editingTerm = term;
    formData = {
      name: term.name,
      year: term.year,
      term_number: term.term_number,
      start_date: term.start_date || '',
      end_date: term.end_date || '',
      is_active: term.is_active
    };
  }
  
  function closeForm() {
    showForm = false;
    editingTerm = null;
  }
  
  async function handleSubmit() {
    try {
      error = '';
      success = '';
      
      if (editingTerm) {
        await termsAPI.update(editingTerm.id, formData);
        success = 'Term updated successfully!';
      } else {
        await termsAPI.create(formData);
        success = 'Term created successfully!';
      }
      
      closeForm();
      await loadTerms();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Operation failed';
      console.error(err);
    }
  }
  
  async function handleActivate(id) {
    try {
      error = '';
      success = '';
      await termsAPI.activate(id);
      success = 'Term activated successfully!';
      await loadTerms();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Activation failed';
      console.error(err);
    }
  }
  
  async function handleDelete(id, name) {
    if (!confirm(`Are you sure you want to delete term "${name}"?`)) {
      return;
    }
    
    try {
      error = '';
      success = '';
      await termsAPI.delete(id);
      success = 'Term deleted successfully!';
      await loadTerms();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
</script>

<div class="container">
  <div class="flex-between mb-20">
    <h2>Manage Terms</h2>
    <button class="btn btn-primary" on:click={openCreateForm}>
      + Add New Term
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
      <p>Loading terms...</p>
    </div>
  {:else if terms.length === 0}
    <div class="card text-center">
      <p>No terms found. Create your first term!</p>
    </div>
  {:else}
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Term Name</th>
            <th>Year</th>
            <th>Term Number</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each terms as term}
            <tr style={term.is_active ? 'background-color: #e8f5e9;' : ''}>
              <td>{term.id}</td>
              <td><strong>{term.name}</strong></td>
              <td>{term.year}</td>
              <td>{term.term_number}</td>
              <td>
                {#if term.is_active}
                  <span style="color: green; font-weight: bold;">● Active</span>
                {:else}
                  <span style="color: gray;">○ Inactive</span>
                {/if}
              </td>
              <td>
                <div class="flex gap-10">
                  {#if !term.is_active}
                    <button 
                      class="btn btn-primary" 
                      style="padding: 5px 15px; background-color: #FF9800;"
                      on:click={() => handleActivate(term.id)}
                    >
                      Activate
                    </button>
                  {/if}
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => openEditForm(term)}
                  >
                    Edit
                  </button>
                  <button 
                    class="btn btn-danger" 
                    style="padding: 5px 15px;"
                    on:click={() => handleDelete(term.id, term.name)}
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
      <h2>{editingTerm ? 'Edit Term' : 'Create New Term'}</h2>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Term Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Term 1 2025"
            required
          />
        </div>
        
        <div class="grid grid-2">
          <div class="form-group">
            <label for="year">Year *</label>
            <input
              type="number"
              id="year"
              bind:value={formData.year}
              min="2020"
              max="2100"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="term_number">Term Number *</label>
            <input
              type="number"
              id="term_number"
              bind:value={formData.term_number}
              min="1"
              max="3"
              required
            />
          </div>
        </div>
        
        <div class="grid grid-2">
          <div class="form-group">
            <label for="start_date">Start Date</label>
            <input
              type="date"
              id="start_date"
              bind:value={formData.start_date}
            />
          </div>
          
          <div class="form-group">
            <label for="end_date">End Date</label>
            <input
              type="date"
              id="end_date"
              bind:value={formData.end_date}
            />
          </div>
        </div>
        
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              bind:checked={formData.is_active}
            />
            Set as Active Term
          </label>
        </div>
        
        <div class="flex gap-10">
          <button type="submit" class="btn btn-primary" style="flex: 1;">
            {editingTerm ? 'Update' : 'Create'}
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