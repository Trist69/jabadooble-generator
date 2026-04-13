<script lang="ts">
  import type { GameCard } from '$lib/types';

  export let card: GameCard;
  export let sizePx = 260;

  const R = sizePx / 2;
  const cx = R;
  const cy = R;

  function hashToUnit(value: string): number {
    let hash = 0;
    for (let i = 0; i < value.length; i++) {
      hash = (hash * 31 + value.charCodeAt(i)) % 0x100000000;
    }
    return (hash % 1000) / 1000;
  }

  function symbolScale(cardIndex: number, label: string): number {
    return 0.85 + hashToUnit(`${cardIndex}:${label}`) * 0.3;
  }
</script>

<svg
  width={sizePx}
  height={sizePx}
  viewBox="0 0 {sizePx} {sizePx}"
  xmlns="http://www.w3.org/2000/svg"
  role="img"
  aria-label="Dobble card {card.index + 1}"
>
  <!-- Card background -->
  <circle {cx} {cy} r={R - 2} fill="white" stroke="#1c1b1f" stroke-width="2" />

  <!-- Symbols -->
  {#each card.placements as p}
    {@const px = cx + p.cx * (R - 4)}
    {@const py = cy - p.cy * (R - 4)}
    {@const sr = p.size * (R - 4) * symbolScale(card.index, p.label)}
    <image
      href={p.url}
      x={px - sr}
      y={py - sr}
      width={sr * 2}
      height={sr * 2}
      preserveAspectRatio="xMidYMid meet"
      clip-path="circle({sr}px at {sr}px {sr}px)"
    />
    <!-- Label tooltip -->
    <title>{p.label}</title>
  {/each}

  <!-- Card number -->
  <text
    x={sizePx - 8}
    y={sizePx - 6}
    font-size="9"
    fill="#aaa"
    text-anchor="end"
    font-family="Roboto, sans-serif"
  >{card.index + 1}</text>
</svg>

<style>
  svg {
    display: block;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    background: white;
  }
</style>
