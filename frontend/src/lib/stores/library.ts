import { writable, derived } from 'svelte/store';
import type { Library } from '$lib/types';
import { api } from '$lib/api/client';

export const libraries = writable<Library[]>([]);
export const loading = writable(false);
export const error = writable<string | null>(null);

export const libraryCount = derived(libraries, ($libs) => $libs.length);

export async function loadLibraries(): Promise<void> {
  loading.set(true);
  error.set(null);
  try {
    const data = await api.libraries.list();
    libraries.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load libraries');
  } finally {
    loading.set(false);
  }
}

export async function createLibrary(name: string, theme: string): Promise<Library | null> {
  try {
    const lib = await api.libraries.create(name, theme);
    libraries.update((prev) => [...prev, lib]);
    return lib;
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to create library');
    return null;
  }
}

export async function deleteLibrary(id: string): Promise<void> {
  await api.libraries.delete(id);
  libraries.update((prev) => prev.filter((l) => l.id !== id));
}
