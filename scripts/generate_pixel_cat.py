#!/usr/bin/env python3
"""
Generate a fully animated transparent GIF for the pixel cat avatar.
Features:
- Blinking eyes with cute smiling curved eyes (^ ^) and sparkling reflections
- Floating pink hearts with sinusoidal vertical drift and subtle scale pulsation
- 4 twinkling cross-stars that scale, rotate, and fade rhythmically across all 4 quadrants
- Gentle idle breathing and tail bob/wagging
- 256x256 crisp downscale
- Seamless 20-frame loop (duration=90ms per frame, 1.8s loop)
- Proper GIF disposal=2 and transparency index for zero ghosting and clean rendering on GitHub dark/light mode
"""

import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

INPUT_PATH = "/Users/jatin/.gemini/antigravity/brain/3d005cfa-8ac8-467b-bd17-a1b415d57247/.user_uploaded/media_1793855169134_d525a5b8.png"
OUTPUT_PATH = "/Users/jatin/.gemini/antigravity/scratch/Mxhi-profile/assets/pixel-cat.gif"

NUM_FRAMES = 20
FRAME_DURATION = 90  # milliseconds per frame (1.8s loop)
TARGET_SIZE = (256, 256)

# High-resolution crop box in 1024x1024 (768x768 centered at (522, 520))
CROP_X1, CROP_Y1 = 136, 138
CROP_X2, CROP_Y2 = 904, 906
CANVAS_SIZE = 768


def extract_components():
    """Load image and segment into cat, hearts, and stars."""
    img = Image.open(INPUT_PATH).convert("RGBA")
    arr = np.array(img)
    alpha = arr[:, :, 3]

    labeled, num_features = ndimage.label(alpha > 20)
    print(f"Segmented {num_features} components.")

    # Component mapping from our structural analysis:
    # 1: Cat body
    # 2: Heart 1 (upper right)
    # 3: Star 1 (upper left)
    # 4: Star 2 (middle right)
    # 5: Heart 2 (lower left)
    # 6: Star 3 (lower left)

    def get_sprite(comp_id):
        mask = (labeled == comp_id)
        sprite_arr = np.zeros_like(arr)
        sprite_arr[mask] = arr[mask]
        rows, cols = np.where(mask)
        rmin, rmax = rows.min(), rows.max()
        cmin, cmax = cols.min(), cols.max()
        # Crop to bounding box
        cropped = sprite_arr[rmin:rmax + 1, cmin:cmax + 1]
        center = ((rmin + rmax) / 2.0, (cmin + cmax) / 2.0)
        return Image.fromarray(cropped, mode="RGBA"), center

    cat_mask = (labeled == 1)
    cat_arr = np.zeros_like(arr)
    cat_arr[cat_mask] = arr[cat_mask]
    cat_base = Image.fromarray(cat_arr, mode="RGBA")

    heart1_img, heart1_center = get_sprite(2)
    star1_img, star1_center = get_sprite(3)
    star2_img, star2_center = get_sprite(4)
    heart2_img, heart2_center = get_sprite(5)
    star3_img, star3_center = get_sprite(6)

    # Create Star 4 by copying Star 1, positioned in upper right
    star4_img = star1_img.copy()
    star4_center = (275.0, 785.0)

    sprites = {
        "cat_base": cat_base,
        "cat_mask": cat_mask,
        "heart1": (heart1_img, heart1_center),
        "heart2": (heart2_img, heart2_center),
        "stars": [
            (star1_img, star1_center, 0.0),             # Star 1: top-left
            (star4_img, star4_center, 0.5 * math.pi),   # Star 4: top-right
            (star2_img, star2_center, 1.0 * math.pi),   # Star 2: mid-right
            (star3_img, star3_center, 1.5 * math.pi),   # Star 3: bot-left
        ]
    }
    return sprites


def render_cat_frame(cat_base, cat_mask, frame_idx):
    """
    Render cat body for this frame:
    - Idle breathing displacement (head/chest rises and falls)
    - Tail bobbing
    - Eye blinking (open -> half-blink -> cute smiling closed eye ^ ^ -> half-open -> open)
    """
    arr = np.array(cat_base)
    t = frame_idx
    phase = 2.0 * math.pi * t / NUM_FRAMES

    # 1. Idle breathing vertical offset (in 1024 space)
    # Sine wave between -3.0 and +3.0 px
    breath_dy = 3.0 * math.sin(phase)

    # 2. Tail displacement
    # Tail tip bobs slightly with phase lead
    tail_dx = 3.5 * math.sin(phase + 0.6)
    tail_dy = 2.0 * math.cos(phase + 0.6)

    # Create deformed cat array
    out_arr = np.zeros_like(arr)
    h, w, _ = arr.shape

    # Apply breathing deformation
    # Rows < 650: full breathing dy
    # Rows 650..820: smooth transition down to 0
    # Rows > 820: 0 (paws stay grounded)
    # Tail region: cols > 730 and rows 620..830
    for r in range(h):
        if not np.any(cat_mask[r, :]):
            continue
        
        # Base factor for breathing
        if r < 650:
            f_breath = 1.0
        elif r <= 820:
            f_breath = 0.5 * (1.0 + math.cos(math.pi * (r - 650) / 170.0))
        else:
            f_breath = 0.0

        target_r = int(round(r - breath_dy * f_breath))
        target_r = max(0, min(h - 1, target_r))

        for c in range(w):
            if not cat_mask[r, c]:
                continue
            
            # Check if this pixel belongs to the tail
            if c > 720 and 620 <= r <= 830:
                # Tail factor: maximum near top of tail (r ~ 650, c ~ 800)
                f_tail = min(1.0, max(0.0, (830 - r) / 180.0 * (c - 720) / 80.0))
                cur_dy = breath_dy * f_breath + tail_dy * f_tail
                cur_dx = tail_dx * f_tail
                tr = int(round(r - cur_dy))
                tc = int(round(c + cur_dx))
                tr = max(0, min(h - 1, tr))
                tc = max(0, min(w - 1, tc))
                out_arr[tr, tc] = arr[r, c]
            else:
                out_arr[target_r, c] = arr[r, c]

    cat_frame_img = Image.fromarray(out_arr, mode="RGBA")
    draw = ImageDraw.Draw(cat_frame_img)

    # Fur color sampled from cat face
    black_fur = (8, 4, 8, 255)

    # Eye center coordinates in original (1024) space, offset by breathing
    cur_eye_dy = int(round(-breath_dy))
    left_cx, left_cy = 425, 475 + cur_eye_dy
    right_cx, right_cy = 605, 475 + cur_eye_dy

    # Blinking schedule across 20 frames:
    # 0..12: Open eyes
    # 13: Half-blink (eyelids closing)
    # 14..15: Fully closed eyes (^ ^ smiling arcs)
    # 16: Half-blink (eyelids opening)
    # 17..19: Open eyes

    if frame_idx in (14, 15):
        # Fully closed eyes with cute smiling curved lines ^ ^
        # Fill eye sparkle regions with black fur
        draw.rectangle([left_cx - 25, left_cy - 27, left_cx + 20, left_cy + 30], fill=black_fur)
        draw.rectangle([right_cx - 20, right_cy - 27, right_cx + 25, right_cy + 30], fill=black_fur)

        # Draw left smiling curved eye ^
        pts_left = []
        for x in range(left_cx - 20, left_cx + 21):
            # Parabolic / sinusoidal arch
            rel_x = (x - (left_cx - 20)) / 40.0
            y = (left_cy + 7) - 13.0 * math.sin(math.pi * rel_x)
            pts_left.append((x, int(round(y))))
        for i in range(len(pts_left) - 1):
            draw.line([pts_left[i], pts_left[i + 1]], fill=(255, 255, 255, 255), width=8)

        # Draw right smiling curved eye ^
        pts_right = []
        for x in range(right_cx - 20, right_cx + 21):
            rel_x = (x - (right_cx - 20)) / 40.0
            y = (right_cy + 7) - 13.0 * math.sin(math.pi * rel_x)
            pts_right.append((x, int(round(y))))
        for i in range(len(pts_right) - 1):
            draw.line([pts_right[i], pts_right[i + 1]], fill=(255, 255, 255, 255), width=8)

        # Cute pink cheek blush accent during smile
        blush_color = (255, 150, 180, 180)
        draw.ellipse([left_cx - 50, left_cy + 15, left_cx - 25, left_cy + 32], fill=blush_color)
        draw.ellipse([right_cx + 25, right_cy + 15, right_cx + 50, right_cy + 32], fill=blush_color)

    elif frame_idx in (13, 16):
        # Half-blink: upper half of sparkles covered by black fur eyelid
        draw.rectangle([left_cx - 25, left_cy - 27, left_cx + 20, left_cy], fill=black_fur)
        draw.rectangle([right_cx - 20, right_cy - 27, right_cx + 25, right_cy], fill=black_fur)
        # Narrow horizontal slit line
        draw.line([(left_cx - 20, left_cy), (left_cx + 20, left_cy)], fill=(255, 255, 255, 220), width=6)
        draw.line([(right_cx - 20, right_cy), (right_cx + 20, right_cy)], fill=(255, 255, 255, 220), width=6)

    elif frame_idx in (4, 5, 6):
        # Eyes open with an extra twinkle glint on the reflection
        glint_cx = left_cx - 5
        glint_cy = left_cy - 12
        draw.line([(glint_cx - 6, glint_cy), (glint_cx + 6, glint_cy)], fill=(255, 255, 255, 255), width=3)
        draw.line([(glint_cx, glint_cy - 6), (glint_cx, glint_cy + 6)], fill=(255, 255, 255, 255), width=3)

        r_glint_cx = right_cx + 3
        r_glint_cy = right_cy - 12
        draw.line([(r_glint_cx - 6, r_glint_cy), (r_glint_cx + 6, r_glint_cy)], fill=(255, 255, 255, 255), width=3)
        draw.line([(r_glint_cx, r_glint_cy - 6), (r_glint_cx, r_glint_cy + 6)], fill=(255, 255, 255, 255), width=3)

    return cat_frame_img


def render_sprite(canvas, sprite_img, center, offset_x=0.0, offset_y=0.0, scale=1.0, angle_deg=0.0, alpha_mult=1.0):
    """Transform and paste a sprite onto the canvas with subpixel positioning."""
    sw, sh = sprite_img.size
    cur_img = sprite_img

    if scale != 1.0:
        nw = max(1, int(round(sw * scale)))
        nh = max(1, int(round(sh * scale)))
        cur_img = cur_img.resize((nw, nh), Image.Resampling.LANCZOS)

    if angle_deg != 0.0:
        cur_img = cur_img.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=True)

    if alpha_mult < 1.0:
        cur_arr = np.array(cur_img, dtype=float)
        cur_arr[:, :, 3] *= alpha_mult
        cur_img = Image.fromarray(np.clip(cur_arr, 0, 255).astype(np.uint8), mode="RGBA")

    # Destination position (centered)
    cx, cy = center[1] + offset_x, center[0] + offset_y
    w, h = cur_img.size
    px = int(round(cx - w / 2.0))
    py = int(round(cy - h / 2.0))

    canvas.paste(cur_img, (px, py), cur_img)


def generate_frames():
    """Generate all 20 animation frames."""
    sprites = extract_components()
    cat_base = sprites["cat_base"]
    cat_mask = sprites["cat_mask"]
    heart1_img, heart1_center = sprites["heart1"]
    heart2_img, heart2_center = sprites["heart2"]
    stars = sprites["stars"]

    rgba_frames = []

    print(f"Generating {NUM_FRAMES} frames...")
    for t in range(NUM_FRAMES):
        # 1024x1024 high-res composite canvas
        canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

        # 1. Render animated cat
        cat_frame = render_cat_frame(cat_base, cat_mask, t)
        canvas.paste(cat_frame, (0, 0), cat_frame)

        # 2. Render floating Heart 1 (upper right)
        h1_phase = 2.0 * math.pi * t / NUM_FRAMES
        h1_dy = 12.0 * math.sin(h1_phase)
        h1_dx = 3.5 * math.cos(h1_phase)
        h1_scale = 1.0 + 0.09 * math.sin(h1_phase)
        h1_rot = 3.5 * math.sin(h1_phase)
        render_sprite(canvas, heart1_img, heart1_center, offset_x=h1_dx, offset_y=h1_dy, scale=h1_scale, angle_deg=h1_rot)

        # 3. Render floating Heart 2 (lower left)
        h2_phase = 2.0 * math.pi * t / NUM_FRAMES + 0.7 * math.pi
        h2_dy = 10.0 * math.sin(h2_phase)
        h2_dx = 3.0 * math.cos(h2_phase)
        h2_scale = 1.0 + 0.08 * math.sin(h2_phase)
        h2_rot = -3.5 * math.sin(h2_phase)
        render_sprite(canvas, heart2_img, heart2_center, offset_x=h2_dx, offset_y=h2_dy, scale=h2_scale, angle_deg=h2_rot)

        # 4. Render 4 twinkling cross-stars
        for s_img, s_center, s_phase_offset in stars:
            s_phase = 2.0 * math.pi * t / NUM_FRAMES + s_phase_offset
            # Twinkle pulse: scale ranges from 0.7 to 1.25
            s_scale = 0.95 + 0.30 * math.sin(s_phase)
            # Subtle rotation between -15 and +15 deg
            s_rot = 18.0 * math.sin(s_phase)
            # Alpha pulse
            s_alpha = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(s_phase))
            # Subtle floating drift
            s_dy = 3.0 * math.cos(s_phase)
            s_dx = 2.0 * math.sin(s_phase)
            render_sprite(canvas, s_img, s_center, offset_x=s_dx, offset_y=s_dy, scale=s_scale, angle_deg=s_rot, alpha_mult=s_alpha)

        # Crop to 768x768 centered bounding box
        cropped = canvas.crop((CROP_X1, CROP_Y1, CROP_X2, CROP_Y2))

        # Downscale crisply to 256x256
        frame_256 = cropped.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        rgba_frames.append(frame_256)

    return rgba_frames


def save_transparent_gif(rgba_frames, output_path):
    """
    Save list of RGBA frames as an optimized transparent animated GIF:
    - Global shared palette across all frames to prevent color flicker
    - Index 255 as transparent color
    - disposal=2 on every frame to prevent ghosting
    - loop=0 for infinite looping
    """
    print("Building global shared palette for clean transparency...")

    # Step 1: Collect opaque pixels across all frames for palette quantization
    combined_samples = []
    for f in rgba_frames:
        f_arr = np.array(f)
        # Select pixels with solid visibility (alpha > 80)
        solid = f_arr[f_arr[:, :, 3] > 80, :3]
        if len(solid) > 0:
            # Sample up to 2000 pixels per frame
            idx = np.random.choice(len(solid), min(2000, len(solid)), replace=False)
            combined_samples.append(solid[idx])

    sample_matrix = np.vstack(combined_samples)
    # Reshape as a 1D image to quantize
    palette_sample_img = Image.fromarray(sample_matrix.reshape((1, -1, 3)).astype(np.uint8), mode="RGB")
    # Quantize to 255 colors (saving index 255 for transparency)
    p_template = palette_sample_img.quantize(colors=255, method=Image.MEDIANCUT)
    raw_palette = p_template.getpalette()[:255 * 3]
    # Color 255 is transparent key: [0, 0, 0]
    global_palette = raw_palette + [0, 0, 0]

    processed_frames = []
    for f in rgba_frames:
        f_arr = np.array(f)
        alpha = f_arr[:, :, 3]
        # Clean binary transparency threshold
        # Alpha > 64 is considered opaque pixel
        opaque_mask = alpha > 64

        rgb_img = Image.new("RGB", TARGET_SIZE, (0, 0, 0))
        # Mask out transparent background so only opaque pixels are colored
        rgb_img.paste(f, mask=Image.fromarray((opaque_mask * 255).astype(np.uint8), mode="L"))

        # Quantize to the global template palette using no dither for pixel-art clarity
        p_frame = rgb_img.quantize(palette=p_template, dither=Image.Dither.NONE)
        p_arr = np.array(p_frame)

        # Set all non-opaque pixels to index 255 (the transparent color)
        p_arr[~opaque_mask] = 255

        final_frame = Image.fromarray(p_arr, mode="P")
        final_frame.putpalette(global_palette)
        final_frame.info["transparency"] = 255
        final_frame.info["disposal"] = 2
        final_frame.info["duration"] = FRAME_DURATION
        processed_frames.append(final_frame)

    print(f"Saving GIF to {output_path}...")
    processed_frames[0].save(
        output_path,
        save_all=True,
        append_images=processed_frames[1:],
        duration=[FRAME_DURATION] * NUM_FRAMES,
        loop=0,
        transparency=255,
        disposal=[2] * NUM_FRAMES,
        optimize=False
    )
    print("Save complete!")


def main():
    rgba_frames = generate_frames()
    save_transparent_gif(rgba_frames, OUTPUT_PATH)

    # Verification
    saved = Image.open(OUTPUT_PATH)
    import os
    size_bytes = os.path.getsize(OUTPUT_PATH)
    print("=== VERIFICATION RESULTS ===")
    print(f"File: {OUTPUT_PATH}")
    print(f"Format: {saved.format}")
    print(f"Dimensions: {saved.size}")
    print(f"Frame Count: {saved.n_frames}")
    print(f"Loop: {saved.info.get('loop', 'default')}")
    print(f"Duration per frame: {saved.info.get('duration')}ms (Total: {saved.n_frames * saved.info.get('duration', 0)}ms)")
    print(f"File Size: {size_bytes / 1024:.1f} KB ({size_bytes} bytes)")


if __name__ == "__main__":
    main()
