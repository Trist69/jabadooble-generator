<script lang="ts">
  export let data;
  import { onMount } from 'svelte';
  import LibraryCard from '$lib/components/LibraryCard.svelte';
  import { libraries, loading, error, loadLibraries, createLibrary, deleteLibrary } from '$lib/stores/library';
  import { api } from '$lib/api/client';
  import type { Library, AppSettings } from '$lib/types';

  // ── State ──────────────────────────────────────────────────────────
  let showCreate = false;
  let newName = '';
  let newTheme = '';
  let selected: Library | null = null;
  let settings: AppSettings | null = null;

  // AI generate
  let aiTheme = '';
  let aiCount = 13;
  let aiProvider = 'gemini';
  let aiGenerating = false;
  let aiMsg = '';
  let aiError = false;

  // Pastelify
  let pastelizing = false;
  let pastelDone = 0;
  let pastelTotal = 0;

  const COUNT_OPTIONS = [
    { value: 7,  label: '7 symbols  (order 2 — mini deck)' },
    { value: 13, label: '13 symbols (order 3 — small deck)' },
    { value: 31, label: '31 symbols (order 5 — medium deck)' },
    { value: 57, label: '57 symbols (order 7 — full Dobble)' },
  ];

  const PROVIDERS = [
    { value: 'gemini', label: 'Gemini Nano Banana 🍌' },
    { value: 'xai', label: 'xAI grok-imagine-image' },
  ];

  const PROVIDER_HINT = {
    gemini: 'Uses Gemini for both subject generation and image generation.',
    xai: 'Uses Gemini for subject generation and xAI for image generation.',
  } as const;

  onMount(async () => {
    await loadLibraries();
    try {
      settings = await api.settings.get();
      aiProvider = settings.ai_provider || 'gemini';
    } catch {
      /* non-critical */
    }
  });

  // ── Library CRUD ───────────────────────────────────────────────────
  async function handleCreate() {
    if (!newName.trim()) return;
    await createLibrary(newName.trim(), newTheme.trim() || 'custom');
    newName = '';
    newTheme = '';
    showCreate = false;
  }

  // ── AI generation ──────────────────────────────────────────────────
  async function handleAiGenerate() {
    if (!selected || !aiTheme.trim()) return;
    aiGenerating = true;
    aiMsg = '';
    aiError = false;
    try {
      const result = await api.libraries.generateAi(selected.id, aiTheme.trim(), aiCount);
      selected = result.library;
      libraries.update((prev) => prev.map((l) => (l.id === selected!.id ? selected! : l)));
      aiMsg = `✓ Generated ${result.done} of ${result.total} symbols`;
      aiTheme = '';
    } catch (e) {
      aiMsg = e instanceof Error ? e.message : 'Generation failed';
      aiError = true;
    } finally {
      aiGenerating = false;
    }
  }

  async function handleProviderChange() {
    if (!settings) return;
    try {
      await api.settings.setProvider(aiProvider);
      settings = await api.settings.get();
      aiMsg = `✓ Provider switched to ${PROVIDERS.find((p) => p.value === aiProvider)?.label}`;
      aiError = false;
    } catch (e) {
      aiMsg = e instanceof Error ? e.message : 'Provider switch failed';
      aiError = true;
    }
  }

  // ── Pastelify ──────────────────────────────────────────────────────
  async function handlePastelifyAll() {
    if (!selected) return;
    const pending = selected.symbols.filter((s) => !s.cartoonized);
    if (!pending.length) return;
    pastelizing = true;
    pastelDone = 0;
    pastelTotal = pending.length;

    for (const sym of pending) {
      try {
        await api.images.cartoonizeUrl(sym.url, selected.id, String(sym.id));
      } catch { /* skip */ }
      pastelDone++;
    }

    const updated = await api.libraries.get(selected.id);
    if (updated) {
      selected = updated;
      libraries.update((prev: Library[]) => prev.map((l: Library) => (l.id === updated.id ? updated : l)));
    }
    pastelizing = false;
    aiMsg = '✓ Pastelify complete';
  }

  async function handleDeleteSymbol(symbolId: string) {
    if (!selected) return;
    await api.libraries.removeSymbol(selected.id, symbolId);
    selected = { ...selected, symbols: selected.symbols.filter((s) => s.id !== symbolId) };
    libraries.update((prev) => prev.map((l) => (l.id === selected!.id ? selected! : l)));
  }

  $: apiKeyMissing =
    Boolean(settings) &&
    (!settings.gemini_api_key_set || (aiProvider === 'xai' && !settings.xai_api_key_set));

  $: allPastelized = selected?.symbols.every((s) => s.cartoonized) ?? true;
  $: hasPendingPastel = selected?.symbols.some((s) => !s.cartoonized && s.url.startsWith('http')) ?? false;
</script>

<div class="page">
  {#if selected}
    <!-- ══ Detail view ════════════════════════════════════════════════ -->
    <div class="detail-header">
      <button class="back-btn" on:click={() => { selected = null; aiMsg = ''; }}>← Libraries</button>
      <h2>{selected.name} <span class="badge">{selected.theme}</span></h2>
      <span class="count">{selected.symbols.length} symbols</span>
    </div>

    <!-- AI Generate panel ------------------------------------------- -->
    <section class="ai-panel">
      <div class="ai-panel-header">
        <span class="ai-title">🤖 Generate with {PROVIDERS.find((p) => p.value === aiProvider)?.label}</span>
        {#if apiKeyMissing}
          <a class="key-warning" href="/settings">⚠ Required API key not set — go to Settings</a>
        {/if}
      </div>

      <div class="provider-row">
        <label>
          Provider
          <select bind:value={aiProvider} on:change={handleProviderChange} disabled={aiGenerating}>
            {#each PROVIDERS as provider}
              <option value={provider.value}>{provider.label}</option>
            {/each}
          </select>
        </label>
      </div>

      <div class="ai-controls">
        <input
          bind:value={aiTheme}
          placeholder='Describe your theme, e.g. "cute zoo animals" or "space adventure"'
          disabled={aiGenerating || apiKeyMissing}
          on:keydown={(e) => e.key === 'Enter' && handleAiGenerate()}
        />
        <select bind:value={aiCount} disabled={aiGenerating || apiKeyMissing}>
          {#each COUNT_OPTIONS as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>
        <button
          class="btn-ai"
          on:click={handleAiGenerate}
          disabled={aiGenerating || !aiTheme.trim() || apiKeyMissing}
        >
          {aiGenerating ? '✨ Generating…' : '✨ Generate'}
        </button>
      </div>

      <p class="ai-hint">
        {PROVIDER_HINT[aiProvider]} {aiProvider === 'xai' ? 'Gemini text still creates subjects; xAI generates the illustration.' : ''}
      </p>
    </section>

    <!-- Pastelify section -------------------------------- -->
    <section class="secondary-panel">
      {#if hasPendingPastel && selected.symbols.length > 0}
        <div class="pastelify-row">
          <span class="muted">🎨 Pastelify converts photo-based symbols to a soft watercolour look</span>
          <button
            class="btn-pastel"
            on:click={handlePastelifyAll}
            disabled={pastelizing || aiGenerating || allPastelized}
          >
            {#if pastelizing}
              Pastelifying… {pastelDone}/{pastelTotal}
            {:else}
              🎨 Pastelify All
            {/if}
          </button>
        </div>
      {/if}
    </section>

    {#if aiMsg}
      <p class="msg" class:error={aiError}>{aiMsg}</p>
    {/if}

    <!-- Symbol grid ------------------------------------------------- -->
    {#if aiGenerating && selected.symbols.length === 0}
      <p class="status">Generating your first symbols…</p>
    {:else}
      <div class="symbol-grid">
        {#each selected.symbols as sym}
          <div class="symbol-tile">
            <img src={sym.cartoonized_url ?? sym.url} alt={sym.label} />
            {#if sym.cartoonized}
              <span class="pastelize-badge" title="Pastelized">🎨</span>
            {/if}
            <span class="sym-label">{sym.label}</span>
            <button class="sym-del" on:click={() => handleDeleteSymbol(sym.id)}>✕</button>
          </div>
        {/each}
        {#if selected.symbols.length === 0}
          <p class="empty">No symbols yet — generate some above.</p>
        {/if}
      </div>
    {/if}

  {:else}
    <!-- ══ Library list ══════════════════════════════════════════════ -->
    <div class="list-header">
      <h2>Libraries</h2>
      <button class="btn-primary" on:click={() => (showCreate = !showCreate)}>+ New Library</button>
    </div>

    {#if showCreate}
      <div class="create-form">
        <input bind:value={newName} placeholder="Library name (e.g. Zoo Animals)" />
        <input bind:value={newTheme} placeholder="Theme tag (e.g. animals)" />
        <button class="btn-primary" on:click={handleCreate}>Create</button>
        <button class="btn-ghost" on:click={() => (showCreate = false)}>Cancel</button>
      </div>
    {/if}

    {#if $loading}
      <p class="status">Loading…</p>
    {:else if $error}
      <p class="status error">{$error}</p>
    {:else if $libraries.length === 0}
      <div class="onboarding">
        <span class="onboarding-icon">🃏</span>
        <h3>Create your first library</h3>
        <p>Give it a name and theme, then use Gemini to generate custom cartoon symbols.</p>
        <button class="btn-primary" on:click={() => (showCreate = true)}>+ Create Library</button>
      </div>
    {:else}
      <div class="library-grid">
        {#each $libraries as lib}
          <LibraryCard
            library={lib}
            on:select={(e) => (selected = e.detail)}
            on:delete={(e) => deleteLibrary(e.detail)}
          />
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 20px; }

  /* Header */
  .list-header, .detail-header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  h2 { font-size: 1.4rem; font-weight: 700; flex: 1; }
  .badge {
    font-size: 0.75rem; background: #e8def8; color: #4a4458;
    padding: 2px 8px; border-radius: 12px; font-weight: 500; vertical-align: middle;
  }
  .count { font-size: 0.85rem; color: #79747e; }
  .back-btn {
    background: none; border: none; cursor: pointer; color: #6750a4;
    font-size: 0.95rem; font-weight: 600; padding: 4px 0;
  }

  /* Buttons */
  .btn-primary {
    background: #6750a4; color: white; border: none; padding: 8px 20px;
    border-radius: 20px; cursor: pointer; font-size: 0.9rem; font-weight: 600;
  }
  .btn-outlined {
    background: none; border: 2px solid #6750a4; color: #6750a4;
    padding: 7px 16px; border-radius: 20px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
    white-space: nowrap;
  }
  .btn-outlined:disabled { opacity: 0.5; cursor: default; }
  .btn-ghost {
    background: none; border: none; color: #49454f; padding: 8px 16px;
    border-radius: 20px; cursor: pointer; font-size: 0.9rem;
  }
  .btn-ai {
    background: linear-gradient(135deg, #6750a4, #9c60d4); color: white;
    border: none; padding: 10px 24px; border-radius: 22px;
    cursor: pointer; font-size: 0.95rem; font-weight: 700;
    box-shadow: 0 2px 10px rgba(103,80,164,0.3); white-space: nowrap;
    transition: box-shadow 0.2s;
  }
  .btn-ai:hover:not(:disabled) { box-shadow: 0 4px 18px rgba(103,80,164,0.45); }
  .btn-ai:disabled { opacity: 0.5; cursor: default; box-shadow: none; }
  .btn-pastel {
    background: #f0bbdd; color: #3c0d20; border: none; padding: 7px 16px;
    border-radius: 20px; cursor: pointer; font-size: 0.85rem; font-weight: 600; white-space: nowrap;
  }
  .btn-pastel:disabled { opacity: 0.5; cursor: default; }

  /* AI panel */
  .ai-panel {
    background: linear-gradient(135deg, #f3edf7, #ede7f6);
    border: 2px solid #d0bcff; border-radius: 18px; padding: 20px;
    display: flex; flex-direction: column; gap: 12px;
  }
  .ai-panel-header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .ai-title { font-size: 1rem; font-weight: 700; }
  .key-warning {
    font-size: 0.82rem; color: #b3261e; background: #fce8e6;
    padding: 4px 10px; border-radius: 12px; text-decoration: none; font-weight: 600;
  }
  .ai-controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
  .ai-controls input {
    flex: 2; min-width: 200px; padding: 10px 14px; border-radius: 10px;
    border: 1.5px solid #cac4d0; font-size: 0.9rem; outline: none; background: white;
  }
  .ai-controls input:focus { border-color: #6750a4; }
  .ai-controls select {
    flex: 1; min-width: 200px; padding: 9px 12px; border-radius: 10px;
    border: 1.5px solid #cac4d0; font-size: 0.85rem; background: white; cursor: pointer;
  }
  .ai-hint { font-size: 0.8rem; color: #79747e; }

  /* Secondary panel */
  .secondary-panel {
    background: #fafafa; border: 1.5px solid #e8e0ec; border-radius: 14px;
    padding: 14px 18px; display: flex; flex-direction: column; gap: 10px;
  }
  .secondary-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
  .pastelify-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
  .muted { font-size: 0.82rem; color: #79747e; }

  /* Create form */
  .create-form {
    display: flex; gap: 10px; flex-wrap: wrap; background: #f3edf7;
    padding: 16px; border-radius: 12px; align-items: center;
  }
  .create-form input {
    flex: 1; min-width: 180px; padding: 8px 12px; border-radius: 8px;
    border: 1.5px solid #cac4d0; font-size: 0.95rem; outline: none;
  }
  .create-form input:focus { border-color: #6750a4; }

  /* Library grid */
  .library-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;
  }

  /* Symbol grid */
  .symbol-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 10px;
  }
  .symbol-tile {
    position: relative; background: #f3edf7; border-radius: 12px;
    overflow: hidden; display: flex; flex-direction: column; align-items: center; padding-bottom: 6px;
  }
  .symbol-tile img { width: 100%; aspect-ratio: 1; object-fit: contain; background: white; }
  .sym-label {
    font-size: 0.68rem; color: #49454f; text-align: center;
    padding: 2px 6px; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .sym-del {
    position: absolute; top: 4px; right: 4px; background: rgba(0,0,0,0.45);
    color: white; border: none; border-radius: 50%; width: 18px; height: 18px;
    font-size: 0.6rem; cursor: pointer; display: none; align-items: center; justify-content: center;
  }
  .symbol-tile:hover .sym-del { display: flex; }
  .pastelize-badge {
    position: absolute; top: 4px; left: 4px; font-size: 0.65rem;
    background: rgba(255,255,255,0.85); border-radius: 4px; padding: 1px 3px;
  }

  /* Onboarding */
  .onboarding {
    display: flex; flex-direction: column; align-items: center; gap: 12px;
    padding: 48px 24px; text-align: center; background: #f3edf7; border-radius: 20px;
  }
  .onboarding-icon { font-size: 3rem; }
  .onboarding p { color: #49454f; font-size: 0.9rem; max-width: 360px; line-height: 1.5; }

  /* Utils */
  .msg { font-size: 0.88rem; background: #ebf5e0; color: #386a20; padding: 8px 14px; border-radius: 8px; }
  .msg.error { background: #fce8e6; color: #b3261e; }
  .status { color: #79747e; font-size: 0.95rem; }
  .status.error { color: #b3261e; }
  .empty { color: #79747e; grid-column: 1/-1; }
</style>
