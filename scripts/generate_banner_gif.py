#!/usr/bin/env python3
"""
High-Quality Animated Banner GIF Generator for Mahi Patni's GitHub Profile.

Features:
1. Left-aligned 'MAHI PATNI' layout with dark left region and red pixel stars on the right.
2. Existing stars pulsing/breathing: Glowing red pixel stars pulse smoothly from darker
   to brighter and back in a seamless sinusoidal loop.
3. Twinkling red sparkle pixels: 8-bit retro red sparkle pixels (crosses, diamonds, glints, embers)
   scattered across the starry background that twinkle on/off with staggered phases.
4. Name light animation: Subtle breathing ambient neon glow and an elegant specular light shimmer
   gliding across the upper letters of 'MAHI PATNI'.
5. Precise technical specs:
   - 1200 x 380 resolution
   - 20 frames at 100ms/frame (2.0s seamless loop)
   - Optimized GIF palette (< 5 MB target) with vibrant colors and razor-sharp pixel typography.
"""

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import scipy.ndimage as ndi

def main():
    repo_root = "/Users/mahipatni/Antigravity/profile"
    bg_source_path = "/Users/mahipatni/.gemini/antigravity/brain/4a57e73e-4d47-428f-a729-78d0704bc591/.user_uploaded/media_1793832947468_51cce90a.jpg"
    font_path = os.path.join(repo_root, "assets", "fonts", "RawPixel.otf")
    output_gif_path = os.path.join(repo_root, "assets", "mahi-patni-banner.gif")

    print(f"Loading source background from: {bg_source_path}")
    bg_orig = Image.open(bg_source_path).convert("RGB")
    print(f"Source size: {bg_orig.size}")

    # ==========================================
    # 1. BASE BACKGROUND & DARK GRADIENT MASK
    # ==========================================
    target_w, target_h = 1200, 380
    scale = target_w / bg_orig.width
    scaled_h = int(bg_orig.height * scale)
    bg_scaled = bg_orig.resize((target_w, scaled_h), Image.Resampling.LANCZOS)
    y_offset = (scaled_h - target_h) // 2
    bg_cropped = bg_scaled.crop((0, y_offset, target_w, y_offset + target_h)).convert("RGBA")

    # Dark gradient overlay on the left side:
    # 0..420: almost solid dark (alpha 235) for maximum contrast
    # 420..720: smooth quadratic falloff into the vibrant starfield
    # 720..1200: 0 alpha (pure cosmic starry background)
    dim_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    d_dim = ImageDraw.Draw(dim_layer)
    for x in range(target_w):
        if x < 420:
            alpha = 235
        elif x < 720:
            t = (x - 420) / (720 - 420)
            alpha = int(235 * (1.0 - t * t))
        else:
            alpha = 0
        d_dim.line([(x, 0), (x, target_h)], fill=(4, 2, 4, alpha))

    base_banner_bg = Image.alpha_composite(bg_cropped, dim_layer).convert("RGB")
    arr_bg_base = np.array(base_banner_bg, dtype=np.float32)

    # ==========================================
    # 2. TYPOGRAPHY & MASKS (RawPixel.otf)
    # ==========================================
    print(f"Loading font from: {font_path}")
    font_name = ImageFont.truetype(font_path, 105)
    font_sub = ImageFont.truetype(font_path, 20)

    left_x = 90
    y_mahi = 50
    y_patni = 160
    sub_y = 285

    # Render clean text masks
    mask_mahi = Image.new("L", (target_w, target_h), 0)
    d_m = ImageDraw.Draw(mask_mahi)
    d_m.text((left_x, y_mahi), "MAHI", font=font_name, fill=255)
    bbox_mahi = mask_mahi.getbbox()
    mid_y_mahi = (bbox_mahi[1] + bbox_mahi[3]) // 2

    mask_patni = Image.new("L", (target_w, target_h), 0)
    d_p = ImageDraw.Draw(mask_patni)
    d_p.text((left_x, y_patni), "PATNI", font=font_name, fill=255)
    bbox_patni = mask_patni.getbbox()
    mid_y_patni = (bbox_patni[1] + bbox_patni[3]) // 2

    arr_mahi = np.array(mask_mahi) > 0
    arr_patni = np.array(mask_patni) > 0
    full_text_mask = arr_mahi | arr_patni

    # Separate upper face (front coral) and lower face (shadow crimson)
    Y, X = np.ogrid[:target_h, :target_w]
    upper_face_mask = (arr_mahi & (Y < mid_y_mahi)) | (arr_patni & (Y < mid_y_patni))
    lower_face_mask = (arr_mahi & (Y >= mid_y_mahi)) | (arr_patni & (Y >= mid_y_patni))

    # Bevel outline mask (5 pixels dilation around text)
    full_text_img = Image.new("L", (target_w, target_h), 0)
    full_text_draw = ImageDraw.Draw(full_text_img)
    full_text_draw.text((left_x, y_mahi), "MAHI", font=font_name, fill=255)
    full_text_draw.text((left_x, y_patni), "PATNI", font=font_name, fill=255)

    outline_w = 5
    dilated_text = full_text_img.filter(ImageFilter.MaxFilter(outline_w * 2 + 1))
    arr_dilated = np.array(dilated_text) > 0
    arr_outline = arr_dilated & (~full_text_mask)

    # Ambient neon glow mask (Gaussian blur of dilated text)
    glow_img_tight = dilated_text.filter(ImageFilter.GaussianBlur(8))
    glow_img_wide  = dilated_text.filter(ImageFilter.GaussianBlur(16))
    arr_glow_tight = np.array(glow_img_tight, dtype=np.float32) / 255.0
    arr_glow_wide  = np.array(glow_img_wide, dtype=np.float32) / 255.0

    # Subtitle pill box
    sub_text = "WRITING MY STORY IN PIXELS ✦ FOREVER CURIOUS"
    dummy_sub = ImageDraw.Draw(Image.new("L", (1, 1)))
    bbox_sub = dummy_sub.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = bbox_sub[2] - bbox_sub[0]
    sub_h = bbox_sub[3] - bbox_sub[1]
    pill_pad_x, pill_pad_y = 16, 5
    pill_rect = [left_x - 4, sub_y - pill_pad_y, left_x + sub_w + pill_pad_x * 2 - 4, sub_y + sub_h + pill_pad_y]

    # Pre-render subtitle badge into an RGBA layer
    sub_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    d_sub = ImageDraw.Draw(sub_layer)
    d_sub.rectangle(pill_rect, fill=(10, 6, 8, 235), outline=(220, 30, 60, 255), width=1)
    d_sub.text((left_x + pill_pad_x - 4, sub_y), sub_text, font=font_sub, fill=(255, 210, 220, 255))
    arr_sub_layer = np.array(sub_layer, dtype=np.float32)
    sub_alpha = arr_sub_layer[:, :, 3:] / 255.0
    sub_rgb = arr_sub_layer[:, :, :3]

    # Total text & subtitle exclusion zone (so stars/sparkles don't collide with text)
    exclusion_mask = arr_dilated | (arr_sub_layer[:, :, 3] > 10)

    # ==========================================
    # 3. EXISTING STARS PULSING & BLOOMING
    # ==========================================
    print("Extracting existing background stars for smooth breathing animation...")
    r_ch = arr_bg_base[:, :, 0]
    g_ch = arr_bg_base[:, :, 1]
    b_ch = arr_bg_base[:, :, 2]
    # Measure star prominence: high red contrast against green/blue, and luminance
    red_prominence = r_ch - np.maximum(g_ch, b_ch)
    star_mask = np.clip((red_prominence * 0.75 + r_ch * 0.25 - 28.0) / 90.0, 0.0, 1.0)
    # Zero out left region and text
    star_mask[:, :480] = 0.0
    star_mask[exclusion_mask] = 0.0

    # Multi-scale Gaussian bloom on existing bright star cores
    bright_cores = np.clip((r_ch - 130.0) / 120.0, 0.0, 1.0) * star_mask
    star_bloom_tight = ndi.gaussian_filter(bright_cores, sigma=3.0)
    star_bloom_wide  = ndi.gaussian_filter(bright_cores, sigma=7.5)

    # Spatial phase field for organic breathing of star clusters
    star_phase_map = (
        np.sin(X / 140.0) * 1.3 +
        np.cos(Y / 85.0) * 1.1 +
        (X - 500.0) / 280.0
    )

    # ==========================================
    # 4. TWINKLING RETRO RED SPARKLE PIXELS
    # ==========================================
    # 8-bit retro sparkle pixels with staggered phases across the starry sky
    sparkle_catalog = [
        # --- Top Sky above MAHI & PATNI ---
        {"x": 125, "y":  24, "type": "glint",   "phase": 0.2},
        {"x": 215, "y":  30, "type": "cross",   "phase": 1.7},
        {"x": 310, "y":  18, "type": "diamond", "phase": 3.4},
        {"x": 420, "y":  26, "type": "glint",   "phase": 5.1},
        # --- Transition Corridor (x: 470..620) ---
        {"x": 485, "y":  72, "type": "cross",   "phase": 0.8},
        {"x": 535, "y": 135, "type": "diamond", "phase": 2.5},
        {"x": 495, "y": 210, "type": "glint",   "phase": 4.2},
        {"x": 555, "y": 270, "type": "cross",   "phase": 5.9},
        {"x": 590, "y":  85, "type": "glint",   "phase": 1.4},
        {"x": 615, "y": 220, "type": "diamond", "phase": 3.6},
        # --- Between PATNI & Subtitle ---
        {"x": 385, "y": 255, "type": "glint",   "phase": 1.2},
        {"x": 445, "y": 260, "type": "cross",   "phase": 3.8},
        # --- Below Subtitle ---
        {"x": 155, "y": 345, "type": "glint",   "phase": 2.0},
        {"x": 265, "y": 340, "type": "cross",   "phase": 4.6},
        {"x": 385, "y": 352, "type": "diamond", "phase": 0.4},
        {"x": 515, "y": 348, "type": "glint",   "phase": 3.0},
        # --- Upper Celestial Starburst & Giant Orb (x: 650..1150, y: 15..110) ---
        {"x": 665, "y":  40, "type": "diamond", "phase": 1.0},
        {"x": 725, "y":  22, "type": "cross",   "phase": 3.1},
        {"x": 795, "y":  46, "type": "diamond", "phase": 5.3},
        {"x": 865, "y":  28, "type": "glint",   "phase": 0.6},
        {"x": 935, "y":  48, "type": "cross",   "phase": 2.8},
        {"x": 1015,"y":  32, "type": "diamond", "phase": 4.7},
        {"x": 1095,"y":  55, "type": "cross",   "phase": 0.1},
        {"x": 1155,"y":  35, "type": "glint",   "phase": 2.3},
        # --- Mid-Sky Starfield (x: 650..1150, y: 120..250) ---
        {"x": 675, "y": 140, "type": "cross",   "phase": 1.5},
        {"x": 745, "y": 185, "type": "diamond", "phase": 3.7},
        {"x": 815, "y": 135, "type": "glint",   "phase": 5.8},
        {"x": 885, "y": 195, "type": "cross",   "phase": 1.1},
        {"x": 955, "y": 145, "type": "diamond", "phase": 3.3},
        {"x": 1035,"y": 180, "type": "glint",   "phase": 5.0},
        {"x": 1115,"y": 150, "type": "cross",   "phase": 0.9},
        {"x": 1175,"y": 200, "type": "diamond", "phase": 3.2},
        # --- Lower Celestial Flare & Clusters (x: 650..1180, y: 260..365) ---
        {"x": 705, "y": 325, "type": "cross",   "phase": 4.1},
        {"x": 765, "y": 255, "type": "diamond", "phase": 0.3},
        {"x": 835, "y": 335, "type": "glint",   "phase": 2.2},
        {"x": 905, "y": 275, "type": "cross",   "phase": 3.9},
        {"x": 975, "y": 330, "type": "diamond", "phase": 5.6},
        {"x": 1055,"y": 265, "type": "glint",   "phase": 1.8},
        {"x": 1115,"y": 325, "type": "cross",   "phase": 4.3},
        {"x": 1165,"y": 280, "type": "diamond", "phase": 0.7},
        {"x": 1155,"y": 355, "type": "glint",   "phase": 2.6},
    ]

    print(f"Loaded {len(sparkle_catalog)} retro sparkle pixels.")

    def render_retro_sparkle(canvas, x, y, star_type, p):
        """Draw an authentic 8-bit retro pixel sparkle onto canvas."""
        if p <= 0.01:
            return

        def put_px(px, py, rgb_val):
            if 0 <= px < target_w and 0 <= py < target_h and not exclusion_mask[py, px]:
                canvas[py, px] = np.maximum(canvas[py, px], rgb_val)

        def add_px(px, py, rgb_val):
            if 0 <= px < target_w and 0 <= py < target_h and not exclusion_mask[py, px]:
                canvas[py, px] = np.clip(canvas[py, px] + rgb_val, 0.0, 255.0)

        if star_type == "glint":
            # Sharp 1-pixel diamond glint
            core = np.array([255.0, 110.0 + 145.0 * p, 130.0 + 125.0 * p], dtype=np.float32) * p
            put_px(x, y, core)
            if p > 0.25:
                arm = np.array([210.0, 35.0, 55.0], dtype=np.float32) * (p - 0.25) / 0.75
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    add_px(x + dx, y + dy, arm)

        elif star_type == "cross":
            # Classic 4-point retro cross star
            core = np.array([255.0, 140.0 + 115.0 * p, 150.0 + 105.0 * p], dtype=np.float32)
            put_px(x, y, core)
            inner = np.array([255.0, 50.0 + 50.0 * p, 75.0 + 40.0 * p], dtype=np.float32) * p
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                put_px(x + dx, y + dy, inner)
            if p > 0.35:
                outer = np.array([195.0, 25.0, 45.0], dtype=np.float32) * (p - 0.35) / 0.65
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    add_px(x + dx, y + dy, outer)
            if p > 0.65:
                diag = np.array([135.0, 20.0, 35.0], dtype=np.float32) * (p - 0.65) / 0.35
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    add_px(x + dx, y + dy, diag)

        elif star_type == "diamond":
            # 8-bit radiant diamond sparkle
            core = np.array([255.0, 240.0, 245.0], dtype=np.float32)
            put_px(x, y, core)
            ring = np.array([255.0, 85.0 + 80.0 * p, 105.0 + 70.0 * p], dtype=np.float32)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                put_px(x + dx, y + dy, ring)
            diag = np.array([185.0, 30.0, 50.0], dtype=np.float32) * p
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                add_px(x + dx, y + dy, diag)
            if p > 0.4:
                tip1 = np.array([230.0, 45.0, 70.0], dtype=np.float32) * (p - 0.4) / 0.6
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    add_px(x + dx, y + dy, tip1)
            if p > 0.7:
                tip2 = np.array([160.0, 25.0, 40.0], dtype=np.float32) * (p - 0.7) / 0.3
                for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
                    add_px(x + dx, y + dy, tip2)

    # ==========================================
    # 5. SYNTHESIS LOOP (20 FRAMES, 100ms/frame)
    # ==========================================
    NUM_FRAMES = 20
    FRAME_DELAY_MS = 100
    print(f"Generating {NUM_FRAMES} seamless animation frames at {FRAME_DELAY_MS}ms per frame...")

    rendered_frames = []

    for frame_idx in range(NUM_FRAMES):
        theta = 2.0 * math.pi * frame_idx / NUM_FRAMES

        # ----------------------------------------------------
        # 5A. Existing Stars Pulsing & Breathing
        # ----------------------------------------------------
        # Sinusoidal breath value in [-1.0, 1.0]
        breath = np.sin(theta + star_phase_map)
        # Scale brightness: 0.7x when dim (-1), 1.35x when bright (+1)
        scale_factor = 1.0 + (0.35 * breath * star_mask)
        frame_canvas = arr_bg_base * scale_factor[:, :, np.newaxis]

        # Dynamic star bloom swelling at peak brightness
        bloom_factor = np.clip(breath, 0.0, 1.0) * star_mask
        tint_tight = np.array([255.0, 70.0, 95.0], dtype=np.float32)
        tint_wide  = np.array([220.0, 25.0, 50.0], dtype=np.float32)
        bloom_rgb = (
            star_bloom_tight[:, :, np.newaxis] * (bloom_factor[:, :, np.newaxis] * 0.45) * tint_tight +
            star_bloom_wide[:, :, np.newaxis]  * (bloom_factor[:, :, np.newaxis] * 0.25) * tint_wide
        )
        frame_canvas += bloom_rgb

        # ----------------------------------------------------
        # 5B. Twinkling Retro Red Sparkle Pixels
        # ----------------------------------------------------
        for s in sparkle_catalog:
            # Twinkle curve with cubic power for authentic on/off blink
            s_val = max(0.0, math.sin(theta + s["phase"])) ** 3.0
            render_retro_sparkle(frame_canvas, s["x"], s["y"], s["type"], s_val)

        # Clamp background colors
        frame_canvas = np.clip(frame_canvas, 0.0, 255.0)

        # ----------------------------------------------------
        # 5C. Name Light Animation: Ambient Glow & Shimmer
        # ----------------------------------------------------
        # 1. Subtle breathing ambient neon glow behind text outline
        # Glow pulse in [0.28, 0.48]
        glow_pulse = 0.38 + 0.10 * math.sin(theta)
        glow_layer = (
            arr_glow_tight[:, :, np.newaxis] * (glow_pulse * 0.7) * np.array([235.0, 30.0, 60.0]) +
            arr_glow_wide[:, :, np.newaxis]  * (glow_pulse * 0.3) * np.array([195.0, 15.0, 35.0])
        )
        # Apply glow where not covered by text or outline
        glow_intensity = np.clip(arr_glow_tight * glow_pulse * 1.2, 0.0, 1.0)
        mask_apply_glow = (glow_intensity > 0.03) & (~arr_dilated)
        frame_canvas[mask_apply_glow] = np.clip(
            frame_canvas[mask_apply_glow] + glow_layer[mask_apply_glow],
            0.0, 255.0
        )

        # 2. Text Bevel Outline (deep crisp charcoal [4, 4, 4])
        frame_canvas[arr_outline] = [4.0, 4.0, 4.0]

        # 3. Lower face (deep 3D shadow crimson [185, 15, 45])
        frame_canvas[lower_face_mask] = [185.0, 15.0, 45.0]

        # 4. Upper face (vivid coral [255, 65, 95]) with elegant specular shimmer sweep
        # Slanted shimmer beam sweeping across upper letters from left to right:
        # Letters span x: 94..346. Beam sweeps from x=30 to x=410.
        x_beam = 30.0 + 380.0 * (frame_idx / NUM_FRAMES)
        # Seamless loop taper: smooth sin envelope so seam at frame 19->0 is 100% continuous
        beam_taper = math.sin(math.pi * frame_idx / NUM_FRAMES)
        # Compute shimmer weight per pixel
        beam_dist = (X - x_beam) + (Y - 50.0) * 0.38
        beam_weight = np.exp(-(beam_dist ** 2) / (2.0 * (18.0 ** 2))) * beam_taper

        # Base coral: [255, 65, 95], Highlight specular: [255, 220, 230]
        coral = np.array([255.0, 65.0, 95.0], dtype=np.float32)
        shimmer_tint = np.array([255.0, 220.0, 230.0], dtype=np.float32)
        shimmer_rgb = (1.0 - 0.65 * beam_weight[:, :, np.newaxis]) * coral + (0.65 * beam_weight[:, :, np.newaxis]) * shimmer_tint

        frame_canvas[upper_face_mask] = shimmer_rgb[upper_face_mask]

        # ----------------------------------------------------
        # 5D. Composite Subtitle Badge Layer
        # ----------------------------------------------------
        frame_canvas = frame_canvas * (1.0 - sub_alpha) + sub_rgb * sub_alpha
        frame_canvas = np.clip(frame_canvas, 0.0, 255.0)

        pil_frame = Image.fromarray(np.uint8(frame_canvas))
        rendered_frames.append(pil_frame)

    # ==========================================
    # 6. PALETTE QUANTIZATION & GIF EXPORT
    # ==========================================
    print("Building high-fidelity master palette from key animation phases...")
    # Sample keyframes across the loop to construct optimal master palette
    sample_indices = [0, 4, 8, 12, 16]
    palette_canvas = Image.new("RGB", (target_w, target_h * len(sample_indices)))
    for idx, f_idx in enumerate(sample_indices):
        palette_canvas.paste(rendered_frames[f_idx], (0, idx * target_h))

    # Quantize to 256 colors using median cut
    master_palette = palette_canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    print("Quantizing all 20 frames with master palette...")
    quantized_frames = [
        f.quantize(palette=master_palette, dither=Image.Dither.FLOYDSTEINBERG)
        for f in rendered_frames
    ]

    print(f"Saving animated GIF to: {output_gif_path}")
    quantized_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True
    )

    # Also copy preview to artifact folder if needed
    preview_artifact = "/Users/mahipatni/.gemini/antigravity/brain/4a57e73e-4d47-428f-a729-78d0704bc591/banner-preview.gif"
    if os.path.exists(os.path.dirname(preview_artifact)):
        import shutil
        shutil.copy2(output_gif_path, preview_artifact)
        print(f"Copied preview to: {preview_artifact}")

    # ==========================================
    # 7. VERIFICATION
    # ==========================================
    if not os.path.exists(output_gif_path):
        raise FileNotFoundError(f"Failed to generate {output_gif_path}")

    file_size_bytes = os.path.getsize(output_gif_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    with Image.open(output_gif_path) as gif:
        n_frames = gif.n_frames
        gif_w, gif_h = gif.size
        durations = [gif.info.get("duration", 0) for _ in range(n_frames)]

    print("\n" + "=" * 60)
    print("✨ ANIMATED BANNER GIF GENERATION SUCCESSFUL!")
    print(f"Path: {output_gif_path}")
    print(f"Dimensions: {gif_w} x {gif_h}")
    print(f"Frame count: {n_frames} frames (target: 20)")
    print(f"Frame delay: {durations[0]} ms (loop length: {sum(durations)/1000:.2f}s)")
    print(f"File size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print(f"Constraint (< 5.0 MB): {'PASSED' if file_size_mb < 5.0 else 'FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
