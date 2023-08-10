import json
import os
import pathlib
import pprint
import re
import threading
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parsers.outputs import included_parsers
from DesktopApp.asset_ripper_parser.parsers.gift_tables import parse_gift_tables
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.parsers.parser_registry import ParserRegistry
from DesktopApp.asset_ripper_parser.parsers.recipes import parse_recipes
from DesktopApp.asset_ripper_parser.parsers.skill_tree import parse_skill_trees

from DesktopApp.progress import Progress
from DesktopApp.SunHaven_Linker import start_linking
from DesktopApp.app_settings import AppSettings
from scrollable_window import ScrolledFrame

class SunHavenRipperApp:
    def __init__(self) -> None:          
        self.checkbuttons = {}  
        
        self.progress = 0
        self.progress_bar = None
        
        self.window = tk.Tk(screenName="Sun Haven Data Ripper")
        self.window.title("Sun Haven Data Ripper")
        self.window.resizable = True
        self.window.geometry("600x400")
        
        # self.window.iconphoto(False, tk.PhotoImage(file='sh_ripper_icon.png'))
        
        self.frame = ScrolledFrame(self.window)
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.settings = AppSettings()
        
        self.total_parsers = 10
        self.current_progress = 0
        self.skip_setup_value = tk.IntVar()
        
        self.status_label_text = tk.StringVar(value="Haven't Started Yet!")
        self.error_label_text = tk.StringVar(value="")
        self.ripper_dir_label = tk.StringVar(value="AssetRipper Directory:")
        self.data_dir_label = tk.StringVar(value="Data Directory:")
        self.code_dir_label = tk.StringVar(value="Code Directory:")
        self.output_dir_label = tk.StringVar(value="Output Directory:")
      
    def has_cutscenes(self, directory_name) -> bool:
      return os.path.exists(f"{directory_name}\SunHaven.Core\Wish")
    
    def has_assets_xml(self, directory_name) -> bool:
      return os.path.isfile(f"{directory_name}/assets.xml")
    
    def has_required_files(self) -> bool:
      return self.settings.ripper_dir is not None and self.settings.output_dir is not None
  
    def select_ripper_dir(self):
        selected_dir = filedialog.askdirectory()
        
        self.settings.ripper_dir = selected_dir
        self.ripper_dir_label.set(f"AssetRipper Directory: {selected_dir}")
        self.check_valid_files()
  
    def select_output_dir(self):
        selected_dir = filedialog.askdirectory()

        self.settings.output_dir = selected_dir
        self.output_dir_label.set(f"Output Directory: {selected_dir}")
        self.check_valid_files() 
  
    def check_valid_files(self):
        if self.has_required_files():
            self.error_label_text.set("No Problems Found.")
            self.start_button = tk.Button(self.frame.inner, text="Start", pady=5, command=self.begin_parsing_in_background)
            self.start_button.pack()
            
            status_label = tk.Label(self.frame.inner, textvariable=self.status_label_text, padx=3, pady=5)
            status_label.pack()
            self.set_current_task("This is gonna take a while...")
            
            if self.progress_bar is None:
              self.progress_bar = ttk.Progressbar(self.frame.inner, length=400)
              self.progress_bar.pack()
              
              self.skip_setup_checkbox = tk.Checkbutton(self.frame.inner, variable=self.skip_setup_value, text="Skip Reading Assets")
              self.skip_setup_checkbox.pack()
              
              skip_setup_label = tk.Label(self.frame.inner, text="NOTE: only enable this if you are rerunning and reusing an output folder.\nOtherwise outputs will be empty.")
              skip_setup_label.pack()
              
              self.frame.scroll_to_bottom()
        
    def set_current_task(self, task):
        self.status_label_text.set(task)
    
    def begin_parsing_in_background(self):
        parser_thread = threading.Thread(
          target=self.parse_data
        )
        parser_thread.start()
        
        # self.progress_bar.start()
        self.start_button["state"] = tk.DISABLED
    
    def update_progress(self, progress: Progress):
        pass
      # if progress.error is not None:
      #   self.start_button["state"] = tk.NORMAL
      #   self.progress_bar.stop()
      #   self.progress_bar.step(0)
        
      # if progress.complete:
      #   logging.debug(f'opening {self.settings.output_dir}')
      #   self.set_current_task("Finished!")
      #   self.progress_bar.step(self.total_parsers + 1)
      #   self.start_button["state"] = tk.NORMAL
      #   os.startfile(self.settings.output_dir)
      # else:
      #   self.set_current_task(progress.message)
      #   if progress.current_progress > 0:
      #     self.progress_bar.stop()
      #     self.progress_bar.configure(mode='determinate', maximum=self.total_parsers)
      #     self.progress_bar.step(progress.current_progress)
    
    def parse_data(self):
        try:
          
          skip_setup = self.skip_setup_value.get() == 1
          
          os.makedirs(self.settings.output_dir, exist_ok=True)
          os.makedirs(os.path.join(self.settings.output_dir, "file_mappings"), exist_ok=True)
          
          tagged_files = os.path.join(self.settings.output_dir, "file_mappings", "tagged_files.csv")
          
          file_indexer = FileIndexer(
            assets_folder=self.settings.ripper_dir,
            ids_file=os.path.join(self.settings.output_dir, "file_mappings", "ids.csv"),
            file_tags_file=tagged_files
          )
          
          if not skip_setup:
              
              self.progress_bar.configure(mode='indeterminate')
              self.progress_bar.start()
              
              self.status_label_text.set(f"Getting file IDs...")
              file_indexer.create_mapping_files()
              
              self.status_label_text.set(f"Determining relevant files and their types...")
              file_indexer.create_organization_file()
          
          enabled_parsers = [key for key, value in self.checkbuttons.items() if value.get() == 1]

          self.progress_bar.stop()
          self.progress_bar.configure(value=0, maximum=len(enabled_parsers), mode='determinate')
          
          def add_to_progress():
              self.progress_bar['value'] += 1
          
          with open(tagged_files, 'r') as tagged_files:
            file_tags = tagged_files.readlines()
            
            parsers = ParserRegistry.registry
            for parser in parsers:
                if parser.label in enabled_parsers:
                    files = {}
                    for tag in parser.tags:
                        files[tag.value] = [line.split(',')[0] for line in file_tags if tag.value in line.strip().split(',')[1:] and "_0" not in line]
                    
                    primary_file_amount = len(next(iter(files.values())))
                    
                    self.status_label_text.set(f"Parsing {primary_file_amount} {parser.label}")
                    self.progress_bar['value'] = 0
                    self.progress_bar['maximum'] = primary_file_amount
                    
                    try:
                        parser.callable(file_indexer, add_to_progress, self.settings.output_dir, files)
                    except Exception as e:
                        logging.error(f"Error when linking {parser.label}", exc_info=True)
          
          self.set_current_task("Finished!")
          self.progress_bar.stop()
          self.start_button["state"] = tk.NORMAL
          os.startfile(self.settings.output_dir)
          
          print("Done!")
        except Exception as e:
          self.update_progress(Progress("Encountered an unexpected error :(", error=e))
          logging.error("Exception in parse_data", exc_info=True)
    
    def create_checkboxes(self):
        checkbox_frame = tk.Frame(self.frame.inner, pady=5)
        checkbox_frame.pack(anchor='w', expand=True)
        
        checkboxes_label = tk.Label(checkbox_frame, font=('Helvetica', 12, 'normal'), text="Outputs:")
        checkboxes_label.pack(anchor='nw')
        
        print(f"registered {len(ParserRegistry.registry)} parsers")
        
        for linker in included_parsers:
            self.checkbuttons[linker.label] = tk.IntVar(value=1)
            
            if "Cutscene" in linker.label:
                self.cutscene_checkbutton = tk.Checkbutton(
                  checkbox_frame, text=linker.label, variable=self.checkbuttons[linker.label]
                )
                self.cutscene_checkbutton.pack(anchor='w')
                
                if not self.has_cutscenes(self.settings.code_dir):
                  self.checkbuttons[linker.label].set(0)
                  self.cutscene_checkbutton['state'] = tk.DISABLED
                  self.error_label_text.set("Cannot link cutscenes without Code directory")
                else:
                  self.cutscene_checkbutton['state'] = tk.NORMAL
                  self.error_label_text.set("No Problems Found.")
            else:
                checkbutton = tk.Checkbutton(
                  checkbox_frame, text=linker.label, variable=self.checkbuttons[linker.label]
                )
                checkbutton.pack(anchor='w')
              

    def start(self):
        """
        | 1               | 2               | 3             |4|
        | title           |                 |               | | 0
        | select ripp dir | ripp dir button | ripp dir label| | 1
        | error label     |                 |               | | 2
        | checkboxes      |                 |               | | 5
        | version label   |  version box    |               | | 6
        | select out dir  | out dir button  | out dir label | | 7
        | start button    |                 |               | | 8
        | status label    |                 |               | | 9
        | progress        |                 |               | | 10
        
        """
        title = tk.Label(self.frame.inner, text="").pack()

        self.directories_frame = tk.Frame(self.frame.inner, pady=10)
        self.directories_frame.pack(anchor='nw', expand=True, fill='both')
        
        ripper_dir = tk.Label(self.directories_frame, font=('Helvetica', 12, 'normal'), textvariable=self.ripper_dir_label)
        ripper_dir.pack(anchor='sw')
        
        ripper_dir_instruction = tk.Label(self.directories_frame, text="- (optional) Should be Assets folder from AssetRipper export")
        ripper_dir_instruction.pack(anchor='nw')
        
        self.ripper_dir_button = tk.Button(self.directories_frame, text="Select...", command=self.select_ripper_dir)
        self.ripper_dir_button.pack(anchor='sw')
        
        tk.Label(self.frame.inner, textvariable=self.error_label_text, font=('Helvetica', 9, 'bold'), justify='left').pack(anchor='sw')
        
        self.create_checkboxes()
        
        version_label = tk.Label(self.frame.inner, text="Game Version:", font=('Helvetica', 12, 'normal'), pady=5)
        version_label.pack(anchor='w')
        
        self.version_text = tk.Text(self.frame.inner, height=1, width=8, pady=5)
        self.version_text.pack(anchor='w')
        
        output_dir = tk.Label(self.frame.inner, textvariable=self.output_dir_label, font=('Helvetica', 12, 'normal'), pady=5)
        output_dir.pack(anchor='w')
        
        output_dir_instruction = tk.Label(self.frame.inner, text="- a folder named <Game Version> will be created inside this folder, where files will be written")
        output_dir_instruction.pack(anchor='w')
        
        self.output_dir_button = tk.Button(self.frame.inner, text="Select...", command=self.select_output_dir)
        self.output_dir_button.pack(anchor='w')
        
        self.window.mainloop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, 
                        #filename="sun_haven_ripper_debug.log"
                        )  
    app = SunHavenRipperApp()
    app.start()
  
