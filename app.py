import os
import threading
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from DesktopApp.parser import Parser
from DesktopApp.linker_registry import LinkerRegistry
from DesktopApp.progress import Progress
from DesktopApp.SunHaven_Linker import start_linking
from DesktopApp.app_settings import AppSettings

class SunHavenRipperApp:
    def __init__(self) -> None:          
        self.checkbuttons = {}  
        
        self.progress = 0
        self.progress_bar = None
        
        self.window = tk.Tk(screenName="Sun Haven Data Ripper")
        self.window.title("Sun Haven Data Ripper")
        self.window.resizable = True
        self.window.geometry("800x800")
        
        # self.window.iconphoto(False, tk.PhotoImage(file='sh_ripper_icon.png'))
        
        # scrollbar = tk.Scrollbar(self.window)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
      
        self.frame = tk.Frame(self.window, padx=10, pady=10, width=600.0)
        self.frame.grid()
        
        self.settings = AppSettings()
        
        self.total_parsers = 10
        self.current_progress = 0
        self.status_label_text = tk.StringVar(value="Haven't Started Yet!")
        self.error_label_text = tk.StringVar(value="")
      
    def has_cutscenes(self, directory_name) -> bool:
      return os.path.exists(f"{directory_name}\SunHaven.Core\Wish")
    
    def has_assets_xml(self, directory_name) -> bool:
      return os.path.isfile(f"{directory_name}/assets.xml")
  
    def has_required_files(self) -> bool:
      return self.has_assets_xml(self.settings.data_dir) and self.settings.output_dir is not None
  
    def select_data_dir(self):
        selected_dir = filedialog.askdirectory()
        
        if not self.has_assets_xml(selected_dir):
          self.error_label_text = "- Could not find assets.xml in this directory.\n"
        else:
          self.settings.data_dir = selected_dir
          data_dir_label = tk.Label(self.frame, text=f"{selected_dir}")
          data_dir_label.grid(column=3, row=1, sticky="W")      
          self.check_valid_files()
    
    def select_code_dir(self):
        selected_dir = filedialog.askdirectory()
        has_files = self.has_cutscenes(selected_dir)
        if not has_files:
          self.error_label_text.set("- Could not find cutscenes files. (Expected to find a folder named \SunHaven.Core\Wish)")
          self.cutscene_checkbutton['state'] = tk.DISABLED
          self.checkbuttons["Cutscenes"].set(0)

        if has_files:
          self.cutscene_checkbutton['state'] = tk.NORMAL
          self.checkbuttons["Cutscenes"].set(1)
          self.error_label_text.set("")
          self.settings.code_dir = selected_dir
          code_dir_label = tk.Label(self.frame, text=f"{selected_dir}")
          code_dir_label.grid(column=3, row=3, sticky="W")      
          self.check_valid_files()
    
    def select_output_dir(self):
        selected_dir = filedialog.askdirectory()

        self.settings.output_dir = selected_dir
        output_dir_label = tk.Label(self.frame, text=f"{selected_dir}")
        output_dir_label.grid(column=3, row=7, sticky="W")
                
        self.check_valid_files() 
  
    def check_valid_files(self):
        if self.has_required_files():
            self.error_label_text.set("")
            self.start_button = tk.Button(self.frame, text="Start", pady=5, command=self.begin_parsing_in_background)
            self.start_button.grid(column=0, row=8, sticky="W")
            
            status_label = tk.Label(self.frame, textvariable=self.status_label_text, padx=3, pady=5)
            status_label.grid(column=0, row=9, columnspan=3, sticky="W")
            self.set_current_task("This is gonna take a while...")
            
            self.progress_bar = ttk.Progressbar(self.frame, length=400)
            self.progress_bar.grid(column=0, row=10, columnspan=3)
        
    def set_current_task(self, task):
        self.status_label_text.set(task)
    
    def begin_parsing_in_background(self):
        parser_thread = threading.Thread(
          target=self.parse_data
        )
        parser_thread.start()
        
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        self.start_button["state"] = tk.DISABLED
    
    def update_progress(self, progress: Progress):
      if progress.error is not None:
        self.start_button["state"] = tk.NORMAL
        self.progress_bar.stop()
        self.progress_bar.step(0)
        
      if progress.complete:  
        logging.debug(f'opening {self.settings.output_dir}')
        self.set_current_task("Finished!")
        self.progress_bar.step(self.total_parsers)
        self.start_button["state"] = tk.NORMAL
        os.startfile(self.settings.output_dir)
      else:
        self.set_current_task(progress.message)
        if progress.current_progress > 0:
          self.progress_bar.stop()
          self.progress_bar.configure(mode='determinate', maximum=self.total_parsers)
          self.progress_bar.step(progress.current_progress)
    
    def parse_data(self):
        try:
          version = self.version_text.get("1.0", "end").rstrip()
          
          logging.basicConfig(level=logging.DEBUG, 
                              filename=os.path.join(self.settings.output_dir, version, "debug.log"))
          
          parser = Parser(
            game_version=version,
            data_path=self.settings.data_dir,
            code_path=self.settings.code_dir,
            output_path=self.settings.output_dir,
            on_progress_update=self.update_progress
          )
          
          linkers = [key for key, value in self.checkbuttons.items() if value.get() == 1]
          self.total_parsers = len(linkers)
          
          start_linking(
            parser,
            enabled_linkers=linkers
          )
        except Exception as e:
          self.update_progress(Progress("Encountered an unexpected error :(", error=e))
          logging.error("Exception in parse_data", exc_info=True)
    
    def create_checkboxes(self):
        checkbox_frame = tk.Frame(self.frame, borderwidth=1, relief="groove")
        checkbox_frame.grid(pady=30)
        
        checkboxes_label = tk.Label(checkbox_frame, text="Outputs:")
        checkboxes_label.grid(column=0, row=len(checkbox_frame.children), sticky="W")
        
        for linker in LinkerRegistry.linkers:
            self.checkbuttons[linker.label] = tk.IntVar(value=1)
            
            if "Cutscene" in linker.label:
                self.cutscene_checkbutton = tk.Checkbutton(
                  checkbox_frame, text=linker.label, variable=self.checkbuttons[linker.label]
                )
                self.cutscene_checkbutton.grid(row=len(checkbox_frame.children), column=0, columnspan=2, sticky="W")
                
                if not self.has_cutscenes(self.settings.code_dir):
                  self.checkbuttons[linker.label].set(0)
                  self.cutscene_checkbutton['state'] = tk.DISABLED
                  self.error_label_text.set("Cannot link cutscenes without Code directory")
                else:
                  self.cutscene_checkbutton['state'] = tk.NORMAL
                  self.error_label_text.set("")
            else:
                checkbutton = tk.Checkbutton(
                  checkbox_frame, text=linker.label, variable=self.checkbuttons[linker.label]
                )
                checkbutton.grid(row=len(checkbox_frame.children), column=0, columnspan=2, sticky="W")
              

    def start(self):
        """
        | 1               | 2               | 3              |
        | title           |                 |                | 0
        | select data dir | data dir button | data dir label | 1
        | error label     |                 |                | 2
        | select code dir | code dir button | code dir label | 3
        | error label     |                 |                | 4
        | checkboxes      |                 |                | 5
        | version label   |  version box    |                | 6
        | select out dir  | out dir button  | out dir label  | 7
        | start button    |                 |                | 8
        | status label    |                 |                | 9
        | progress        |                 |                | 10
        
        """
        title = tk.Label(self.frame, text="").grid(column=0, row=0, columnspan=2)
        
        data_dir = tk.Label(self.frame, text="Data directory:")
        data_dir.grid(column=0, row=1, sticky="W")
        
        self.data_dir_button = tk.Button(self.frame, text="Select...", command=self.select_data_dir)
        self.data_dir_button.grid(column=1, row=1)
        
        code_dir = tk.Label(self.frame, text="Code directory:")
        code_dir.grid(column=0, row=3, sticky="W")
        
        self.code_dir_button = tk.Button(self.frame, text="Select...", command=self.select_code_dir)
        self.code_dir_button.grid(column=1, row=3)
        
        tk.Label(self.frame, textvariable=self.error_label_text, justify='left').grid(column=0, row=4, columnspan=2)
        
        self.create_checkboxes()
        
        version_label = tk.Label(self.frame, text="Game Version:", pady=5)
        version_label.grid(column=0, row=6, sticky="W")
        
        self.version_text = tk.Text(self.frame, height=1, width=8, pady=5)
        self.version_text.grid(column=1, row=6)
        
        output_dir = tk.Label(self.frame, text="Output directory:", pady=5)
        output_dir.grid(column=0, row=7, sticky="W")
        
        self.output_dir_button = tk.Button(self.frame, text="Select...", command=self.select_output_dir)
        self.output_dir_button.grid(column=1, row=7)
        
        self.window.mainloop()

if __name__ == '__main__':
    app = SunHavenRipperApp()
    app.start()
  
