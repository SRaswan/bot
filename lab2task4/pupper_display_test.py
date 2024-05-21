#!/usr/bin/python
###############
# Name: pupper_display_test.py
# Description: Test code for Pupper's display. It will convert images and
#   	       resize as needed.
#
# Author: Prof. Riek
# Date: 26 Apr 2024
#############

#### Import ####
# Pupper libraries for using the LCD Display. Display provies basic functions,
# BehaviorState allows you to change the display's state depending on the robot
# (e.g., low battery, boot, etc). 
from MangDang.mini_pupper.display import Display, BehaviorState
import time
from resizeimage import resizeimage  # library for image resizing
from PIL import Image, ImageDraw, ImageFont # library for image manip.

MAX_WIDTH = 320   # max width of the LCD display

# Get access to the display so we can display things
disp = Display()

# Open the image (Your image file name goes here)
imgLoc = "img/anime.jpg"
imgFile = Image.open(imgLoc)

# Convert to RGBA if needed
if (imgFile.format == 'PNG'):
	if (imgFile.mode != 'RGBA'):
		imgOld = imgFile.convert("RGBA")
		imgFile = Image.new('RGBA', imgOld.size, (255, 255, 255))

# We likely also need to resize to the pupper LCD display size (320x240).
# Note, this is sometimes a little buggy, but you can get the idea. 
width_size = (MAX_WIDTH / float(imgFile.size[0]))
imgFile = resizeimage.resize_width(imgFile, MAX_WIDTH)

newFileLoc = 'img/animeRZ.png'   #rename as you like

# now output it (super inefficient, but it is what it is)
imgFile.save(newFileLoc, imgFile.format)

# Display it on Pupper's LCD display
disp.show_image(newFileLoc)
