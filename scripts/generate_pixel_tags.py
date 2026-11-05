#!/usr/bin/env python3
"""
Generate retro pixel heart health-bar tags for Mahi Patni's GitHub Profile.
Based on the custom pixel-art tag reference provided by the user.

Creates:
- assets/tags/tag-followers.png
- assets/tags/tag-voyagers.png
- assets/tags/tag-linkedin.png
- assets/tags/tag-mail.png
- assets/tags/tag-location.png
- assets/tags/tag-status.png
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from collections import deque

def prepare_base_tag():
    ref_path = "/Users/mahipatni/.gemini/antigravity/brain/26c58cb5-4bcf-44a2-8939-c5c8152856d8/.user_uploaded/media_1793889252022_a21f7f1d.png"
    im = Image.open(ref_path).convert("RGBA")
    
    # Crop clean tag boundaries (excluding screenshot crop handles on the right)
    clean_tag = im.crop((35, 35, 480, 125))
    arr = np.array(clean_tag)
    
    # Flood-fill transparency from outside edges
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    
    for y in range(h):
        for x in [0, 1, w-2, w-1]:
            if arr[y, x, :3].mean() > 200:
                q.append((y, x))
                visited[y, x] = True

    for x in range(w):
        for y in [0, 1, h-2, h-1]:
            if arr[y, x, :3].mean() > 200 and not visited[y, x]:
                q.append((y, x))
                visited[y, x] = True

    while q:
        cy, cx = q.popleft()
        arr[cy, cx, 3] = 0
        for ny, nx in [(cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)]:
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if arr[ny, nx, :3].mean() > 160:
                    visited[ny, nx] = True
                    q.append((ny, nx))
                    
    return Image.fromarray(arr)

def main():
    repo_root = "/Users/mahipatni/Antigravity/profile"
    tags_dir = os.path.join(repo_root, "assets", "tags")
    os.makedirs(tags_dir, exist_ok=True)
    
    base_tag = prepare_base_tag()
    left_cap = base_tag.crop((0, 0, 98, 90))
    right_cap = base_tag.crop((435, 0, 444, 90))
    center_slice = base_tag.crop((200, 0, 201, 90))
    
    font_path = os.path.join(repo_root, "assets", "fonts", "RawPixel.otf")
    font = ImageFont.truetype(font_path, 24)
    
    badges = [
        ("followers", "5", "tag-followers.png"),
        ("voyagers charted", "97", "tag-voyagers.png"),
        ("LinkedIn", "Mahi Patni", "tag-linkedin.png"),
        ("Mail", "mahipatni1828@gmail.com", "tag-mail.png"),
        ("Location", "India", "tag-location.png"),
        ("Open to", "Collaborate & Build", "tag-status.png"),
    ]
    
    print("Generating pixel heart tags...")
    for label, val, filename in badges:
        b_l = font.getbbox(label)
        w_l = b_l[2] - b_l[0]
        b_v = font.getbbox(val)
        w_v = b_v[2] - b_v[0]
        sep = " · "
        b_s = font.getbbox(sep)
        w_s = b_s[2] - b_s[0]
        
        pad_h = 18
        inner_w = w_l + w_s + w_v + pad_h * 2
        total_w = left_cap.width + inner_w + right_cap.width
        
        tag = Image.new("RGBA", (total_w, 90), (0, 0, 0, 0))
        tag.paste(left_cap, (0, 0))
        tag.paste(center_slice.resize((inner_w, 90), Image.Resampling.NEAREST), (left_cap.width, 0))
        tag.paste(right_cap, (left_cap.width + inner_w, 0))
        
        draw = ImageDraw.Draw(tag)
        h_l = b_l[3] - b_l[1]
        ty = 21 + (52 - h_l) // 2 - b_l[1]
        
        cur_x = left_cap.width + pad_h
        draw.text((cur_x, ty), label, font=font, fill="#080406")
        cur_x += w_l
        draw.text((cur_x, ty), sep, font=font, fill="#71717a")
        cur_x += w_s
        draw.text((cur_x, ty), val, font=font, fill="#e11d48")
        
        out_file = os.path.join(tags_dir, filename)
        tag.save(out_file)
        print(f"  ✓ Saved {filename} ({tag.size[0]}x{tag.size[1]})")

if __name__ == "__main__":
    main()
