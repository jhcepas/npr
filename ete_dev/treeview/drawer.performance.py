import signal

from PyQt4  import QtGui
import layouts
from main import save
#from qt4_render import _TreeScene, render, get_tree_img_map, init_tree_style

import render
from qt4_tile_gui import TilingGUI
#from  import TilingGUI

__all__ = ["show_tree", "render_tree"]

_QApp = None
GUI_TIMEOUT = None

def exit_gui(a,b):
    _QApp.exit(0)
    
def init_scene(t, layout, ts):
    global _QApp

    ts = init_tree_style(t, ts)
    if layout: 
        ts.layout_fn  = layout
        
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    return scene, ts

#@profile
def show_tree(t, layout=None, tree_style=None, win_name=None):
    """ Interactively shows a tree."""
    global _QApp
    
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])
    
    node_regions = render.render(t, tree_style)
    mainapp = TilingGUI(t, node_regions, tree_style)
    if win_name:
        mainapp.setObjectName(win_name)
    mainapp.show()
    
    # Restore Ctrl-C behavior
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if GUI_TIMEOUT is not None:
        signal.signal(signal.SIGALRM, exit_gui) 
        signal.alarm(GUI_TIMEOUT) 
   
    _QApp.exec_()
    
def render_tree(t, imgName, w=None, h=None, layout=None, \
                    tree_style = None, header=None, units="px"):
    """ Render tree image into a file."""
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)

    scene.init_values(t, img, n2i, n2f)
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    save(scene, imgName, w=w, h=h, units=units)
    imgmap = get_tree_img_map(n2i)

    return imgmap
    


