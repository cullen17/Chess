from PIL import Image
import numpy as np


inp = "C:/Users/culle/OneDrive/Desktop/Coding/Chess/Images/raw/"
out = "C:/Users/culle/OneDrive/Desktop/Coding/Chess/Images/"

light = (240, 229, 200)
dark = (120, 170, 120)

images = ["bP", "bR", "bN", "bB", "bQ", "bK", "wP", "wR", "wN", "wB", "wQ", "wK"]

for img in images:

	im = Image.open(inp + img + ".jpg")


	im = im.convert('RGBA')
	data = np.array(im) 
	red, green, blue, alpha = data.T 

	
	min_v = 150
	max_v = 245

	if img == 'wK':
		max_v = 210

	b = []
	for i in range(len(red)):
		b.append([])
		for j in range(len(red[i])):
			b[i].append([])
			if (red[i][j] >= min_v and red[i][j] <= max_v):
				b[i][j] = True
			else:
				b[i][j] = False

	background = np.asarray(b)

	data[..., :-1][background.T] = light # Transpose back needed

	new_im = Image.fromarray(data)
	new_im = new_im.resize((100,100))

	print("saving l" + img + ".png")
	new_im.save(out + "l" + img + ".png")

	data[..., :-1][background.T] = dark # Transpose back needed

	new_im = Image.fromarray(data)
	new_im = new_im.resize((100,100))

	print("saving d" + img + ".png")
	new_im.save(out + "d" + img + ".png")


#empty light tile
im = Image.open(inp + "bP.jpg")

im = im.convert('RGBA')
data = np.array(im)

for i in range(len(data)):
	for j in range(len(data[i])):
		data[i][j] = [240, 229, 200, 255]

new_im = Image.fromarray(data)
new_im = new_im.resize((100,100))
	
print("saving l0.png")
new_im.save(out + "l0.png")

#empty dark tile
im = Image.open(inp + "bP.jpg")

im = im.convert('RGBA')
data = np.array(im)

for i in range(len(data)):
	for j in range(len(data[i])):
		data[i][j] = [120, 170, 120, 255]

new_im = Image.fromarray(data)
new_im = new_im.resize((100,100))
	
print("saving d0.png")
new_im.save(out + "d0.png")

