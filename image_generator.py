from PIL import Image, ImageDraw, ImageFont

file_title = "A Doll's House"
font = ImageFont.truetype("static/ChunkFive-Regular.otf", 16)
history_thumbnail = Image.open("static/find text book bg.png")
drawer = ImageDraw.Draw(history_thumbnail)
w, h = drawer.textsize(file_title, font)
drawer.text(((300-w)/2, (300-h)/2), file_title, fill="black", font=font)

history_thumbnail.save(f"static/find_text_imgs/{file_title}.png")
