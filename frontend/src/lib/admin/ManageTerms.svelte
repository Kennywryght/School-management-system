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
  
  // Statistics
  let termStats = {
    totalTerms: 0,
    activeTerms: 0,
    currentYearTerms: 0,
    upcomingTerms: 0
  };
  
  // Filter
  let searchTerm = '';
  let statusFilter = 'all';
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = '';
      terms = await termsAPI.getAll();
      calculateTermStats();
    } catch (err) {
      error = 'Failed to load terms';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function calculateTermStats() {
    const currentYear = new Date().getFullYear();
    const now = new Date();
    
    const stats = {
      totalTerms: terms.length,
      activeTerms: terms.filter(t => t.is_active).length,
      currentYearTerms: terms.filter(t => t.year === currentYear).length,
      upcomingTerms: terms.filter(t => {
        if (!t.start_date) return false;
        const startDate = new Date(t.start_date);
        return startDate > now;
      }).length
    };
    
    termStats = stats;
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
      await loadData();
      
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
      await loadData();
      
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
      await loadData();
      
      setTimeout(() => { success = ''; }, 3000);
    } catch (err) {
      error = err.response?.data?.detail || 'Delete failed';
      console.error(err);
    }
  }
  
  function getFilteredTerms() {
    let filtered = terms;
    
    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(term) ||
        t.year.toString().includes(term) ||
        t.term_number.toString().includes(term)
      );
    }
    
    // Apply status filter
    if (statusFilter === 'active') {
      filtered = filtered.filter(t => t.is_active);
    } else if (statusFilter === 'inactive') {
      filtered = filtered.filter(t => !t.is_active);
    }
    
    return filtered;
  }
  
  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  }
  
  function getTermStatus(term) {
    if (term.is_active) return 'Active';
    
    const now = new Date();
    if (term.start_date && new Date(term.start_date) > now) return 'Upcoming';
    if (term.end_date && new Date(term.end_date) < now) return 'Completed';
    
    return 'Inactive';
  }
  
  function getTermStatusColor(status) {
    switch (status) {
      case 'Active': return '#2ecc71';
      case 'Upcoming': return '#3498db';
      case 'Completed': return '#95a5a6';
      default: return '#7f8c8d';
    }
  }
  
  // Handle modal overlay click
  function handleModalOverlayClick(event) {
    if (event.target.classList.contains('modal-overlay')) {
      closeForm();
    }
  }
</script>

<div class="page-container">
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1>Manage Terms</h1>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-number">{termStats.totalTerms}</div>
            <div class="stat-label">Total Terms</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{termStats.activeTerms}</div>
            <div class="stat-label">Active Terms</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{termStats.upcomingTerms}</div>
            <div class="stat-label">Upcoming</div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" on:click={openCreateForm}>
          <span class="btn-icon">+</span>
          <span class="btn-text">Add Term</span>
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
    
    <!-- Search and Filter -->
    <div class="card filter-card">
      <div class="filter-grid">
        <div class="search-container">
          <div class="search-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8" stroke-width="2"/>
              <path d="M21 21l-4.35-4.35" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Search terms by name, year, or term number..."
            class="search-input"
          />
          {#if searchTerm}
            <button class="btn btn-clear-search" on:click={() => searchTerm = ''} aria-label="Clear search">
              ×
            </button>
          {/if}
        </div>
        
        <div class="filter-actions">
          <select bind:value={statusFilter} class="filter-select">
            <option value="all">All Status</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    {#if loading}
      <div class="card text-center loading-container">
        <div class="spinner"></div>
        <p>Loading terms...</p>
      </div>
      
    <!-- Empty State -->
    {:else if terms.length === 0}
      <div class="card text-center empty-state">
        <div class="empty-icon">📅</div>
        <h3>No Terms Found</h3>
        <p>Create your first term to get started!</p>
        <button class="btn btn-primary" on:click={openCreateForm}>
          Create First Term
        </button>
      </div>
      
    <!-- Terms List -->
    {:else}
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {#if searchTerm || statusFilter !== 'all'}
              Filtered Terms ({getFilteredTerms().length})
            {:else}
              All Terms ({terms.length})
            {/if}
          </h3>
        </div>
        
        <!-- Mobile Card View -->
        <div class="mobile-cards-view">
          {#each getFilteredTerms() as term (term.id)}
            <div class="term-card" class:active-term={term.is_active}>
              <div class="term-card-header">
                <div class="term-id">#{term.id}</div>
                <div 
                  class="term-status-badge" 
                  style="background-color: {getTermStatusColor(getTermStatus(term))}20; color: {getTermStatusColor(getTermStatus(term))};"
                >
                  {getTermStatus(term)}
                </div>
              </div>
              <div class="term-card-body">
                <h3 class="term-name">{term.name}</h3>
                <div class="term-info">
                  <div class="info-item">
                    <span class="info-label">Year:</span>
                    <span class="info-value">{term.year}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Term Number:</span>
                    <span class="info-value">{term.term_number}</span>
                  </div>
                </div>
                <div class="term-dates">
                  <div class="date-item">
                    <span class="date-icon">📅</span>
                    <div class="date-info">
                      <div class="date-label">Start Date</div>
                      <div class="date-value">{formatDate(term.start_date)}</div>
                    </div>
                  </div>
                  <div class="date-item">
                    <span class="date-icon">📅</span>
                    <div class="date-info">
                      <div class="date-label">End Date</div>
                      <div class="date-value">{formatDate(term.end_date)}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="term-card-actions">
                {#if !term.is_active}
                  <button 
                    class="btn btn-warning btn-block" 
                    on:click={() => handleActivate(term.id)}
                  >
                    Activate
                  </button>
                {/if}
                <button 
                  class="btn btn-secondary btn-block" 
                  on:click={() => openEditForm(term)}
                >
                  Edit
                </button>
                <button 
                  class="btn btn-danger btn-block" 
                  on:click={() => handleDelete(term.id, term.name)}
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
            <table class="terms-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Term Name</th>
                  <th>Year</th>
                  <th>Term No.</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each getFilteredTerms() as term (term.id)}
                  <tr class={term.is_active ? 'active-term-row' : ''}>
                    <td>{term.id}</td>
                    <td>
                      <strong class="term-name-cell">{term.name}</strong>
                    </td>
                    <td>{term.year}</td>
                    <td>
                      <span class="term-number-badge">{term.term_number}</span>
                    </td>
                    <td>{formatDate(term.start_date)}</td>
                    <td>{formatDate(term.end_date)}</td>
                    <td>
                      <span 
                        class="status-badge" 
                        style="background-color: {getTermStatusColor(getTermStatus(term))}20; color: {getTermStatusColor(getTermStatus(term))};"
                      >
                        {getTermStatus(term)}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        {#if !term.is_active}
                          <button 
                            class="btn btn-warning btn-sm" 
                            on:click={() => handleActivate(term.id)}
                          >
                            Activate
                          </button>
                        {/if}
                        <button 
                          class="btn btn-secondary btn-sm" 
                          on:click={() => openEditForm(term)}
                        >
                          Edit
                        </button>
                        <button 
                          class="btn btn-danger btn-sm" 
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
        </div>
        
        <!-- Empty Search Results -->
        {#if (searchTerm || statusFilter !== 'all') && getFilteredTerms().length === 0}
          <div class="empty-search-results">
            <p>No terms found matching your filters</p>
            <button class="btn btn-secondary btn-sm" on:click={() => { searchTerm = ''; statusFilter = 'all'; }}>
              Clear Filters
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<!-- Term Form Modal -->
{#if showForm}
  <div class="modal-overlay" on:click={handleModalOverlayClick}>
    <div class="modal-content card">
      <div class="modal-header">
        <h2>{editingTerm ? 'Edit Term' : 'Create New Term'}</h2>
        <button class="btn btn-close" on:click={closeForm} aria-label="Close modal">×</button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="name">Term Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            placeholder="e.g., Term 1 2025"
            required
            autocomplete="off"
          />
          <div class="field-note">Descriptive name for the term</div>
        </div>
        
        <div class="form-grid">
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
            <div class="field-note">Academic year</div>
          </div>
          
          <div class="form-group">
            <label for="term_number">Term Number *</label>
            <select id="term_number" bind:value={formData.term_number}>
              <option value="1">Term 1</option>
              <option value="2">Term 2</option>
              <option value="3">Term 3</option>
            </select>
            <div class="field-note">Term position in the year</div>
          </div>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="start_date">Start Date</label>
            <input
              type="date"
              id="start_date"
              bind:value={formData.start_date}
            />
            <div class="field-note">Optional start date</div>
          </div>
          
          <div class="form-group">
            <label for="end_date">End Date</label>
            <input
              type="date"
              id="end_date"
              bind:value={formData.end_date}
            />
            <div class="field-note">Optional end date</div>
          </div>
        </div>
        
        <div class="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              bind:checked={formData.is_active}
            />
            <span class="checkbox-label">Set as Active Term</span>
          </label>
          <div class="field-note">Only one term can be active at a time</div>
        </div>
        
        <div class="modal-actions">
          <button type="submit" class="btn btn-primary btn-submit">
            {editingTerm ? 'Update Term' : 'Create Term'}
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
  /* Reuse base styles from teachers page */
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
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
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
    font-size: 1.8rem;
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
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: #3498db;
    color: white;
  }
  
  .btn-primary:hover {
    background: #2980b9;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #5a6268;
  }
  
  .btn-warning {
    background: #f39c12;
    color: white;
  }
  
  .btn-warning:hover {
    background: #e67e22;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  .btn-danger:hover {
    background: #c82333;
  }
  
  .btn-sm {
    padding: 8px 16px;
    font-size: 0.875rem;
  }
  
  .btn-block {
    width: 100%;
    justify-content: center;
  }
  
  .btn-icon {
    font-size: 1.1rem;
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
  
  /* Search and Filter */
  .filter-card {
    margin-bottom: 20px;
  }
  
  .filter-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .search-container {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
  }
  
  .search-icon {
    position: absolute;
    left: 16px;
    color: #666;
  }
  
  .search-input {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
  }
  
  .btn-clear-search {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
  
  .filter-actions {
    display: flex;
    gap: 12px;
  }
  
  .filter-select {
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    min-height: 44px;
    background: white;
    color: #333;
    cursor: pointer;
    flex: 1;
  }
  
  .filter-select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
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
  
  /* Term Cards (Mobile) */
  .mobile-cards-view {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .term-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    border-left: 4px solid #3498db;
    transition: all 0.2s;
  }
  
  .term-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }
  
  .term-card.active-term {
    border-left: 4px solid #2ecc71;
  }
  
  .term-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .term-id {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .term-status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .term-card-body {
    margin-bottom: 16px;
  }
  
  .term-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 16px;
  }
  
  .term-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .info-label {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
  }
  
  .info-value {
    font-size: 1rem;
    color: #333;
    font-weight: 600;
  }
  
  .term-dates {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .date-item {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .date-icon {
    font-size: 1.2rem;
    width: 24px;
    text-align: center;
  }
  
  .date-info {
    flex: 1;
  }
  
  .date-label {
    font-size: 0.875rem;
    color: #666;
  }
  
  .date-value {
    font-size: 0.95rem;
    color: #333;
    font-weight: 500;
  }
  
  .term-card-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
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
  
  .terms-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .terms-table th {
    background: #f8f9fa;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #e9ecef;
    font-size: 0.9rem;
    white-space: nowrap;
  }
  
  .terms-table td {
    padding: 16px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
  }
  
  .terms-table tr:last-child td {
    border-bottom: none;
  }
  
  .terms-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .active-term-row {
    background-color: #e8f5e9 !important;
  }
  
  .term-name-cell {
    color: #2c3e50;
  }
  
  .term-number-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
    display: inline-block;
  }
  
  .status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: inline-block;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  /* Empty Search Results */
  .empty-search-results {
    text-align: center;
    padding: 30px 20px;
    border-top: 1px solid #e9ecef;
    margin-top: 20px;
  }
  
  .empty-search-results p {
    color: #666;
    margin-bottom: 16px;
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
  input[type="number"],
  input[type="date"],
  select {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    min-height: 44px;
    background: white;
  }
  
  input:focus,
  select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
  }
  
  .field-note {
    font-size: 0.875rem;
    color: #666;
    margin-top: 6px;
  }
  
  .checkbox-group {
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }
  
  .checkbox-group label {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    cursor: pointer;
  }
  
  .checkbox-group input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }
  
  .checkbox-label {
    font-weight: 500;
    color: #2c3e50;
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
      grid-template-columns: repeat(3, 140px);
      gap: 16px;
    }
    
    .stat-number {
      font-size: 2rem;
    }
    
    .filter-grid {
      flex-direction: row;
      gap: 16px;
      align-items: center;
    }
    
    .filter-actions {
      width: 200px;
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
    
    .term-card-actions {
      grid-template-columns: repeat(3, 1fr);
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
    
    .term-card {
      padding: 16px;
    }
    
    .term-name {
      font-size: 1.1rem;
    }
    
    .term-card-actions {
      grid-template-columns: 1fr;
      gap: 8px;
    }
    
    .modal-content {
      padding: 20px;
    }
    
    .modal-header h2 {
      font-size: 1.3rem;
    }
    
    input,
    select {
      padding: 12px 14px;
    }
  }
  
  /* Touch improvements */
  button, 
  input,
  select {
    min-height: 44px;
  }
  
  button {
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  
  /* Accessibility focus styles */
  button:focus-visible,
  input:focus-visible,
  select:focus-visible {
    outline: 2px solid #3498db;
    outline-offset: 2px;
  }
  
  /* Reduce motion */
  @media (prefers-reduced-motion: reduce) {
    .spinner,
    .term-card,
    .modal-content {
      animation: none;
      transition: none;
    }
  }
</style>