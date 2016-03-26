#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import fnmatch
import os
import random
import sys

from PIL import Image

import math


def main(argv):

    # Parse arguments

    parser = argparse.ArgumentParser(
                        description='''\
                        ---------------
                        photomosaic
                        ---------------
                        A simple Python script which creates photographic mosaics.

                        Fundamentally, photographic mosaics are created by taking one image and then dividing it
                        up into many smaller images. You can use the average RGB values of the smaller images to
                        find other images which have similar average RGB values. Those other images can be used as
                        replacements to the smaller images.

                        Built with:
                        - Python 3
                        - Pillow (3.1.1)

                        ''',
                        epilog='''\
                        ---------------
                        Created by Cody Skonecy. MIT license.
                        https://github.com/cskonecy

                        ''',
                        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('input_directory',
                        action='store',
                        help='input directory to search for image files')

    parser.add_argument('input_file',
                        action='store',
                        help='input file to be used for the photographic mosaic (e.g. C:\\input.png)')

    parser.add_argument('output_file',
                        action='store',
                        help='output file (e.g. C:\\output.png)')

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='run verbose')

    parser.add_argument('-r',
                        '--recursive',
                        action='store_true',
                        help='recursively search input directory')

    parser.add_argument('--allowable-error',
                        metavar='X',
                        type=int,
                        action='store',
                        help="(default: 15) error amount which the average RGB of the sub-image must fall within "
                        " (in terms of the sample average RGB) in order to qualify as a replacement",
                        default=15)

    parser.add_argument('--sample-size',
                        metavar='Y',
                        type=int,
                        action='store',
                        help="(default: 10) size in pixels of the square which will be used to sample the input image "
                             "(e.g. 10 = every 10x10 pixel square will be replaced with a sub-image)",
                        default=10)

    parser.add_argument('--sub-image-size',
                        metavar='Z',
                        type=int,
                        action='store',
                        help="(default: sample-size) size in pixels of the sub-image square which will replace the "
                             "original sample in the input image "
                             "(e.g. 10 = every sub-image will be scaled to a 10x10 pixel square)")

    args = parser.parse_args(argv[1:])

    if args.sub_image_size is None:
        args.sub_image_size = args.sample_size

    print('Importing images...')

    image_list = _retrieve_images(args.input_directory, args.recursive, args.verbose)

    print('Creating output...')

    create_mosaic(image_list,
                  args.sample_size,
                  args.sub_image_size,
                  args.allowable_error,
                  args.input_file,
                  args.output_file)

    print("Photographic mosaic saved to output file: {}".format(args.output_file))

    return 0


def create_mosaic(image_list, sample_size, sub_image_size, allowable_error, input_file, output_file):
    with Image.open(input_file) as image:
        crop_width_offset = image.width % sample_size
        crop_height_offset = image.height % sample_size
        image = image.crop((
            0,
            0,
            image.width - crop_width_offset,
            image.height - crop_height_offset))
        image = image.convert('RGB')
        mosaic_image_width = int(image.width / sample_size * sub_image_size)
        mosaic_image_height = int(image.height / sample_size * sub_image_size)
        average_rgb_list = _get_image_average_rgb_by_sample_size(image, sample_size)

    with Image.new('RGB', (mosaic_image_width, mosaic_image_height)) as mosaic_image:
        for x_location, y_location, average_r, average_g, average_b in average_rgb_list:
            image_data = _get_fitting_image(image_list, allowable_error, average_r, average_g, average_b)
            if image_data is not None:
                with Image.new('RGB', (25, 25)) as sub_image:
                    sub_image.putdata(image_data)
                    sub_image = sub_image.resize((sub_image_size, sub_image_size), Image.NEAREST)
                    mosaic_image.paste(sub_image, (x_location * sub_image_size, y_location * sub_image_size))
        mosaic_image.save(output_file)


def _retrieve_images(input_directory, recursive, verbose):
    file_types = ['*.bmp', '*.jpg', '*.jpeg', '*.png']
    file_list = _retrieve_file_list(input_directory, recursive, file_types)
    image_list = []
    for file in file_list:
        _process_image(file, image_list, verbose)
    return image_list


def _process_image(file, image_list, verbose):
    with Image.open(file) as image:
        width_height_difference = abs(image.width - image.height)
        if width_height_difference > 1:
            if image.width > image.height:
                crop_size = image.height
                crop_width_offset = math.floor(width_height_difference / 2)
                crop_height_offset = 0
            else:
                crop_size = image.width
                crop_width_offset = 0
                crop_height_offset = math.floor(width_height_difference / 2)
        else:
            crop_size = image.width
            crop_width_offset = 0
            crop_height_offset = 0
        image = image.crop((
            0 + crop_width_offset,
            0 + crop_height_offset,
            crop_size + crop_width_offset,
            crop_size + crop_height_offset))
        image.thumbnail((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        r, g, b = _get_image_average_rgb(image)
        image_list.append((image.getdata(), r, g, b))

        if verbose:
            print("Processed image (RGB: {},{},{}) - {}".format(r, g, b, file))


def _get_image_average_rgb(image):
    total_r = 0
    total_g = 0
    total_b = 0
    for i in range(image.width):
        for j in range(image.height):
            r, g, b = image.getpixel((i, j))
            total_r += r
            total_g += g
            total_b += b
    average_r = math.floor(total_r / (image.height * image.width))
    average_g = math.floor(total_g / (image.height * image.width))
    average_b = math.floor(total_b / (image.height * image.width))
    return average_r, average_g, average_b


def _get_image_average_rgb_by_sample_size(image, sample_size):
    average_rgb_list = []
    for i in range(0, image.width, sample_size):
        for j in range(0, image.height, sample_size):
                total_r = 0
                total_g = 0
                total_b = 0
                for i_sub in range(i, i + sample_size):
                    for j_sub in range(j, j + sample_size):
                        r, g, b = image.getpixel((i, j))
                        total_r += r
                        total_g += g
                        total_b += b
                average_r = math.floor(total_r / (sample_size * sample_size))
                average_g = math.floor(total_g / (sample_size * sample_size))
                average_b = math.floor(total_b / (sample_size * sample_size))
                average_rgb_list.append((int(i / sample_size), int(j / sample_size), average_r, average_g, average_b))
    return average_rgb_list


def _get_fitting_image(image_list, allowable_error, average_r, average_g, average_b):
    fitting_image_list = []
    for image_data, r, g, b in image_list:
        if ((average_r - allowable_error) <= r <= (average_r + allowable_error)) and ((average_g - allowable_error) <= g <= (average_g + allowable_error)) and ((average_b - allowable_error) <= b <= (average_b + allowable_error)):
            fitting_image_list.append(image_data)
    if len(fitting_image_list) > 0:
        return random.choice(fitting_image_list)
    else:
        return None


def _retrieve_file_list(input_directory, recursive, file_types):
    file_list = []
    for root_directory, sub_directories, file_names in os.walk(input_directory):
        if not recursive:
            while len(sub_directories) > 0:
                sub_directories.pop()
        for extension in file_types:
            for filename in fnmatch.filter(file_names, extension):
                file_list.append(os.path.join(root_directory, filename))
    return file_list


if __name__ == '__main__':
    sys.exit(main(sys.argv))
