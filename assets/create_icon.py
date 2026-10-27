"""Deterministic, high-contrast white box-truck application icon."""
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parent
im=Image.new('RGBA',(512,512));d=ImageDraw.Draw(im)
d.rounded_rectangle((12,12,500,500),radius=108,fill='#164D43')
# Box, cab and chassis; broad shapes survive 16px tray rendering.
d.rounded_rectangle((68,125,310,335),radius=10,fill='white')
d.polygon([(324,192),(390,192),(444,253),(444,334),(324,334)],fill='white')
d.polygon([(342,209),(382,209),(418,252),(342,252)],fill='#70ABBE')
d.rounded_rectangle((62,322,453,352),radius=8,fill='#BBCED0')
d.rectangle((339,275,367,283),fill='#164D43')
d.rectangle((423,299,444,314),fill='#F2C86A')
for x in (144,376):
 d.ellipse((x-47,311,x+47,405),fill='#102D30')
 d.ellipse((x-24,334,x+24,382),fill='#E6F1F0')
 d.ellipse((x-10,348,x+10,368),fill='#688B8A')
im.save(root/'dispatch.png')
im.save(root/'dispatch.ico',sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(64,64),(128,128),(256,256)])
