import PIL
import PIL.Image

import piexif

import os
import shutil

import re
import random

ok = re.compile(r'^PICT\d\d\d\d$')

def rename(f):
  while True:
    nf = "PICT%04d.JPG" % random.randint(1111,9999)
    if not os.path.isfile(nf):
      print(f,"->",nf)
      return nf

# Fix image paths
for f in os.listdir('.'):
  if f.upper().endswith('JPG'):
    a, b = os.path.splitext(f)
    if not ok.match(a):
      shutil.move(f, rename(f))
      
for f in os.listdir('.'):
  if f.upper().endswith('JPG'):
    print("Checking", f)
    # Find the image size
    im = PIL.Image.open(f)
    im_size = im.size
  
    if im_size != (3648,2736) and im_size != (2736,3648):
      print("Resizing image to POLAROID dimensions")
      im = im.resize((im_size[0] * 4, im_size[1] * 4))
      if im_size[0] > im_size[1]:
        into = PIL.Image.new(im.mode, (3648,2736))
        im.thumbnail((3648,2736), PIL.Image.ANTIALIAS)
      else:
        into = PIL.Image.new(im.mode, (2736,3648))
        im.thumbnail((2736,3648), PIL.Image.ANTIALIAS)
      into.paste(im, (int((into.size[0] - im.size[0]) / 2), int((into.size[1] - im.size[1]) / 2)))
      into.save(f)
      im = into
  
    im_size = im.size

    source_image = piexif.load(im.info["exif"])
    print(source_image)
    
    try:
      exif_width = source_image["Exif"][piexif.ExifIFD.PixelXDimension]
      exif_height = source_image["Exif"][piexif.ExifIFD.PixelYDimension]
    except IndexError:
      exif_width = None
      exif_height = None

    for k,v in source_image.items():
      print(k,v)
    
    if exif_width != im_size[0] or exif_height != im_size[1]:
      print("EXIF data was bad for %s" % f)
      print("  width  - ", exif_width, im_size[0])
      print("  height - ", exif_height, im_size[1])

      source_image["Exif"][piexif.ExifIFD.PixelXDimension] = im_size[0]
      source_image["Exif"][piexif.ExifIFD.PixelYDimension] = im_size[1]
      print(source_image)
      exif_bytes = piexif.dump(source_image)
      im.save(f, "jpeg", exif=exif_bytes)
