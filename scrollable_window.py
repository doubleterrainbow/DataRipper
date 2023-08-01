
import tkinter as tk

class ScrolledFrame(tk.Frame):
    
    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)
        
        # canvas for inner frame
        self._canvas = tk.Canvas(self)
        self._canvas.pack(expand=True, fill='both', side=tk.LEFT)

        # create right scrollbar and connect to canvas Y
        self._vertical_bar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        if vertical:
            self._vertical_bar.pack(side = tk.RIGHT, fill = tk.Y)
            
        # Reset the view
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)
    
        self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # inner frame for widgets
        self.inner = tk.Frame(self._canvas)
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')

        # autoresize inner frame
        self.columnconfigure(0, weight=1) # changed
        self.rowconfigure(0, weight=1) # changed

        # resize when configure changed
        self.inner.bind('<Configure>', self.resize)
        self._canvas.bind('<Configure>', self.frame_width)

        
        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (self.inner.winfo_reqwidth(), self.inner.winfo_reqheight())
            self._canvas.config(scrollregion="0 0 %s %s" % size)
            if self.inner.winfo_reqwidth() != self._canvas.winfo_width():
                # Update the self._canvas's width to fit the self.inner frame.
                self._canvas.config(width=self.inner.winfo_reqwidth())
        self.inner.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if self.inner.winfo_reqwidth() != self._canvas.winfo_width():
                # Update the inner frame's width to fill the self._canvas.
                self._canvas.itemconfigure(self._window, width=self._canvas.winfo_width())
        
        self._canvas.bind('<Configure>', _configure_canvas)
        self._canvas.bind('<Enter>', self._bound_to_mousewheel)
        self._canvas.bind('<Leave>', self._unbound_to_mousewheel)
        

    def _bound_to_mousewheel(self, event):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        self._canvas.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1*(event.delta/120)), "units") 
        
    
    def scroll_to_bottom(self):
        self._canvas.yview_moveto(1)
    
    
    def frame_width(self, event):
        # resize inner frame to canvas size
        canvas_width = event.width
        self._canvas.itemconfig(self._window, width = canvas_width)

    def resize(self, event=None): 
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))