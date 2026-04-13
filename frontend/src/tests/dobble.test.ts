import { describe, it, expect } from 'vitest';
import { dobbleEngine } from '$lib/utils/dobble';

describe('dobbleEngine stub', () => {
  it('is a callable function', () => {
    expect(typeof dobbleEngine).toBe('function');
  });

  it('throws NotImplementedError until Phase 2', () => {
    expect(() => dobbleEngine(7)).toThrow('not yet implemented');
  });
});
