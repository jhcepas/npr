from PyQt4.QtGui import *
from PyQt4 import QtCore

from collections import defaultdict
import math

import _mainwindow, _search_dialog, _show_newick, _open_newick, _about
from qt4_paint import paint, get_collision_paths
from main import timeit
# Some name shortcuts for node_region vector
(_xpos, _ypos, _w0, _w1, _w2, _w3, _w4, _w5, _h0, _h1, _h2, _h3, _h4,
 _h5, _w1a, _w1b, _h1a, _h1b, _nw, _nh, _fnw, _fnh, _ycen) = range(23)

# Aliases for circular mode
_rad = _xpos
_astart = _ypos
_aend = _fnh
_acen = _ycen

class TiledTreeView(QGraphicsView):
    """Fake Scene containing tiles corresponding to actual items at a
    given zoom size
    """
    def __init__(self, zoom_factor, smart_renderer):
        img_w, img_h = smart_renderer.zoom_img_dim[zoom_factor]
        self.img_w, self.imeg_h = (img_w, img_h)
        self.tile_w = 1000
        self.tile_h = 1000
        self.max_rows = None
        self.max_cols = None
        self.current_mouse_pos = QtCore.QPointF(0, 0)
        nonedict = lambda: defaultdict(lambda: None)
        self.tiles = defaultdict(nonedict)
        self.zoom_factor = zoom_factor
        
        # Create and adjust the tiled scene rect
        self._scene = QGraphicsScene(-100, -100, scene_width + 100, scene_height + 100)
        QGraphicsView.__init__(self, self._scene)
        
        # tiles that have already been rendered
        self.visible_tiles = set()
        
        # This flag prevents updating tiles every single time that a
        # resize event is emitted. 
        self.NO_TILE_UPDATE = False
        
        self.setMouseTracking(True)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#333")))
        self.setup_tiles_grid()
        
    def setup_tiles_grid(self):
        # Set up default tile size
        self.tile_w = min(self.tile_w, self.img_w)
        self.tile_h = min(self.tile_h, self.img_h)

        # Tile Grid dimension
        self.max_rows = int(math.ceil(self.img_h / self.tile_h))
        self.max_cols = int(math.ceil(self.img_w / self.tile_w))
        
    @timeit
    def update_tile_view(self):
        print "Current scale", self.scale_factor
        self.setFocus()
        self.widgets = []
        TILE_CACHE_COL = 0
        TILE_CACHE_ROW = 0
        
        ## Get visible scene region 
        vrect = self.visibleRegion().boundingRect()
        match = self.mapToScene(vrect)
        srect = match.boundingRect()

        # Calculate grid of tiles necessary to draw
        p1 = srect.topLeft()
        p2 = srect.bottomRight()
        col_start = int((p1.x()) / self.tile_w) 
        row_start = int((p1.y()) / self.tile_h)  
        col_end = int((p2.x()) / self.tile_w)
        row_end = int((p2.y()) / self.tile_h)

        # Add cache tiles to the visisble tile grid
        col_start = max(0, col_start - TILE_CACHE_COL)
        col_end = min(self.max_cols-1, col_end + TILE_CACHE_COL)
        row_start = max(0, row_start - TILE_CACHE_ROW)
        row_end = min(self.max_rows-1, row_end + TILE_CACHE_ROW)

        sf = self.scale_factor
        for row in xrange(row_start, row_end + 1):
            for col in xrange(col_start, col_end + 1):
                coord = (row, col)
                if coord in self.visible_tiles:
                    continue
                # Correct tile size to hit img boundaries 
                _tile_w, _tile_h = self.tile_w, self.tile_h
                x = col * _tile_w
                y = row * _tile_h

                if x + _tile_w > self.img_w:
                    _tile_w = self.img_w - x
                if y + _tile_h > self.img_h:
                    _tile_h = self.img_h - y

                if not _tile_w or not _tile_h:
                    continue
                    
                tile_rect = [x, y, _tile_w, _tile_h]

                if not self.tiles[row][col]:
                    tile_img = smart_renderer.draw_region(tile_rect, zoom_factor)
                    pix = QPixmap(tile_image.width(), tile_image.height())
                    pix = pix.fromImage(tile_image)
                    tile_item = self._scene.addPixmap(pix)
                    tile_item.setPos(x, y)
                    self.tiles[row][col] = tile_item
                    
                    ## temp pixmap
                    #pixmap = QPixmap(_tile_w, _tile_h)
                    #pixmap.fill(QColor("#ddd"))
                    #item = self.scene().addPixmap(pixmap)
                    #item.setPos(x, y)
                    
                    # Add grid
                    border = self._scene.addRect(tile_item.boundingRect())
                    border.setPos(x, y)
                    pen = QPen(QColor("lightgrey"))
                    pen.setStyle(QtCore.Qt.DashLine)   
                    border.setPen(pen)
                    
    def resizeEvent(self, e):
        """ Update viewport size and reload tiles """
        QGraphicsView.resizeEvent(self, e)
        #self.show_fake_tiles()
        if not self.NO_TILE_UPDATE: 
            self.update_tile_view()
                    
    def keyPressEvent(self,e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            #self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setDragMode(QGraphicsView.NoDrag)
        QGraphicsView.keyPressEvent(self,e)            

    def keyReleaseEvent(self,e):
        if not (e.modifiers() & QtCore.Qt.ControlModifier):
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        key = e.key()
        if key  == QtCore.Qt.Key_Left:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
            self.update()
        elif key  == QtCore.Qt.Key_Right:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
            self.update()
        elif key  == QtCore.Qt.Key_Up:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
            self.update()
        elif key  == QtCore.Qt.Key_Down:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )
            self.update()
        elif key == 49:
            self.gui.scale_up()
        print "PRESSED", key
        QGraphicsView.keyReleaseEvent(self,e)

        
    def mouseReleaseEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            pass
        else:
            self.update_tile_view()
            #items = self.items_under(e)
            #if items:
            #    self.gui.node_properties.update_properties(items[0].node)
            pass

        QGraphicsView.mouseReleaseEvent(self, e)

    def mouseMoveEvent(self, e):
        #items = self.items_under(e)
        #if items: 
        #    self.setCursor(QtCore.Qt.PointingHandCursor)
        #else:
        #    self.setCursor(QtCore.Qt.ArrowCursor)
        self.current_mouse_pos = e.pos()
        QGraphicsView.mouseMoveEvent(self, e)
                           
    def wheelEvent(self, e):
        factor =  (-e.delta() / 360.0)
        if abs(factor)>=1:
            factor = 0.0
        
        # Ctrl+Shift -> Zoom in X
        if  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.ShiftModifier):
            self.gui.safe_scale(1+factor, 1)

        # Ctrl+Alt -> Zomm in Y
        elif  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.AltModifier):
            self.gui.safe_scale(1,1+factor)

        # Ctrl -> Zoom X,Y
        elif e.modifiers() & QtCore.Qt.ControlModifier:
            self.gui.safe_scale(1-factor, 1-factor)

        # Shift -> Horizontal scroll
        elif e.modifiers() &  QtCore.Qt.ShiftModifier:
            if e.delta()>0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
        else:
            self.gui.safe_scale(1-factor, 1-factor)
                
        # No modifiers ->  Vertival scroll
        #else:
        #    if e.delta()>0:
        #        self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
        #    else:
        #        self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )


                
    def fake_scale(self, xfactor, yfactor):
        self.setTransformationAnchor(self.AnchorUnderMouse)

        xscale = self.matrix().m11()
        yscale = self.matrix().m22()
        srect = self.sceneRect()

        if (xfactor>1 and xscale>200000) or \
                (yfactor>1 and yscale>200000):
            QMessageBox.information(self, "!",\
                                              "Wait, I will take the microscope!")
            return

        # Do not allow to reduce scale to a value producing height or
        # with smaller than 20 pixels No restrictions to zoom in
        if (yfactor<1 and  srect.width() * yscale < 20):
            pass
        elif (xfactor<1 and  srect.width() * xscale < 20):
            pass
        else:
            self.scale(xfactor, yfactor)

             
class TilingGUI(QMainWindow):
    def __init__(self, tree, node_regions, tree_style, *args):
        ZOOM_GRANULARITY = 20

        self.tree = tree
        self.node_regions = node_regions
        self.collision_paths = None
        
        QMainWindow.__init__(self, *args)
        self.node_properties = _PropertiesDialog()
        self.main = _mainwindow.Ui_MainWindow()
        self.main.setupUi(self)
        
        if tree_style.show_branch_length: 
            self.main.actionBranchLength.setChecked(True)
        if tree_style.show_branch_support: 
            self.main.actionBranchSupport.setChecked(True)
        if tree_style.show_leaf_name: 
            self.main.actionLeafName.setChecked(True)
        if tree_style.force_topology: 
            self.main.actionForceTopology.setChecked(True)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.node_properties)
        self.setCentralWidget(self.splitter)
        # I create a single dialog to keep the last search options
        self.searchDialog = QDialog()
        # Don't know if this is the best way to set up the dialog and
        # its variables
        self.searchDialog._conf = _search_dialog.Ui_Dialog()
        self.searchDialog._conf.setupUi(self.searchDialog)

        # Set up scale views
        if tree_style.mode == "c":
            self.scene_width = node_regions[tree._id][_fnw] * 2
            self.scene_height = self.scene_width
            self.collision_paths = get_collision_paths(tree, node_regions, self.scene_width, self.scene_height)
        else:
            self.scene_width = node_regions[tree._id][_fnw]
            self.scene_height = node_regions[tree._id][_fnh]
        
        self.views = []
        sf1 = 2048.0  / self.scene_width  
        sf2 = 1024.0 / self.scene_height
        sf = min([sf1, sf2, 1.0])
        scales = [sf]
        for level in xrange(0, ZOOM_GRANULARITY):
            level += 1
            scales.append(scales[-1] * 1.75)
        self.current_scale_factor = sf
        self.scales = scales

        mapitems, mapIitems = {}, {}
        for index, scale in enumerate(self.scales):
            view = TiledTreeView(scale, tree, node_regions,
                                 tree_style, self.scene_width,
                                 self.scene_height)
            view.gui = self
            self.views.append(view)
            
        self.current_view = 0
        self.view = self.views[0]
        self.splitter.insertWidget(0, self.view)
        #self.view.update_tile_view()
        # Check for updates
        # self.check = CheckUpdates()
        # self.check.start()
        # self.connect(self.check, SIGNAL("output(QString)"), self._updatestatus)
               
    def _updatestatus(self, msg):
        self.main.statusbar.showMessage(msg)
    @timeit 
    def set_scale(self, index):
        viewport =  self.view.viewport()
        vrect = viewport.rect()
        mouse_pos = viewport.mapFromGlobal(QCursor.pos())
        # The following seems to be less precise
        #vrect = self.view.visibleRegion().boundingRect()
        #mouse_pos = self.view.current_mouse_pos
        prev_view = self.view
        
        # Switch view
        self.view.setParent(None)
        self.current_view = index
        self.views[index].current_mouse_pos = self.view.current_mouse_pos
        self.view = self.views[index]
        self.view.NO_TILE_UPDATE = True
        self.splitter.insertWidget(0, self.view)

        # Translate center for UnderMouseAnchor effect
        sf1 = prev_view.scale_factor
        sf2 = self.view.scale_factor
        center_dist = QtCore.QPointF(vrect.center() - mouse_pos)
        scene_mouse_pos = prev_view.mapToScene(mouse_pos) / sf1
        new_center = scene_mouse_pos * sf2
        new_center = QtCore.QPointF(new_center.x() + center_dist.x(), new_center.y() + center_dist.y())
        
        self.view.centerOn(new_center)

        # Refresh tile view content
        self.view.update_tile_view()
        self.view.NO_TILE_UPDATE = False
        self.view.setFocus()

                    
    def safe_scale(self, xfactor, yfactor):
        if xfactor == yfactor:
            #self.current_scale_factor *= xfactor
            if xfactor > 1:
                self.scale_up()
            else:
                self.scale_down()
        
    def scale_up(self):
        if self.current_view < len(self.views) - 1:
            self.set_scale(self.current_view + 1)
            print "UP", self.view.scale_factor
            
    def scale_down(self):
        if self.current_view > 0:
            self.set_scale(self.current_view - 1)
            print "DOWN", self.view.scale_factor
            
    @QtCore.pyqtSignature("")
    def on_actionETE_triggered(self):
        try:
            __VERSION__
        except:
            __VERSION__= "development branch"

        d = QDialog()
        d._conf = _about.Ui_About()
        d._conf.setupUi(d)
        d._conf.version.setText("Version: %s" %__VERSION__)
        d._conf.version.setAlignment(QtCore.Qt.AlignHCenter)
        d.exec_()

    @QtCore.pyqtSignature("")
    def on_actionZoomOut_triggered(self):
        self.scale_down()

    @QtCore.pyqtSignature("")
    def on_actionZoomIn_triggered(self):
        self.scale_up()

    @QtCore.pyqtSignature("")
    def on_actionZoomInX_triggered(self):
        self.scene.img.scale += self.scene.img.scale * 0.05
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomOutX_triggered(self):
        self.scene.img.scale -= self.scene.img.scale * 0.05
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomInY_triggered(self):
        self.scene.img.branch_vertical_margin += 5 
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomOutY_triggered(self):
        if self.scene.img.branch_vertical_margin > 0:
            margin = self.scene.img.branch_vertical_margin - 5 
            if margin > 0: 
                self.scene.img.branch_vertical_margin = margin
            else:
                self.scene.img.branch_vertical_margin = 0.0
            self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionFit2tree_triggered(self):
        #self.view.fitInView(self.view.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.set_scale(0)
        
    @QtCore.pyqtSignature("")
    def on_actionFit2region_triggered(self):
        if self.scene.highlighter.isVisible():
            R = self.scene.highlighter.rect()
        else:
            R = self.scene.selector.rect()
        if R.width()>0 and R.height()>0:
            self.view.fitInView(R.x(), R.y(), R.width(),\
                                    R.height(), QtCore.Qt.KeepAspectRatio)

    @QtCore.pyqtSignature("")
    def on_actionSearchNode_triggered(self):
        setup = self.searchDialog._conf
        setup.attrValue.setFocus()
        ok = self.searchDialog.exec_()
        if ok:
            mType = setup.attrType.currentIndex()
            aName = str(setup.attrName.text())
            if mType >= 2 and mType <=6:
                try:
                    aValue =  float(setup.attrValue.text())
                except ValueError:
                    QMessageBox.information(self, "!",\
                                              "A numeric value is expected")
                    return
            elif mType == 7:
                aValue = re.compile(str(setup.attrValue.text()))
            elif mType == 0 or mType == 1:
                aValue =  str(setup.attrValue.text())

            if mType == 1 or mType == 2: #"is or =="
                cmpFn = lambda x,y: x == y
            elif mType == 0: # "contains"
                cmpFn = lambda x,y: y in x
            elif mType == 3:
                cmpFn = lambda x,y: x >= y
            elif mType == 4:
                cmpFn = lambda x,y: x > y
            elif mType == 5:
                cmpFn = lambda x,y: x <= y
            elif mType == 6:
                cmpFn = lambda x,y: x < y
            elif mType == 7:
                cmpFn = lambda x,y: re.search(y, x)

            for n in self.scene.tree.traverse():
                if setup.leaves_only.isChecked() and not n.is_leaf():
                    continue
                if hasattr(n, aName) \
                        and cmpFn(getattr(n, aName), aValue ):
                    self.scene.view.highlight_node(n)

    @QtCore.pyqtSignature("")
    def on_actionClear_search_triggered(self):
        # This could be much more efficient
        for n in self.view.n2hl.keys():
            self.scene.view.unhighlight_node(n)

    @QtCore.pyqtSignature("")
    def on_actionBranchLength_triggered(self):
        self.scene.img.show_branch_length ^= True
        self.scene.draw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSignature("")
    def on_actionBranchSupport_triggered(self):
        self.scene.img.show_branch_support ^= True
        self.scene.draw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSignature("")
    def on_actionLeafName_triggered(self):
        self.scene.img.show_leaf_name ^= True
        self.scene.draw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSignature("")
    def on_actionForceTopology_triggered(self):
        self.scene.img.force_topology ^= True
        self.scene.draw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSignature("")
    def on_actionShow_newick_triggered(self):
        d = NewickDialog(self.scene.tree)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec_()

    @QtCore.pyqtSignature("")
    def on_actionChange_orientation_triggered(self):
        self.scene.props.orientation ^= 1
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionShow_phenogram_triggered(self):
        self.scene.props.style = 0
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionShowCladogram_triggered(self):
        self.scene.props.style = 1
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionOpen_triggered(self):
        d = QFileDialog()
        d._conf = _open_newick.Ui_OpenNewick()
        d._conf.setupUi(d)
        d.exec_()
        return
        fname = QFileDialog.getOpenFileName(self ,"Open File",
                                                 "/home",
                                                 )
        try:
            t = Tree(str(fname))
        except Exception, e:
            print e
        else:
            self.scene.tree = t
            self.img = TreeStyle()
            self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionSave_newick_triggered(self):
        fname = QFileDialog.getSaveFileName(self ,"Save File",
                                                 "/home",
                                                 "Newick (*.nh *.nhx *.nw )")
        nw = self.scene.tree.write()
        try:
            OUT = open(fname,"w")
        except Exception, e:
            print e
        else:
            OUT.write(nw)
            OUT.close()

    @QtCore.pyqtSignature("")
    def on_actionRenderPDF_triggered(self):
        F = QFileDialog(self)
        if F.exec_():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            save(self.scene, imgName)


    @QtCore.pyqtSignature("")
    def on_actionRender_selected_region_triggered(self):
        if not self.scene.selector.isVisible():
            return QMessageBox.information(self, "!",\
                                              "You must select a region first")

        F = QFileDialog(self)
        if F.exec_():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            self.scene.save(imgName, take_region=True)


    @QtCore.pyqtSignature("")
    def on_actionPaste_newick_triggered(self):
        text,ok = QInputDialog.getText(self,\
                                                 "Paste Newick",\
                                                 "Newick:")
        if ok:
            try:
                t = Tree(str(text))
            except Exception,e:
                print e
            else:
                self.scene.initialize_tree_scene(t,"basic", TreeImageProperties())
                self.scene.draw()

class _PropertiesDialog(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self,*args)
        #self.scene = scene
        self._mode = 0
        self.layout =  QVBoxLayout()
        self.tableView = QTableView()
        self.tableView.verticalHeader().setVisible(False)
        #self.tableView.horizontalHeader().setVisible(True)
        #self.tableView.setVerticalHeader(None)
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)
        self.tableView.setGeometry (0, 0, 200,200)


    def update_properties(self, node):
        self.node = node
        self._edited_indexes =  set([])
        self._style_indexes = set([])
        self._prop_indexes = set([])

        self.get_prop_table(node)

    def get_props_in_nodes(self, nodes):
        # sorts properties and faces of selected nodes
        self.prop2nodes = {}
        self.prop2values = {}
        self.style2nodes = {}
        self.style2values = {}

        for n in nodes:
            for pname in n.features:
                pvalue = getattr(n,pname)
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.prop2nodes.setdefault(pname,[]).append(n)
                    self.prop2values.setdefault(pname,[]).append(pvalue)

            for pname,pvalue in n.img_style.iteritems():
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.style2nodes.setdefault(pname,[]).append(n)
                    self.style2values.setdefault(pname,[]).append(pvalue)

    def get_prop_table(self, node):
        if self._mode == 0: # node
            self.get_props_in_nodes([node])
        elif self._mode == 1: # childs
            self.get_props_in_nodes(node.get_leaves())
        elif self._mode == 2: # partition
            self.get_props_in_nodes([node]+node.get_descendants())

        total_props = len(self.prop2nodes) + len(self.style2nodes.keys())
        self.model = QStandardItemModel(total_props, 2)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Feature")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Value")
        self.tableView.setModel(self.model)
        self.delegate = _TableItem(self)
        self.tableView.setItemDelegate(self.delegate)

        row = 0
        items = self.prop2nodes.items()
        for name, nodes in sorted(items):
            value= getattr(nodes[0],name)

            index1 = self.model.index(row, 0, QtCore.QModelIndex())
            index2 = self.model.index(row, 1, QtCore.QModelIndex())
            f = QtCore.QVariant(name)
            v = QtCore.QVariant(value)
            self.model.setData(index1, f)
            self.model.setData(index2, v)
            self._prop_indexes.add( (index1, index2) )
            row +=1

        keys = self.style2nodes.keys()
        for name in sorted(keys):
            value= self.style2values[name][0]
            index1 = self.model.index(row, 0, QtCore.QModelIndex())
            index2 = self.model.index(row, 1, QtCore.QModelIndex())

            self.model.setData(index1, QtCore.QVariant(name))
            v = QtCore.QVariant(value)
            self.model.setData(index2, v)
            # Creates a variant element
            self._style_indexes.add( (index1, index2) )
            row +=1
        return

    def apply_changes(self):
        # Apply changes on styles
        for i1, i2 in self._style_indexes:
            if (i2.row(), i2.column()) not in self._edited_indexes:
                continue
            name = str(self.model.data(i1).toString())
            value = str(self.model.data(i2).toString())
            for n in self.style2nodes[name]:
                typedvalue = type(n.img_style[name])(value)
                try:
                    n.img_style[name] = typedvalue
                except:
                    #logger(-1, "Wrong format for attribute:", name)
                    break

        # Apply changes on properties
        for i1, i2 in self._prop_indexes:
            if (i2.row(), i2.column()) not in self._edited_indexes:
                continue
            name = str(self.model.data(i1).toString())
            value = str(self.model.data(i2).toString())
            for n in self.prop2nodes[name]:
                try:
                    setattr(n, name, type(getattr(n,name))(value))
                except Exception, e:
                    #logger(-1, "Wrong format for attribute:", name)
                    print e
                    break
        self.update_properties(self.node)
        #self.scene.img._scale = None
        self.redraw()
        return

                
