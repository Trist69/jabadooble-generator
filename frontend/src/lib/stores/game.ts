import { writable } from 'svelte/store';
import type { Game } from '$lib/types';
import { api } from '$lib/api/client';

export const games = writable<Game[]>([]);
export const activeGame = writable<Game | null>(null);
export const loading = writable(false);
export const error = writable<string | null>(null);

export async function loadGames(): Promise<void> {
  loading.set(true);
  try {
    games.set(await api.games.list());
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load games');
  } finally {
    loading.set(false);
  }
}

export async function generateGame(libraryId: string, order: number): Promise<Game | null> {
  loading.set(true);
  error.set(null);
  try {
    const game = await api.games.generate(libraryId, order);
    games.update((prev) => [game, ...prev]);
    activeGame.set(game);
    return game;
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to generate game');
    return null;
  } finally {
    loading.set(false);
  }
}

export async function deleteGame(id: string): Promise<void> {
  await api.games.delete(id);
  games.update((prev) => prev.filter((g) => g.id !== id));
  activeGame.update((g) => (g?.id === id ? null : g));
}
