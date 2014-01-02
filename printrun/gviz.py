# This file is part of the Printrun suite.
#
# Printrun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Printrun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Printrun.  If not, see <http://www.gnu.org/licenses/>.
import wx, time

from printrun_utils import imagefile

ID_ABOUT = 101
ID_EXIT = 110
class window(wx.Frame):
    def __init__(self, f, size = (600, 600), build_dimensions = [200, 200, 100, 0, 0, 0], grid = (10, 50), extrusion_width = 0.5):
        wx.Frame.__init__(self, None, title = "Gcode view, shift to move view, mousewheel to set layer", size = (size[0], size[1]))
        self.p = gviz(self, size = size, build_dimensions = build_dimensions, grid = grid, extrusion_width = extrusion_width)

        vbox = wx.BoxSizer(wx.VERTICAL)
        toolbar = wx.ToolBar(self, -1, style = wx.TB_HORIZONTAL | wx.NO_BORDER)
        toolbar.AddSimpleTool(1, wx.Image(imagefile('zoom_in.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Zoom In [+]', '')
        toolbar.AddSimpleTool(2, wx.Image(imagefile('zoom_out.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Zoom Out [-]', '')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(3, wx.Image(imagefile('arrow_up.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Move Up a Layer [U]', '')
        toolbar.AddSimpleTool(4, wx.Image(imagefile('arrow_down.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Move Down a Layer [D]', '')
        toolbar.AddSimpleTool(5, wx.EmptyBitmap(16, 16), 'Reset view', '')
        toolbar.AddSimpleTool(6, wx.Image(imagefile('arrow_right.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Move to next Segment [->]', '')
        toolbar.AddSimpleTool(7, wx.Image(imagefile('arrow_left.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Move to previous Segment [<-]', '')
        toolbar.AddSeparator()
        #toolbar.AddSimpleTool(5, wx.Image('./images/inject.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Insert Code at start of this layer', '')
        toolbar.Realize()
        vbox.Add(toolbar, 0, border = 5)
        self.SetSizer(vbox)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.zoom(200, 200, 1.2), id = 1)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.zoom(200, 200, 1/1.2), id = 2)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.layerup(), id = 3)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.layerdown(), id = 4)
        self.Bind(wx.EVT_TOOL, self.resetview, id = 5)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.line_next(), id=6)
        self.Bind(wx.EVT_TOOL, lambda x:self.p.line_prev(), id=7)
        #self.Bind(wx.EVT_TOOL, lambda x:self.p.inject(), id = 5)


        self.CreateStatusBar(1);
        self.SetStatusText("Layer number and Z position show here when you scroll");
        #self.bu = wx.Button(self.p,-1, "U", pos = (0, 100), size = (40, 140))
        #self.bd = wx.Button(self.p,-1, "D", pos = (0, 140), size = (40, 140))
        #self.bi = wx.Button(self.p,-1, "+", pos = (40, 100), size = (40, 140))
        #self.bo = wx.Button(self.p,-1, "-", pos = (40, 140), size = (40, 140))
        #self.bs = wx.Button(self.p, -1, "Inject", pos = (85, 103), size = (50, 20))

        #self.bu.SetToolTip(wx.ToolTip("Move up one layer"))
        #self.bd.SetToolTip(wx.ToolTip("Move down one layer"))
        #self.bi.SetToolTip(wx.ToolTip("Zoom view in"))
        #self.bo.SetToolTip(wx.ToolTip("Zoom view out"))
        #self.bs.SetToolTip(wx.ToolTip("Insert Code at start of this layer"))

        #self.bu.Bind(wx.EVT_BUTTON, lambda x:self.p.layerup())
        #self.bd.Bind(wx.EVT_BUTTON, lambda x:self.p.layerdown())
        #self.bi.Bind(wx.EVT_BUTTON, lambda x:self.p.zoom(200, 200, 1.2))
        #self.bo.Bind(wx.EVT_BUTTON, lambda x:self.p.zoom(200, 200, 1/1.2))
        #self.bs.Bind(wx.EVT_BUTTON, lambda x:self.p.inject())

        s = time.time()
        #print time.time()-s
        self.initpos = [0, 0]
        self.p.Bind(wx.EVT_KEY_DOWN, self.key)
        #self.bu.Bind(wx.EVT_KEY_DOWN, self.key)
        #self.bd.Bind(wx.EVT_KEY_DOWN, self.key)
        #self.bi.Bind(wx.EVT_KEY_DOWN, self.key)
        #self.bo.Bind(wx.EVT_KEY_DOWN, self.key)
        #self.Bind(wx.EVT_KEY_DOWN, self.key)
        self.Bind(wx.EVT_CHAR_HOOK, self.key)
        self.p.Bind(wx.EVT_MOUSEWHEEL, self.zoom)
        self.Bind(wx.EVT_MOUSEWHEEL, self.zoom)
        self.p.Bind(wx.EVT_MOUSE_EVENTS, self.mouse)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.mouse)

    def resetview(self, event):
        self.p.translate = [0.0, 0.0]
        self.p.scale = self.p.basescale
        self.p.zoom(0, 0, 1.0)

    def mouse(self, event):
        if event.ButtonUp(wx.MOUSE_BTN_LEFT):
            if(self.initpos is not None):
                self.initpos = None
        elif event.Dragging():
            e = event.GetPositionTuple()
            if self.initpos is None or not hasattr(self, "basetrans"):
                self.initpos = e
                self.basetrans = self.p.translate
            #print self.p.translate, e, self.initpos
            self.p.translate = [ self.basetrans[0]+(e[0]-self.initpos[0]),
                            self.basetrans[1]+(e[1]-self.initpos[1]) ]
            self.p.repaint()
            self.p.Refresh()

        
        #TODO sort out coordinates - jmg
        elif event.Moving():
            e=event.GetPositionTuple()
            self.basetrans=self.p.translate
            _x = (e[0] - self.p.translate[0]) / self.p.scale[0]
            #e[0] = self.scale[0]*x[0]+self.translate[0]
            _y = (e[1]  - self.p.translate[1]) / self.p.scale[1]
            #self.SetStatusText("X%0.3f Y%0.3f Scale %0.3f Pan X%0.3f Y%0.3f Cursor X%0.3f Y%0.3f" % (e[0], e[1], self.p.scale[0], self.p.translate[0], self.p.translate[1], _x, _y))
            self.SetStatusText("Cursor X%0.3f Y%0.3f" % (_x, _y))
        else:
            event.Skip()

    def key(self, event):
        #  Keycode definitions
        kup = [85, 315]               # Up keys
        kdo = [68, 317]               # Down Keys
        klf = [80, 314] #[wx.WXK_LEFT]
        krt = [78, 316] #[wx.WXK_RIGHT]
        kzi=[388, 61]        # Zoom In Keys
        kzo=[390, 45]       # Zoom Out Keys
        x = event.GetKeyCode()
        #print "Key event - "+str(x)
        #if event.ShiftDown():
        cx, cy = self.p.translate
        #   if x == wx.WXK_UP:
        #      self.p.zoom(cx, cy, 1.2)
        #   if x == wx.WXK_DOWN:
        #       self.p.zoom(cx, cy, 1/1.2)
        #else:
        #   if x == wx.WXK_UP:
        #       self.p.layerup()
        #   if x == wx.WXK_DOWN:
        #       self.p.layerdown()
        if x in kup:
            self.p.layerup()
        if x in kdo:
            self.p.layerdown()
        if x in klf:
            self.p.line_prev()
        if x in krt:
            self.p.line_next()
        if x in kzi:
            self.p.zoom(cx, cy, 1.2)
        if x in kzo:
            self.p.zoom(cx, cy, 1/1.2)

        #print p.lines.keys()
    def zoom(self, event):
        z = event.GetWheelRotation()
        if event.ShiftDown():
            if z > 0:   self.p.layerdown()
            elif z < 0: self.p.layerup()
        else:
            if z > 0:   self.p.zoom(event.GetX(), event.GetY(), 1.2)
            elif z < 0: self.p.zoom(event.GetX(), event.GetY(), 1/1.2)
            #print self.p.scale

class gviz(wx.Panel):
    def __init__(self, parent, size = (200, 200), build_dimensions = [200, 200, 100, 0, 0, 0], grid = (10, 50), extrusion_width = 0.5):
        wx.Panel.__init__(self, parent,-1, size = (size[0], size[1]))
        self.parent = parent
        self.size = size
        self.build_dimensions = build_dimensions
        self.grid = grid
        self.lastpos = [0, 0, 0, 0, 0, 0, 0]
        self.hilightpos = self.lastpos[:]
        self.Bind(wx.EVT_PAINT, self.paint)
        self.Bind(wx.EVT_SIZE, self.resize)
        self.lines = {}
        self.pens = {}
        self.arcs = {}
        self.arcpens = {}
        self.layers = []
        self.layerindex = 0
        self.filament_width = extrusion_width # set it to 0 to disable scaling lines with zoom
        self.basescale = 2 * [min(float(self.size[0] - 1) / self.build_dimensions[0],
                                  float(self.size[1] - 1) / self.build_dimensions[1])]
        self.scale = self.basescale
        penwidth = max(1.0, self.filament_width*((self.scale[0]+self.scale[1])/2.0))
        self.translate = [0.0, 0.0]
        self.mainpen = wx.Pen(wx.Colour(0, 0, 0), penwidth)
        self.arcpen = wx.Pen(wx.Colour(255, 0, 0), penwidth)
        self.travelpen = wx.Pen(wx.Colour(10, 80, 80), penwidth)
        self.hlpen = wx.Pen(wx.Colour(200, 50, 50), penwidth)
        self.fades = [wx.Pen(wx.Colour(250-0.6**i*100, 250-0.6**i*100, 200-0.4**i*50), penwidth) for i in xrange(6)]
        self.penslist = [self.mainpen, self.travelpen, self.hlpen]+self.fades
        self.showall = 0
        self.hilight = []
        self.hilightarcs = []
        self.dirty = 1
        self.blitmap = wx.EmptyBitmap(self.GetClientSize()[0], self.GetClientSize()[1],-1)
        self.lines_=0

    def inject(self):
        #import pdb; pdb.set_trace()
        print"Inject code here..."
        print  "Layer "+str(self.layerindex +1)+" - Z = "+str(self.layers[self.layerindex])+" mm"

    def clear(self):
        self.lastpos = [0, 0, 0, 0, 0, 0, 0]
        self.lines = {}
        self.pens = {}
        self.arcs = {}
        self.arcpens = {}
        self.layers = []
        self.hilight = []
        self.hilightarcs = []
        self.layerindex = 0
        self.showall = 0
        self.dirty = 1
        #self.repaint()
    def layerup(self):
        if(self.layerindex+1<len(self.layers)):
            self.layerindex+=1
            # Display layer info on statusbar (Jezmy)
            self.parent.SetStatusText("Layer "+str(self.layerindex +1)+" - Going Up - Z = "+str(self.layers[self.layerindex])+" mm", 0)
            self.lines_ = 0
            self.repaint()
            self.Refresh()

    def layerdown(self):
        if(self.layerindex>0):
            self.layerindex-=1
            # Display layer info on statusbar (Jezmy)
            self.parent.SetStatusText("Layer "+str(self.layerindex + 1)+" - Going Down - Z = "+str(self.layers[self.layerindex])+ " mm", 0)
            self.lines_ = 0
            self.repaint()
            self.Refresh()

    def _move_pens(self,pen):
        newpen = self.hlpen if pen != self.travelpen else self.travelpen
        #pens = wx.Pen(wx.Colour(0,255,0),max(1.0,self.filament_width*((self.scale[0]+self.scale[1])/2.0)))#self.hlpen
        return newpen

    def line_next(self):
        self.lines_ += 1
        #print "move_lines " + str(self.lines_);
        self.move_pens = map(self._move_pens,self.pens[self.layers[self.layerindex]][:self.lines_])
        #print self.move_pens
        self.repaint(self.lines_)
        self.Refresh()

    def line_prev(self):
        self.lines_ -= 1
        #print "move_lines " + str(self.lines_);
        self.move_pens = map(self._move_pens,self.pens[self.layers[self.layerindex]][:self.lines_])
        self.repaint(self.lines_)
        self.Refresh()

    def setlayer(self, layer):
        try:
            self.layerindex = self.layers.index(layer)
            self.repaint()
            wx.CallAfter(self.Refresh)
            self.showall = 0
        except:
            pass

    def resize(self, event):
        size = self.GetClientSize()
        size = [max(1.0, size[0]), max(1.0, size[1])]
        self.size = [max(1.0, self.size[0]), max(1.0, self.size[1])]
        newsize = min(float(size[0])/self.size[0], float(size[1])/self.size[1])
        self.size = self.GetClientSize()
        wx.CallAfter(self.zoom, 0, 0, newsize)


    def zoom(self, x, y, factor):
        self.scale = [s * factor for s in self.scale]

        self.translate = [ x - (x-self.translate[0]) * factor,
                            y - (y-self.translate[1]) * factor]
        penwidth = max(1.0, self.filament_width*((self.scale[0]+self.scale[1])/2.0))
        for pen in self.penslist:
            pen.SetWidth(penwidth)
        #self.dirty = 1
        self.repaint()
        self.Refresh()


    def repaint(self, lines=-1):
        self.blitmap = wx.EmptyBitmap(self.GetClientSize()[0], self.GetClientSize()[1],-1)
        dc = wx.MemoryDC()
        dc.SelectObject(self.blitmap)
        dc.SetBackground(wx.Brush((250, 250, 200)))
        dc.Clear()
        dc.SetPen(wx.Pen(wx.Colour(180, 180, 150)))
        for grid_unit in self.grid:
            if grid_unit > 0:
                for x in xrange(int(self.build_dimensions[0]/grid_unit)+1):
                    dc.DrawLine(self.translate[0]+x*self.scale[0]*grid_unit, self.translate[1], self.translate[0]+x*self.scale[0]*grid_unit, self.translate[1]+self.scale[1]*self.build_dimensions[1])
                for y in xrange(int(self.build_dimensions[1]/grid_unit)+1):
                    dc.DrawLine(self.translate[0], self.translate[1]+y*self.scale[1]*grid_unit, self.translate[0]+self.scale[0]*self.build_dimensions[0], self.translate[1]+y*self.scale[1]*grid_unit)
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0)))
        if not self.showall:
            self.size = self.GetSize()
            dc.SetBrush(wx.Brush((43, 144, 255)))
            dc.DrawRectangle(self.size[0]-15, 0, 15, self.size[1])
            dc.SetBrush(wx.Brush((0, 255, 0)))
            if len(self.layers):
                dc.DrawRectangle(self.size[0]-14, (1.0-(1.0*(self.layerindex+1))/len(self.layers))*self.size[1], 13, self.size[1]-1)

        def _drawlines(lines, pens):
            def _scaler(x):
                return (self.scale[0]*x[0]+self.translate[0],
                        self.scale[1]*x[1]+self.translate[1],
                        self.scale[0]*x[2]+self.translate[0],
                        self.scale[1]*x[3]+self.translate[1],)
            scaled_lines = map(_scaler, lines)
            dc.DrawLineList(scaled_lines, pens)

        def _drawarcs(arcs, pens):
            def _scaler(x):
                return (self.scale[0]*x[0]+self.translate[0],
                        self.scale[1]*x[1]+self.translate[1],
                        self.scale[0]*x[2]+self.translate[0],
                        self.scale[1]*x[3]+self.translate[1],
                        self.scale[0]*x[4]+self.translate[0],
                        self.scale[1]*x[5]+self.translate[1],)
            scaled_arcs = map(_scaler, arcs)
            for i in range(len(scaled_arcs)):
                dc.SetPen(pens[i] if type(pens).__name__ == 'list' else pens)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawArc(*scaled_arcs[i])

        if self.showall:
            l = []
            for i in self.layers:
                dc.DrawLineList(l, self.fades[0])
                _drawlines(self.lines[i], self.pens[i])
                _drawarcs(self.arcs[i], self.arcpens[i])
            return
        if self.layerindex<len(self.layers) and self.layers[self.layerindex] in self.lines.keys():
            for layer_i in xrange(max(0, self.layerindex-6), self.layerindex):
                #print i, self.layerindex, self.layerindex-i
                _drawlines(self.lines[self.layers[layer_i]], self.fades[self.layerindex-layer_i-1])
                _drawarcs(self.arcs[self.layers[layer_i]], self.fades[self.layerindex-layer_i-1])
            if (lines > 0 and lines <= len(self.lines[self.layers[self.layerindex]])):
                _drawlines(self.lines[self.layers[self.layerindex]][:lines], self.move_pens)
               #_drawlines(self.lines[self.layers[self.layerindex]][lines:], self.pens[self.layers[self.layerindex]][lines:])
                self.parent.SetStatusText("X" + str(self.lines[self.layers[self.layerindex]][lines][0]) + " Y" + str(self.build_dimensions[1]-self.lines[self.layers[self.layerindex]][lines][1]))
            else:
              _drawlines(self.lines[self.layers[self.layerindex]], self.pens[self.layers[self.layerindex]])
              _drawarcs(self.arcs[self.layers[self.layerindex]], self.arcpens[self.layers[self.layerindex]])

        _drawlines(self.hilight, self.hlpen)
        _drawarcs(self.hilightarcs, self.hlpen)

        dc.SelectObject(wx.NullBitmap)

    def paint(self, event):
        dc = wx.PaintDC(self)
        if(self.dirty):
            self.repaint()
        self.dirty = 0
        sz = self.GetClientSize()
        dc.DrawBitmap(self.blitmap, 0, 0)
        del dc

    def addfile(self, gcodes = []):
        self.clear()
        for i in gcodes:
            self.addgcode(i)

    def addgcode(self, gcode = "M105", hilight = 0):
        gcode = gcode.split("*")[0]
        gcode = gcode.split(";")[0]
        gcode = gcode.lower().strip().split()
        if len(gcode) == 0:
            return
        if gcode[0][0] == 'n':
            gcode.pop(0)

        def _readgcode():
            target = self.lastpos[:]
            target[5]=0.0
            target[6]=0.0
            if hilight:
                target = self.hilightpos[:]
            for i in gcode:
                if i[0]=="x":
                    target[0]=float(i[1:])
                elif i[0]=="y":
                    target[1]=float(i[1:])
                elif i[0]=="z":
                    target[2]=float(i[1:])
                elif i[0]=="e":
                    target[3]=float(i[1:])
                elif i[0]=="f":
                    target[4]=float(i[1:])
                elif i[0]=="i":
                    target[5]=float(i[1:])
                elif i[0]=="j":
                    target[6]=float(i[1:])
            if not hilight:
                if not target[2] in self.lines.keys():
                    self.lines[target[2]]=[]
                    self.pens[target[2]]=[]
                    self.arcs[target[2]]=[]
                    self.arcpens[target[2]]=[]
                    self.layers+=[target[2]]
            return target

        def _y(y):
            return self.build_dimensions[1]-(y-self.build_dimensions[4])
        def _x(x):
            return x-self.build_dimensions[3]

        start_pos = self.hilightpos[:] if hilight else self.lastpos[:]

        if gcode[0] in [ "g0", "g1" ]:
            target = _readgcode()
            line = [ _x(start_pos[0]), _y(start_pos[1]), _x(target[0]), _y(target[1]) ]
            if not hilight:
                self.lines[ target[2] ] += [line]
                self.pens[ target[2] ]  += [self.mainpen if target[3] != self.lastpos[3] else self.travelpen]
                self.lastpos = target
            else:
                self.hilight += [line]
                self.hilightpos = target
            self.dirty = 1

        if gcode[0] in [ "g2", "g3" ]:
            target = _readgcode()
            arc = []
            arc += [ _x(start_pos[0]), _y(start_pos[1]) ]
            arc += [ _x(target[0]), _y(target[1]) ]
            arc += [ _x(start_pos[0] + target[5]), _y(start_pos[1] + target[6]) ]  # center
            if gcode[0] == "g2":  # clockwise, reverse endpoints
                arc[0], arc[1], arc[2], arc[3] = arc[2], arc[3], arc[0], arc[1]

            if not hilight:
                self.arcs[ target[2] ]    += [arc]
                self.arcpens[ target[2] ] += [self.arcpen]
                self.lastpos = target
            else:
                self.hilightarcs += [arc]
                self.hilightpos = target
            self.dirty = 1

if __name__ == '__main__':
    app = wx.App(False)
    #main = window(open("/home/kliment/designs/spinner/arm_export.gcode"))
    main = window(open("jam.gcode"))
    main.Show()
    app.MainLoop()
