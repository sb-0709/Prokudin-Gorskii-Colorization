import os
import cv2
import numpy as np
from alignment import split_channels, align_simple, shift_image, align_pyramid

input_dir = "data"

for filename in os.listdir(input_dir):
    if not filename.lower().endswith((".jpg", ".tif", ".png")):
        continue

    img_path = os.path.join(input_dir, filename)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    # img = cv2.cvtColor(img_path, cv2.COLOR_BGR2RGB)
    assert img is not None, f"Failed to load {filename}"

    B, G, R = split_channels(img)

    if min(img.shape) > 1000:
        dx_g, dy_g = align_pyramid(G, B)
        dx_r, dy_r = align_pyramid(R, B)

        method = "pyramid"
    else:
        dx_g, dy_g = align_simple(G, B)
        dx_r, dy_r = align_simple(R, B)

        method = "simple"

    G_aligned = shift_image(G, dx_g, dy_g)
    R_aligned = shift_image(R, dx_r, dy_r)

    color = np.dstack([B, G_aligned, R_aligned])

    # print(aligned_rgb.dtype, aligned_rgb.min(), aligned_rgb.max())

    name = os.path.splitext(filename)[0]
    cv2.imwrite(f"outputs/06_test/{name}_{method}.jpg", color)
    
    # cv2.imwrite(f"{output_dir}/{name}_B.jpg", B)
    # cv2.imwrite(f"{output_dir}/{name}_G.jpg", G)
    # cv2.imwrite(f"{output_dir}/{name}_R.jpg", R)

    print(f"Saved channels for {filename}")



# # im = skio.imread("cathedral.jpg")
# # im = sk.img_as_float(im)


# for filename in os.listdir(input_dir):
#     if not filename.lower().endswith((".jpg", ".tif", ".png")):
#         continue

#     img_path = os.path.join(input_dir, filename)

#     img = skio.imread(img_path)
#     img = sk.img_as_float(img)

#     # img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
#     # img = cv2.cvtColor(img_path, cv2.COLOR_BGR2RGB)

#     assert img is not None, f"Failed to load {filename}"

#     B, G, R = split_channels_color(img)

#     if min(img.shape) > 1000:
#         dx_g, dy_g = align_gaussian_pyramid(G, B) #align_pyramid(G, B)
#         dx_r, dy_r = align_gaussian_pyramid(R, B) #align_pyramid(R, B)

#         method = "pyramid"
#     else:
#         dx_g, dy_g = align_simple(G, B)
#         dx_r, dy_r = align_simple(R, B)

#         method = "simple"

#     G_aligned = shift_image(G, dx_g, dy_g)
#     R_aligned = shift_image(R, dx_r, dy_r)

#     color = np.dstack([R_aligned, G_aligned, B])  # RGB order
#     name = os.path.splitext(filename)[0]
#     color = np.clip(color, 0, 1)
#     color_uint8 = (color * 255).astype(np.uint8)
#     skio.imsave(f"outputs/05_gaussian_pyramid/{name}_{method}.jpg", color_uint8)


#     print(f"Saved channels for {filename}")

    # color = np.dstack([B, G_aligned, R_aligned])
    # print(color.dtype, color.min(), color.max())

    # name = os.path.splitext(filename)[0]
    # cv2.imwrite(f"outputs/05_gaussian_pyramid/{name}_{method}.jpg", color)
    # cv2.imwrite(f"outputs/04_pyramid_align/{name}_{method}.jpg", color)

    # os.makedirs("outputs/03_simple_align", exist_ok=True)
    # cv2.imwrite(f"outputs/03_simple_align/{name}_simple.jpg", color)
    
    # cv2.imwrite(f"{output_dir}/{name}_B.jpg", B)
    # cv2.imwrite(f"{output_dir}/{name}_G.jpg", G)
    # cv2.imwrite(f"{output_dir}/{name}_R.jpg", R)

    





