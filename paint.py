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

	try: tail_body_px = find_align_pixel(im_tail, BODY_TAIL_APX)
	except ValueError: raise ValueError("tail_body missing alignment pixel: " + str(BODY_TAIL_APX))
	try: body_tail_px = find_align_pixel(im_body, BODY_TAIL_APX)
	except ValueError: raise ValueError("body_tail missing alignment pixel: " + str(BODY_TAIL_APX))
	try: body_head_px = find_align_pixel(im_body, HEAD_BODY_APX)
	except ValueError: raise ValueError("body_head missing alignment pixel: " + str(HEAD_BODY_APX))
	try: head_body_px = find_align_pixel(im_head, HEAD_BODY_APX)
	except ValueError: raise ValueError("head_body missing alignment pixel: " + str(HEAD_BODY_APX))

	# Remove the alignment pixels with black
	# im_tail.putpixel(tail_body_px, (0, 0, 0, 255))
	# im_body.putpixel(body_tail_px, (0, 0, 0, 255))
	# im_body.putpixel(body_head_px, (0, 0, 0, 255))
	# im_head.putpixel(head_body_px, (0, 0, 0, 255))

	# With top left pixel
	im_tail.putpixel(tail_body_px, im_tail.getpixel((tail_body_px[0]+1, tail_body_px[1]+1)))
	im_body.putpixel(body_tail_px, im_body.getpixel((body_tail_px[0]+1, body_tail_px[1]+1)))
	im_body.putpixel(body_head_px, im_body.getpixel((body_head_px[0]+1, body_head_px[1]+1)))
	im_head.putpixel(head_body_px, im_head.getpixel((head_body_px[0]+1, head_body_px[1]+1)))

	# Find the exact canvas size and where each box is (top left most pixel)

	def align_parts(head_len, head_p, body_len, body_p1, body_p2, tail_len, tail_p):
		# Use body as the referance point and shift head and tail to align with pixel
		# x_len = length, x_p = point 1D, x_d = delta, p1 = body_head, p2 = body_tail
		head_d = body_p1 - head_p
		tail_d = body_p2 - tail_p

		# Find the new locations of the x1 and x2... (can be negative)
		x1 = head_d
		x2 = x1 + head_len

		z1 = tail_d
		z2 = z1 + tail_len

		# Find the offset (values that go negative)
		# Since we anchor on body it will be 0 at the lowest value
		offset = -min(x1, 0, z1)

		# Find the biggest size
		maximum = max(x2, body_len, z2)

		# Return the cords max_value head_align body_align tail_align
		return (offset+maximum, offset+x1, offset, offset+z1)

	# Get offsets
	offsets_x = align_parts(im_head.width, head_body_px[0], im_body.width, body_head_px[0], body_tail_px[0], im_tail.width, tail_body_px[0])
	offsets_y = align_parts(im_head.height, head_body_px[1], im_body.height, body_head_px[1], body_tail_px[1], im_tail.height, tail_body_px[1])

	# Generate a canvas to lay images on
	im_cat = Image.new("RGBA", (offsets_x[0], offsets_y[0]), (0, 0, 0, 0))

	head_box = (offsets_x[1], offsets_y[1])
	body_box = (offsets_x[2], offsets_y[2])
	tail_box = (offsets_x[3], offsets_y[3])

	#Image.alpha_composite(im, dest=0, 0, source=0, 0)
	im_cat.paste(im_tail, box=tail_box, mask=im_tail)
	im_cat.paste(im_body, box=body_box, mask=im_body)
	im_cat.paste(im_head, box=head_box, mask=im_head)

	# Bbox it Crop it (remove in the future since all inputs are bboxed already)
	im_cat = im_cat.crop(box=im_cat.getbbox())

	# Align it Center it
	cat_box = ((FULL_SIZE[0]-im_cat.width)//2, (FULL_SIZE[1]-im_cat.height)//2)

	# Put the real bg img
	bgim = Image.new("RGBA", FULL_SIZE, bg_color)

	# Combine
	bgim.paste(im_cat, box=cat_box, mask=im_cat)

	# Return the cat
	return bgim
