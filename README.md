# PDF and Image Comparison Tool

 This project provides a tool to compare two PDF documents by extracting images from each page and computing the Structural Similarity Index (SSIM) between corresponding images. The tool uses PyMuPDF for PDF processing, Pillow for image handling, and scikit-image for SSIM computation.

 
## Features

- Extract Images: Extract images from each page of a PDF.
- SSIM Calculation: Compute the Structural Similarity Index (SSIM) between images.
- PDF Comparison: Compare two PDFs and determine if they are identical based on image similarity.


## Requirements

- Python 3.x
- PyMuPDF
- Pillow
- NumPy
- scikit-image
- Matplotlib
    
## Run Locally

Clone the project

```bash
  git clone git@github.com:saboor-siddiqui/image_and_pdf_comparator.git
```

Go to the project directory

```bash
  cd <path where you cloned the project>/image_and_pdf_comparator
```

Build and Run with Docker

```bash
  docker pull saboorsiddiqui/image-and-pdf-comparator-py
  docker build -t image-and-pdf-comparator-py .
```

Start the Container

```bash
docker run -p 8888:8888 -v <path_to_resource_file>
```

Access the Jupyter Notebook
```
After running the Docker container, check the logs for the local Jupyter kernel link. Access the notebook via the provided URL and run the code with the correct resource paths.
```

