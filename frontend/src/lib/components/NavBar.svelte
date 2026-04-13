<script lang="ts">
  import { page } from '$app/stores';

  const links = [
    { href: '/',          label: 'Home'      },
    { href: '/library',   label: 'Libraries' },
    { href: '/game',      label: 'Play'      },
    { href: '/settings',  label: '⚙ Settings' },
  ];
</script>

<header>
  <a class="brand" href="/">🃏 Dobble Generator</a>
  <nav>
    {#each links as link}
      <a
        href={link.href}
        class:active={$page.url.pathname === link.href}
      >{link.label}</a>
    {/each}
  </nav>
</header>

<style>
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    background: #6750a4;
    color: white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  }
  .brand {
    font-size: 1.2rem;
    font-weight: 700;
    color: white;
    text-decoration: none;
    letter-spacing: 0.02em;
  }
  nav {
    display: flex;
    gap: 8px;
  }
  nav a {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.9rem;
    transition: background 0.15s;
  }
  nav a:hover,
  nav a.active {
    background: rgba(255,255,255,0.18);
    color: white;
  }
</style>
