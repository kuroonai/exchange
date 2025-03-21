#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Extension Changer

Based on the original work by Naveen Kumar Vasudevan
"""

import os
import sys
import pathlib
import PySimpleGUI as sg
import multiprocessing
from tqdm import tqdm
from contextlib import contextmanager
import threading
import time

class ExtensionChanger:
    def __init__(self):
        # Set theme
        sg.theme('LightGrey1')
        
        # Define the window's contents
        self.layout = [
            [sg.Text("Extension Changer", font=("Helvetica", 16))],
            [sg.HorizontalSeparator()],
            [sg.Text("Source:", size=(10, 1)), 
             sg.Input(key="folder_path", size=(40, 1), enable_events=True),
             sg.FolderBrowse(key="folder_browser")],
            [sg.Text("Or select files:", size=(10, 1)), 
             sg.Input(key="files_path", size=(40, 1), enable_events=True),
             sg.FilesBrowse(key="files_browser")],
            [sg.HorizontalSeparator()],
            [sg.Frame('Extension Options', [
                [sg.Text("From:", size=(10, 1)), 
                 sg.Combo([], size=(10, 1), key="from_ext", enable_events=True)],
                [sg.Text("To:", size=(10, 1)), 
                 sg.Input(size=(10, 1), key="to_ext")],
                [sg.Checkbox("Keep original files (create copies)", key="keep_original")]
            ])],
            [sg.HorizontalSeparator()],
            [sg.Frame('Advanced Options', [
                [sg.Checkbox("Use multiprocessing (faster for many files)", default=True, key="use_mp")],
                [sg.Text("CPU cores to use:"), 
                 sg.Slider(range=(1, multiprocessing.cpu_count()), default_value=multiprocessing.cpu_count(),
                          orientation='h', size=(15, 15), key="cpu_cores")]
            ], visible=True, key="advanced_frame")],
            [sg.HorizontalSeparator()],
            [sg.Text("Status: Ready", key="status")],
            [sg.ProgressBar(100, orientation='h', size=(50, 20), key="progress")],
            [sg.Text("0/0 files processed", key="progress_text")],
            [sg.HorizontalSeparator()],
            [sg.Button("Convert", key="convert", size=(10, 1)), 
             sg.Button("Preview", key="preview", size=(10, 1)),
             sg.Button("Cancel", key="cancel", size=(10, 1), visible=False),
             sg.Push(), 
             sg.Button("Exit", key="exit", size=(10, 1))]
        ]

        # Create the window
        self.window = sg.Window(
            "Extension Changer", 
            self.layout, 
            finalize=True, 
            icon='exc.ico',  # Use the specified icon
            resizable=True
        )
        
        # Initialize variables
        self.files = []
        self.extensions = set()
        self.processing = False
        self.cancel_operation = False
        
    @contextmanager
    def poolcontext(self, *args, **kwargs):
        pool = multiprocessing.Pool(*args, **kwargs)
        yield pool
        pool.terminate()
        
    def update_extension_list(self):
        """Update the extension dropdown with available extensions"""
        self.extensions = set()
        
        for file in self.files:
            ext = pathlib.Path(file).suffix
            if ext:
                self.extensions.add(ext)
        
        ext_list = sorted(list(self.extensions))
        self.window["from_ext"].update(values=ext_list)
        
        if ext_list:
            self.window["from_ext"].update(value=ext_list[0])
            
    def get_files_with_extension(self, extension):
        """Filter files by extension"""
        return [f for f in self.files if f.endswith(extension)]
    
    def rename_file(self, file_path, from_ext, to_ext, keep_original):
        """Rename a single file's extension"""
        try:
            path = pathlib.Path(file_path)
            if keep_original:
                # Create a copy instead of renaming
                new_path = path.with_suffix(to_ext)
                with open(path, 'rb') as src_file:
                    with open(new_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
            else:
                # Rename the file
                path.rename(path.with_suffix(to_ext))
            return True
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def convert_files(self, files, from_ext, to_ext, keep_original, use_mp, cpu_cores):
        """Convert multiple files, either with multiprocessing or sequentially"""
        if not to_ext.startswith('.'):
            to_ext = '.' + to_ext
            
        success_count = 0
        file_count = len(files)
        
        if use_mp and file_count > 1:
            # Use multiprocessing for multiple files
            with self.poolcontext(processes=int(cpu_cores)) as pool:
                results = []
                for i, file in enumerate(files):
                    if self.cancel_operation:
                        break
                    result = pool.apply_async(
                        self.rename_file, 
                        (file, from_ext, to_ext, keep_original)
                    )
                    results.append(result)
                    
                    # Update progress
                    self.window["progress"].update(current_count=(i+1), max=file_count)
                    self.window["progress_text"].update(f"{i+1}/{file_count} files processed")
                    self.window.refresh()
                
                # Get results
                for result in results:
                    if result.get():
                        success_count += 1
        else:
            # Process files sequentially
            for i, file in enumerate(files):
                if self.cancel_operation:
                    break
                if self.rename_file(file, from_ext, to_ext, keep_original):
                    success_count += 1
                
                # Update progress
                self.window["progress"].update(current_count=(i+1), max=file_count)
                self.window["progress_text"].update(f"{i+1}/{file_count} files processed")
                self.window.refresh()
        
        return success_count
    
    def preview_changes(self, files, from_ext, to_ext):
        """Show a preview of the changes to be made"""
        if not files:
            sg.popup("No matching files found")
            return
        
        if not to_ext.startswith('.'):
            to_ext = '.' + to_ext
            
        preview_list = []
        for file in files[:100]:  # Limit preview to first 100 files
            path = pathlib.Path(file)
            old_name = path.name
            new_name = path.stem + to_ext
            preview_list.append([old_name, new_name])
        
        # Create a popup with a table showing the changes
        if len(files) > 100:
            footer_text = f"Showing first 100 of {len(files)} files"
        else:
            footer_text = f"Showing all {len(files)} files"
            
        layout = [
            [sg.Text(f"Preview of extension changes ({from_ext} → {to_ext})")],
            [sg.Table(
                values=preview_list,
                headings=["Original Filename", "New Filename"],
                auto_size_columns=True,
                display_row_numbers=False,
                justification='left',
                num_rows=min(25, len(preview_list)),
                key='table',
                expand_x=True,
                expand_y=True
            )],
            [sg.Text(footer_text)],
            [sg.Button("Close")]
        ]
        
        preview_window = sg.Window("Preview Changes", layout, modal=True, resizable=True)
        
        while True:
            event, values = preview_window.read()
            if event == "Close" or event == sg.WIN_CLOSED:
                break
                
        preview_window.close()
            
    def process_in_thread(self, files, from_ext, to_ext, keep_original, use_mp, cpu_cores):
        """Process files in a separate thread to keep GUI responsive"""
        self.processing = True
        self.cancel_operation = False
        self.window["convert"].update(visible=False)
        self.window["preview"].update(visible=False)
        self.window["cancel"].update(visible=True)
        self.window["exit"].update(disabled=True)
        self.window["status"].update("Status: Processing...")
        
        success_count = self.convert_files(files, from_ext, to_ext, keep_original, use_mp, cpu_cores)
        
        if self.cancel_operation:
            self.window["status"].update("Status: Operation cancelled")
        else:
            self.window["status"].update(f"Status: Completed - {success_count}/{len(files)} files processed successfully")
        
        self.window["convert"].update(visible=True)
        self.window["preview"].update(visible=True)
        self.window["cancel"].update(visible=False)
        self.window["exit"].update(disabled=False)
        self.processing = False
        
    def run(self):
        """Run the main application loop"""
        # Event Loop to process events
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WIN_CLOSED or event == "exit":
                break
                
            elif event == "folder_path":
                # Get all files in the selected folder
                if values["folder_path"]:
                    try:
                        self.files = [
                            os.path.join(values["folder_path"], f) 
                            for f in os.listdir(values["folder_path"])
                            if os.path.isfile(os.path.join(values["folder_path"], f))
                        ]
                        self.update_extension_list()
                        self.window["status"].update(f"Status: Found {len(self.files)} files in folder")
                        self.window["files_path"].update("")  # Clear the file selection field
                    except Exception as e:
                        sg.popup_error(f"Error accessing folder: {e}")
                        
            elif event == "files_path":
                # Get selected files
                if values["files_path"]:
                    self.files = values["files_path"].split(";")
                    self.update_extension_list()
                    self.window["status"].update(f"Status: Selected {len(self.files)} files")
                    self.window["folder_path"].update("")  # Clear the folder selection field
            
            elif event == "from_ext":
                # Update count of matching files
                if values["from_ext"]:
                    matching_files = self.get_files_with_extension(values["from_ext"])
                    self.window["status"].update(f"Status: {len(matching_files)} files match the selected extension")
            
            elif event == "preview":
                # Show preview of changes
                from_ext = values["from_ext"]
                to_ext = values["to_ext"]
                
                if not from_ext:
                    sg.popup("Please select a source extension first")
                    continue
                    
                if not to_ext:
                    sg.popup("Please enter a destination extension")
                    continue
                
                matching_files = self.get_files_with_extension(from_ext)
                self.preview_changes(matching_files, from_ext, to_ext)
            
            elif event == "convert":
                # Start conversion process
                from_ext = values["from_ext"]
                to_ext = values["to_ext"]
                keep_original = values["keep_original"]
                use_mp = values["use_mp"]
                cpu_cores = values["cpu_cores"]
                
                if not from_ext:
                    sg.popup("Please select a source extension first")
                    continue
                    
                if not to_ext:
                    sg.popup("Please enter a destination extension")
                    continue
                
                matching_files = self.get_files_with_extension(from_ext)
                
                if not matching_files:
                    sg.popup("No files match the selected extension")
                    continue
                
                # Ask for confirmation
                if sg.popup_yes_no(f"Convert {len(matching_files)} files from {from_ext} to {to_ext}?") == "Yes":
                    # Start processing in a separate thread
                    processing_thread = threading.Thread(
                        target=self.process_in_thread,
                        args=(matching_files, from_ext, to_ext, keep_original, use_mp, cpu_cores)
                    )
                    processing_thread.daemon = True
                    processing_thread.start()
            
            elif event == "cancel":
                # Cancel the operation
                if self.processing:
                    self.cancel_operation = True
                    self.window["status"].update("Status: Cancelling...")
        
        # Close the window
        self.window.close()

if __name__ == "__main__":
    app = ExtensionChanger()
    app.run()
