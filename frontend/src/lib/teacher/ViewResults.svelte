<script>
  import { onMount } from 'svelte';
  import { teacherAPI } from '../teacherAPI.js';
  
  let results = [];
  let loading = true;
  let error = '';
  let success = '';
  
  let editingResult = null;
  let editMarks = 0;
  
  onMount(async () => {
    await loadResults();
  });
  
  async function loadResults() {
    try {
      loading = true;
      error = '';
      results = await teacherAPI.getMyResults();
    } catch (err) {
      error = 'Failed to load results';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function startEdit(result) {
    editingResult = result;
    editMarks = result.marks;
  }
  
  function cancelEdit() {
    editingResult = null;
    editMarks = 0;
  }
  
  async function saveEdit() {
    try {
      error = '';
      success = '';
      
      if (editMarks < 0 || editMarks > 100) {
        error = 'Marks must be between 0 and 100';
        return;
      }
      
      await teacherAPI.updateResult(editingResult.id, { marks: editMarks });
      success = 'Result updated successfully!';
      
      cancelEdit();
      await loadResults();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Failed to update result';
      console.error(err);
    }
  }
</script>

<div class="container">
  <h2>Uploaded Results</h2>
  
  {#if success}
    <div class="alert alert-success">{success}</div>
  {/if}
  
  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}
  
  {#if loading}
    <div class="card text-center">
      <p>Loading results...</p>
    </div>
  {:else if results.length === 0}
    <div class="card text-center">
      <p>You haven't uploaded any results yet.</p>
    </div>
  {:else}
    <div class="overflow-x: auto;">
      <table style="min-width: 600px;">
        <thead>
          <tr>
            <th>Student</th>
            <th>Subject</th>
            <th>Term</th>
            <th>Marks</th>
            <th>Uploaded</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each results as result}
            <tr>
              <td><strong>{result.student_name}</strong></td>
              <td>{result.subject_name}</td>
              <td>{result.term_name}</td>
              <td>
                {#if editingResult && editingResult.id === result.id}
                  <input
                    type="number"
                    bind:value={editMarks}
                    min="0"
                    max="100"
                    step="0.5"
                    style="width: 100px; padding: 5px;"
                  />
                {:else}
                  {result.marks}
                {/if}
              </td>
              <td>{new Date(result.uploaded_at).toLocaleString()}</td>
              <td>
                {#if editingResult && editingResult.id === result.id}
                  <div class="flex gap-10">
                    <button 
                      class="btn btn-primary" 
                      style="padding: 5px 15px;"
                      on:click={saveEdit}
                    >
                      Save
                    </button>
                    <button 
                      class="btn btn-secondary" 
                      style="padding: 5px 15px;"
                      on:click={cancelEdit}
                    >
                      Cancel
                    </button>
                  </div>
                {:else}
                  <button 
                    class="btn btn-secondary" 
                    style="padding: 5px 15px;"
                    on:click={() => startEdit(result)}
                  >
                    Edit
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>