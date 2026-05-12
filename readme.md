#**Colorizing the Prokudin-Gorskii Photo Collection**

**Author:** Sanskriti Bansal

## Overview

This project colorizes the Prokudin-Gorskii glass plate images by aligning three color channels (B, G, R) using image processing techniques. The implementation includes both basic alignment methods and several "bells & whistles" enhancements.

## Project Structure

```
hw1/
└── code/
    ├── README.md                   # This file
    ├── utils.py                    # necessary fucntionalities with bells & whistles
    ├── main.py                     # Full script (4 versions per image)
└── web/
    ├── index.html                  # Webpage writeup
    ├── CS4732 HW1.pdf              # pdf submission
└── outputs/                        # Generated results
    ├── 01_basic_ssd/               # Basic SSD results
    ├── 02_basic_ncc/               # Basic NCC results
    ├── 03_enhanced_ssd/            # Enhanced SSD results
    ├── 04_enhanced_ncc/            # Enhanced NCC results
```

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```bash
pip install numpy opencv-python
```

## Installation

1. **Download the project files**

2. **Install dependencies:**
   ```bash
   pip install numpy opencv-python
   ```

3. **Download the dataset:**
   - Download [data.zip](https://drive.google.com/file/d/1nYdWKBnqxFmvB_DXE-giQEjwvBfPH2Ks/view?usp=share_link)
   - Extract to a `data/` directory in the project root

## Usage

### Generate All Comparisons

Run the full comparison script to generate 4 versions of each image:

```bash
python main.py
```

**Output:**
- `outputs/01_basic_ssd/` - Basic alignment with SSD metric
- `outputs/02_basic_ncc/` - Basic alignment with NCC metric
- `outputs/03_enhanced_ssd/` - SSD with edge features + enhancements
- `outputs/04_enhanced_ncc/` - NCC with edge features + enhancements

## How It Works

### Basic Alignment

1. **Channel Splitting:** Divide each glass plate image into three equal parts (B, G, R channels)

2. **Alignment Methods:**
   - **Simple alignment:** Exhaustive search over [-15, 15] pixel window (for small .jpg images)
   - **Pyramid alignment:** Coarse-to-fine multi-scale search (for large .tif images)

3. **Similarity Metrics:**
   - **SSD (Sum of Squared Differences):** Simple pixel-wise difference
   - **NCC (Normalized Cross-Correlation):** Robust to brightness variations

### Bells & Whistles Enhancements

1. **Edge-Based Features**
   - Uses Sobel edge detection instead of raw pixels
   - Solves alignment failures on images with brightness differences
   - Automatically applied to emir.tif and all enhanced versions

2. **Automatic Border Cropping**
   - Detects and removes colored borders from channel misalignment
   - Uses edge detection to find image content boundaries

3. **Automatic Contrast Enhancement**
   - Rescales intensities to use full 0-255 range
   - Uses percentile-based scaling to avoid outliers

4. **Automatic White Balance**
   - Corrects color casts using "gray world" assumption
   - Produces more natural-looking colors

## Results Summary

### Key Findings

- **Basic SSD fails on church.tif** due to brightness differences between color channels
- **NCC metric solves the problem** by normalizing brightness
- **Edge-based features** provide an alternative solution
- **Pyramid approach** is essential for efficient processing (20× speedup on large images)
- **Post-processing enhancements** significantly improve visual quality

### Example Offsets

**cathedral.jpg** (Simple alignment):
- G offset: (2, 5)
- R offset: (3, 12)

## File Descriptions

### Core Files

- **`utils.py`**
  - All alignment algorithms and enhancement functions
  - Functions: `split_channels`, `align_simple`, `align_pyramid`, `compute_edges`, `auto_crop`, etc.

- **`main.py`**
  - Processes all images with 4 different configurations
  - Generates comprehensive comparison data
  - Best for understanding differences between methods

### Web Files

- **`index.html`**
  - Webpage writeup with results and analysis
  - Includes all images, offsets, and explanations
  - Open in browser to view

### Output Directories

1. **`outputs/01_basic_ssd/`**
   - Basic implementation with SSD metric
   - Shows baseline performance

2. **`outputs/02_basic_ncc/`**
   - Basic implementation with NCC metric
   - Demonstrates importance of better metric

3. **`outputs/03_enhanced_ssd/`**
   - Edge features + SSD + post-processing
   - Shows edge features solving alignment issues

4. **`outputs/04_enhanced_ncc/`**
   - Edge features + NCC + post-processing
   - Best overall quality 

## Implementation Notes

### Design Decisions

1. **Blue as reference channel**
   - Align G and R to B (B stays fixed)
   - Arbitrary choice, any channel could work

2. **Border cropping (20 pixels)**
   - Avoids edge artifacts when computing metrics
   - Critical for good alignment

3. **Automatic edge detection for emir.tif**
   - Hardcoded in `main_enhanced.py` to ensure success
   - Line: `use_edges = 'emir' in name_lower or use_bells_whistles`

4. **Image shifting with np.roll()**
   - Efficient circular shift
   - Simpler than cv2.warpAffine for this use case
