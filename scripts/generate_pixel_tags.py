#!/usr/bin/env python3
"""
Generate custom retro red star health-bar tags for Mahi Patni's GitHub Profile.

Design:
- Star emblem: Red 5-pointed halftone star with black center cutout (based on user reference).
- Banner container: Pitch black (#080406) with crimson borders (#e11d48).
- Typography: Crisp white label text (#ffffff), subtle separator (#71717a), vibrant red value (#ff2a4b).
- Retina-ready: High resolution (88px height) for sharp display on any display.
"""

import math
import os
import numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def prepare_star(repo_root):
    star_path = os.path.join(repo_root, "assets", "icons", "star-emblem.jpg")
    star_orig = Image.open(star_path)
    
    # Crop tightly to the star graphic
    star_crop = star_orig.crop((75, 75, 695, 665))
    star_h = 46  # Calibrated to 46px to fit proportionally within the 48px banner box
    star_w = int(star_crop.width * (star_h / star_crop.height))
    star_scaled = star_crop.resize((star_w, star_h), Image.Resampling.LANCZOS).convert("RGBA")
    
    arr = np.array(star_scaled, dtype=np.float32)
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    
    for y in range(h):
        for x in [0, 1, w - 2, w - 1]:
            if arr[y, x, 0] < 30:
                q.append((y, x))
                visited[y, x] = True

    for x in range(w):
        for y in [0, 1, h - 2, h - 1]:
            if arr[y, x, 0] < 30 and not visited[y, x]:
                q.append((y, x))
                visited[y, x] = True

    while q:
        cy, cx = q.popleft()
        arr[cy, cx, 3] = min(255, max(0, arr[cy, cx, 0] * 3.5))
        for ny, nx in [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]:
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if arr[ny, nx, 0] < 50:
                    visited[ny, nx] = True
                    q.append((ny, nx))
                    
    # Subdue aggressive red channel & brightness to match elegant profile crimson
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.82, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.70, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.70, 0, 255)
    
    clean_star = Image.fromarray(arr.astype(np.uint8))
    clean_star = ImageEnhance.Color(clean_star).enhance(0.85)
    clean_star = ImageEnhance.Brightness(clean_star).enhance(0.82)
    return clean_star

def render_tag(label, val, star_img, font):
    TAG_H = 88
    star_w, star_h = star_img.size
    
    b_l = font.getbbox(label)
    w_l = b_l[2] - b_l[0]
    b_v = font.getbbox(val)
    w_v = b_v[2] - b_v[0]
    sep = " · "
    b_s = font.getbbox(sep)
    w_s = b_s[2] - b_s[0]
    
    content_w = w_l + w_s + w_v
    pad_l = 22
    pad_r = 16
    
    box_x1 = star_w - 12  # Clean overlap with right arm of star
    box_w = content_w + pad_l + pad_r
    box_x2 = box_x1 + box_w
    
    total_w = box_x2 + 4
    
    tag = Image.new("RGBA", (total_w, TAG_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tag)
    
    by1 = 20
    by2 = 68
    border_w = 3
    
    # 1. Black banner fill (#080406)
    draw.rectangle([box_x1, by1, box_x2, by2], fill=(8, 4, 6, 255))
    
    # 2. Crimson borders (#e11d48)
    border_color = (225, 29, 72, 255)
    # Top border
    draw.rectangle([box_x1, by1, box_x2, by1 + border_w - 1], fill=border_color)
    # Bottom border
    draw.rectangle([box_x1, by2 - border_w + 1, box_x2, by2], fill=border_color)
    # Right border
    draw.rectangle([box_x2 - border_w + 1, by1, box_x2, by2], fill=border_color)
    
    # 3. Paste star
    star_y = (TAG_H - star_h) // 2
    tag.paste(star_img, (0, star_y), star_img)
    
    # 4. Typography
    h_l = b_l[3] - b_l[1]
    ty = by1 + (by2 - by1 - h_l) // 2 - b_l[1]
    
    start_x = box_x1 + pad_l
    draw.text((start_x, ty), label, font=font, fill="#ffffff")
    cur_x = start_x + w_l
    draw.text((cur_x, ty), sep, font=font, fill="#71717a")
    cur_x += w_s
    draw.text((cur_x, ty), val, font=font, fill="#e11d48")
    
    return tag

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tags_dir = os.path.join(repo_root, "assets", "tags")
    os.makedirs(tags_dir, exist_ok=True)
    
    print("Preparing star emblem...")
    star_img = prepare_star(repo_root)
    
    font_path = os.path.join(repo_root, "assets", "fonts", "RawPixel.otf")
    font = ImageFont.truetype(font_path, 28)
    
    badges = [
        ("followers", "5", "tag-followers.png"),
        ("voyagers charted", "97", "tag-voyagers.png"),
        ("LinkedIn", "Mahi Patni", "tag-linkedin.png"),
        ("Mail", "mahipatni1828@gmail.com", "tag-mail.png"),
        ("Location", "India", "tag-location.png"),
        ("Open to", "Collaborate & Build", "tag-status.png"),
    ]
    
    print("Generating black & red star tags...")
    for label, val, filename in badges:
        tag = render_tag(label, val, star_img, font)
        out_file = os.path.join(tags_dir, filename)
        tag.save(out_file)
        print(f"  ✓ Saved {filename} ({tag.size[0]}x{tag.size[1]})")

if __name__ == "__main__":
    main()
