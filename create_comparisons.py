"""
Comparison script to visualize the effect of bells & whistles.
Run this after processing images to create side-by-side comparisons.
"""
import os
import cv2
import numpy as np
from utils import (
    split_channels, align_simple, shift_image, align_pyramid,
    auto_crop, auto_contrast_color, white_balance_gray_world
)

def create_comparison(filename, input_dir="data"):
    """
    Create a comparison image showing:
    1. Basic alignment (SSD)
    2. Basic alignment (NCC) 
    3. With edge features
    4. Full bells & whistles
    """
    print(f"\nCreating comparison for: {filename}")
    
    img_path = os.path.join(input_dir, filename)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"  Failed to load {filename}")
        return
    
    B, G, R = split_channels(img)
    use_pyramid = min(img.shape) > 1000
    
    results = []
    
    # Version 1: Basic SSD
    print("  [1/4] Basic SSD...")
    if use_pyramid:
        dx_g, dy_g = align_pyramid(G, B, use_edges=False, use_ncc=False)
        dx_r, dy_r = align_pyramid(R, B, use_edges=False, use_ncc=False)
    else:
        dx_g, dy_g = align_simple(G, B, use_edges=False, use_ncc=False)
        dx_r, dy_r = align_simple(R, B, use_edges=False, use_ncc=False)
    
    G1 = shift_image(G, dx_g, dy_g)
    R1 = shift_image(R, dx_r, dy_r)
    color1 = np.dstack([B, G1, R1])
    results.append(("Basic SSD", color1, (dx_g, dy_g), (dx_r, dy_r)))
    
    # Version 2: Basic NCC
    print("  [2/4] Basic NCC...")
    if use_pyramid:
        dx_g, dy_g = align_pyramid(G, B, use_edges=False, use_ncc=True)
        dx_r, dy_r = align_pyramid(R, B, use_edges=False, use_ncc=True)
    else:
        dx_g, dy_g = align_simple(G, B, use_edges=False, use_ncc=True)
        dx_r, dy_r = align_simple(R, B, use_edges=False, use_ncc=True)
    
    G2 = shift_image(G, dx_g, dy_g)
    R2 = shift_image(R, dx_r, dy_r)
    color2 = np.dstack([B, G2, R2])
    results.append(("Basic NCC", color2, (dx_g, dy_g), (dx_r, dy_r)))
    
    # Version 3: Edge features + NCC
    print("  [3/4] Edge-based NCC...")
    if use_pyramid:
        dx_g, dy_g = align_pyramid(G, B, use_edges=True, use_ncc=True)
        dx_r, dy_r = align_pyramid(R, B, use_edges=True, use_ncc=True)
    else:
        dx_g, dy_g = align_simple(G, B, use_edges=True, use_ncc=True)
        dx_r, dy_r = align_simple(R, B, use_edges=True, use_ncc=True)
    
    G3 = shift_image(G, dx_g, dy_g)
    R3 = shift_image(R, dx_r, dy_r)
    color3 = np.dstack([B, G3, R3])
    results.append(("Edge + NCC", color3, (dx_g, dy_g), (dx_r, dy_r)))
    
    # Version 4: Full bells & whistles
    print("  [4/4] Full enhancement...")
    B4, G4, R4 = auto_crop(B, G3, R3)
    color4 = np.dstack([B4, G4, R4])
    color4 = auto_contrast_color(color4)
    color4 = white_balance_gray_world(color4)
    results.append(("Full Enhanced", color4, (dx_g, dy_g), (dx_r, dy_r)))
    
    # Create comparison grid (2x2)
    # Resize all to same size (use smallest)
    heights = [img.shape[0] for _, img, _, _ in results]
    widths = [img.shape[1] for _, img, _, _ in results]
    target_h = min(heights)
    target_w = min(widths)
    
    resized = []
    for label, img, g_off, r_off in results:
        if img.shape[0] != target_h or img.shape[1] != target_w:
            img_resized = cv2.resize(img, (target_w, target_h))
        else:
            img_resized = img
        
        # Add text label
        img_labeled = img_resized.copy()
        cv2.putText(img_labeled, label, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(img_labeled, f"G:{g_off} R:{r_off}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        resized.append(img_labeled)
    
    # Create 2x2 grid
    top_row = np.hstack([resized[0], resized[1]])
    bottom_row = np.hstack([resized[2], resized[3]])
    comparison = np.vstack([top_row, bottom_row])
    
    # Save comparison
    name = os.path.splitext(filename)[0]
    output_dir = "outputs/comparisons"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{name}_comparison.jpg")
    cv2.imwrite(output_path, comparison)
    
    print(f"  Saved comparison: {output_path}")
    
    return results


def main():
    """Generate comparisons for all images"""
    input_dir = "data"
    
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} directory not found!")
        return
    
    image_files = [f for f in os.listdir(input_dir) 
                   if f.lower().endswith((".jpg", ".tif", ".png"))]
    
    if not image_files:
        print(f"No images found in {input_dir}!")
        return
    
    print(f"Creating comparisons for {len(image_files)} images...")
    print("This will show the effect of each enhancement.\n")
    
    for filename in sorted(image_files):
        try:
            create_comparison(filename, input_dir)
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
    
    print("\n" + "="*60)
    print("COMPARISON COMPLETE")
    print("="*60)
    print("Check outputs/comparisons/ for side-by-side visualizations")
    print("\nEach comparison shows:")
    print("  Top-left:     Basic SSD (baseline)")
    print("  Top-right:    Basic NCC (better metric)")
    print("  Bottom-left:  Edge-based NCC (handles brightness differences)")
    print("  Bottom-right: Full enhancement (crop + contrast + white balance)")


if __name__ == "__main__":
    main()