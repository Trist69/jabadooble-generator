<script lang="ts">
  export let data;
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import type { AppSettings } from '$lib/types';

  let settings: AppSettings | null = null;
  let apiKeyInput = '';
  let xaiApiKeyInput = '';
  let styleInput = '';
  let selectedProvider = 'gemini';
  let selectedModel = 'gemini-2.5-flash-image';
  let saving = false;
  let checking = false;
  let msg = '';
  let msgOk = true;

  const PROVIDERS = [
    { value: 'gemini', label: 'Gemini / Google Gemini' },
    { value: 'xai', label: 'xAI / grok-imagine-image' },
  ];

  const MODEL_OPTIONS = {
    gemini: [
      { value: 'gemini-2.5-flash-image', label: 'Nano Banana 🍌 — gemini-2.5-flash-image (recommended, free tier)' },
      { value: 'gemini-2.0-flash-preview-image-generation', label: 'gemini-2.0-flash-preview-image-generation (legacy preview)' },
    ],
    xai: [
      { value: 'grok-imagine-image', label: 'grok-imagine-image (xAI image generation)' },
    ],
  };

  onMount(async () => {
    settings = await api.settings.get();
    styleInput = settings.generation_style;
    selectedProvider = settings.ai_provider || 'gemini';
    selectedModel = selectedProvider === 'xai' ? settings.xai_model : settings.gemini_model;
  });

  function currentModelOptions() {
    return MODEL_OPTIONS[selectedProvider];
  }

  function providerChanged() {
    const options = currentModelOptions();
    selectedModel = options.length ? options[0].value : selectedModel;
  }

  async function saveGeminiApiKey() {
    if (!apiKeyInput.trim()) return;
    saving = true;
    msg = '';
    try {
      await api.settings.setApiKey('gemini', apiKeyInput.trim());
      settings = await api.settings.get();
      apiKeyInput = '';
      msg = '✓ Gemini API key saved';
      msgOk = true;
    } catch (e) {
      msg = e instanceof Error ? e.message : 'Failed to save Gemini API key';
      msgOk = false;
    } finally {
      saving = false;
    }
  }

  async function removeGeminiApiKey() {
    await api.settings.deleteApiKey('gemini');
    settings = await api.settings.get();
    msg = 'Gemini API key removed';
    msgOk = true;
  }

  async function saveXaiApiKey() {
    if (!xaiApiKeyInput.trim()) return;
    saving = true;
    msg = '';
    try {
      await api.settings.setApiKey('xai', xaiApiKeyInput.trim());
      settings = await api.settings.get();
      xaiApiKeyInput = '';
      msg = '✓ xAI API key saved';
      msgOk = true;
    } catch (e) {
      msg = e instanceof Error ? e.message : 'Failed to save xAI API key';
      msgOk = false;
    } finally {
      saving = false;
    }
  }

  async function removeXaiApiKey() {
    await api.settings.deleteApiKey('xai');
    settings = await api.settings.get();
    msg = 'xAI API key removed';
    msgOk = true;
  }

  async function saveProvider() {
    await api.settings.setProvider(selectedProvider);
    settings = await api.settings.get();
    selectedModel = selectedProvider === 'xai' ? settings?.xai_model : settings?.gemini_model;
    msg = '✓ Provider saved';
    msgOk = true;
  }

  async function saveModel() {
    await api.settings.setModel(selectedProvider, selectedModel);
    msg = '✓ Model saved';
    msgOk = true;
  }

  async function saveStyle() {
    await api.settings.setStyle(styleInput);
    msg = '✓ Style saved';
    msgOk = true;
  }

  async function checkConnection() {
    checking = true;
    msg = '';
    try {
      const result = await api.settings.check();
      if (result.ok) {
        msg = `✓ Connected — model: ${result.model}`;
        msgOk = true;
      } else {
        msg = `✗ ${result.error}`;
        msgOk = false;
      }
    } catch (e) {
      msg = e instanceof Error ? e.message : 'Check failed';
      msgOk = false;
    } finally {
      checking = false;
    }
  }
</script>

<div class="page">
  <h2>Settings</h2>

  {#if msg}
    <p class="msg" class:ok={msgOk} class:err={!msgOk}>{msg}</p>
  {/if}

  <!-- ── Provider ─────────────────────────────────────────────────── -->
  <section class="card">
    <h3>🧠 AI Provider</h3>
    <p class="hint">Choose whether image generation should use Gemini or xAI.</p>
    <div class="input-row">
      <select bind:value={selectedProvider} on:change={providerChanged}>
        {#each PROVIDERS as provider}
          <option value={provider.value}>{provider.label}</option>
        {/each}
      </select>
      <button class="btn-outlined" on:click={saveProvider}>Save provider</button>
    </div>
    <p class="hint">Note: subject generation still uses Gemini text prompt generation.</p>
  </section>

  <!-- ── Gemini API Key ──────────────────────────────────────────── -->
  <section class="card">
    <h3>🔑 Gemini API Key</h3>
    <p class="hint">
      Get a free key from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">Google AI Studio</a>.
      Free tier: 500 images/day (Nano Banana 🍌).
    </p>

    {#if settings?.gemini_api_key_set}
      <div class="key-status">
        <span class="badge-ok">✓ API key is set</span>
        <button class="btn-ghost danger" on:click={removeGeminiApiKey}>Remove key</button>
        <button class="btn-outlined" on:click={checkConnection} disabled={checking}>
          {checking ? 'Checking…' : 'Test connection'}
        </button>
      </div>
    {:else}
      <p class="warn">⚠ No Gemini API key configured — subject generation will not work.</p>
    {/if}

    <div class="input-row">
      <input
        type="password"
        bind:value={apiKeyInput}
        placeholder={settings?.gemini_api_key_set ? 'Enter new key to replace…' : 'Paste your API key…'}
        autocomplete="off"
      />
      <button class="btn-primary" on:click={saveGeminiApiKey} disabled={saving || !apiKeyInput.trim()}>
        {saving ? 'Saving…' : settings?.gemini_api_key_set ? 'Replace key' : 'Save key'}
      </button>
    </div>
  </section>

  <!-- ── xAI API Key ─────────────────────────────────────────────── -->
  <section class="card">
    <h3>🔑 xAI API Key</h3>
    <p class="hint">
      Get an API key from <a href="https://console.x.ai/" target="_blank" rel="noreferrer">xAI</a>.
      Use this key when the provider is set to xAI.
    </p>

    {#if settings?.xai_api_key_set}
      <div class="key-status">
        <span class="badge-ok">✓ API key is set</span>
        <button class="btn-ghost danger" on:click={removeXaiApiKey}>Remove key</button>
      </div>
    {:else}
      <p class="warn">⚠ No xAI API key configured — xAI image generation is disabled.</p>
    {/if}

    <div class="input-row">
      <input
        type="password"
        bind:value={xaiApiKeyInput}
        placeholder={settings?.xai_api_key_set ? 'Enter new key to replace…' : 'Paste your xAI API key…'}
        autocomplete="off"
      />
      <button class="btn-primary" on:click={saveXaiApiKey} disabled={saving || !xaiApiKeyInput.trim()}>
        {saving ? 'Saving…' : settings?.xai_api_key_set ? 'Replace key' : 'Save key'}
      </button>
    </div>
  </section>

  <!-- ── Model ───────────────────────────────────────────────────── -->
  <section class="card">
    <h3>🤖 Model</h3>
    <p class="hint">Choose the model used by the selected image provider.</p>
    <div class="input-row">
      <select bind:value={selectedModel}>
        {#each currentModelOptions() as m}
          <option value={m.value}>{m.label}</option>
        {/each}
      </select>
      <button class="btn-outlined" on:click={saveModel}>Save</button>
    </div>
  </section>

  <!-- ── Generation style ────────────────────────────────────────── -->
  <section class="card">
    <h3>🎨 Default Image Style</h3>
    <p class="hint">Appended to every AI image prompt. Tune this to change the overall look.</p>
    <textarea bind:value={styleInput} rows="3" />
    <button class="btn-outlined" on:click={saveStyle}>Save style</button>
  </section>
</div>

<style>
  .page { display: flex; flex-direction: column; gap: 20px; max-width: 640px; }
  h2 { font-size: 1.4rem; font-weight: 700; }
  h3 { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }

  .card {
    background: #f3edf7; border-radius: 16px; padding: 20px;
    display: flex; flex-direction: column; gap: 10px;
  }
  .hint { font-size: 0.85rem; color: #49454f; }
  .hint a { color: #6750a4; }
  .warn { font-size: 0.85rem; color: #7d3c00; background: #fff3cd; padding: 8px 12px; border-radius: 8px; }

  .key-status { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .badge-ok {
    background: #ebf5e0; color: #386a20; padding: 4px 12px;
    border-radius: 12px; font-size: 0.85rem; font-weight: 600;
  }

  .input-row { display: flex; gap: 10px; flex-wrap: wrap; }
  input[type="password"] {
    flex: 1; min-width: 220px; padding: 8px 12px; border-radius: 8px;
    border: 1.5px solid #cac4d0; font-size: 0.9rem; outline: none; background: white;
  }
  input[type="password"]:focus { border-color: #6750a4; }
  select {
    flex: 1; padding: 8px 12px; border-radius: 8px;
    border: 1.5px solid #cac4d0; font-size: 0.85rem; background: white; cursor: pointer;
  }
  textarea {
    width: 100%; padding: 10px 12px; border-radius: 8px;
    border: 1.5px solid #cac4d0; font-size: 0.85rem; resize: vertical;
    font-family: inherit; outline: none; background: white;
  }
  textarea:focus { border-color: #6750a4; }

  .btn-primary {
    background: #6750a4; color: white; border: none; padding: 8px 20px;
    border-radius: 20px; cursor: pointer; font-size: 0.9rem; font-weight: 600; white-space: nowrap;
  }
  .btn-primary:disabled { opacity: 0.5; cursor: default; }
  .btn-outlined {
    background: none; border: 2px solid #6750a4; color: #6750a4;
    padding: 7px 16px; border-radius: 20px; cursor: pointer; font-size: 0.85rem; font-weight: 600; white-space: nowrap;
  }
  .btn-outlined:disabled { opacity: 0.5; cursor: default; }
  .btn-ghost {
    background: none; border: none; color: #79747e;
    padding: 6px 12px; border-radius: 20px; cursor: pointer; font-size: 0.85rem;
  }
  .btn-ghost.danger:hover { color: #b3261e; }

  .msg { padding: 8px 14px; border-radius: 8px; font-size: 0.88rem; }
  .msg.ok  { background: #ebf5e0; color: #386a20; }
  .msg.err { background: #fce8e6; color: #b3261e; }
</style>
