import numpy as np
import cv2

#split into R, G, B channels
def split_channels(img):
    h, w = img.shape
    ch = h // 3
    B = img[0:ch]
    G = img[ch:2*ch]
    R = img[2*ch:3*ch]
    return B, G, R


#simple alignment using SSD
def compute_ssd(img1, img2):
    diff = img1.astype(np.float32) - img2.astype(np.float32)
    return np.sum(diff * diff)

# def shift_image(img, dx, dy):
#     M = np.float32([[1, 0, dx], [0, 1, dy]])
#     shifted = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
#     return shifted

def shift_image(img, dx, dy):
    return np.roll(np.roll(img, dy, axis=0), dx, axis=1)

#crop images
def crop_border(img, border=20):
    h, w = img.shape[:2]
    return img[border:h-border, border:w-border]


def align_simple(channel, reference, search_range=15):
    best_score = float("inf")
    best_dx, best_dy = 0, 0

    ref_crop = crop_border(reference)

    for dx in range(-search_range, search_range + 1):
        for dy in range(-search_range, search_range + 1):
            shifted = shift_image(channel, dx, dy)
            shifted_crop = crop_border(shifted)

            score = compute_ssd(shifted_crop, ref_crop)

            if score < best_score:
                best_score = score
                best_dx, best_dy = dx, dy

    return best_dx, best_dy

#pyramid alignment
def align_pyramid(channel, reference, level=4):
    # Base case: image is small or pyramid bottom reached
    if level == 0 or min(channel.shape) < 100:
        return align_simple(channel, reference, search_range=15)

    # Downsample
    ch_small = channel[::2, ::2]
    ref_small = reference[::2, ::2]

    # Align at lower resolution
    dx, dy = align_pyramid(ch_small, ref_small, level - 1)

    # Scale offsets to current resolution
    dx *= 2
    dy *= 2

    # Refine around scaled offsets
    best_dx, best_dy = dx, dy
    best_score = float("inf")

    ref_crop = crop_border(reference)

    for ddx in range(-2, 3):
        for ddy in range(-2, 3):
            test_dx = dx + ddx
            test_dy = dy + ddy

            shifted = shift_image(channel, test_dx, test_dy)
            shifted_crop = crop_border(shifted)

            score = compute_ssd(shifted_crop, ref_crop)

            if score < best_score:
                best_score = score
                best_dx, best_dy = test_dx, test_dy

    return best_dx, best_dy

# bells and whistles
# automattic cropping
# def crop_border_auto(img, tol=20):
#     mask = np.max(img, axis=2) > tol
#     coords = np.argwhere(mask)
#     y0, x0 = coords.min(axis=0)
#     y1, x1 = coords.max(axis=0) + 1
#     return img[y0:y1, x0:x1]



# # automatic contrasting
# def contrast_stretch(img):
#     min_val = img.min()
#     max_val = img.max()
#     if max_val - min_val == 0:
#         return img
#     stretched = (img - min_val) * 255.0 / (max_val - min_val)
#     return stretched.astype(np.uint8)



#gaussian pyramid approach with NCC
# def compute_ncc(img1, img2):
#     f1 = img1.astype(np.float32)
#     f2 = img2.astype(np.float32)

#     f1 = (f1 - f1.mean()) / (f1.std() + 1e-5)
#     f2 = (f2 - f2.mean()) / (f2.std() + 1e-5)

#     return np.sum(f1 * f2)

# def pre_crop(img, crop_fraction=0.05):
#     h, w = img.shape
#     dh = int(h * crop_fraction)
#     dw = int(w * crop_fraction)
#     return img[dh:h-dh, dw:w-dw]

# def downsample(img):
#     blurred = cv2.GaussianBlur(img, (5,5), 1.0)
#     return blurred[::2, ::2]


# def align_gaussian_pyramid(channel, reference, levels=4):
#     # Pre-crop
#     channel = pre_crop(channel)
#     reference = pre_crop(reference)

#     if levels == 0 or min(channel.shape) < 150:
#         return align_simple(channel, reference, search_range=15, metric="ncc")

#     ch_small = downsample(channel)
#     ref_small = downsample(reference)

#     dx, dy = align_pyramid(ch_small, ref_small, levels - 1)
#     dx *= 2
#     dy *= 2

#     best_dx, best_dy = dx, dy
#     best_score = -1e9  # for NCC

#     ref_crop = pre_crop(reference)

#     for ddx in range(-5, 6):
#         for ddy in range(-5, 6):
#             test_dx = dx + ddx
#             test_dy = dy + ddy

#             shifted = shift_image(channel, test_dx, test_dy)
#             score = compute_ncc(pre_crop(shifted), ref_crop)

#             if score > best_score:
#                 best_score = score
#                 best_dx, best_dy = test_dx, test_dy

#     return best_dx, best_dy


# def split_channels_color(img):
#     height = img.shape[0] // 3

#     b = img[:height]
#     g = img[height:2*height]
#     r = img[2*height:3*height]
#     return b, g, r

# crop images
# def crop_border_ratio(img, ratio=0.1):
#     h, w = img.shape[:2]
#     dh = int(h * ratio)
#     dw = int(w * ratio)
#     return img[dh:h-dh, dw:w-dw]