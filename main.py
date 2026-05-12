import os
import cv2
import numpy as np
from utils import (split_channels, align_simple, shift_image, align_pyramid, auto_crop, auto_contrast_color, white_balance_gray_world)

def process_image(filename, input_dir="data", output_dir="outputs", use_bells_whistles=True, metric='ssd'):
    
    img_path = os.path.join(input_dir, filename)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None, f"Failed to load {filename}"
    
    # Split into channels
    B, G, R = split_channels(img)
    
    # Determine if we need pyramid (for large images)
    use_pyramid = min(img.shape) > 1000
    
    # Determine alignment parameters
    name_lower = filename.lower()
    use_edges = 'emir' in name_lower or use_bells_whistles
    use_ncc = metric == 'ncc'
    
    # Align channels
    if use_pyramid:
        dx_g, dy_g = align_pyramid(G, B, use_edges=use_edges, use_ncc=use_ncc)
        dx_r, dy_r = align_pyramid(R, B, use_edges=use_edges, use_ncc=use_ncc)
        method = "pyramid"
    else:
        dx_g, dy_g = align_simple(G, B, use_edges=use_edges, use_ncc=use_ncc)
        dx_r, dy_r = align_simple(R, B, use_edges=use_edges, use_ncc=use_ncc)
        method = "simple"
    
    # Shift channels
    G_aligned = shift_image(G, dx_g, dy_g)
    R_aligned = shift_image(R, dx_r, dy_r)
    
    # Stack into color image
    color = np.dstack([B, G_aligned, R_aligned])
    
    # Applying bells & whistles
    enhancements = []
    if use_bells_whistles:
        # 1. Auto crop borders
        B_crop, G_crop, R_crop = auto_crop(B, G_aligned, R_aligned)
        color = np.dstack([B_crop, G_crop, R_crop])
        enhancements.append("auto_crop")
        
        # 2. Auto contrast
        color = auto_contrast_color(color, percentile=1)
        enhancements.append("auto_contrast")
        
        # 3. White balance 
        color = white_balance_gray_world(color)
        enhancements.append("white_balance_gray_world")
    
    name = os.path.splitext(filename)[0]
    suffix = f"_{method}"
    if use_edges:
        suffix += "_edges"
    if use_ncc:
        suffix += "_ncc"
    if use_bells_whistles:
        suffix += "_enhanced"
    
    output_path = os.path.join(output_dir, f"{name}{suffix}.jpg")
    os.makedirs(output_dir, exist_ok=True)
    cv2.imwrite(output_path, color)
    
    return {
        'filename': filename,
        'method': method,
        'metric': 'NCC' if use_ncc else 'SSD',
        'features': 'edges' if use_edges else 'pixels',
        'g_offset': (dx_g, dy_g),
        'r_offset': (dx_r, dy_r),
        'enhancements': enhancements,
        'output_path': output_path
    }


def main():
    input_dir = "data"
    
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} directory not found!")
        print("Please create it and add the Prokudin-Gorskii images.")
        return
    
    image_files = [f for f in os.listdir(input_dir) 
                   if f.lower().endswith((".jpg", ".tif", ".png"))]
    
    if not image_files:
        print(f"No images found in {input_dir}!")
        return
    
    print(f"Found {len(image_files)} images to process\n")
    
    results = []
    
    # Process each image with different configurations
    for filename in sorted(image_files):
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")
        
        # Configuration 1: Basic alignment with SSD
        print("\n[1/4] Basic alignment (SSD, no enhancements)...")
        result = process_image(
            filename, 
            input_dir=input_dir,
            output_dir="outputs/01_basic_ssd",
            use_bells_whistles=False,
            metric='ssd'
        )
        results.append(result)
        print(f"  G offset: {result['g_offset']}")
        print(f"  R offset: {result['r_offset']}")
        
        # Configuration 2: Basic alignment with NCC
        print("\n[2/4] Basic alignment (NCC, no enhancements)...")
        result = process_image(
            filename,
            input_dir=input_dir,
            output_dir="outputs/02_basic_ncc",
            use_bells_whistles=False,
            metric='ncc'
        )
        results.append(result)
        print(f"  G offset: {result['g_offset']}")
        print(f"  R offset: {result['r_offset']}")
        
        # Configuration 3: Enhanced with SSD
        print("\n[3/4] Enhanced alignment (SSD + bells & whistles)...")
        result = process_image(
            filename,
            input_dir=input_dir,
            output_dir="outputs/03_enhanced_ssd",
            use_bells_whistles=True,
            metric='ssd'
        )
        results.append(result)
        print(f"  G offset: {result['g_offset']}")
        print(f"  R offset: {result['r_offset']}")
        print(f"  Enhancements: {', '.join(result['enhancements'])}")
        
        # Configuration 4: Enhanced with NCC
        print("\n[4/4] Enhanced alignment (NCC + bells & whistles)...")
        result = process_image(
            filename,
            input_dir=input_dir,
            output_dir="outputs/04_enhanced_ncc",
            use_bells_whistles=True,
            metric='ncc'
        )
        results.append(result)
        print(f"  G offset: {result['g_offset']}")
        print(f"  R offset: {result['r_offset']}")
        print(f"  Enhancements: {', '.join(result['enhancements'])}")
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("PROCESSING COMPLETE - SUMMARY")
    print(f"{'='*60}\n")
    
    # Group by image
    from collections import defaultdict
    by_image = defaultdict(list)
    for r in results:
        by_image[r['filename']].append(r)
    
    for filename in sorted(by_image.keys()):
        print(f"\n{filename}:")
        for r in by_image[filename]:
            config = f"{r['metric']} + {r['features']}"
            if r['enhancements']:
                config += " + enhanced"
            print(f"  {config:30s} -> G:{r['g_offset']}, R:{r['r_offset']}")
    
    print(f"\n\nAll outputs saved in the 'outputs' directory.")


if __name__ == "__main__":
    main()