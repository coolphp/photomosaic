# photomosaic
A simple Python script which creates photographic mosaics

Built with Python 3 and Pillow 3.1.1.

# Usage
```
photomosaic.py  [-h] [-v] [-r] [--allowable-error X] [--sample-size Y] [--sub-image-size Z]
                input_directory input_file output_file
```

# Positional Parameters
- **input_directory**
  - input directory to search for image files
- **input_file**
  - input file to be used for the photographic mosaic
- **output_file**
  - output file

# Optional Parameters

##### Definitions Note
- **sample**: Fundamentally, photographic mosaics are created by taking one image and then dividing it up into many smaller images. *Sample* refers to one of the smaller images.
- **sub-image**: Refers to an image which will replace the *sample* in the final output image

---

- **--help**
  - show help
- **--verbose**
  - run verbose
- **--recursive**
  - recursively search input directory
- **--allowable-error (int)**
  - (default: 15) error amount which the average RGB of the sub-image must fall within (in terms of the sample average RGB) in order to qualify as a replacement
- **--sample-size (int)**
  - (default: 10) size in pixels of the square which will be used to sample the input image (e.g. 10 = every 10x10 pixel square will be replaced with a sub-image)
- **--sub-image-size (int)**
  - (default: sample-size) size in pixels of the sub-image square which will replace the original sample in the input image (e.g. 10 = every sub-image will be scaled to a 10x10 pixel square)
  - Use this parameter to give the sub-images more detail when zoomed in, but at the cost of having a larger file size

# Usage Example
```
python photomosaic.py "C:\Users\JDoe\Pictures" "C:\Users\JDoe\Pictures\input.png" "C:\Users\JDoe\Pictures\output.png" 
```

# License
MIT

### Other Notes
At the time of creating this project, I am a programmer who comes from C# and PHP -- I am new to Python. Please do not use this project as a Python best-practices example, but rather as an educational resource for creating a photographic mosaic.
