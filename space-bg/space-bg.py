#! /usr/bin/env python2

from gimpfu import *

import random
import time

rng = random.Random()

def generate_seed():
    return round(time.clock() * 1000.0)

def rand_bool():
    return bool(rng.getrandbits(1))

def rand_sign():
    return rng.choice([-1.0, 1.0])

def space_bg(
        image, layer,
        width, height,
        mask, max_big_stars_count,
        mist_count, mist_size, hue_variation,
        supernova, plasma,
        image_count, export, output_directory, filename):
    for i in range(image_count):
        try:
            # initial variables
            aspect_ratio = float(width) / float(height)
            hue_base = rng.random() * 360.0

            # create an image, add initial layer
            image_space = pdb.gimp_image_new(width, height, RGB)
            layer_stars = pdb.gimp_layer_new(
                image_space, width, height, RGBA_IMAGE, "Stars",
                100, LAYER_MODE_NORMAL_LEGACY)
            pdb.gimp_image_insert_layer(image_space, layer_stars, None, -1)
            pdb.gimp_display_new(image_space)

            # generate stars
            pdb.gimp_drawable_fill(layer_stars, FILL_WHITE)
            pdb.gimp_drawable_invert(layer_stars, True)
            pdb.plug_in_hsv_noise(image_space, layer_stars, 8, 0, 255, 255)
            pdb.gimp_drawable_levels(
                layer_stars, HISTOGRAM_VALUE,
                0.32, 0.56, False, 1.0, 0.0, 1.0, False)
            pdb.gimp_drawable_desaturate(layer_stars, DESATURATE_VALUE)
            pdb.plug_in_sparkle(
                image_space, layer_stars, 0.001, 0.2, 20, 4, -1, 0.1, 0.0, 0.0,
                0.0, False, False, False, 0)
            
            # generate bigger stars
            if max_big_stars_count > 0:
                layer_stars2 = pdb.gimp_layer_new(
                    image_space, width, height, RGBA_IMAGE, "Stars2",
                    50, LAYER_MODE_NORMAL_LEGACY)
                pdb.gimp_image_insert_layer(image_space, layer_stars2, None, -1)
                brush_stars2 = "space-bg-stars2"
                pdb.gimp_brush_new(brush_stars2)
                pdb.gimp_brush_set_radius(brush_stars2, width / 250.0)
                pdb.gimp_brush_set_hardness(brush_stars2, 0.75)
                pdb.gimp_context_set_brush(brush_stars2)
                pdb.gimp_context_set_default_colors()
                pdb.gimp_context_swap_colors()
                for j in range(rng.randrange(0, max_big_stars_count)):
                    coords = [
                        rng.randrange(0, width),
                        rng.randrange(0, height)]
                    pdb.gimp_paintbrush_default(layer_stars2, 2, coords)
                pdb.gimp_brush_delete(brush_stars2)
                pdb.gimp_drawable_levels(
                    layer_stars2, HISTOGRAM_VALUE,
                    0.0, 0.4, False, 1.0, 0.0, 1.0, False)

            # mask stars
            if mask:
                layer_mask = pdb.gimp_layer_new(
                    image_space, width, height, RGBA_IMAGE, "Mask",
                    100, LAYER_MODE_MULTIPLY_LEGACY)
                pdb.gimp_image_insert_layer(image_space, layer_mask, None, -1)
                mask_width = 16.0
                mask_height = 16.0
                if aspect_ratio > 1.0:
                    mask_height /= aspect_ratio
                elif aspect_ratio < 1.0:
                    mask_width *= aspect_ratio
                pdb.plug_in_solid_noise(
                    image_space, layer_mask, True, True,
                    generate_seed(), 0, mask_width, mask_height)
                pdb.gimp_drawable_levels(
                    layer_mask, HISTOGRAM_VALUE, 0.0, 0.7, False, 1.0, 0.0, 1.0, False)
                pdb.gimp_layer_set_opacity(layer_mask, 95)

            # add supernova
            if supernova:
                layer_supernova = pdb.gimp_layer_new(
                    image_space, width, height, RGBA_IMAGE, "Supernova",
                    100, LAYER_MODE_NORMAL_LEGACY)
                pdb.gimp_image_insert_layer(image_space, layer_supernova, None, -1)
                nova_x = rng.randrange(0, width)
                nova_y = rng.randrange(0, height)
                pdb.plug_in_nova(image_space, layer_supernova,
                    nova_x, nova_y, (255, 255, 255), 10, 10, hue_variation)

            # generate mist layers
            if mist_count > 0:
                mist_size_x = mist_size
                mist_size_y = mist_size
                if aspect_ratio > 1.0:
                    mist_size_y /= aspect_ratio
                elif aspect_ratio < 1.0:
                    mist_size_x *= aspect_ratio
                for j in range(mist_count):
                    layer_mist = pdb.gimp_layer_new(
                        image_space, width, height, RGBA_IMAGE, "Mist" + str(j),
                        1.5 + rng.random() * 8.5, LAYER_MODE_NORMAL_LEGACY)
                    pdb.gimp_image_insert_layer(image_space, layer_mist, None, -1)
                    pdb.plug_in_solid_noise(
                        image_space, layer_mist, False, False,
                        generate_seed(), 0, mist_size_x, mist_size_y)
                    pdb.gimp_drawable_desaturate(layer_mist, DESATURATE_VALUE)
                    hue_final = hue_base + rand_sign() * hue_variation * rng.random()
                    if hue_final < 0.0:
                        hue_final = 360.0 + hue_final
                    elif hue_final > 360.0:
                        hue_final = hue_final - 360.0
                    pdb.gimp_drawable_colorize_hsl(layer_mist,
                        hue_final,
                        rng.random() * 100.0,
                        rng.random() * -100.0)

            # plasma texture for color modulation
            if plasma:
                layer_plasma = pdb.gimp_layer_new(
                    image_space, width, height, RGBA_IMAGE, "Plasma",
                    1.5, LAYER_MODE_NORMAL_LEGACY)
                pdb.gimp_image_insert_layer(image_space, layer_plasma, None, -1)
                pdb.plug_in_plasma(image_space, layer_plasma, generate_seed(), 3)
                pdb.plug_in_blur(image_space, layer_plasma)

            # export to png
            if export:
                output_path = output_directory + "/" + filename + str(i) + ".png"
                layer_export = pdb.gimp_image_merge_visible_layers(
                    image_space, CLIP_TO_IMAGE)
                pdb.file_png_save_defaults(
                    image_space, layer_export, output_path, output_path)
        except Exception as error:
            pdb.gimp_message("Unexpected error: " + str(error))

register(
            "python-fu-space-bg",
            "Generates a space-like image.",
            """Creates a space-like image. 
            Uses HSV noise and solid noise for procedural generation. 
            You can optionally export all generated images to a defined folder.""",
            "Wichamir",
            "Wichamir",
            "2021",
            "<Image>/Filters/Render/Space Background...",
            "*",
            [
                (PF_INT, "Width", "Image width", 4096),
                (PF_INT, "Height", "Image height", 2304),
                (PF_BOOL, "Mask", "Mask stars?", True),
                (PF_INT, "BigStars", "Max number of bigger stars", 20),
                (PF_INT, "Layers", "Number of mist layers", 3),
                (PF_SLIDER, "Size", "Mist size", 5.0, (0.1, 16.0, 0.001)),
                (PF_SLIDER, "Variation", "Hue variation", 30, (0.0, 180.0, 0.001)),
                (PF_BOOL, "Supernova", "Add supernova?", False),
                (PF_BOOL, "Plasma", "Generate plasma?", True),
                (PF_INT, "Images", "Number of images to generate", 1),
                (PF_BOOL, "Export", "Export?", False),
                (PF_DIRNAME, "OutputDirectory", "Output directory (if exporting)", ""),
                (PF_STRING, "Filename", "Filename (if exporting)", "space"),
            ],
            [],
            space_bg
)

main()