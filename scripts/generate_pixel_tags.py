#!/usr/bin/env python3
"""
Generate flawless retro pixel heart health-bar tags for Mahi Patni's GitHub Profile.

Features:
- 100% symmetrical, unclipped retro 8-bit heart with specular shine highlight.
- Smooth black borders and solid white interior box.
- Pixel typography using RawPixel.otf with dark labels (#080406) and crimson values (#e11d48).
- High-resolution 2x/3x Retina rendering (8px blocks, 88px height) for razor-sharp display at height="38".
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

HEART_GRID = [
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0],
    [1, 2, 3, 3, 2, 2, 1, 2, 2, 2, 2, 2, 1], # row 2: top border of bar connects at col 12
    [1, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],
    [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],
    [0, 0, 0, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0], # row 8: bottom border of bar connects at col 8
    [0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
]

BLOCK = 8
H_BLOCKS = len(HEART_GRID)  # 11 blocks high (88px)
W_HEART = len(HEART_GRID[0])  # 13 blocks wide (104px)

def render_tag(label, val, font):
    b_l = font.getbbox(label)
    w_l = b_l[2] - b_l[0]
    b_v = font.getbbox(val)
    w_v = b_v[2] - b_v[0]
    sep = " · "
    b_s = font.getbbox(sep)
    w_s = b_s[2] - b_s[0]
    
    content_w = w_l + w_s + w_v
    pad_px = 24  # 3 blocks horizontal padding
    box_w_px = content_w + pad_px * 2
    inner_blocks = math.ceil(box_w_px / BLOCK)
    total_blocks_w = W_HEART + inner_blocks + 1
    
    img_w = total_blocks_w * BLOCK
    img_h = H_BLOCKS * BLOCK
    
    tag = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tag)
    
    # 1. Fill white interior of bar (rows 3 to 7)
    for r in range(3, 8):
        max_c = max([c for c, v in enumerate(HEART_GRID[r]) if v != 0])
        start_c = max_c + 1
        x1 = start_c * BLOCK
        x2 = (total_blocks_w - 1) * BLOCK
        y1 = r * BLOCK
        y2 = (r + 1) * BLOCK
        draw.rectangle([x1, y1, x2 - 1, y2 - 1], fill=(255, 255, 255, 255))
        
    # 2. Draw bar black borders
    # Top border: row 2 from col 12 to total_blocks_w - 1
    draw.rectangle([12 * BLOCK, 2 * BLOCK, (total_blocks_w - 1) * BLOCK, 3 * BLOCK - 1], fill=(0, 0, 0, 255))
    
    # Bottom border: row 8 from col 8 to total_blocks_w - 1
    draw.rectangle([8 * BLOCK, 8 * BLOCK, (total_blocks_w - 1) * BLOCK, 9 * BLOCK - 1], fill=(0, 0, 0, 255))
    
    # Right border: col total_blocks_w - 1 from row 2 to 8
    draw.rectangle([(total_blocks_w - 1) * BLOCK, 2 * BLOCK, total_blocks_w * BLOCK - 1, 9 * BLOCK - 1], fill=(0, 0, 0, 255))
    
    # 3. Draw clean symmetrical pixel heart
    colors = {
        0: None,
        1: (0, 0, 0, 255),       # black outline
        2: (225, 29, 72, 255),   # #e11d48 crimson red
        3: (255, 255, 255, 255), # white specular shine
    }
    for r in range(H_BLOCKS):
        for c in range(W_HEART):
            v = HEART_GRID[r][c]
            if v != 0:
                x = c * BLOCK
                y = r * BLOCK
                draw.rectangle([x, y, x + BLOCK - 1, y + BLOCK - 1], fill=colors[v])
                
    # 4. Draw Typography
    actual_inner_w = (total_blocks_w - 1 - W_HEART) * BLOCK
    start_x = W_HEART * BLOCK + (actual_inner_w - content_w) // 2
    
    h_l = b_l[3] - b_l[1]
    ty = 3 * BLOCK + (5 * BLOCK - h_l) // 2 - b_l[1]
    
    cur_x = start_x
    draw.text((cur_x, ty), label, font=font, fill="#080406")
    cur_x += w_l
    draw.text((cur_x, ty), sep, font=font, fill="#71717a")
    cur_x += w_s
    draw.text((cur_x, ty), val, font=font, fill="#e11d48")
    
    return tag

def main():
    repo_root = "/Users/mahipatni/Antigravity/profile"
    tags_dir = os.path.join(repo_root, "assets", "tags")
    os.makedirs(tags_dir, exist_ok=True)
    
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
    
    print("Generating pure symmetrical pixel tags...")
    for label, val, filename in badges:
        tag = render_tag(label, val, font)
        out_file = os.path.join(tags_dir, filename)
        tag.save(out_file)
        print(f"  ✓ Saved {filename} ({tag.size[0]}x{tag.size[1]})")

if __name__ == "__main__":
    main()
