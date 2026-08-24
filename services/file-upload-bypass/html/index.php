<?php
// BlueOffice Breach - ID Badge Photo Upload (port 4500)
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlueOffice | ID Badge Photo Upload</title>
<style>
  :root { --navy: #0f2137; --accent: #2563eb; --border: #e2e8f0; --text: #1c2b3a; --text-dim: #5b6b82; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
         background: #f5f7fa; color: var(--text); }
  header { display: flex; align-items: center; gap: 0.6rem; padding: 1rem 2.5rem;
           background: var(--navy); color: #fff; font-weight: 700; font-size: 1.1rem; }
  header .mark { width: 26px; height: 26px; border-radius: 6px;
           background: linear-gradient(135deg, #0891b2, var(--accent)); }
  main { max-width: 480px; margin: 3rem auto; padding: 0 1.5rem; }
  .eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em;
             font-size: 0.75rem; font-weight: 600; }
  h1 { font-size: 1.4rem; margin: 0.5rem 0 0.4rem; }
  p.lead { color: var(--text-dim); font-size: 0.92rem; margin-bottom: 1.4rem; }
  .box { background: #fff; border: 1px solid var(--border); border-radius: 10px;
         padding: 1.6rem; box-shadow: 0 1px 3px rgba(15,33,55,0.06); }
  input[type=file] { display: block; width: 100%; padding: 8px; margin-bottom: 1rem;
         border: 1px dashed var(--border); border-radius: 6px; }
  button { padding: 10px 20px; background: var(--accent); color: white; border: none;
           border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
  button:hover { background: #1d4ed8; }
</style>
</head>
<body>
<header><span class="mark"></span> BlueOffice</header>
<main>
  <div class="eyebrow">HR &amp; Facilities</div>
  <h1>ID Badge Photo Upload</h1>
  <p class="lead">Upload your employee ID badge photo. JPG or PNG files only.</p>
  <div class="box">
    <form method="post" action="/upload.php" enctype="multipart/form-data">
      <input type="file" name="photo">
      <button type="submit">Upload</button>
    </form>
  </div>
</main>
</body>
</html>
