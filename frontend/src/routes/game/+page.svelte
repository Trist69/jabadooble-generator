<script lang="ts">
  export let data;
  import { onMount } from 'svelte';
  import DobbleCard from '$lib/components/DobbleCard.svelte';
  import { libraries, loadLibraries } from '$lib/stores/library';
  import { games, activeGame, loading, error, loadGames, generateGame, deleteGame } from '$lib/stores/game';
  import { api } from '$lib/api/client';

  let selectedLibraryId = '';
  let order = 7;
  let previewPage = 0;
  const CARDS_PER_PAGE = 12;

  onMount(async () => {
    await Promise.all([loadLibraries(), loadGames()]);
    if ($libraries.length > 0) selectedLibraryId = $libraries[0].id;
  });

  $: cardsOnPage = $activeGame
    ? $activeGame.cards.slice(previewPage * CARDS_PER_PAGE, (previewPage + 1) * CARDS_PER_PAGE)
    : [];
  $: totalPages = $activeGame ? Math.ceil($activeGame.total_cards / CARDS_PER_PAGE) : 0;
  $: savedGames = selectedLibraryId
    ? $games.filter((g) => g.library_id === selectedLibraryId)
    : $games;
  $: selectedLibrary = $libraries.find((lib) => lib.id === selectedLibraryId);

  async function handleGenerate() {
    if (!selectedLibraryId) return;
    await generateGame(selectedLibraryId, order);
    previewPage = 0;
  }
</script>

<div class="page">
  <h2>Generate a Dobble Deck</h2>

  <!-- Controls -->
  <div class="controls-card">
    <label>
      Library
      <select bind:value={selectedLibraryId} disabled={$libraries.length === 0}>
        {#each $libraries as lib}
          <option value={lib.id}>{lib.name} ({lib.symbols.length} symbols)</option>
        {/each}
        {#if $libraries.length === 0}
          <option value="">No libraries — create one first</option>
        {/if}
      </select>
    </label>

    <label>
      Order <small>(n — cards = n²+n+1)</small>
      <select bind:value={order}>
        <option value={2}>2 → 7 cards, 3 symbols</option>
        <option value={3}>3 → 13 cards, 4 symbols</option>
        <option value={5}>5 → 31 cards, 6 symbols</option>
        <option value={7}>7 → 57 cards, 8 symbols (standard)</option>
      </select>
    </label>

    <button class="btn-primary" on:click={handleGenerate} disabled={$loading || !selectedLibraryId}>
      {$loading ? 'Generating…' : '🃏 Generate Deck'}
    </button>
  </div>

  {#if $error}
    <p class="msg error">{$error}</p>
  {/if}

  <!-- Active game preview -->
  {#if $activeGame}
    <div class="game-header">
      <h3>Deck — {$activeGame.total_cards} cards</h3>
      <div class="game-actions">
        <a
          class="btn-outlined"
          href={api.games.exportPdfUrl($activeGame.id)}
          target="_blank"
          rel="noreferrer"
        >🖨️ Export PDF</a>
        <button class="btn-ghost" on:click={() => $activeGame && deleteGame($activeGame.id)}>Delete</button>
      </div>
    </div>

    <div class="card-grid">
      {#each cardsOnPage as card}
        <DobbleCard {card} sizePx={220} />
      {/each}
    </div>

    {#if totalPages > 1}
      <div class="pagination">
        <button on:click={() => (previewPage = Math.max(0, previewPage - 1))} disabled={previewPage === 0}>‹</button>
        <span>{previewPage + 1} / {totalPages}</span>
        <button on:click={() => (previewPage = Math.min(totalPages - 1, previewPage + 1))} disabled={previewPage === totalPages - 1}>›</button>
      </div>
    {/if}
  {/if}

  <h3>Saved Decks{selectedLibrary ? ` for ${selectedLibrary.name}` : ''}</h3>
  {#if savedGames.length > 0}
    <div class="saved-list">
      {#each savedGames as g}
        <div class="saved-item">
          <div>
            <strong>{g.total_cards} cards</strong>
            <span class="muted">order {g.order} · {g.id.slice(0, 8)}</span>
          </div>
          <div class="saved-actions">
            <button class="btn-outlined" on:click={() => activeGame.set(g)}>View</button>
            <a class="btn-outlined" href={api.games.exportPdfUrl(g.id)} target="_blank" rel="noreferrer">PDF</a>
            <button class="btn-ghost" on:click={() => deleteGame(g.id)}>✕</button>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <p class="empty">No decks yet for this library — generate one above.</p>
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 24px; }
  h2 { font-size: 1.4rem; font-weight: 700; }
  h3 { font-size: 1.1rem; font-weight: 600; }

  .controls-card {
    background: #f3edf7; border-radius: 16px; padding: 20px;
    display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end;
  }
  label {
    display: flex; flex-direction: column; gap: 6px;
    font-size: 0.85rem; font-weight: 600; color: #49454f;
  }
  label small { font-weight: 400; color: #79747e; }
  select {
    padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cac4d0;
    font-size: 0.9rem; background: white; cursor: pointer; min-width: 220px;
  }
  select:focus { outline: none; border-color: #6750a4; }

  .btn-primary {
    background: #6750a4; color: white; border: none; padding: 10px 24px;
    border-radius: 22px; cursor: pointer; font-size: 0.95rem; font-weight: 600;
    align-self: flex-end;
  }
  .btn-primary:disabled { opacity: 0.5; cursor: default; }
  .btn-outlined {
    background: none; border: 2px solid #6750a4; color: #6750a4;
    padding: 6px 16px; border-radius: 20px; cursor: pointer; font-size: 0.85rem;
    font-weight: 600; text-decoration: none; display: inline-block;
  }
  .btn-ghost {
    background: none; border: none; color: #79747e; padding: 6px 12px;
    border-radius: 20px; cursor: pointer; font-size: 0.85rem;
  }

  .msg.error { color: #b3261e; background: #fce8e6; padding: 10px 14px; border-radius: 8px; }

  .game-header {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  }
  .game-header h3 { flex: 1; }
  .game-actions { display: flex; gap: 8px; align-items: center; }

  .card-grid {
    display: flex; flex-wrap: wrap; gap: 16px; justify-content: flex-start;
  }

  .pagination {
    display: flex; gap: 12px; align-items: center; justify-content: center;
  }
  .pagination button {
    background: #e8def8; border: none; border-radius: 50%; width: 34px; height: 34px;
    cursor: pointer; font-size: 1.1rem;
  }
  .pagination button:disabled { opacity: 0.35; cursor: default; }

  .saved-list { display: flex; flex-direction: column; gap: 10px; }
  .saved-item {
    display: flex; justify-content: space-between; align-items: center;
    background: #f3edf7; padding: 12px 16px; border-radius: 12px; flex-wrap: wrap; gap: 10px;
  }
  .saved-actions { display: flex; gap: 8px; align-items: center; }
  .muted { font-size: 0.8rem; color: #79747e; margin-left: 8px; }
  .empty { color: #79747e; }
</style>
