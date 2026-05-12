import numpy as np
import cv2

# ============ BASIC ALIGNMENT FUNCTIONS ============

def split_channels(img):
    """Split into R, G, B channels"""
    h, w = img.shape
    ch = h // 3
    B = img[0:ch]
    G = img[ch:2*ch]
    R = img[2*ch:3*ch]
    return B, G, R


def compute_ssd(img1, img2):
    """Compute Sum of Squared Differences"""
    diff = img1.astype(np.float32) - img2.astype(np.float32)
    return np.sum(diff * diff)


def shift_image(img, dx, dy):
    """Shift image by dx, dy pixels"""
    return np.roll(np.roll(img, dy, axis=0), dx, axis=1)


def crop_border(img, border=20):
    """Crop border pixels from image"""
    h, w = img.shape[:2]
    return img[border:h-border, border:w-border]


# ============ BELLS & WHISTLES: BETTER FEATURES ============

def compute_edges(img):
    """Compute edge map using Sobel operator."""
    # Normalize to 0-255 range
    img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Compute gradients
    sobelx = cv2.Sobel(img_norm, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img_norm, cv2.CV_64F, 0, 1, ksize=3)
    
    # Combine gradients
    edges = np.sqrt(sobelx**2 + sobely**2)
    return edges


def compute_ncc(img1, img2):
    """Compute Normalized Cross-Correlation."""
    img1_norm = (img1 - np.mean(img1)) / (np.std(img1) + 1e-10)
    img2_norm = (img2 - np.mean(img2)) / (np.std(img2) + 1e-10)
    return np.sum(img1_norm * img2_norm)


# ============ ENHANCED ALIGNMENT FUNCTIONS ============

def align_simple(channel, reference, search_range=15, use_edges=False, use_ncc=False):
    """Simple alignment with optional edge-based matching and NCC."""
    best_score = -float("inf") if use_ncc else float("inf")
    best_dx, best_dy = 0, 0
    
    # Optionally convert to edges
    if use_edges:
        channel_proc = compute_edges(channel)
        ref_proc = compute_edges(reference)
    else:
        channel_proc = channel
        ref_proc = reference
    
    ref_crop = crop_border(ref_proc)
    
    for dx in range(-search_range, search_range + 1):
        for dy in range(-search_range, search_range + 1):
            shifted = shift_image(channel_proc, dx, dy)
            shifted_crop = crop_border(shifted)
            
            # Compute score
            if use_ncc:
                score = compute_ncc(shifted_crop, ref_crop)
                if score > best_score:
                    best_score = score
                    best_dx, best_dy = dx, dy
            else:
                score = compute_ssd(shifted_crop, ref_crop)
                if score < best_score:
                    best_score = score
                    best_dx, best_dy = dx, dy
    
    return best_dx, best_dy


def align_pyramid(channel, reference, level=4, use_edges=False, use_ncc=False):
    """Pyramid alignment with optional edge-based matching and NCC."""
    # Base case: image is small or pyramid bottom reached
    if level == 0 or min(channel.shape) < 100:
        return align_simple(channel, reference, search_range=15, 
                          use_edges=use_edges, use_ncc=use_ncc)
    
    # Downsample
    ch_small = channel[::2, ::2]
    ref_small = reference[::2, ::2]
    
    # Align at lower resolution
    dx, dy = align_pyramid(ch_small, ref_small, level - 1, 
                          use_edges=use_edges, use_ncc=use_ncc)
    
    # Scale offsets to current resolution
    dx *= 2
    dy *= 2
    
    # Refine around scaled offsets
    best_dx, best_dy = dx, dy
    best_score = -float("inf") if use_ncc else float("inf")
    
    # Optionally convert to edges
    if use_edges:
        channel_proc = compute_edges(channel)
        ref_proc = compute_edges(reference)
    else:
        channel_proc = channel
        ref_proc = reference
    
    ref_crop = crop_border(ref_proc)
    
    for ddx in range(-2, 3):
        for ddy in range(-2, 3):
            test_dx = dx + ddx
            test_dy = dy + ddy
            
            shifted = shift_image(channel_proc, test_dx, test_dy)
            shifted_crop = crop_border(shifted)
            
            # Compute score
            if use_ncc:
                score = compute_ncc(shifted_crop, ref_crop)
                if score > best_score:
                    best_score = score
                    best_dx, best_dy = test_dx, test_dy
            else:
                score = compute_ssd(shifted_crop, ref_crop)
                if score < best_score:
                    best_score = score
                    best_dx, best_dy = test_dx, test_dy
    
    return best_dx, best_dy


# ============ BELLS & WHISTLES: AUTO CROPPING ============

def detect_border(channel, threshold=0.05):
    """Detect border region by finding where image content starts."""
    # Compute edges
    edges = compute_edges(channel)
    
    # Normalize
    edges_norm = edges / (edges.max() + 1e-10)
    
    # Find content boundaries by looking for strong edges
    edge_threshold = threshold
    
    # Find rows and columns with sufficient edge content
    row_edges = np.max(edges_norm, axis=1)
    col_edges = np.max(edges_norm, axis=0)
    
    # Find first and last rows/cols with significant edges
    significant_rows = np.where(row_edges > edge_threshold)[0]
    significant_cols = np.where(col_edges > edge_threshold)[0]
    
    if len(significant_rows) > 0 and len(significant_cols) > 0:
        top = significant_rows[0]
        bottom = significant_rows[-1]
        left = significant_cols[0]
        right = significant_cols[-1]
    else:
        # Fallback: crop 5% from each side
        h, w = channel.shape
        top, bottom = int(h * 0.05), int(h * 0.95)
        left, right = int(w * 0.05), int(w * 0.95)
    
    return top, bottom, left, right


def auto_crop(B, G, R):
    """Automatically crop borders from all three channels."""
    # Detect borders in each channel
    b_crop = detect_border(B)
    g_crop = detect_border(G)
    r_crop = detect_border(R)
    
    # Take intersection (most conservative crop)
    top = max(b_crop[0], g_crop[0], r_crop[0])
    bottom = min(b_crop[1], g_crop[1], r_crop[1])
    left = max(b_crop[2], g_crop[2], r_crop[2])
    right = min(b_crop[3], g_crop[3], r_crop[3])
    
    # Apply crop to all channels
    B_cropped = B[top:bottom, left:right]
    G_cropped = G[top:bottom, left:right]
    R_cropped = R[top:bottom, left:right]
    
    return B_cropped, G_cropped, R_cropped


# ============ BELLS & WHISTLES: AUTO CONTRAST ============

def auto_contrast(img, percentile=1):
    """Automatic contrast adjustment."""
    img_float = img.astype(np.float32)
    
    # Use percentiles to be robust to outliers
    min_val = np.percentile(img_float, percentile)
    max_val = np.percentile(img_float, 100 - percentile)
    
    # Avoid division by zero
    if max_val - min_val < 1e-10:
        return img
    
    # Rescale to 0-255
    img_contrasted = (img_float - min_val) / (max_val - min_val) * 255
    img_contrasted = np.clip(img_contrasted, 0, 255).astype(np.uint8)
    
    return img_contrasted


def auto_contrast_color(color_img, percentile=1):
    """Apply auto contrast to each channel of a color image."""
    result = np.zeros_like(color_img)
    for i in range(3):
        result[:, :, i] = auto_contrast(color_img[:, :, i], percentile)
    return result


# ============ BELLS & WHISTLES: WHITE BALANCE ============

def white_balance_gray_world(color_img):
    """White balance using gray world assumption."""
    img_float = color_img.astype(np.float32)
    
    # Compute mean of each channel
    avg_b = np.mean(img_float[:, :, 0])
    avg_g = np.mean(img_float[:, :, 1])
    avg_r = np.mean(img_float[:, :, 2])
    
    # Compute gray value (average of all channels)
    gray = (avg_b + avg_g + avg_r) / 3
    
    # Compute scaling factors
    scale_b = gray / (avg_b + 1e-10)
    scale_g = gray / (avg_g + 1e-10)
    scale_r = gray / (avg_r + 1e-10)
    
    # Apply scaling
    result = img_float.copy()
    result[:, :, 0] *= scale_b
    result[:, :, 1] *= scale_g
    result[:, :, 2] *= scale_r
    
    # Clip and convert back
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result