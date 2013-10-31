import random
import colorsys

all = ["SVG_COLORS", "COLOR_SCHEMES", "random_color"]

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

# http://colorbrewer2.org/
#schemas = {'Spectral': {3: [(252, 141, 89), (255, 255, 191), (153, 213, 148)], 4: [(215, 25, 28), (253, 174, 97), (171, 221, 164), (43, 131, 186)], 5: [(215, 25, 28), (253, 174, 97), (255, 255, 191), (171, 221, 164), (43, 131, 186)], 6: [(213, 62, 79), (252, 141, 89), (254, 224, 139), (230, 245, 152), (153, 213, 148), (50, 136, 189)], 7: [(213, 62, 79), (252, 141, 89), (254, 224, 139), (255, 255, 191), (230, 245, 152), (153, 213, 148), (50, 136, 189)], 8: [(213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189)], 9: [(213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189)], 10: [(158, 1, 66), (213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189), (94, 79, 162)], 11: [(158, 1, 66), (213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189), (94, 79, 162)]}, 'RdYlGn': {3: [(252, 141, 89), (255, 255, 191), (145, 207, 96)], 4: [(215, 25, 28), (253, 174, 97), (166, 217, 106), (26, 150, 65)], 5: [(215, 25, 28), (253, 174, 97), (255, 255, 191), (166, 217, 106), (26, 150, 65)], 6: [(215, 48, 39), (252, 141, 89), (254, 224, 139), (217, 239, 139), (145, 207, 96), (26, 152, 80)], 7: [(215, 48, 39), (252, 141, 89), (254, 224, 139), (255, 255, 191), (217, 239, 139), (145, 207, 96), (26, 152, 80)], 8: [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80)], 9: [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80)], 10: [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80), (0, 104, 55)], 11: [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80), (0, 104, 55)]}, 'Set2': {3: [(102, 194, 165), (252, 141, 98), (141, 160, 203)], 4: [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195)], 5: [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84)], 6: [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47)], 7: [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47), (229, 196, 148)], 8: [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47), (229, 196, 148), (179, 179, 179)]}, 'Accent': {3: [(127, 201, 127), (190, 174, 212), (253, 192, 134)], 4: [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153)], 5: [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176)], 6: [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127)], 7: [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127), (191, 91, 23)], 8: [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127), (191, 91, 23), (102, 102, 102)]}, 'OrRd': {3: [(254, 232, 200), (253, 187, 132), (227, 74, 51)], 4: [(254, 240, 217), (253, 204, 138), (252, 141, 89), (215, 48, 31)], 5: [(254, 240, 217), (253, 204, 138), (252, 141, 89), (227, 74, 51), (179, 0, 0)], 6: [(254, 240, 217), (253, 212, 158), (253, 187, 132), (252, 141, 89), (227, 74, 51), (179, 0, 0)], 7: [(254, 240, 217), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (153, 0, 0)], 8: [(255, 247, 236), (254, 232, 200), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (153, 0, 0)], 9: [(255, 247, 236), (254, 232, 200), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (179, 0, 0), (127, 0, 0)]}, 'Set1': {3: [(228, 26, 28), (55, 126, 184), (77, 175, 74)], 4: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163)], 5: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0)], 6: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51)], 7: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40)], 8: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40), (247, 129, 191)], 9: [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40), (247, 129, 191), (153, 153, 153)]}, 'PuBu': {3: [(236, 231, 242), (166, 189, 219), (43, 140, 190)], 4: [(241, 238, 246), (189, 201, 225), (116, 169, 207), (5, 112, 176)], 5: [(241, 238, 246), (189, 201, 225), (116, 169, 207), (43, 140, 190), (4, 90, 141)], 6: [(241, 238, 246), (208, 209, 230), (166, 189, 219), (116, 169, 207), (43, 140, 190), (4, 90, 141)], 7: [(241, 238, 246), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (3, 78, 123)], 8: [(255, 247, 251), (236, 231, 242), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (3, 78, 123)], 9: [(255, 247, 251), (236, 231, 242), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (4, 90, 141), (2, 56, 88)]}, 'Set3': {3: [(141, 211, 199), (255, 255, 179), (190, 186, 218)], 4: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114)], 5: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211)], 6: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98)], 7: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105)], 8: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229)], 9: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217)], 10: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189)], 11: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189), (204, 235, 197)], 12: [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189), (204, 235, 197), (255, 237, 111)]}, 'BuPu': {3: [(224, 236, 244), (158, 188, 218), (136, 86, 167)], 4: [(237, 248, 251), (179, 205, 227), (140, 150, 198), (136, 65, 157)], 5: [(237, 248, 251), (179, 205, 227), (140, 150, 198), (136, 86, 167), (129, 15, 124)], 6: [(237, 248, 251), (191, 211, 230), (158, 188, 218), (140, 150, 198), (136, 86, 167), (129, 15, 124)], 7: [(237, 248, 251), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (110, 1, 107)], 8: [(247, 252, 253), (224, 236, 244), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (110, 1, 107)], 9: [(247, 252, 253), (224, 236, 244), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (129, 15, 124), (77, 0, 75)]}, 'Dark2': {3: [(27, 158, 119), (217, 95, 2), (117, 112, 179)], 4: [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138)], 5: [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30)], 6: [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2)], 7: [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2), (166, 118, 29)], 8: [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2), (166, 118, 29), (102, 102, 102)]}, 'RdBu': {3: [(239, 138, 98), (247, 247, 247), (103, 169, 207)], 4: [(202, 0, 32), (244, 165, 130), (146, 197, 222), (5, 113, 176)], 5: [(202, 0, 32), (244, 165, 130), (247, 247, 247), (146, 197, 222), (5, 113, 176)], 6: [(178, 24, 43), (239, 138, 98), (253, 219, 199), (209, 229, 240), (103, 169, 207), (33, 102, 172)], 7: [(178, 24, 43), (239, 138, 98), (253, 219, 199), (247, 247, 247), (209, 229, 240), (103, 169, 207), (33, 102, 172)], 8: [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172)], 9: [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (247, 247, 247), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172)], 10: [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172), (5, 48, 97)], 11: [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (247, 247, 247), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172), (5, 48, 97)]}, 'Oranges': {3: [(254, 230, 206), (253, 174, 107), (230, 85, 13)], 4: [(254, 237, 222), (253, 190, 133), (253, 141, 60), (217, 71, 1)], 5: [(254, 237, 222), (253, 190, 133), (253, 141, 60), (230, 85, 13), (166, 54, 3)], 6: [(254, 237, 222), (253, 208, 162), (253, 174, 107), (253, 141, 60), (230, 85, 13), (166, 54, 3)], 7: [(254, 237, 222), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (140, 45, 4)], 8: [(255, 245, 235), (254, 230, 206), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (140, 45, 4)], 9: [(255, 245, 235), (254, 230, 206), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (166, 54, 3), (127, 39, 4)]}, 'BuGn': {3: [(229, 245, 249), (153, 216, 201), (44, 162, 95)], 4: [(237, 248, 251), (178, 226, 226), (102, 194, 164), (35, 139, 69)], 5: [(237, 248, 251), (178, 226, 226), (102, 194, 164), (44, 162, 95), (0, 109, 44)], 6: [(237, 248, 251), (204, 236, 230), (153, 216, 201), (102, 194, 164), (44, 162, 95), (0, 109, 44)], 7: [(237, 248, 251), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 88, 36)], 8: [(247, 252, 253), (229, 245, 249), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 88, 36)], 9: [(247, 252, 253), (229, 245, 249), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 109, 44), (0, 68, 27)]}, 'PiYG': {3: [(233, 163, 201), (247, 247, 247), (161, 215, 106)], 4: [(208, 28, 139), (241, 182, 218), (184, 225, 134), (77, 172, 38)], 5: [(208, 28, 139), (241, 182, 218), (247, 247, 247), (184, 225, 134), (77, 172, 38)], 6: [(197, 27, 125), (233, 163, 201), (253, 224, 239), (230, 245, 208), (161, 215, 106), (77, 146, 33)], 7: [(197, 27, 125), (233, 163, 201), (253, 224, 239), (247, 247, 247), (230, 245, 208), (161, 215, 106), (77, 146, 33)], 8: [(197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33)], 9: [(197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (247, 247, 247), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33)], 10: [(142, 1, 82), (197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33), (39, 100, 25)], 11: [(142, 1, 82), (197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (247, 247, 247), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33), (39, 100, 25)]}, 'YlOrBr': {3: [(255, 247, 188), (254, 196, 79), (217, 95, 14)], 4: [(255, 255, 212), (254, 217, 142), (254, 153, 41), (204, 76, 2)], 5: [(255, 255, 212), (254, 217, 142), (254, 153, 41), (217, 95, 14), (153, 52, 4)], 6: [(255, 255, 212), (254, 227, 145), (254, 196, 79), (254, 153, 41), (217, 95, 14), (153, 52, 4)], 7: [(255, 255, 212), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (140, 45, 4)], 8: [(255, 255, 229), (255, 247, 188), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (140, 45, 4)], 9: [(255, 255, 229), (255, 247, 188), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (153, 52, 4), (102, 37, 6)]}, 'YlGn': {3: [(247, 252, 185), (173, 221, 142), (49, 163, 84)], 4: [(255, 255, 204), (194, 230, 153), (120, 198, 121), (35, 132, 67)], 5: [(255, 255, 204), (194, 230, 153), (120, 198, 121), (49, 163, 84), (0, 104, 55)], 6: [(255, 255, 204), (217, 240, 163), (173, 221, 142), (120, 198, 121), (49, 163, 84), (0, 104, 55)], 7: [(255, 255, 204), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 90, 50)], 8: [(255, 255, 229), (247, 252, 185), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 90, 50)], 9: [(255, 255, 229), (247, 252, 185), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 104, 55), (0, 69, 41)]}, 'Reds': {3: [(254, 224, 210), (252, 146, 114), (222, 45, 38)], 4: [(254, 229, 217), (252, 174, 145), (251, 106, 74), (203, 24, 29)], 5: [(254, 229, 217), (252, 174, 145), (251, 106, 74), (222, 45, 38), (165, 15, 21)], 6: [(254, 229, 217), (252, 187, 161), (252, 146, 114), (251, 106, 74), (222, 45, 38), (165, 15, 21)], 7: [(254, 229, 217), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (153, 0, 13)], 8: [(255, 245, 240), (254, 224, 210), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (153, 0, 13)], 9: [(255, 245, 240), (254, 224, 210), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (165, 15, 21), (103, 0, 13)]}, 'RdPu': {3: [(253, 224, 221), (250, 159, 181), (197, 27, 138)], 4: [(254, 235, 226), (251, 180, 185), (247, 104, 161), (174, 1, 126)], 5: [(254, 235, 226), (251, 180, 185), (247, 104, 161), (197, 27, 138), (122, 1, 119)], 6: [(254, 235, 226), (252, 197, 192), (250, 159, 181), (247, 104, 161), (197, 27, 138), (122, 1, 119)], 7: [(254, 235, 226), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119)], 8: [(255, 247, 243), (253, 224, 221), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119)], 9: [(255, 247, 243), (253, 224, 221), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119), (73, 0, 106)]}, 'Greens': {3: [(229, 245, 224), (161, 217, 155), (49, 163, 84)], 4: [(237, 248, 233), (186, 228, 179), (116, 196, 118), (35, 139, 69)], 5: [(237, 248, 233), (186, 228, 179), (116, 196, 118), (49, 163, 84), (0, 109, 44)], 6: [(237, 248, 233), (199, 233, 192), (161, 217, 155), (116, 196, 118), (49, 163, 84), (0, 109, 44)], 7: [(237, 248, 233), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 90, 50)], 8: [(247, 252, 245), (229, 245, 224), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 90, 50)], 9: [(247, 252, 245), (229, 245, 224), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 109, 44), (0, 68, 27)]}, 'PRGn': {3: [(175, 141, 195), (247, 247, 247), (127, 191, 123)], 4: [(123, 50, 148), (194, 165, 207), (166, 219, 160), (0, 136, 55)], 5: [(123, 50, 148), (194, 165, 207), (247, 247, 247), (166, 219, 160), (0, 136, 55)], 6: [(118, 42, 131), (175, 141, 195), (231, 212, 232), (217, 240, 211), (127, 191, 123), (27, 120, 55)], 7: [(118, 42, 131), (175, 141, 195), (231, 212, 232), (247, 247, 247), (217, 240, 211), (127, 191, 123), (27, 120, 55)], 8: [(118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55)], 9: [(118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (247, 247, 247), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55)], 10: [(64, 0, 75), (118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55), (0, 68, 27)], 11: [(64, 0, 75), (118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (247, 247, 247), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55), (0, 68, 27)]}, 'YlGnBu': {3: [(237, 248, 177), (127, 205, 187), (44, 127, 184)], 4: [(255, 255, 204), (161, 218, 180), (65, 182, 196), (34, 94, 168)], 5: [(255, 255, 204), (161, 218, 180), (65, 182, 196), (44, 127, 184), (37, 52, 148)], 6: [(255, 255, 204), (199, 233, 180), (127, 205, 187), (65, 182, 196), (44, 127, 184), (37, 52, 148)], 7: [(255, 255, 204), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (12, 44, 132)], 8: [(255, 255, 217), (237, 248, 177), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (12, 44, 132)], 9: [(255, 255, 217), (237, 248, 177), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (37, 52, 148), (8, 29, 88)]}, 'RdYlBu': {3: [(252, 141, 89), (255, 255, 191), (145, 191, 219)], 4: [(215, 25, 28), (253, 174, 97), (171, 217, 233), (44, 123, 182)], 5: [(215, 25, 28), (253, 174, 97), (255, 255, 191), (171, 217, 233), (44, 123, 182)], 6: [(215, 48, 39), (252, 141, 89), (254, 224, 144), (224, 243, 248), (145, 191, 219), (69, 117, 180)], 7: [(215, 48, 39), (252, 141, 89), (254, 224, 144), (255, 255, 191), (224, 243, 248), (145, 191, 219), (69, 117, 180)], 8: [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180)], 9: [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (255, 255, 191), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180)], 10: [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180), (49, 54, 149)], 11: [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (255, 255, 191), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180), (49, 54, 149)]}, 'Paired': {3: [(166, 206, 227), (31, 120, 180), (178, 223, 138)], 4: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44)], 5: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153)], 6: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28)], 7: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111)], 8: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0)], 9: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214)], 10: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154)], 11: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154), (255, 255, 153)], 12: [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154), (255, 255, 153), (177, 89, 40)]}, 'BrBG': {3: [(216, 179, 101), (245, 245, 245), (90, 180, 172)], 4: [(166, 97, 26), (223, 194, 125), (128, 205, 193), (1, 133, 113)], 5: [(166, 97, 26), (223, 194, 125), (245, 245, 245), (128, 205, 193), (1, 133, 113)], 6: [(140, 81, 10), (216, 179, 101), (246, 232, 195), (199, 234, 229), (90, 180, 172), (1, 102, 94)], 7: [(140, 81, 10), (216, 179, 101), (246, 232, 195), (245, 245, 245), (199, 234, 229), (90, 180, 172), (1, 102, 94)], 8: [(140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94)], 9: [(140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (245, 245, 245), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94)], 10: [(84, 48, 5), (140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94), (0, 60, 48)], 11: [(84, 48, 5), (140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (245, 245, 245), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94), (0, 60, 48)]}, 'Purples': {3: [(239, 237, 245), (188, 189, 220), (117, 107, 177)], 4: [(242, 240, 247), (203, 201, 226), (158, 154, 200), (106, 81, 163)], 5: [(242, 240, 247), (203, 201, 226), (158, 154, 200), (117, 107, 177), (84, 39, 143)], 6: [(242, 240, 247), (218, 218, 235), (188, 189, 220), (158, 154, 200), (117, 107, 177), (84, 39, 143)], 7: [(242, 240, 247), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (74, 20, 134)], 8: [(252, 251, 253), (239, 237, 245), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (74, 20, 134)], 9: [(252, 251, 253), (239, 237, 245), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (84, 39, 143), (63, 0, 125)]}, 'Pastel2': {3: [(179, 226, 205), (253, 205, 172), (203, 213, 232)], 4: [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228)], 5: [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201)], 6: [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174)], 7: [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174), (241, 226, 204)], 8: [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174), (241, 226, 204), (204, 204, 204)]}, 'Pastel1': {3: [(251, 180, 174), (179, 205, 227), (204, 235, 197)], 4: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228)], 5: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166)], 6: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204)], 7: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189)], 8: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189), (253, 218, 236)], 9: [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189), (253, 218, 236), (242, 242, 242)]}, 'GnBu': {3: [(224, 243, 219), (168, 221, 181), (67, 162, 202)], 4: [(240, 249, 232), (186, 228, 188), (123, 204, 196), (43, 140, 190)], 5: [(240, 249, 232), (186, 228, 188), (123, 204, 196), (67, 162, 202), (8, 104, 172)], 6: [(240, 249, 232), (204, 235, 197), (168, 221, 181), (123, 204, 196), (67, 162, 202), (8, 104, 172)], 7: [(240, 249, 232), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 88, 158)], 8: [(247, 252, 240), (224, 243, 219), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 88, 158)], 9: [(247, 252, 240), (224, 243, 219), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 104, 172), (8, 64, 129)]}, 'Greys': {3: [(240, 240, 240), (189, 189, 189), (99, 99, 99)], 4: [(247, 247, 247), (204, 204, 204), (150, 150, 150), (82, 82, 82)], 5: [(247, 247, 247), (204, 204, 204), (150, 150, 150), (99, 99, 99), (37, 37, 37)], 6: [(247, 247, 247), (217, 217, 217), (189, 189, 189), (150, 150, 150), (99, 99, 99), (37, 37, 37)], 7: [(247, 247, 247), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37)], 8: [(255, 255, 255), (240, 240, 240), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37)], 9: [(255, 255, 255), (240, 240, 240), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37), (0, 0, 0)]}, 'RdGy': {3: [(239, 138, 98), (255, 255, 255), (153, 153, 153)], 4: [(202, 0, 32), (244, 165, 130), (186, 186, 186), (64, 64, 64)], 5: [(202, 0, 32), (244, 165, 130), (255, 255, 255), (186, 186, 186), (64, 64, 64)], 6: [(178, 24, 43), (239, 138, 98), (253, 219, 199), (224, 224, 224), (153, 153, 153), (77, 77, 77)], 7: [(178, 24, 43), (239, 138, 98), (253, 219, 199), (255, 255, 255), (224, 224, 224), (153, 153, 153), (77, 77, 77)], 8: [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77)], 9: [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (255, 255, 255), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77)], 10: [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77), (26, 26, 26)], 11: [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (255, 255, 255), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77), (26, 26, 26)]}, 'YlOrRd': {3: [(255, 237, 160), (254, 178, 76), (240, 59, 32)], 4: [(255, 255, 178), (254, 204, 92), (253, 141, 60), (227, 26, 28)], 5: [(255, 255, 178), (254, 204, 92), (253, 141, 60), (240, 59, 32), (189, 0, 38)], 6: [(255, 255, 178), (254, 217, 118), (254, 178, 76), (253, 141, 60), (240, 59, 32), (189, 0, 38)], 7: [(255, 255, 178), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (177, 0, 38)], 8: [(255, 255, 204), (255, 237, 160), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (177, 0, 38)], 9: [(255, 255, 204), (255, 237, 160), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (189, 0, 38), (128, 0, 38)]}, 'PuOr': {3: [(241, 163, 64), (247, 247, 247), (153, 142, 195)], 4: [(230, 97, 1), (253, 184, 99), (178, 171, 210), (94, 60, 153)], 5: [(230, 97, 1), (253, 184, 99), (247, 247, 247), (178, 171, 210), (94, 60, 153)], 6: [(179, 88, 6), (241, 163, 64), (254, 224, 182), (216, 218, 235), (153, 142, 195), (84, 39, 136)], 7: [(179, 88, 6), (241, 163, 64), (254, 224, 182), (247, 247, 247), (216, 218, 235), (153, 142, 195), (84, 39, 136)], 8: [(179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136)], 9: [(179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (247, 247, 247), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136)], 10: [(127, 59, 8), (179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136), (45, 0, 75)], 11: [(127, 59, 8), (179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (247, 247, 247), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136), (45, 0, 75)]}, 'PuRd': {3: [(231, 225, 239), (201, 148, 199), (221, 28, 119)], 4: [(241, 238, 246), (215, 181, 216), (223, 101, 176), (206, 18, 86)], 5: [(241, 238, 246), (215, 181, 216), (223, 101, 176), (221, 28, 119), (152, 0, 67)], 6: [(241, 238, 246), (212, 185, 218), (201, 148, 199), (223, 101, 176), (221, 28, 119), (152, 0, 67)], 7: [(241, 238, 246), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (145, 0, 63)], 8: [(247, 244, 249), (231, 225, 239), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (145, 0, 63)], 9: [(247, 244, 249), (231, 225, 239), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (152, 0, 67), (103, 0, 31)]}, 'Blues': {3: [(222, 235, 247), (158, 202, 225), (49, 130, 189)], 4: [(239, 243, 255), (189, 215, 231), (107, 174, 214), (33, 113, 181)], 5: [(239, 243, 255), (189, 215, 231), (107, 174, 214), (49, 130, 189), (8, 81, 156)], 6: [(239, 243, 255), (198, 219, 239), (158, 202, 225), (107, 174, 214), (49, 130, 189), (8, 81, 156)], 7: [(239, 243, 255), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 69, 148)], 8: [(247, 251, 255), (222, 235, 247), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 69, 148)], 9: [(247, 251, 255), (222, 235, 247), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 81, 156), (8, 48, 107)]}, 'PuBuGn': {3: [(236, 226, 240), (166, 189, 219), (28, 144, 153)], 4: [(246, 239, 247), (189, 201, 225), (103, 169, 207), (2, 129, 138)], 5: [(246, 239, 247), (189, 201, 225), (103, 169, 207), (28, 144, 153), (1, 108, 89)], 6: [(246, 239, 247), (208, 209, 230), (166, 189, 219), (103, 169, 207), (28, 144, 153), (1, 108, 89)], 7: [(246, 239, 247), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 100, 80)], 8: [(255, 247, 251), (236, 226, 240), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 100, 80)], 9: [(255, 247, 251), (236, 226, 240), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 108, 89), (1, 70, 54)]}}
COLOR_SCHEMES = {'accent': ['#7fc97f',
  '#beaed4',
  '#fdc086',
  '#ffff99',
  '#386cb0',
  '#f0027f',
  '#bf5b17',
  '#666666'],
 'blues': ['#f7fbff',
  '#deebf7',
  '#c6dbef',
  '#9ecae1',
  '#6baed6',
  '#4292c6',
  '#2171b5',
  '#08519c',
  '#08306b'],
 'brbg': ['#543005',
  '#8c510a',
  '#bf812d',
  '#dfc27d',
  '#f6e8c3',
  '#f5f5f5',
  '#c7eae5',
  '#80cdc1',
  '#35978f',
  '#01665e',
  '#003c30'],
 'bugn': ['#f7fcfd',
  '#e5f5f9',
  '#ccece6',
  '#99d8c9',
  '#66c2a4',
  '#41ae76',
  '#238b45',
  '#006d2c',
  '#00441b'],
 'bupu': ['#f7fcfd',
  '#e0ecf4',
  '#bfd3e6',
  '#9ebcda',
  '#8c96c6',
  '#8c6bb1',
  '#88419d',
  '#810f7c',
  '#4d004b'],
 'dark2': ['#1b9e77',
  '#d95f02',
  '#7570b3',
  '#e7298a',
  '#66a61e',
  '#e6ab02',
  '#a6761d',
  '#666666'],
 'gnbu': ['#f7fcf0',
  '#e0f3db',
  '#ccebc5',
  '#a8ddb5',
  '#7bccc4',
  '#4eb3d3',
  '#2b8cbe',
  '#0868ac',
  '#084081'],
 'greens': ['#f7fcf5',
  '#e5f5e0',
  '#c7e9c0',
  '#a1d99b',
  '#74c476',
  '#41ab5d',
  '#238b45',
  '#006d2c',
  '#00441b'],
 'greys': ['#ffffff',
  '#f0f0f0',
  '#d9d9d9',
  '#bdbdbd',
  '#969696',
  '#737373',
  '#525252',
  '#252525',
  '#000000'],
 'orrd': ['#fff7ec',
  '#fee8c8',
  '#fdd49e',
  '#fdbb84',
  '#fc8d59',
  '#ef6548',
  '#d7301f',
  '#b30000',
  '#7f0000'],
 'oranges': ['#fff5eb',
  '#fee6ce',
  '#fdd0a2',
  '#fdae6b',
  '#fd8d3c',
  '#f16913',
  '#d94801',
  '#a63603',
  '#7f2704'],
 'prgn': ['#40004b',
  '#762a83',
  '#9970ab',
  '#c2a5cf',
  '#e7d4e8',
  '#f7f7f7',
  '#d9f0d3',
  '#a6dba0',
  '#5aae61',
  '#1b7837',
  '#00441b'],
 'paired': ['#a6cee3',
  '#1f78b4',
  '#b2df8a',
  '#33a02c',
  '#fb9a99',
  '#e31a1c',
  '#fdbf6f',
  '#ff7f00',
  '#cab2d6',
  '#6a3d9a',
  '#ffff99',
  '#b15928'],
 'pastel1': ['#fbb4ae',
  '#b3cde3',
  '#ccebc5',
  '#decbe4',
  '#fed9a6',
  '#ffffcc',
  '#e5d8bd',
  '#fddaec',
  '#f2f2f2'],
 'pastel2': ['#b3e2cd',
  '#fdcdac',
  '#cbd5e8',
  '#f4cae4',
  '#e6f5c9',
  '#fff2ae',
  '#f1e2cc',
  '#cccccc'],
 'piyg': ['#8e0152',
  '#c51b7d',
  '#de77ae',
  '#f1b6da',
  '#fde0ef',
  '#f7f7f7',
  '#e6f5d0',
  '#b8e186',
  '#7fbc41',
  '#4d9221',
  '#276419'],
 'pubu': ['#fff7fb',
  '#ece7f2',
  '#d0d1e6',
  '#a6bddb',
  '#74a9cf',
  '#3690c0',
  '#0570b0',
  '#045a8d',
  '#023858'],
 'pubugn': ['#fff7fb',
  '#ece2f0',
  '#d0d1e6',
  '#a6bddb',
  '#67a9cf',
  '#3690c0',
  '#02818a',
  '#016c59',
  '#014636'],
 'puor': ['#7f3b08',
  '#b35806',
  '#e08214',
  '#fdb863',
  '#fee0b6',
  '#f7f7f7',
  '#d8daeb',
  '#b2abd2',
  '#8073ac',
  '#542788',
  '#2d004b'],
 'purd': ['#f7f4f9',
  '#e7e1ef',
  '#d4b9da',
  '#c994c7',
  '#df65b0',
  '#e7298a',
  '#ce1256',
  '#980043',
  '#67001f'],
 'purples': ['#fcfbfd',
  '#efedf5',
  '#dadaeb',
  '#bcbddc',
  '#9e9ac8',
  '#807dba',
  '#6a51a3',
  '#54278f',
  '#3f007d'],
 'rdbu': ['#67001f',
  '#b2182b',
  '#d6604d',
  '#f4a582',
  '#fddbc7',
  '#f7f7f7',
  '#d1e5f0',
  '#92c5de',
  '#4393c3',
  '#2166ac',
  '#053061'],
 'rdgy': ['#67001f',
  '#b2182b',
  '#d6604d',
  '#f4a582',
  '#fddbc7',
  '#ffffff',
  '#e0e0e0',
  '#bababa',
  '#878787',
  '#4d4d4d',
  '#1a1a1a'],
 'rdpu': ['#fff7f3',
  '#fde0dd',
  '#fcc5c0',
  '#fa9fb5',
  '#f768a1',
  '#dd3497',
  '#ae017e',
  '#7a0177',
  '#49006a'],
 'rdylbu': ['#a50026',
  '#d73027',
  '#f46d43',
  '#fdae61',
  '#fee090',
  '#ffffbf',
  '#e0f3f8',
  '#abd9e9',
  '#74add1',
  '#4575b4',
  '#313695'],
 'rdylgn': ['#a50026',
  '#d73027',
  '#f46d43',
  '#fdae61',
  '#fee08b',
  '#ffffbf',
  '#d9ef8b',
  '#a6d96a',
  '#66bd63',
  '#1a9850',
  '#006837'],
 'reds': ['#fff5f0',
  '#fee0d2',
  '#fcbba1',
  '#fc9272',
  '#fb6a4a',
  '#ef3b2c',
  '#cb181d',
  '#a50f15',
  '#67000d'],
 'set1': ['#e41a1c',
  '#377eb8',
  '#4daf4a',
  '#984ea3',
  '#ff7f00',
  '#ffff33',
  '#a65628',
  '#f781bf',
  '#999999'],
 'set2': ['#66c2a5',
  '#fc8d62',
  '#8da0cb',
  '#e78ac3',
  '#a6d854',
  '#ffd92f',
  '#e5c494',
  '#b3b3b3'],
 'set3': ['#8dd3c7',
  '#ffffb3',
  '#bebada',
  '#fb8072',
  '#80b1d3',
  '#fdb462',
  '#b3de69',
  '#fccde5',
  '#d9d9d9',
  '#bc80bd',
  '#ccebc5',
  '#ffed6f'],
 'spectral': ['#9e0142',
  '#d53e4f',
  '#f46d43',
  '#fdae61',
  '#fee08b',
  '#ffffbf',
  '#e6f598',
  '#abdda4',
  '#66c2a5',
  '#3288bd',
  '#5e4fa2'],
 'ylgn': ['#ffffe5',
  '#f7fcb9',
  '#d9f0a3',
  '#addd8e',
  '#78c679',
  '#41ab5d',
  '#238443',
  '#006837',
  '#004529'],
 'ylgnbu': ['#ffffd9',
  '#edf8b1',
  '#c7e9b4',
  '#7fcdbb',
  '#41b6c4',
  '#1d91c0',
  '#225ea8',
  '#253494',
  '#081d58'],
 'ylorbr': ['#ffffe5',
  '#fff7bc',
  '#fee391',
  '#fec44f',
  '#fe9929',
  '#ec7014',
  '#cc4c02',
  '#993404',
  '#662506'],
 'ylorrd': ['#ffffcc',
  '#ffeda0',
  '#fed976',
  '#feb24c',
  '#fd8d3c',
  '#fc4e2a',
  '#e31a1c',
  '#bd0026',
  '#800026']}

def random_color(h=None, l=None, s=None):
    """ returns the RGB code of a random color. Hue (h), Lightness (l)
    and Saturation (s) of the generated color could be fixed using the
    pertinent function argument.  """
    def rgb2hex(rgb):
        return '#%02x%02x%02x' % rgb
    def hls2hex(h, l, s):
        return rgb2hex( tuple(map(lambda x: int(x*255), colorsys.hls_to_rgb(h, l, s))))

    if not h:
        h = 1.0 / random.randint(0, 360)
    if not s: 
        s = 0.5
    if not l:
        l = 0.5
    return hls2hex(h, l, s)
