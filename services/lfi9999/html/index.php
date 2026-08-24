<?php
// BlueOffice Breach - Challenge 8: LFI (port 9999)
// Plain landing page - nothing interesting here directly.
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlueOffice | Internal Tools</title>
<style>
  :root { --navy: #0a1628; --navy-2: #0f2137; --accent: #38bdf8; --text: #e6edf5; --text-dim: #94a7bf; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
         background: var(--navy); color: var(--text); }
  header { display: flex; align-items: center; gap: 0.6rem; padding: 1rem 2.5rem;
           background: var(--navy-2); border-bottom: 1px solid rgba(255,255,255,0.08);
           font-weight: 700; font-size: 1.1rem; }
  header .mark { width: 26px; height: 26px; border-radius: 6px;
           background: linear-gradient(135deg, var(--accent), #2563eb); }
  main { max-width: 640px; margin: 3.5rem auto; padding: 0 1.5rem; }
  .eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em;
             font-size: 0.75rem; font-weight: 600; }
  h1 { font-size: 1.7rem; margin: 0.5rem 0 0.6rem; }
  p.lead { color: var(--text-dim); font-size: 0.95rem; max-width: 460px; line-height: 1.6; }
</style>
</head>
<body>
<header><span class="mark"></span> BlueOffice</header>
<main>
  <div class="eyebrow">IT Operations</div>
  <h1>Internal Tools</h1>
  <p class="lead">This server hosts a few small internal utilities maintained by IT operations.</p>
</main>
</body>
</html>
