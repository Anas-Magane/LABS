export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>{`
          :root {
            --navy: #0a1628; --navy-2: #0f2137; --surface: #16233a; --text: #e6edf5;
            --text-dim: #94a7bf; --accent: #38bdf8; --accent-2: #2563eb; --border: rgba(255,255,255,0.08);
          }
          * { box-sizing: border-box; }
          html, body { margin: 0; padding: 0; }
          body {
            font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
            background: var(--navy);
            color: var(--text);
          }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
