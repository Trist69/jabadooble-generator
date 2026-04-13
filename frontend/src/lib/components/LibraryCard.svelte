<script lang="ts">
  import type { Library } from '$lib/types';
  import { createEventDispatcher } from 'svelte';

  export let library: Library;

  const dispatch = createEventDispatcher<{ select: Library; delete: string }>();

  const previewSymbols = library.symbols.slice(0, 4);
</script>

<div class="library-card" role="button" tabindex="0"
     on:click={() => dispatch('select', library)}
     on:keydown={(e) => e.key === 'Enter' && dispatch('select', library)}>
  <div class="previews">
    {#each previewSymbols as sym}
      <img src={sym.cartoonized_url ?? sym.url} alt={sym.label} />
    {/each}
    {#if previewSymbols.length === 0}
      <span class="empty-icon">🃏</span>
    {/if}
  </div>
  <div class="info">
    <span class="name">{library.name}</span>
    <span class="count">{library.symbols.length} symbols</span>
  </div>
  <button
    class="delete-btn"
    aria-label="Delete library"
    on:click|stopPropagation={() => dispatch('delete', library.id)}
  >✕</button>
</div>

<style>
  .library-card {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    border-radius: 16px;
    background: #f3edf7;
    cursor: pointer;
    transition: box-shadow 0.2s;
    outline: none;
  }
  .library-card:hover,
  .library-card:focus-visible {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.14);
  }
  .previews {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }
  .previews img {
    width: 44px;
    height: 44px;
    object-fit: cover;
    border-radius: 8px;
    background: #e8e0ec;
  }
  .empty-icon {
    font-size: 2rem;
  }
  .info {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }
  .name {
    font-weight: 600;
    font-size: 1rem;
  }
  .count {
    font-size: 0.8rem;
    color: #79747e;
  }
  .delete-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: none;
    border: none;
    cursor: pointer;
    color: #79747e;
    font-size: 0.9rem;
    padding: 2px 6px;
    border-radius: 50%;
    transition: background 0.15s;
  }
  .delete-btn:hover {
    background: #e8e0ec;
    color: #b3261e;
  }
</style>
