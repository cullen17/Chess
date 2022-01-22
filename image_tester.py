from PIL import Image
import numpy as np

inp = "C:/Users/culle/OneDrive/Desktop/Coding/Chess/Images/raw/"
out = "C:/Users/culle/OneDrive/Desktop/Coding/Chess/Images/"

light = (240, 229, 200)
dark = (120, 170, 120)

board = Image.open(out + "board.png")

for i in range(8):
	for j in range(8):
		if (i + j)%2 == 0:
			p = Image.open(out + "lwP.png")
		else:
			p = Image.open(out + "dwP.png")

		board.paste(p, (66+i*100, 66+j*100))
board.show()