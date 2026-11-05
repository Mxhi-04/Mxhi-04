#!/usr/bin/env python3
"""
Generate animated banner GIF for Mahi Patni GitHub profile.
Features:
- Glowing and un-glowing pixel stars around the text and across the celestial cosmos
- Pulsing brightness, intensity, and expanding/contracting bloom/glow radius on celestial structures
- Pristine, stable, razor-sharp text ('MAHI PATNI' and 'WRITING MY STORY IN PIXELS ⌧ FOREVER CURIOUS')
- Seamless sinusoidal looping animation (20 frames, 90ms/frame, ~1.8s loop)
- File size optimized (< 2.5 MB) via high-fidelity palette quantization
"""

import math
import os
import numpy as np
from PIL import Image, ImageFilter
import scipy.ndimage as ndi

def main():
    repo_root = "/Users/jatin/.gemini/antigravity/scratch/Mxhi-profile"
    input_png = os.path.join(repo_root, "assets", "mahi-patni-banner.png")
    output_gif = os.path.join(repo_root, "assets", "mahi-patni-banner.gif")

    print(f"Loading input banner: {input_png}")
    orig_img = Image.open(input_png).convert("RGB")
    orig_arr = np.array(orig_img, dtype=np.float32)
    H, W, _ = orig_arr.shape
    print(f"Image dimensions: {W}x{H}")

    # ==========================================
    # 1. TEXT SEGMENTATION & ISOLATION
    # ==========================================
    # Text box for "MAHI PATNI" (rows 50..245, cols 80..480)
    # Front face: [255, 65, 95], 3D extrusion/shadow: [185, 15, 45]
    mahi_patni_box = (80, 50, 480, 245)
    x0, y0, x1, y1 = mahi_patni_box
    mp_crop = orig_arr[y0:y1, x0:x1]
    mp_is_text = (
        ((mp_crop[:, :, 0] == 255) & (mp_crop[:, :, 1] == 65) & (mp_crop[:, :, 2] == 95)) |
        ((mp_crop[:, :, 0] == 185) & (mp_crop[:, :, 1] == 15) & (mp_crop[:, :, 2] == 45))
    )
    mask_mp = np.zeros((H, W), dtype=bool)
    mask_mp[y0:y1, x0:x1] = mp_is_text

    # Subtitle box for "WRITING MY STORY IN PIXELS ⌧ FOREVER CURIOUS" (rows 280..315, cols 80..930)
    sub_box = (80, 280, 930, 315)
    sx0, sy0, sx1, sy1 = sub_box
    sub_crop = orig_arr[sy0:sy1, sx0:sx1]
    sub_lum = 0.299 * sub_crop[:, :, 0] + 0.587 * sub_crop[:, :, 1] + 0.114 * sub_crop[:, :, 2]
    sub_is_text = sub_lum > 30.0
    mask_sub = np.zeros((H, W), dtype=bool)
    mask_sub[sy0:sy1, sx0:sx1] = sub_is_text

    full_text_mask = mask_mp | mask_sub
    print(f"Extracted crisp text mask: {np.sum(full_text_mask)} text pixels")

    # Inpaint the background behind the text with dark space color so the animated glow
    # radiates naturally from behind the text without artifacts
    bg_base = orig_arr.copy()
    bg_base[full_text_mask] = [6.0, 2.0, 4.0]

    # ==========================================
    # 2. CELESTIAL STRUCTURES (RIGHT SIDE)
    # ==========================================
    # Identify key celestial features:
    # 1. Lower-right Radiant Star Flare with cross rays (cx: 789, cy: 330)
    # 2. Upper-middle Starburst / Nebula cluster (cx: 726, cy: 50)
    # 3. Upper-right Giant Cosmic Orb / Planet (cx: 1027, cy: 61)
    # 4. Bottom-right Corner Star / Flare (cx: 1177, cy: 367)
    Y, X = np.ogrid[:H, :W]
    celestial_centers = [
        # (cx, cy, phase_offset, influence_radius, intensity_amp, bloom_amp)
        (789.0, 330.0, 0.0,              150.0, 0.42, 0.55),  # Lower Radiant Flare
        (726.0,  50.0, 2.0 * math.pi / 3, 135.0, 0.35, 0.45),  # Upper Starburst
        (1027.0, 61.0, 4.0 * math.pi / 3, 115.0, 0.30, 0.40),  # Upper Planet Orb
        (1177.0, 367.0, 0.5 * math.pi,    95.0, 0.45, 0.50),  # Corner Flare
    ]

    # Pre-extract bright core highlights of celestial structures for bloom
    lum_bg = 0.299 * bg_base[:, :, 0] + 0.587 * bg_base[:, :, 1] + 0.114 * bg_base[:, :, 2]
    # Highlight mask (stars and celestial cores)
    celestial_highlight = np.clip((lum_bg - 45.0) / 210.0, 0.0, 1.0)
    # Zero out text region from bloom generation
    celestial_highlight[full_text_mask] = 0.0

    # Multi-scale Gaussian bloom kernels
    bloom_tight = ndi.gaussian_filter(celestial_highlight, sigma=3.0)
    bloom_mid   = ndi.gaussian_filter(celestial_highlight, sigma=7.0)
    bloom_wide  = ndi.gaussian_filter(celestial_highlight, sigma=14.0)

    # ==========================================
    # 3. CONSTELLATION OF PIXEL STARS
    # ==========================================
    # Rich constellation of pixel stars around the text and throughout open sky
    stars = [
        # --- Region 1: Above MAHI (y: 12..44, x: 50..550) ---
        {'x':  70, 'y': 22, 'type': 'cross',   'phase': 0.0, 'freq': 1},
        {'x': 110, 'y': 35, 'type': 'micro',   'phase': 1.2, 'freq': 1},
        {'x': 145, 'y': 18, 'type': 'radiant', 'phase': 2.4, 'freq': 1},
        {'x': 195, 'y': 38, 'type': 'micro',   'phase': 3.8, 'freq': 1},
        {'x': 240, 'y': 20, 'type': 'cross',   'phase': 4.5, 'freq': 1},
        {'x': 285, 'y': 32, 'type': 'ember',   'phase': 0.8, 'freq': 1},
        {'x': 335, 'y': 16, 'type': 'micro',   'phase': 2.1, 'freq': 1},
        {'x': 380, 'y': 34, 'type': 'radiant', 'phase': 5.2, 'freq': 1},
        {'x': 430, 'y': 22, 'type': 'cross',   'phase': 1.7, 'freq': 1},
        {'x': 480, 'y': 36, 'type': 'micro',   'phase': 3.3, 'freq': 1},
        {'x': 525, 'y': 18, 'type': 'ember',   'phase': 4.9, 'freq': 1},
        {'x': 565, 'y': 32, 'type': 'cross',   'phase': 0.5, 'freq': 1},

        # --- Region 2: Left of MAHI PATNI (x: 18..72, y: 50..265) ---
        {'x':  35, 'y':  55, 'type': 'micro',   'phase': 1.9, 'freq': 1},
        {'x':  58, 'y':  82, 'type': 'cross',   'phase': 3.4, 'freq': 1},
        {'x':  28, 'y': 118, 'type': 'ember',   'phase': 5.0, 'freq': 1},
        {'x':  62, 'y': 148, 'type': 'radiant', 'phase': 0.7, 'freq': 1},
        {'x':  32, 'y': 182, 'type': 'micro',   'phase': 2.5, 'freq': 1},
        {'x':  55, 'y': 215, 'type': 'cross',   'phase': 4.1, 'freq': 1},
        {'x':  38, 'y': 252, 'type': 'ember',   'phase': 1.1, 'freq': 1},

        # --- Region 3: Right of MAHI & PATNI (x: 360..480, y: 55..235) ---
        {'x': 375, 'y':  72, 'type': 'cross',   'phase': 2.8, 'freq': 1},
        {'x': 420, 'y':  95, 'type': 'radiant', 'phase': 4.6, 'freq': 1},
        {'x': 460, 'y':  68, 'type': 'micro',   'phase': 0.3, 'freq': 1},
        {'x': 385, 'y': 140, 'type': 'ember',   'phase': 3.1, 'freq': 1},
        {'x': 445, 'y': 155, 'type': 'cross',   'phase': 5.7, 'freq': 1},
        {'x': 395, 'y': 195, 'type': 'micro',   'phase': 1.5, 'freq': 1},
        {'x': 455, 'y': 225, 'type': 'radiant', 'phase': 3.9, 'freq': 1},

        # --- Region 4: Between PATNI & Subtitle (y: 246..276, x: 60..580) ---
        {'x':  95, 'y': 260, 'type': 'micro',   'phase': 0.9, 'freq': 1},
        {'x': 155, 'y': 265, 'type': 'cross',   'phase': 2.3, 'freq': 1},
        {'x': 220, 'y': 258, 'type': 'radiant', 'phase': 4.2, 'freq': 1},
        {'x': 295, 'y': 266, 'type': 'micro',   'phase': 5.5, 'freq': 1},
        {'x': 370, 'y': 258, 'type': 'cross',   'phase': 1.3, 'freq': 1},
        {'x': 450, 'y': 264, 'type': 'ember',   'phase': 3.0, 'freq': 1},
        {'x': 520, 'y': 256, 'type': 'cross',   'phase': 4.8, 'freq': 1},

        # --- Region 5: Below Subtitle (y: 322..368, x: 50..620) ---
        {'x':  75, 'y': 345, 'type': 'cross',   'phase': 1.6, 'freq': 1},
        {'x': 130, 'y': 335, 'type': 'micro',   'phase': 3.2, 'freq': 1},
        {'x': 190, 'y': 355, 'type': 'ember',   'phase': 4.7, 'freq': 1},
        {'x': 260, 'y': 338, 'type': 'radiant', 'phase': 0.4, 'freq': 1},
        {'x': 340, 'y': 356, 'type': 'micro',   'phase': 2.2, 'freq': 1},
        {'x': 420, 'y': 336, 'type': 'cross',   'phase': 3.7, 'freq': 1},
        {'x': 490, 'y': 352, 'type': 'ember',   'phase': 5.3, 'freq': 1},
        {'x': 560, 'y': 338, 'type': 'radiant', 'phase': 1.0, 'freq': 1},

        # --- Region 6: Transition corridor to celestial structures (x: 500..660, y: 60..250) ---
        {'x': 520, 'y':  85, 'type': 'radiant', 'phase': 2.7, 'freq': 1},
        {'x': 570, 'y': 120, 'type': 'micro',   'phase': 4.4, 'freq': 1},
        {'x': 540, 'y': 175, 'type': 'cross',   'phase': 0.2, 'freq': 1},
        {'x': 600, 'y': 195, 'type': 'radiant', 'phase': 3.5, 'freq': 1},
        {'x': 560, 'y': 225, 'type': 'micro',   'phase': 5.1, 'freq': 1},
        {'x': 635, 'y': 240, 'type': 'cross',   'phase': 1.8, 'freq': 1},

        # --- Region 7: Mid-sky between celestial bodies (x: 680..1120, y: 160..240) ---
        {'x': 710, 'y': 180, 'type': 'micro',   'phase': 3.6, 'freq': 1},
        {'x': 770, 'y': 205, 'type': 'cross',   'phase': 5.4, 'freq': 1},
        {'x': 840, 'y': 175, 'type': 'radiant', 'phase': 0.6, 'freq': 1},
        {'x': 910, 'y': 210, 'type': 'micro',   'phase': 2.6, 'freq': 1},
        {'x': 980, 'y': 185, 'type': 'cross',   'phase': 4.0, 'freq': 1},
        {'x': 1050, 'y': 215, 'type': 'radiant', 'phase': 5.8, 'freq': 1},
        {'x': 1110, 'y': 190, 'type': 'micro',   'phase': 1.4, 'freq': 1},

        # --- Region 8: Outer borders & corners (x: 1120..1185, y: 20..350) ---
        {'x': 1145, 'y':  35, 'type': 'cross',   'phase': 2.9, 'freq': 1},
        {'x': 1175, 'y':  85, 'type': 'radiant', 'phase': 4.3, 'freq': 1},
        {'x': 1135, 'y': 140, 'type': 'micro',   'phase': 0.8, 'freq': 1},
        {'x': 1165, 'y': 245, 'type': 'cross',   'phase': 3.2, 'freq': 1},
        {'x': 1130, 'y': 310, 'type': 'ember',   'phase': 5.1, 'freq': 1},
    ]

    print(f"Loaded constellation catalog with {len(stars)} pixel stars")

    def draw_pixel_star(canvas, x, y, star_type, pulse):
        p = max(0.0, min(1.0, pulse))

        def add_px(px, py, rgb_val):
            if 0 <= px < W and 0 <= py < H and not full_text_mask[py, px]:
                canvas[py, px] = np.maximum(canvas[py, px], rgb_val)

        def blend_px(px, py, rgb_val):
            if 0 <= px < W and 0 <= py < H and not full_text_mask[py, px]:
                canvas[py, px] = np.clip(canvas[py, px] + rgb_val, 0.0, 255.0)

        if star_type == 'micro':
            # Single pixel sparkle with 4-cross halo
            core = np.array([80.0 + 175.0 * p, 12.0 + 88.0 * p, 25.0 + 115.0 * p], dtype=np.float32)
            add_px(x, y, core)
            if p > 0.35:
                halo = np.array([125.0, 28.0, 48.0], dtype=np.float32) * (p - 0.35) / 0.65
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    blend_px(x + dx, y + dy, halo)

        elif star_type == 'ember':
            # 2x2 warm breathing ember
            core = np.array([60.0 + 180.0 * p, 10.0 + 40.0 * p, 20.0 + 55.0 * p], dtype=np.float32)
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                add_px(x + dx, y + dy, core)
            if p > 0.45:
                glow = np.array([75.0, 16.0, 28.0], dtype=np.float32) * (p - 0.45) / 0.55
                for dx, dy in [(-1, 0), (-1, 1), (2, 0), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)]:
                    blend_px(x + dx, y + dy, glow)

        elif star_type == 'cross':
            # 4-point classic retro pixel star
            core = np.array([160.0 + 95.0 * p, 25.0 + 225.0 * p, 45.0 + 205.0 * p], dtype=np.float32)
            add_px(x, y, core)
            inner = np.array([120.0 + 135.0 * p, 20.0 + 80.0 * p, 35.0 + 105.0 * p], dtype=np.float32)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                add_px(x + dx, y + dy, inner)
            if p > 0.35:
                outer = np.array([210.0, 48.0, 80.0], dtype=np.float32) * (p - 0.35) / 0.65
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    blend_px(x + dx, y + dy, outer)
            if p > 0.65:
                diag = np.array([110.0, 22.0, 38.0], dtype=np.float32) * (p - 0.65) / 0.35
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    blend_px(x + dx, y + dy, diag)

        elif star_type == 'radiant':
            # Radiant diamond sparkle flare with bloom
            if p > 0.65:
                core = np.array([255.0, 255.0, 255.0], dtype=np.float32)
            else:
                core = np.array([220.0 + 35.0 * p / 0.65, 140.0 + 115.0 * p / 0.65, 160.0 + 95.0 * p / 0.65], dtype=np.float32)
            add_px(x, y, core)
            arm1 = np.array([255.0, 120.0 * p + 60.0, 140.0 * p + 80.0], dtype=np.float32)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                add_px(x + dx, y + dy, arm1)
            arm2 = np.array([255.0 * p, 80.0 * p, 110.0 * p], dtype=np.float32)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                blend_px(x + dx, y + dy, arm2)
            if p > 0.4:
                arm3 = np.array([200.0, 45.0, 70.0], dtype=np.float32) * (p - 0.4) / 0.6
                for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
                    blend_px(x + dx, y + dy, arm3)
            if p > 0.7:
                arm4 = np.array([145.0, 28.0, 50.0], dtype=np.float32) * (p - 0.7) / 0.3
                for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4)]:
                    blend_px(x + dx, y + dy, arm4)
            diag = np.array([160.0, 35.0, 60.0], dtype=np.float32) * p
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                blend_px(x + dx, y + dy, diag)

    # ==========================================
    # 4. ANIMATION FRAME SYNTHESIS (20 FRAMES)
    # ==========================================
    NUM_FRAMES = 20
    FRAME_DELAY_MS = 90
    print(f"Generating {NUM_FRAMES} smooth sinusoidal animation frames ({FRAME_DELAY_MS}ms per frame)...")

    rendered_frames = []

    for frame_idx in range(NUM_FRAMES):
        theta = 2.0 * math.pi * frame_idx / NUM_FRAMES

        # 4A. Celestial brightness modulation & expanding bloom radius
        mod_map = np.ones((H, W), dtype=np.float32)
        bloom_tight_weight = np.zeros((H, W), dtype=np.float32)
        bloom_wide_weight  = np.zeros((H, W), dtype=np.float32)

        for cx, cy, phase, r, i_amp, b_amp in celestial_centers:
            d2 = (X - cx)**2 + (Y - cy)**2
            spatial_w = np.exp(-d2 / (2.0 * r**2))
            pulse = 0.5 + 0.5 * math.sin(theta + phase)

            # Brightness factor
            bright_factor = (1.0 - i_amp * 0.4) + (i_amp * 1.4) * pulse
            mod_map += spatial_w * (bright_factor - 1.0)

            # Expanding bloom radius: tight bloom dominates when dim, wide bloom swells when peak
            bloom_tight_weight += spatial_w * (b_amp * (0.3 + 0.5 * (1.0 - pulse)))
            bloom_wide_weight  += spatial_w * (b_amp * (0.2 + 0.9 * pulse))

        # Modulate base celestial background brightness
        bg_frame = bg_base * mod_map[:, :, np.newaxis]

        # Composite dynamic expanding bloom
        bloom_tint_coral = np.array([255.0, 65.0, 95.0], dtype=np.float32)
        bloom_tint_rose  = np.array([245.0, 30.0, 65.0], dtype=np.float32)

        bloom_rgb = (
            bloom_tight[:, :, np.newaxis] * bloom_tight_weight[:, :, np.newaxis] * bloom_tint_coral +
            bloom_wide[:, :, np.newaxis]  * bloom_wide_weight[:, :, np.newaxis]  * bloom_tint_rose
        )
        bg_frame += bloom_rgb

        # 4B. Render the 59 background pixel stars
        for s in stars:
            s_pulse = 0.5 + 0.5 * math.sin(s['freq'] * theta + s['phase'])
            draw_pixel_star(bg_frame, s['x'], s['y'], s['type'], s_pulse)

        # 4C. Clamp background
        bg_frame = np.clip(bg_frame, 0.0, 255.0)

        # 4D. Composite text layer on top: 100% stable, crisp, and unchanged
        frame_final = bg_frame.copy()
        frame_final[full_text_mask] = orig_arr[full_text_mask]

        pil_frame = Image.fromarray(np.uint8(frame_final))
        rendered_frames.append(pil_frame)

    # ==========================================
    # 5. PALETTE QUANTIZATION & GIF EXPORT
    # ==========================================
    print("Building optimal 256-color palette across the animation cycle...")
    # Sample keyframes across the loop to construct the optimal master palette
    sample_indices = [0, 4, 8, 12, 16]
    palette_canvas = Image.new("RGB", (W, H * len(sample_indices)))
    for idx, f_idx in enumerate(sample_indices):
        palette_canvas.paste(rendered_frames[f_idx], (0, idx * H))

    master_palette = palette_canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    print("Quantizing all frames with master palette...")
    quantized_frames = [
        f.quantize(palette=master_palette, dither=Image.Dither.FLOYDSTEINBERG)
        for f in rendered_frames
    ]

    print(f"Saving animated GIF to: {output_gif}")
    quantized_frames[0].save(
        output_gif,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True
    )

    # ==========================================
    # 6. VERIFICATION
    # ==========================================
    if not os.path.exists(output_gif):
        raise FileNotFoundError(f"Failed to generate {output_gif}")

    file_size_bytes = os.path.getsize(output_gif)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Check frame count
    with Image.open(output_gif) as gif:
        n_frames = gif.n_frames
        gif_w, gif_h = gif.size

    print("\n" + "=" * 50)
    print("ANIMATED BANNER GIF GENERATION COMPLETE!")
    print(f"Path: {output_gif}")
    print(f"Dimensions: {gif_w} x {gif_h}")
    print(f"Frame count: {n_frames} frames")
    print(f"Frame delay: {FRAME_DELAY_MS} ms ({1000/FRAME_DELAY_MS:.1f} fps, ~{n_frames*FRAME_DELAY_MS/1000:.2f}s loop)")
    print(f"File size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print(f"Size constraint (< 2.5 MB): {'PASSED' if file_size_mb < 2.5 else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    main()
