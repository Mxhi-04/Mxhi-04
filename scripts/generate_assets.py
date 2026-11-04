#!/usr/bin/env python3
"""
Procedural SVG asset generator for Mahi Patni's (@Mxhi-04) GitHub Profile.
Generates:
1. assets/odyssey-header.svg - High-tech cosmic/oceanic header banner
2. assets/divider.svg        - Glowing cyber-astral divider rule
3. assets/odyssey-footer.svg - Thematic Grand Line & pixel horizon footer
"""

import math
import os
import random

random.seed(42)

def generate_header():
    width = 1200
    height = 300
    
    # Constellation / Multi-Agent / Polymer Physics graph nodes
    nodes = []
    for _ in range(36):
        x = random.uniform(40, width - 40)
        y = random.uniform(25, height - 25)
        r = random.uniform(1.5, 3.5)
        alpha = random.uniform(0.3, 0.85)
        color = random.choice(["#38bdf8", "#818cf8", "#c084fc", "#34d399", "#f43f5e"])
        nodes.append((x, y, r, alpha, color))
    
    # Calculate connections between nearby nodes
    connections = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            x1, y1, _, _, _ = nodes[i]
            x2, y2, _, _, _ = nodes[j]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < 110:
                opacity = max(0.05, (1 - dist / 110) * 0.28)
                connections.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#38bdf8" stroke-opacity="{opacity:.3f}" stroke-width="0.75" />')

    node_elements = []
    for x, y, r, alpha, color in nodes:
        node_elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" fill-opacity="{alpha:.2f}" filter="url(#glow-light)" />')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- Gradients -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#040711" />
      <stop offset="50%" stop-color="#080e1e" />
      <stop offset="100%" stop-color="#050a14" />
    </linearGradient>

    <radialGradient id="nebula-cyan" cx="15%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.32" />
      <stop offset="60%" stop-color="#0369a1" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#0284c7" stop-opacity="0" />
    </radialGradient>

    <radialGradient id="nebula-violet" cx="85%" cy="70%" r="55%">
      <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.25" />
      <stop offset="50%" stop-color="#4f46e5" stop-opacity="0.06" />
      <stop offset="100%" stop-color="#4f46e5" stop-opacity="0" />
    </radialGradient>

    <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="35%" stop-color="#e0f2fe" />
      <stop offset="70%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#818cf8" />
    </linearGradient>

    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.0" />
      <stop offset="25%" stop-color="#38bdf8" stop-opacity="0.6" />
      <stop offset="50%" stop-color="#818cf8" stop-opacity="0.9" />
      <stop offset="75%" stop-color="#c084fc" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.0" />
    </linearGradient>

    <!-- Glow filters -->
    <filter id="glow-light" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glow-strong" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Subtle Dot Grid Pattern -->
    <pattern id="dot-grid" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#38bdf8" fill-opacity="0.1" />
    </pattern>
  </defs>

  <style>
    @keyframes pulse {{
      0%, 100% {{ opacity: 0.75; }}
      50% {{ opacity: 1; }}
    }}
    .mono {{
      font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Courier New', monospace;
    }}
    .sans {{
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }}
    .pulsing {{
      animation: pulse 4s ease-in-out infinite;
    }}
  </style>

  <!-- Background Base -->
  <rect width="{width}" height="{height}" rx="12" fill="url(#bg-grad)" />
  <rect width="{width}" height="{height}" rx="12" fill="url(#nebula-cyan)" />
  <rect width="{width}" height="{height}" rx="12" fill="url(#nebula-violet)" />
  <rect width="{width}" height="{height}" rx="12" fill="url(#dot-grid)" />

  <!-- Outer Frame -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="11" fill="none" stroke="url(#border-grad)" stroke-width="1.2" />

  <!-- Constellation Connections & Nodes -->
  <g class="pulsing">
    {' '.join(connections)}
    {' '.join(node_elements)}
  </g>

  <!-- High-tech HUD corner marks -->
  <path d="M 18,32 L 18,18 L 32,18" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round" />
  <path d="M {width - 18},32 L {width - 18},18 L {width - 32},18" fill="none" stroke="#818cf8" stroke-width="1.8" stroke-linecap="round" />
  <path d="M 18,{height - 32} L 18,{height - 18} L 32,{height - 18}" fill="none" stroke="#818cf8" stroke-width="1.8" stroke-linecap="round" />
  <path d="M {width - 18},{height - 32} L {width - 18},{height - 18} L {width - 32},{height - 18}" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round" />

  <!-- Center Content -->
  <!-- Top Terminal Logline -->
  <g transform="translate({width / 2}, 62)">
    <rect x="-195" y="-14" width="390" height="26" rx="13" fill="#0b1329" fill-opacity="0.85" stroke="#38bdf8" stroke-opacity="0.3" stroke-width="1" />
    <circle cx="-176" cy="-1" r="3.5" fill="#34d399" filter="url(#glow-light)" />
    <text x="-162" y="3" fill="#94a3b8" font-size="11.5" font-weight="500" class="mono" letter-spacing="1.5">SYSTEM // ODYSSEY LOG · CSE UNDERGRAD</text>
  </g>

  <!-- Main Hero Title -->
  <text x="{width / 2}" y="136" text-anchor="middle" class="sans" font-size="52" font-weight="900" letter-spacing="4" fill="url(#title-grad)" filter="url(#glow-strong)">MAHI PATNI</text>

  <!-- Thematic Subtitle -->
  <text x="{width / 2}" y="174" text-anchor="middle" class="mono" font-size="15" font-weight="500" letter-spacing="3" fill="#93c5fd">
    WRITING MY STORY IN PIXELS ✦ VOYAGE THROUGH CODE &amp; REASON
  </text>

  <!-- Tagline Pillars -->
  <g transform="translate({width / 2}, 225)">
    <!-- Pill 1: Physics-Informed ML -->
    <g transform="translate(-250, 0)">
      <rect x="-95" y="-13" width="190" height="26" rx="6" fill="#0f172a" fill-opacity="0.9" stroke="#38bdf8" stroke-opacity="0.4" stroke-width="1" />
      <text x="0" y="4" text-anchor="middle" class="mono" font-size="11" font-weight="600" fill="#38bdf8" letter-spacing="1">⚛ PHYSICS-INFORMED ML</text>
    </g>

    <!-- Pill 2: Multi-Agent Systems -->
    <g transform="translate(0, 0)">
      <rect x="-95" y="-13" width="190" height="26" rx="6" fill="#0f172a" fill-opacity="0.9" stroke="#818cf8" stroke-opacity="0.4" stroke-width="1" />
      <text x="0" y="4" text-anchor="middle" class="mono" font-size="11" font-weight="600" fill="#a5b4fc" letter-spacing="1">🛰 MULTI-AGENT SWARMS</text>
    </g>

    <!-- Pill 3: Immersive 3D Experiences -->
    <g transform="translate(250, 0)">
      <rect x="-95" y="-13" width="190" height="26" rx="6" fill="#0f172a" fill-opacity="0.9" stroke="#c084fc" stroke-opacity="0.4" stroke-width="1" />
      <text x="0" y="4" text-anchor="middle" class="mono" font-size="11" font-weight="600" fill="#e9d5ff" letter-spacing="1">🌊 IMMERSIVE 3D WORLDS</text>
    </g>
  </g>

  <!-- Subtle bottom horizon line with coordinates -->
  <line x1="120" y1="{height - 24}" x2="{width - 120}" y2="{height - 24}" stroke="url(#border-grad)" stroke-width="0.8" />
  <circle cx="{width / 2}" cy="{height - 24}" r="2.5" fill="#38bdf8" filter="url(#glow-light)" />
</svg>"""
    return svg

def generate_divider():
    width = 1200
    height = 24
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <linearGradient id="div-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0" />
      <stop offset="20%" stop-color="#38bdf8" stop-opacity="0.25" />
      <stop offset="48%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#818cf8" stop-opacity="1" />
      <stop offset="52%" stop-color="#c084fc" stop-opacity="0.8" />
      <stop offset="80%" stop-color="#c084fc" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#c084fc" stop-opacity="0" />
    </linearGradient>
    <filter id="div-glow">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Glowing Line -->
  <line x1="80" y1="{height / 2}" x2="{width - 80}" y2="{height / 2}" stroke="url(#div-grad)" stroke-width="1.2" />

  <!-- Center Diamond & Accents -->
  <g transform="translate({width / 2}, {height / 2})" filter="url(#div-glow)">
    <polygon points="0,-5 5,0 0,5 -5,0" fill="#38bdf8" />
    <circle cx="-16" cy="0" r="1.5" fill="#818cf8" opacity="0.8" />
    <circle cx="16" cy="0" r="1.5" fill="#818cf8" opacity="0.8" />
  </g>
</svg>"""
    return svg

def generate_footer():
    width = 1200
    height = 140
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="footer-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#050a14" stop-opacity="0.2" />
      <stop offset="100%" stop-color="#040711" stop-opacity="0.9" />
    </linearGradient>
    <linearGradient id="footer-accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.1" />
      <stop offset="50%" stop-color="#818cf8" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#c084fc" stop-opacity="0.1" />
    </linearGradient>
    <filter id="footer-glow">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .footer-mono {{
      font-family: 'JetBrains Mono', 'SF Mono', monospace;
    }}
  </style>

  <rect width="{width}" height="{height}" rx="10" fill="url(#footer-bg)" />
  <line x1="100" y1="20" x2="{width - 100}" y2="20" stroke="url(#footer-accent)" stroke-width="1.2" />

  <!-- Compass / Log Pose Center Indicator -->
  <g transform="translate({width / 2}, 20)" filter="url(#footer-glow)">
    <circle cx="0" cy="0" r="8" fill="#080e1e" stroke="#38bdf8" stroke-width="1.2" />
    <polygon points="0,-4 3,0 0,4 -3,0" fill="#38bdf8" />
  </g>

  <!-- Quote & Coordinates -->
  <text x="{width / 2}" y="65" text-anchor="middle" class="footer-mono" font-size="14" font-weight="600" fill="#e2e8f0" letter-spacing="2">
    &quot;INHERITED WILL, THE SWELL OF THE AGE, AND THE DREAMS OF ITS PEOPLE.&quot;
  </text>
  <text x="{width / 2}" y="92" text-anchor="middle" class="footer-mono" font-size="12" fill="#64748b" letter-spacing="3">
    THE HORIZON STRETCHES ENDLESSLY · THE GRAND LINE OF COMPUTATION AWAITS
  </text>

  <!-- Coordinates -->
  <text x="{width / 2}" y="116" text-anchor="middle" class="footer-mono" font-size="10.5" fill="#38bdf8" opacity="0.8" letter-spacing="2">
    ✦ CRAFTED BY MAHI PATNI (@MXHI-04) · ALL COORDINATES VERIFIED ✦
  </text>
</svg>"""
    return svg

def main():
    os.makedirs("assets", exist_ok=True)
    with open("assets/odyssey-header.svg", "w", encoding="utf-8") as f:
        f.write(generate_header())
    print("Generated assets/odyssey-header.svg")

    with open("assets/divider.svg", "w", encoding="utf-8") as f:
        f.write(generate_divider())
    print("Generated assets/divider.svg")

    with open("assets/odyssey-footer.svg", "w", encoding="utf-8") as f:
        f.write(generate_footer())
    print("Generated assets/odyssey-footer.svg")

if __name__ == "__main__":
    main()

