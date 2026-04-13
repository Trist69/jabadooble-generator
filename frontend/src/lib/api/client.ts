import type { Library, Symbol, Game, AppSettings, AiGenerateProgress } from '$lib/types';

const BASE = 'http://localhost:8000/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const res = await fetch(`${BASE}${path}`, {
    headers: isFormData ? undefined : { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`API ${res.status}: ${msg}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Settings ──────────────────────────────────────────────────────────────

export const api = {
  settings: {
    get: () => request<AppSettings>('/settings'),
    setApiKey: (provider: string, api_key: string) =>
      request<void>('/settings/api-key', { method: 'PUT', body: JSON.stringify({ provider, api_key }) }),
    deleteApiKey: (provider: string) =>
      request<void>(`/settings/api-key/${provider}`, { method: 'DELETE' }),
    setProvider: (provider: string) =>
      request<void>('/settings/provider', { method: 'PUT', body: JSON.stringify({ provider }) }),
    setModel: (provider: string, model: string) =>
      request<void>('/settings/model', { method: 'PUT', body: JSON.stringify({ provider, model }) }),
    setStyle: (style: string) =>
      request<void>('/settings/style', { method: 'PUT', body: JSON.stringify({ style }) }),
    check: () => request<{ ok: boolean; model?: string; error?: string }>('/settings/check'),
  },

  // ── Libraries ───────────────────────────────────────────────────────────

  libraries: {
    list: () => request<Library[]>('/libraries'),
    get: (id: string) => request<Library>(`/libraries/${id}`),
    create: (name: string, theme: string) =>
      request<Library>('/libraries', { method: 'POST', body: JSON.stringify({ name, theme }) }),
    delete: (id: string) =>
      request<void>(`/libraries/${id}`, { method: 'DELETE' }),

    generateAi: (libraryId: string, theme: string, count: number, style?: string) =>
      request<AiGenerateProgress>(`/libraries/${libraryId}/generate/ai`, {
        method: 'POST',
        body: JSON.stringify({ theme, count, ...(style ? { style } : {}) }),
      }),

    addSymbol: (libraryId: string, label: string, url: string) =>
      request<Symbol>(`/libraries/${libraryId}/symbols`, {
        method: 'POST', body: JSON.stringify({ label, url }),
      }),

    removeSymbol: (libraryId: string, symbolId: string) =>
      request<void>(`/libraries/${libraryId}/symbols/${symbolId}`, { method: 'DELETE' }),

    uploadSymbol: (libraryId: string, file: File) => {
      const fd = new FormData();
      fd.append('file', file);
      return request<Symbol>(`/libraries/${libraryId}/symbols/upload`, { method: 'POST', body: fd });
    },
  },

  // ── Games ────────────────────────────────────────────────────────────────

  games: {
    generate: (libraryId: string, order = 7) =>
      request<Game>('/games', { method: 'POST', body: JSON.stringify({ library_id: libraryId, order }) }),
    list: () => request<Game[]>('/games'),
    get: (id: string) => request<Game>(`/games/${id}`),
    delete: (id: string) => request<void>(`/games/${id}`, { method: 'DELETE' }),
    exportPdfUrl: (id: string) => `${BASE}/games/${id}/export/pdf`,
  },

  // ── Images ───────────────────────────────────────────────────────────────

  images: {
    cartoonizeUrl: (url: string, libraryId?: string, symbolId?: string) =>
      request<void>('/images/cartoonize/url', {
        method: 'POST',
        body: JSON.stringify({ url, library_id: libraryId, symbol_id: symbolId }),
      }),
  },
};
