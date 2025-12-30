<script>
  import { onMount } from 'svelte';
  import { teacherAPI } from '../teacherAPI.js';
  
  export let assignment;
  export let onBack;
  
  let students = [];
  let loading = true;
  let error = '';
  let success = '';
  let submitting = false;
  
  // Store marks for each student
  let marks = {};
  
  onMount(async () => {
    await loadStudents();
  });
  
  async function loadStudents() {
    try {
      loading = true;
      error = '';
      students = await teacherAPI.getStudentsInClass(assignment.class_id);
      
      // Initialize marks object
      students.forEach(student => {
        marks[student.id] = '';
      });
    } catch (err) {
      error = 'Failed to load students';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function handleSubmit() {
    try {
      submitting = true;
      error = '';
      success = '';
      
      // Prepare results array
      const results = [];
      for (let studentId in marks) {
        if (marks[studentId] !== '' && marks[studentId] !== null) {
          const markValue = parseFloat(marks[studentId]);
          if (markValue >= 0 && markValue <= 100) {
            results.push({
              student_id: parseInt(studentId),
              marks: markValue
            });
          }
        }
      }
      
      if (results.length === 0) {
        error = 'Please enter at least one mark';
        return;
      }
      
      // Upload bulk results
      const response = await teacherAPI.uploadBulkResults({
        subject_id: assignment.subject_id,
        term_id: assignment.term_id,
        class_id: assignment.class_id,
        results: results
      });
      
      success = `Successfully uploaded ${response.created} new results and updated ${response.updated} existing results!`;
      
      if (response.errors && response.errors.length > 0) {
        error = `Some errors occurred: ${response.errors.join(', ')}`;
      }
      
      // Clear form
      students.forEach(student => {
        marks[student.id] = '';
      });
      
    } catch (err) {
      error = err.response?.data?.detail || 'Failed to upload results';
      console.error(err);
    } finally {
      submitting = false;
    }
  }
  
  function validateMark(value) {
    if (value === '') return true;
    const num = parseFloat(value);
    return !isNaN(num) && num >= 0 && num <= 100;
  }
</script>

<div class="container">
  <button class="btn btn-secondary mb-20" on:click={onBack}>
    ← Back to Assignments
  </button>
  
  <div class="card" style="background: #4CAF50; color: white; margin-bottom: 20px;">
    <h2 style="margin: 0 0 10px 0;">Upload Results</h2>
    <p style="margin: 5px 0;"><strong>Subject:</strong> {assignment.subject_name}</p>
    <p style="margin: 5px 0;"><strong>Class:</strong> {assignment.class_name}</p>
    <p style="margin: 5px 0;"><strong>Term:</strong> {assignment.term_name}</p>
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
      <p>No students found in this class.</p>
    </div>
  {:else}
    <form on:submit|preventDefault={handleSubmit}>
      <div class="overflow-x: auto;">
        <h3>Enter Marks for Students</h3>
        <p style="color: #666; margin-bottom: 20px;">Enter marks between 0 and 100. Leave blank to skip.</p>
        
        <table style="min-width: 600px;">
          <thead>
            <tr>
              <th>Admission #</th>
              <th>Student Name</th>
              <th>Email</th>
              <th>Marks (0-100)</th>
            </tr>
          </thead>
          <tbody>
            {#each students as student}
              <tr>
                <td><strong>{student.admission_number}</strong></td>
                <td>{student.first_name} {student.last_name}</td>
                <td>{student.email}</td>
                <td>
                  <input
                    type="number"
                    bind:value={marks[student.id]}
                    min="0"
                    max="100"
                    step="0.5"
                    placeholder="Enter marks"
                    style="width: 150px; padding: 8px;"
                    class:invalid={!validateMark(marks[student.id])}
                  />
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      
      <div class="flex gap-10 mt-20">
        <button 
          type="submit" 
          class="btn btn-primary" 
          style="flex: 1;"
          disabled={submitting}
        >
          {submitting ? 'Uploading...' : 'Upload All Results'}
        </button>
        <button 
          type="button" 
          class="btn btn-secondary" 
          style="flex: 1;"
          on:click={onBack}
        >
          Cancel
        </button>
      </div>
    </form>
  {/if}
</div>

<style>
  .invalid {
    border: 2px solid #f44336 !important;
  }
</style>