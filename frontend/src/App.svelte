<script>
  import { onMount } from 'svelte';
  import { user, initAuth } from './lib/stores.js';
  import Login from './lib/Login.svelte';
  import AdminDashboard from './lib/AdminDashboard.svelte';
  import TeacherDashboard from './lib/TeacherDashboard.svelte';
  import StudentDashboard from './lib/StudentDashboard.svelte';
  
  onMount(() => {
    initAuth();
  });
</script>

{#if $user}
  {#if $user.role === 'admin'}
    <AdminDashboard />
  {:else if $user.role === 'teacher'}
    <TeacherDashboard />
  {:else if $user.role === 'student'}
    <StudentDashboard />
  {/if}
{:else}
  <Login />
{/if}