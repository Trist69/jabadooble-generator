<script lang="ts">
  export let data;
  const steps = [
    { icon: '📚', title: 'Create a Library', desc: 'Import images from the Harry Potter API, upload your own, or paste a JSON list.' },
    { icon: '🎨', title: 'Cartoonize', desc: 'Apply the cartoon filter to give your symbols a consistent fun look.' },
    { icon: '🃏', title: 'Generate Deck', desc: 'Click Generate — the Dobble algorithm builds 57 cards with 8 symbols each.' },
    { icon: '🖨️', title: 'Print & Play', desc: 'Export a PDF, print it, laminate the cards, and start playing!' },
  ];
</script>

<section class="hero">
  <h1>Dobble Generator</h1>
  <p class="subtitle">Create your own custom Dobble card game in minutes.</p>
  <div class="cta-row">
    <a class="btn-primary" href="/library">Get Started</a>
    <a class="btn-secondary" href="/game">View Games</a>
  </div>
</section>

<section class="how-it-works">
  <h2>How it works</h2>
  <div class="steps">
    {#each steps as step, i}
      <div class="step">
        <span class="step-icon">{step.icon}</span>
        <span class="step-num">0{i + 1}</span>
        <h3>{step.title}</h3>
        <p>{step.desc}</p>
      </div>
    {/each}
  </div>
</section>

<style>
  .hero {
    text-align: center;
    padding: 60px 16px 48px;
  }
  h1 {
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    color: #6750a4;
    margin-bottom: 12px;
  }
  .subtitle {
    font-size: 1.15rem;
    color: #49454f;
    margin-bottom: 32px;
  }
  .cta-row {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
  .btn-primary, .btn-secondary {
    padding: 12px 28px;
    border-radius: 24px;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    transition: box-shadow 0.2s, transform 0.1s;
  }
  .btn-primary {
    background: #6750a4;
    color: white;
  }
  .btn-primary:hover { box-shadow: 0 4px 14px rgba(103,80,164,0.4); transform: translateY(-1px); }
  .btn-secondary {
    background: #e8def8;
    color: #4a4458;
  }
  .btn-secondary:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.12); transform: translateY(-1px); }

  .how-it-works {
    padding: 32px 0;
  }
  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 24px;
    color: #1c1b1f;
  }
  .steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
  }
  .step {
    background: #f3edf7;
    border-radius: 16px;
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .step-icon { font-size: 2rem; }
  .step-num { font-size: 0.75rem; font-weight: 700; color: #9c8eb0; letter-spacing: 0.08em; }
  .step h3 { font-size: 1.05rem; font-weight: 600; }
  .step p { font-size: 0.88rem; color: #49454f; line-height: 1.5; }
</style>
