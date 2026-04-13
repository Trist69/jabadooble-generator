<script lang="ts">
  import NavBar from '$lib/components/NavBar.svelte';
  export let data;
</script>

<div class="app-shell">
  <NavBar />
  <main>
    <slot />
  </main>
</div>

<style>
  :global(*, *::before, *::after) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  :global(body) {
    font-family: 'Roboto', system-ui, sans-serif;
    background: #fffbfe;
    color: #1c1b1f;
    min-height: 100vh;
  }
  .app-shell {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  main {
    flex: 1;
    padding: 24px;
    max-width: 1100px;
    margin: 0 auto;
    width: 100%;
  }
</style>
