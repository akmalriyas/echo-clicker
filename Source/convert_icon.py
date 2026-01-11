from PIL import Image
import os

img_path = r"C:/Users/akmal/.gemini/antigravity/brain/822f7a2a-16d8-433f-9924-c0a288529a1d/echo_clicker_icon_1768161255927.png"
out_path = r"f:/Python Projects/Echo Clicker/icon.ico"

img = Image.open(img_path)
img.save(out_path, format='ICO', sizes=[(256, 256)])
print(f"Icon saved to {out_path}")
