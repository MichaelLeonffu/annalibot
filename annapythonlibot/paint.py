# paint.py


# Adding images together in a fancy way

from PIL import Image


# Align pixel values
HEAD_BODY_APX = (255, 0, 255, 255)
BODY_TAIL_APX = (255, 255, 0, 255)


# Find pixel
def find_align_pixel(im, align_pixel):
	# Flatten data to be array (scans left to right then top to bottom)
	im_data = im.getdata()
	for i, px in enumerate(im_data):
		# Find first pixel that matches the alignment pixel
		if px == align_pixel:
			return (i%im.width, i//im.width)

	raise ValueError("Failed to find px")

# Check this cat part for the pixel (helper for discord function upload cat)
def has_align_pixel(fp_cat, cat_part):

	# We can assume that cat_part is good

	# Open as an image
	im_cat_part = Image.open(fp_cat)

	if cat_part == "head":
		try: find_align_pixel(im_cat_part, HEAD_BODY_APX)
		except ValueError: return "head_body missing alignment pixel: " + str(HEAD_BODY_APX)

	if cat_part == "body":
		try: find_align_pixel(im_cat_part, HEAD_BODY_APX)
		except ValueError: return "body_head missing alignment pixel: " + str(HEAD_BODY_APX)
		try: find_align_pixel(im_cat_part, BODY_TAIL_APX)
		except ValueError: return "body_tail missing alignment pixel: " + str(BODY_TAIL_APX)

	if cat_part == "tail":
		try: find_align_pixel(im_cat_part, BODY_TAIL_APX)
		except ValueError: return "tail_body missing alignment pixel: " + str(BODY_TAIL_APX)

	return True

# Make the image smaller (remove extra space)
def bbox_crop_from_bytes(cat_part_bytes):

	# Open as an image
	im_cat_part = Image.open(cat_part_bytes)

	# Crop by bbox (remove later for more speed)
	return im_cat_part.crop(box=im_cat_part.getbbox())

# Compiles a cat from a head body and tail
def compile_cat(file_head, file_body, file_tail, bg_color=(240, 170, 240, 255)):

	# Defaults:
	FULL_SIZE = (1024, 1024)

	# Get im files
	im_head = Image.open(file_head)
	im_body = Image.open(file_body)
	im_tail = Image.open(file_tail)

	# Generate a canvas to lay images on (should be exes height and width)
	sum_width = im_head.width + im_body.width + im_tail.width
	sum_height = im_head.height + im_body.height + im_tail.height
	im_cat = Image.new("RGBA", (sum_width, sum_height), (0, 0, 0, 0))

	try: tail_body_px = find_align_pixel(im_tail, BODY_TAIL_APX)
	except ValueError: raise ValueError("tail_body missing alignment pixel: " + str(BODY_TAIL_APX))
	try: body_tail_px = find_align_pixel(im_body, BODY_TAIL_APX)
	except ValueError: raise ValueError("body_tail missing alignment pixel: " + str(BODY_TAIL_APX))
	try: body_head_px = find_align_pixel(im_body, HEAD_BODY_APX)
	except ValueError: raise ValueError("body_head missing alignment pixel: " + str(HEAD_BODY_APX))
	try: head_body_px = find_align_pixel(im_head, HEAD_BODY_APX)
	except ValueError: raise ValueError("head_body missing alignment pixel: " + str(HEAD_BODY_APX))

	# Remove the alignment pixels with black
	im_tail.putpixel(tail_body_px, (0, 0, 0, 255))
	im_body.putpixel(body_tail_px, (0, 0, 0, 255))
	im_body.putpixel(body_head_px, (0, 0, 0, 255))
	im_head.putpixel(head_body_px, (0, 0, 0, 255))

	# So that pasting doesn't go out of bounds
	canvas_offset = (im_cat.width//3, im_cat.height//3)
	# canvas_offset = (0, 0)

	tail_box = (body_tail_px[0] - tail_body_px[0] + canvas_offset[0], body_tail_px[1] - tail_body_px[1] + canvas_offset[1])
	body_box = (canvas_offset[0], canvas_offset[1])
	head_box = (body_head_px[0] - head_body_px[0] + canvas_offset[0], body_head_px[1] - head_body_px[1] + canvas_offset[1])

	#Image.alpha_composite(im, dest=0, 0, source=0, 0)
	im_cat.paste(im_tail, box=tail_box, mask=im_tail)
	im_cat.paste(im_body, box=body_box, mask=im_body)
	im_cat.paste(im_head, box=head_box, mask=im_head)

	# Bbox it Crop it
	im_cat = im_cat.crop(box=im_cat.getbbox())

	# Align it Center it
	cat_box = ((FULL_SIZE[0]-im_cat.width)//2, (FULL_SIZE[1]-im_cat.height)//2)

	# Put the real bg img
	bgim = Image.new("RGBA", FULL_SIZE, bg_color)

	# Combine
	bgim.paste(im_cat, box=cat_box, mask=im_cat)

	# Return the cat
	return bgim
