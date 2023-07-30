from PIL import Image, ImageGrab
import numpy as np
import os

NO_SHOW = False

clip = ImageGrab.grabclipboard().convert("RGB")
# clip.show()
cliparr = np.asarray(clip)
sz = cliparr.shape
# print(cliparr.dtype)
np.zeros((sz[0], sz[1], 4), dtype="uint8")
black = cliparr[0, 0, :]
delta = np.zeros((sz[0], sz[1], 4), dtype="uint8")
dims = [0, 0, sz[0], sz[1]]  # maxxy minxy
thresh = 10.0
for index, _ in np.ndenumerate(cliparr[:, :, 0]):
    col = cliparr[index]
    # print(col)
    dist = np.linalg.norm(col.astype("float")-black.astype("float"))
    # print(dist)
    alpha = 0
    if dist > thresh:
        dims[0] = max(index[0], dims[0])
        dims[1] = max(index[1], dims[1])
        dims[2] = min(index[0], dims[2])
        dims[3] = min(index[1], dims[3])
        alpha = 255
    delta[index[0], index[1], 0:3] = col
    delta[index[0], index[1], 3] = alpha

# Image.fromarray(delta).show()
# print(dims)

cut = delta[dims[2]:dims[0], dims[3]:dims[1], :]
if cut.shape[0] > cut.shape[1]:
    cut = np.rot90(cut,3)

stop = False
im = Image.fromarray(cut)
if not NO_SHOW:
    im.show()
while not stop:
    if not NO_SHOW:
        print(im.size)
    szi = input("Pixel size: ")
    sz = []
    if "," in szi:
        sz = [float(x)/im.size[k] for k, x in enumerate(szi.split(","))]
    else:
        sz = [float(szi) for _ in range(2)]
    im2 = im.resize(
        (round(im.size[0]/sz[0]), round(im.size[1]/sz[1])), Image.NEAREST)
    if not NO_SHOW:
        im2.show()
    stop = input("good? Y/N: ").lower() == "y"
imarr = np.asarray(im2)


path = r"C:\Users\natha\AppData\LocalLow\Nolla_Games_Noita\data"
exts = r"\items_gfx\wands"
extw = r"\scripts\gun\procedural\wands.lua"
image_db = []
files = os.listdir(path+exts)
minid = -1
mind = 2**32
for file in files:
    if file == "custom":
        continue
    image = Image.open(os.path.join(path+exts, file)
                       ).convert('RGBA').resize(im2.size)
    arr = np.asarray(image).astype("float")
    dist = np.linalg.norm(arr-imarr)
    # print(dist)
    if dist < mind:
        mind = dist
        minid = int(file[5:-4])
    # print(arr.shape)
    # print(image.mode)
strid = str(minid)
strid = "0"*(4-len(strid))+strid
print(strid)
if not NO_SHOW:
    Image.open(path+exts+"\wand_"+strid+".png").show()

with open(path+extw, "r") as file:
    content = file.read()

cmd = ("{"+"".join(
    content[content.find(strid):]
    .split("}")
    [0]
    .split("\n")
    [5:])
    .replace("=", "\":")
    .replace("  ", "\"")
    [:-1]
    .replace(" \"", "\"")
    + "}"
)
print(cmd)
data = eval(cmd)

data["fire_rate_wait"] = (data["fire_rate_wait"] + 1) * 7 - 5
data["actions_per_round"] = data["actions_per_round"] + 1
data["shuffle_deck_when_empty"] = data["shuffle_deck_when_empty"] == 1
data["deck_capacity"] = data["deck_capacity"] * 3 + 3
data["spread_degrees"] = (data["spread_degrees"] + 1) * 5 - 5
data["reload_time"] = (data["reload_time"] + 1) * 25 - 5
# data = {"fire_rate_wait ": 4,"actions_per_round ": 0,"shuffle_deck_when_empty ": 0,"deck_capacity ": 5,"spread_degrees": 1,"reload_time ": 1,}
# print(data)
cd = data["fire_rate_wait"]
sc = data["actions_per_round"]
sh = data["shuffle_deck_when_empty"]
sz = data["deck_capacity"]
sp = data["spread_degrees"]
rc = data["reload_time"]
print(f"""
Shuffle:        {"Yes" if sh else "No"}
Spells/Cast:    {sc:.0f}
Cast delay:     {cd / 60:.2f} s
Rechrg. Time:   {rc / 60:.2f} s
Capacity:       {sz:.0f}
Spread:         {sp:.1f} Deg
""")
