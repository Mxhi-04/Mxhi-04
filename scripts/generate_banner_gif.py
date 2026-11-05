#!/usr/bin/env python3
"""
Gentle Animated Banner GIF Generator for Mahi Patni's GitHub Profile.

Refinements:
1. Subtly defined borders on the square pixels of the stars.
2. Increased density of twinkling retro red pixel sparkles (45 total).
3. Soft star glow with low-amplitude breathing (~8.5%).
4. Tranquil 3.6-second loop (24 frames @ 150ms).
5. Elegant specular shimmer sweep and neon aura across 'MAHI PATNI'.
6. 1200x380 resolution, seamless loop, optimized palette (~2.3 MB).
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

    # ==========================================
    # 1. BASE BACKGROUND & DARK GRADIENT MASK
    # ==========================================
    target_w, target_h = 1200, 380
    scale = target_w / bg_orig.width
    scaled_h = int(bg_orig.height * scale)
    bg_scaled = bg_orig.resize((target_w, scaled_h), Image.Resampling.LANCZOS)
    y_offset = (scaled_h - target_h) // 2
    bg_cropped = bg_scaled.crop((0, y_offset, target_w, y_offset + target_h)).convert("RGBA")

    # Smooth dark gradient overlay on the left side
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

    Y, X = np.ogrid[:target_h, :target_w]
    upper_face_mask = (arr_mahi & (Y < mid_y_mahi)) | (arr_patni & (Y < mid_y_patni))
    lower_face_mask = (arr_mahi & (Y >= mid_y_mahi)) | (arr_patni & (Y >= mid_y_patni))

    full_text_img = Image.new("L", (target_w, target_h), 0)
    full_text_draw = ImageDraw.Draw(full_text_img)
    full_text_draw.text((left_x, y_mahi), "MAHI", font=font_name, fill=255)
    full_text_draw.text((left_x, y_patni), "PATNI", font=font_name, fill=255)

    outline_w = 5
    dilated_text = full_text_img.filter(ImageFilter.MaxFilter(outline_w * 2 + 1))
    arr_dilated = np.array(dilated_text) > 0
    arr_outline = arr_dilated & (~full_text_mask)

    glow_img = dilated_text.filter(ImageFilter.GaussianBlur(10))
    arr_glow = np.array(glow_img, dtype=np.float32) / 255.0

    # Subtitle badge & Sparkle sprite (inspired by pixel sparkle sheet row 1 center)
    sub_text = "Crafting Little Worlds, Pixel by Pixel."
    dummy_sub = ImageDraw.Draw(Image.new("L", (1, 1)))
    bbox_sub = dummy_sub.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = bbox_sub[2] - bbox_sub[0]
    sub_h = bbox_sub[3] - bbox_sub[1]

    sparkle_size = 17
    sparkle_gap = 10
    pill_pad_x = 16
    pill_pad_y = 6

    pill_w = pill_pad_x * 2 + sub_w + sparkle_gap + sparkle_size
    pill_h = max(sub_h, sparkle_size) + pill_pad_y * 2
    pill_left = left_x - 4
    pill_top = sub_y + bbox_sub[1] - pill_pad_y
    pill_right = pill_left + pill_w
    pill_bottom = pill_top + pill_h
    pill_rect = [pill_left, pill_top, pill_right, pill_bottom]

    sp_x = pill_left + pill_pad_x + sub_w + sparkle_gap
    sp_y = pill_top + (pill_h - sparkle_size) // 2

    # Sparkle sprite template (17x17)
    sparkle_grid = np.zeros((17, 17), dtype=int)
    sparkle_grid[8, 8] = 5
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        sparkle_grid[8 + dy, 8 + dx] = 4
    for y in range(17):
        for x in range(17):
            m = abs(y - 8) + abs(x - 8)
            if m == 2:
                sparkle_grid[y, x] = max(sparkle_grid[y, x], 4)
            elif m == 3:
                sparkle_grid[y, x] = max(sparkle_grid[y, x], 3)
            elif m == 4 and abs(y - 8) <= 2 and abs(x - 8) <= 2:
                sparkle_grid[y, x] = max(sparkle_grid[y, x], 3)
    # Rays
    for y in [2, 3, 4, 12, 13, 14]:
        sparkle_grid[y, 8] = 2
    for y in [5, 11]:
        sparkle_grid[y, 8] = 3
    for x in [2, 3, 4, 12, 13, 14]:
        sparkle_grid[8, x] = 2
    for x in [5, 11]:
        sparkle_grid[8, x] = 3
    # Corner accent sparkles from sprite sheet
    sparkle_grid[2, 3] = 1; sparkle_grid[3, 2] = 1; sparkle_grid[3, 4] = 1; sparkle_grid[4, 3] = 1; sparkle_grid[3, 3] = 4
    sparkle_grid[3, 13] = 4; sparkle_grid[2, 13] = 1; sparkle_grid[4, 13] = 1; sparkle_grid[3, 12] = 1; sparkle_grid[3, 14] = 1
    sparkle_grid[13, 3] = 1; sparkle_grid[13, 4] = 1
    sparkle_grid[13, 13] = 1; sparkle_grid[14, 13] = 1

    def make_sparkle_img(twinkle, t_dot):
        c5 = [255, 180 + int(75 * twinkle), 200 + int(55 * twinkle), 255]
        c4 = [255, 45 + int(70 * twinkle), 85 + int(50 * twinkle), 255]
        c3 = [225 + int(30 * twinkle), 20 + int(30 * twinkle), 65 + int(30 * twinkle), 255]
        c2 = [190 + int(55 * twinkle), 15 + int(25 * twinkle), 50 + int(25 * twinkle), int(180 + 75 * twinkle)]
        c1 = [245, 55 + int(80 * t_dot), 95 + int(60 * t_dot), int(150 + 105 * t_dot)]
        palette = {0: [0, 0, 0, 0], 1: c1, 2: c2, 3: c3, 4: c4, 5: c5}
        arr = np.zeros((17, 17, 4), dtype=np.uint8)
        for k, col in palette.items():
            arr[sparkle_grid == k] = col
        return Image.fromarray(arr, "RGBA")

    # Pre-render 24 subtitle badge frames with twinkling red sparkle
    NUM_FRAMES = 24
    FRAME_DELAY_MS = 150
    sub_frames_rgb = []
    sub_frames_alpha = []
    for f_idx in range(NUM_FRAMES):
        theta = 2.0 * math.pi * f_idx / NUM_FRAMES
        twinkle = 0.5 + 0.5 * math.sin(theta)
        t_dot = 0.5 + 0.5 * math.sin(theta + 1.2)
        sp_frame = make_sparkle_img(twinkle, t_dot)

        sub_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        d_sub = ImageDraw.Draw(sub_layer)
        d_sub.rectangle(pill_rect, fill=(10, 6, 8, 235), outline=(220, 30, 60, 255), width=1)
        d_sub.text((pill_left + pill_pad_x, sub_y), sub_text, font=font_sub, fill=(255, 215, 225, 255))
        sub_layer.paste(sp_frame, (sp_x, sp_y), sp_frame)

        arr_sub_layer = np.array(sub_layer, dtype=np.float32)
        sub_frames_alpha.append(arr_sub_layer[:, :, 3:] / 255.0)
        sub_frames_rgb.append(arr_sub_layer[:, :, :3])

    # Exclusion mask covers text and the full subtitle pill
    exclusion_mask = arr_dilated.copy()
    exclusion_mask[pill_top:pill_bottom, pill_left:pill_right] = True

    # =======================================================
    # 3. STAR MASK & SUBTLY DEFINED PIXEL BORDERS
    # =======================================================
    gray_bg = arr_bg_base.mean(axis=2)
    r_ch = arr_bg_base[:, :, 0]
    g_ch = arr_bg_base[:, :, 1]
    b_ch = arr_bg_base[:, :, 2]
    star_mask = np.clip((r_ch - np.maximum(g_ch, b_ch) * 1.2 - 20.0) / 80.0, 0.0, 1.0)
    star_mask[:, :480] = 0.0
    star_mask[exclusion_mask] = 0.0

    # Very slightly define borders between pixel blocks in the stars
    grad_x = np.abs(ndi.sobel(gray_bg, axis=1))
    grad_y = np.abs(ndi.sobel(gray_bg, axis=0))
    grad = np.sqrt(grad_x**2 + grad_y**2)
    grad_norm = np.clip(grad / 280.0, 0.0, 1.0) * star_mask
    border_sub = (grad_norm * 18.0)[:, :, np.newaxis]
    arr_bg_defined = np.clip(arr_bg_base - border_sub, 0.0, 255.0)

    # =======================================================
    # 4. INCREASED DENSITY OF RED PIXEL SPARKLES (45 TOTAL)
    # =======================================================
    sparkles = [
        # Top sky
        (140,  28, 0.0, 1), (210,  22, 1.3, 2), (280,  32, 2.7, 1), (360,  18, 4.1, 2), (430,  26, 5.4, 1),
        # Transition corridor (x: 470..640)
        (485,  75, 0.8, 2), (530, 120, 2.1, 1), (495, 175, 3.5, 2), (565, 215, 4.8, 1), (510, 265, 0.4, 2),
        (585,  95, 1.7, 1), (620, 160, 3.1, 2), (590, 240, 4.4, 1), (635, 290, 5.8, 2),
        # Upper starfield & near top star (x: 650..1180, y: 15..110)
        (670,  38, 0.5, 1), (725,  20, 1.9, 2), (785,  45, 3.2, 1), (840,  25, 4.6, 2), (895,  48, 5.9, 1),
        (955,  30, 1.2, 2), (1015, 52, 2.5, 1), (1075, 22, 3.8, 2), (1135, 45, 5.1, 1), (1175, 28, 0.7, 2),
        # Mid sky & between stars (x: 650..1180, y: 120..250)
        (685, 135, 2.3, 2), (735, 180, 3.7, 1), (795, 140, 5.0, 2), (850, 195, 0.6, 1), (910, 150, 2.0, 2),
        (970, 205, 3.3, 1), (1030, 160, 4.7, 2), (1090, 210, 0.2, 1), (1150, 170, 1.6, 2),
        # Lower sky & near bottom star (x: 650..1180, y: 260..365)
        (690, 320, 3.0, 1), (745, 270, 4.3, 2), (805, 335, 5.7, 1), (865, 285, 1.1, 2), (925, 340, 2.4, 1),
        (985, 295, 3.8, 2), (1045, 345, 5.2, 1), (1105, 300, 0.5, 2), (1165, 350, 1.9, 1),
        # Under subtitle / bottom left
        (220, 345, 3.6, 1), (340, 340, 5.0, 1), (440, 345, 0.9, 2),
    ]

    # ==========================================
    # 5. SYNTHESIS LOOP (24 FRAMES, 150ms/frame = 3.6s)
    # ==========================================
    print(f"Generating {NUM_FRAMES} seamless animation frames at {FRAME_DELAY_MS}ms per frame (3.6s loop)...")

    rendered_frames = []
    for f_idx in range(NUM_FRAMES):
        theta = 2.0 * math.pi * f_idx / NUM_FRAMES
        pulse = math.sin(theta)
        scale_factor = 1.0 + (0.085 * pulse * star_mask)
        frame_canvas = arr_bg_defined * scale_factor[:, :, np.newaxis]

        # Twinkling Retro Red Sparkles
        for sx, sy, s_phase, s_type in sparkles:
            sp = max(0.0, math.sin(theta + s_phase)) ** 4.0
            if sp > 0.08 and not exclusion_mask[sy, sx]:
                c_rgb = np.array([255.0, 140.0 + 115.0 * sp, 160.0 + 95.0 * sp]) * sp
                frame_canvas[sy, sx] = np.maximum(frame_canvas[sy, sx], c_rgb)
                if s_type == 2 and sp > 0.4:
                    arm_rgb = np.array([230.0, 40.0, 70.0]) * (sp - 0.4) / 0.6
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if 0 <= sx + dx < target_w and 0 <= sy + dy < target_h:
                            frame_canvas[sy + dy, sx + dx] = np.maximum(frame_canvas[sy + dy, sx + dx], arm_rgb)

        # Soft Neon Aura behind text
        glow_val = 0.36 + 0.05 * math.sin(theta)
        glow_mask_apply = (arr_glow > 0.04) & (~arr_dilated)
        glow_color = np.array([220.0, 25.0, 50.0], dtype=np.float32)
        frame_canvas[glow_mask_apply] += (arr_glow[glow_mask_apply, np.newaxis] * glow_val) * glow_color

        # Text Outline
        frame_canvas[arr_outline] = [4.0, 4.0, 4.0]

        # Lower Face
        frame_canvas[lower_face_mask] = [185.0, 15.0, 45.0]

        # Upper Face with subtle specular sweep
        x_beam = -40.0 + 520.0 * (f_idx / NUM_FRAMES)
        beam_dist = (X - x_beam) + (Y - 50.0) * 0.35
        beam_weight = np.exp(-(beam_dist ** 2) / (2.0 * (24.0 ** 2)))

        coral = np.array([255.0, 65.0, 95.0], dtype=np.float32)
        shimmer_tint = np.array([255.0, 200.0, 215.0], dtype=np.float32)
        shimmer_rgb = (1.0 - 0.40 * beam_weight[:, :, np.newaxis]) * coral + (0.40 * beam_weight[:, :, np.newaxis]) * shimmer_tint
        frame_canvas[upper_face_mask] = shimmer_rgb[upper_face_mask]

        # Subtitle badge with animated red sparkle
        sub_alpha = sub_frames_alpha[f_idx]
        sub_rgb = sub_frames_rgb[f_idx]
        frame_canvas = frame_canvas * (1.0 - sub_alpha) + sub_rgb * sub_alpha
        frame_canvas = np.clip(frame_canvas, 0.0, 255.0)

        rendered_frames.append(Image.fromarray(np.uint8(frame_canvas)))

    # Master Palette Quantization
    sample_indices = [0, 4, 8, 12, 16, 20]
    palette_canvas = Image.new("RGB", (target_w, target_h * len(sample_indices)))
    for idx, f_idx in enumerate(sample_indices):
        palette_canvas.paste(rendered_frames[f_idx], (0, idx * target_h))

    master_palette = palette_canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    quantized_frames = [
        f.quantize(palette=master_palette, dither=Image.Dither.FLOYDSTEINBERG)
        for f in rendered_frames
    ]

    quantized_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_DELAY_MS,
        loop=0,
        optimize=True
    )

    # Copy to v2 asset for cache busting and preview artifact
    v2_gif_path = os.path.join(repo_root, "assets", "mahi-patni-banner-v2.gif")
    import shutil
    shutil.copy2(output_gif_path, v2_gif_path)

    preview_artifact = "/Users/mahipatni/.gemini/antigravity/brain/4a57e73e-4d47-428f-a729-78d0704bc591/banner-preview.gif"
    if os.path.exists(os.path.dirname(preview_artifact)):
        shutil.copy2(output_gif_path, preview_artifact)
        print(f"Copied preview to: {preview_artifact}")

    file_size_bytes = os.path.getsize(output_gif_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    print("\n" + "=" * 60)
    print("✨ ANIMATED BANNER GIF GENERATION SUCCESSFUL!")
    print(f"Path: {output_gif_path}")
    print(f"File Size: {file_size_mb:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    main()
