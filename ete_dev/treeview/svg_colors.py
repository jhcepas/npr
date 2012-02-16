import random
import colorsys

SVG_COLORS = set([
    "indianred", # 	CD5C5C 	2059292
    "lightcoral", # 	F08080 	240128128
    "salmon", # 	FA8072 	250128114
    "darksalmon", # 	E9967A 	233150122
    "lightsalmon", # 	FFA07A 	255160122
    "crimson", # 	DC143C 	2202060
    "red", # 	FF0000 	25500
    "firebrick", # 	B22222 	1783434
    "darkred", # 	8B0000 	13900
    "pink", # 	FFC0CB 	255192203
    "lightpink", # 	FFB6C1 	255182193
    "hotpink", # 	FF69B4 	255105180
    "deeppink", # 	FF1493 	25520147
    "mediumvioletred", # 	C71585 	19921133
    "palevioletred", # 	DB7093 	219112147
    "lightsalmon", # 	FFA07A 	255160122
    "coral", # 	FF7F50 	25512780
    "tomato", # 	FF6347 	2559971
    "orangered", # 	FF4500 	255690
    "darkorange", # 	FF8C00 	2551400
    "orange", # 	FFA500 	2551650
    "gold", # 	FFD700 	2552150
    "yellow", # 	FFFF00 	2552550
    "lightyellow", # 	FFFFE0 	255255224
    "lemonchiffon", # 	FFFACD 	255250205
    "lightgoldenrodyellow", # 	FAFAD2 	250250210
    "papayawhip", # 	FFEFD5 	255239213
    "moccasin", # 	FFE4B5 	255228181
    "peachpuff", # 	FFDAB9 	255218185
    "palegoldenrod", # 	EEE8AA 	238232170
    "khaki", # 	F0E68C 	240230140
    "darkkhaki", # 	BDB76B 	189183107
    "lavender", # 	E6E6FA 	230230250
    "thistle", # 	D8BFD8 	216191216
    "plum", # 	DDA0DD 	221160221
    "violet", # 	EE82EE 	238130238
    "orchid", # 	DA70D6 	218112214
    "fuchsia", # 	FF00FF 	2550255
    "magenta", # 	FF00FF 	2550255
    "mediumorchid", # 	BA55D3 	18685211
    "mediumpurple", # 	9370DB 	147112219
    "amethyst", # 	9966CC 	153102204
    "blueviolet", # 	8A2BE2 	13843226
    "darkviolet", # 	9400D3 	1480211
    "darkorchid", # 	9932CC 	15350204
    "darkmagenta", # 	8B008B 	1390139
    "purple", # 	800080 	1280128
    "indigo", # 	4B0082 	750130
    "slateblue", # 	6A5ACD 	10690205
    "darkslateblue", # 	483D8B 	7261139
    "mediumslateblue", # 	7B68EE 	123104238
    "greenyellow", # 	ADFF2F 	17325547
    "chartreuse", # 	7FFF00 	1272550
    "lawngreen", # 	7CFC00 	1242520
    "lime", # 	00FF00 	02550
    "limegreen", # 	32CD32 	5020550
    "palegreen", # 	98FB98 	152251152
    "lightgreen", # 	90EE90 	144238144
    "mediumspringgreen", # 	00FA9A 	0250154
    "springgreen", # 	00FF7F 	0255127
    "mediumseagreen", # 	3CB371 	60179113
    "seagreen", # 	2E8B57 	4613987
    "forestgreen", # 	228B22 	3413934
    "green", # 	008000 	01280
    "darkgreen", # 	006400 	01000
    "yellowgreen", # 	9ACD32 	15420550
    "olivedrab", # 	6B8E23 	10714235
    "olive", # 	808000 	1281280
    "darkolivegreen", # 	556B2F 	8510747
    "mediumaquamarine", # 	66CDAA 	102205170
    "darkseagreen", # 	8FBC8F 	143188143
    "lightseagreen", # 	20B2AA 	32178170
    "darkcyan", # 	008B8B 	0139139
    "teal", # 	008080 	0128128
    "aqua", # 	00FFFF 	0255255
    "cyan", # 	00FFFF 	0255255
    "lightcyan", # 	E0FFFF 	224255255
    "paleturquoise", # 	AFEEEE 	175238238
    "aquamarine", # 	7FFFD4 	127255212
    "turquoise", # 	40E0D0 	64224208
    "mediumturquoise", # 	48D1CC 	72209204
    "darkturquoise", # 	00CED1 	0206209
    "cadetblue", # 	5F9EA0 	95158160
    "steelblue", # 	4682B4 	70130180
    "lightsteelblue", # 	B0C4DE 	176196222
    "powderblue", # 	B0E0E6 	176224230
    "lightblue", # 	ADD8E6 	173216230
    "skyblue", # 	87CEEB 	135206235
    "lightskyblue", # 	87CEFA 	135206250
    "deepskyblue", # 	00BFFF 	0191255
    "dodgerblue", # 	1E90FF 	30144255
    "cornflowerblue", # 	6495ED 	100149237
    "mediumslateblue", # 	7B68EE 	123104238
    "royalblue", # 	4169E1 	65105225
    "blue", # 	0000FF 	00255
    "mediumblue", # 	0000CD 	00205
    "darkblue", # 	00008B 	00139
    "navy", # 	000080 	00128
    "midnightblue", # 	191970 	2525112
    "cornsilk", # 	FFF8DC 	255248220
    "blanchedalmond", # 	FFEBCD 	255235205
    "bisque", # 	FFE4C4 	255228196
    "navajowhite", # 	FFDEAD 	255222173
    "wheat", # 	F5DEB3 	245222179
    "burlywood", # 	DEB887 	222184135
    "tan", # 	D2B48C 	210180140
    "rosybrown", # 	BC8F8F 	188143143
    "sandybrown", # 	F4A460 	24416496
    "goldenrod", # 	DAA520 	21816532
    "darkgoldenrod", # 	B8860B 	18413411
    "peru", # 	CD853F 	20513363
    "chocolate", # 	D2691E 	21010530
    "saddlebrown", # 	8B4513 	1396919
    "sienna", # 	A0522D 	1608245
    "brown", # 	A52A2A 	1654242
    "maroon", # 	800000 	12800
    "white", # 	FFFFFF 	255255255
    "snow", # 	FFFAFA 	255250250
    "honeydew", # 	F0FFF0 	240255240
    "mintcream", # 	F5FFFA 	245255250
    "azure", # 	F0FFFF 	240255255
    "aliceblue", # 	F0F8FF 	240248255
    "ghostwhite", # 	F8F8FF 	248248255
    "whitesmoke", # 	F5F5F5 	245245245
    "seashell", # 	FFF5EE 	255245238
    "beige", # 	F5F5DC 	245245220
    "oldlace", # 	FDF5E6 	253245230
    "floralwhite", # 	FFFAF0 	255250240
    "ivory", # 	FFFFF0 	255255240
    "antiquewhite", # 	FAEBD7 	250235215
    "linen", # 	FAF0E6 	250240230
    "lavenderblush", # 	FFF0F5 	255240245
    "mistyrose", # 	FFE4E1 	255228225
    "gainsboro", # 	DCDCDC 	220220220
    "lightgrey", # 	D3D3D3 	211211211
    "silver", # 	C0C0C0 	192192192
    "darkgray", # 	A9A9A9 	169169169
    "gray", # 	808080 	128128128
    "dimgray", # 	696969 	105105105
    "lightslategray", # 	778899 	119136153
    "slategray", # 	708090 	112128144
    "darkslategray", # 	2F4F4F 	477979
    "black"] ) # 	000000 	000

def random_color(h=None, l=None, s=None):
    def rgb2hex(rgb):
        return '#%02x%02x%02x' % rgb
    def hls2hex(h, l, s):
        return rgb2hex( tuple(map(lambda x: int(x*255), colorsys.hls_to_rgb(h, l, s))))

    if not h:
        h = random.random()
    if not s: 
        s = 0.5
    if not l:
        l = 0.5
    return hls2hex(h, l, s)


