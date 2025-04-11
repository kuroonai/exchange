#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Extension Changer
"""

import os
import sys
import pathlib
import multiprocessing
from contextlib import contextmanager
import threading
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
    QComboBox, QCheckBox, QGroupBox, QSlider, QTableWidget, 
    QTableWidgetItem, QDialog, QScrollArea, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSize
from PySide6.QtGui import QIcon


class ConversionThread(QThread):
    """Worker thread for file conversion operations"""
    progress_updated = Signal(int, int)  # current, total
    status_updated = Signal(str)
    conversion_finished = Signal(int, int)  # success_count, total_count
    
    def __init__(self, files, from_ext, to_ext, keep_original, use_mp, cpu_cores, rename_func):
        super().__init__()
        self.files = files
        self.from_ext = from_ext
        self.to_ext = to_ext
        self.keep_original = keep_original
        self.use_mp = use_mp
        self.cpu_cores = cpu_cores
        self.rename_func = rename_func
        self.cancel = False
        
    @contextmanager
    def poolcontext(self, *args, **kwargs):
        pool = multiprocessing.Pool(*args, **kwargs)
        yield pool
        pool.terminate()
        
    def run(self):
        """Convert files in background thread"""
        if not self.to_ext.startswith('.'):
            self.to_ext = '.' + self.to_ext
            
        success_count = 0
        file_count = len(self.files)
        
        self.status_updated.emit("Processing files...")
        
        if self.use_mp and file_count > 1:
            # Use multiprocessing for multiple files
            with self.poolcontext(processes=int(self.cpu_cores)) as pool:
                results = []
                for i, file in enumerate(self.files):
                    if self.cancel:
                        break
                    result = pool.apply_async(
                        self.rename_func, 
                        (file, self.from_ext, self.to_ext, self.keep_original)
                    )
                    results.append(result)
                    
                    # Update progress
                    self.progress_updated.emit(i+1, file_count)
                
                # Get results
                for result in results:
                    if result.get():
                        success_count += 1
        else:
            # Process files sequentially
            for i, file in enumerate(self.files):
                if self.cancel:
                    break
                if self.rename_func(file, self.from_ext, self.to_ext, self.keep_original):
                    success_count += 1
                
                # Update progress
                self.progress_updated.emit(i+1, file_count)
        
        if self.cancel:
            self.status_updated.emit("Operation cancelled")
        else:
            self.status_updated.emit(f"Completed - {success_count}/{file_count} files processed successfully")
        
        self.conversion_finished.emit(success_count, file_count)


class PreviewDialog(QDialog):
    """Dialog for previewing file changes"""
    def __init__(self, files, from_ext, to_ext, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Changes")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"Preview of extension changes ({from_ext} → {to_ext})")
        layout.addWidget(header_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Original Filename", "New Filename"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        if not to_ext.startswith('.'):
            to_ext = '.' + to_ext
            
        # Limit preview to first 100 files
        preview_files = files[:100]
        self.table.setRowCount(len(preview_files))
        
        for row, file in enumerate(preview_files):
            path = pathlib.Path(file)
            old_name = path.name
            new_name = path.stem + to_ext
            
            self.table.setItem(row, 0, QTableWidgetItem(old_name))
            self.table.setItem(row, 1, QTableWidgetItem(new_name))
        
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)
        
        # Footer
        if len(files) > 100:
            footer_text = f"Showing first 100 of {len(files)} files"
        else:
            footer_text = f"Showing all {len(files)} files"
        footer_label = QLabel(footer_text)
        layout.addWidget(footer_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


class ExtensionChanger(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Extension Changer")
        self.setMinimumSize(600, 500)
        
        # Set icon if available
        try:
            self.setWindowIcon(QIcon("exc.ico"))
        except:
            pass  # Ignore if icon file not found
        
        # Initialize variables
        self.files = []
        self.extensions = set()
        self.processing = False
        self.worker_thread = None
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Extension Changer")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator1)
        
        # Source section
        source_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        source_label.setMinimumWidth(80)
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        browse_folder_button = QPushButton("Browse Folder")
        browse_folder_button.clicked.connect(self.browse_folder)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.folder_path)
        source_layout.addWidget(browse_folder_button)
        main_layout.addLayout(source_layout)
        
        # Files section
        files_layout = QHBoxLayout()
        files_label = QLabel("Or select files:")
        files_label.setMinimumWidth(80)
        self.files_path = QLineEdit()
        self.files_path.setReadOnly(True)
        browse_files_button = QPushButton("Browse Files")
        browse_files_button.clicked.connect(self.browse_files)
        
        files_layout.addWidget(files_label)
        files_layout.addWidget(self.files_path)
        files_layout.addWidget(browse_files_button)
        main_layout.addLayout(files_layout)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator2)
        
        # Extension options group
        ext_group = QGroupBox("Extension Options")
        ext_layout = QVBoxLayout()
        
        # From extension
        from_layout = QHBoxLayout()
        from_label = QLabel("From:")
        from_label.setMinimumWidth(80)
        self.from_ext = QComboBox()
        self.from_ext.currentIndexChanged.connect(self.update_matching_files)
        
        from_layout.addWidget(from_label)
        from_layout.addWidget(self.from_ext)
        from_layout.addStretch()
        ext_layout.addLayout(from_layout)
        
        # To extension
        to_layout = QHBoxLayout()
        to_label = QLabel("To:")
        to_label.setMinimumWidth(80)
        self.to_ext = QLineEdit()
        
        to_layout.addWidget(to_label)
        to_layout.addWidget(self.to_ext)
        to_layout.addStretch()
        ext_layout.addLayout(to_layout)
        
        # Keep original checkbox
        self.keep_original = QCheckBox("Keep original files (create copies)")
        ext_layout.addWidget(self.keep_original)
        
        ext_group.setLayout(ext_layout)
        main_layout.addWidget(ext_group)
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator3)
        
        # Advanced options group
        adv_group = QGroupBox("Advanced Options")
        adv_layout = QVBoxLayout()
        
        # Multiprocessing checkbox
        self.use_mp = QCheckBox("Use multiprocessing (faster for many files)")
        self.use_mp.setChecked(True)
        adv_layout.addWidget(self.use_mp)
        
        # CPU cores slider
        cores_layout = QHBoxLayout()
        cores_label = QLabel("CPU cores to use:")
        self.cpu_cores = QSlider(Qt.Horizontal)
        self.cpu_cores.setMinimum(1)
        self.cpu_cores.setMaximum(multiprocessing.cpu_count())
        self.cpu_cores.setValue(multiprocessing.cpu_count())
        self.cores_value = QLabel(str(self.cpu_cores.value()))
        
        self.cpu_cores.valueChanged.connect(lambda v: self.cores_value.setText(str(v)))
        
        cores_layout.addWidget(cores_label)
        cores_layout.addWidget(self.cpu_cores)
        cores_layout.addWidget(self.cores_value)
        adv_layout.addLayout(cores_layout)
        
        adv_group.setLayout(adv_layout)
        main_layout.addWidget(adv_group)
        
        # Separator
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.HLine)
        separator4.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator4)
        
        # Status section
        self.status_label = QLabel("Status: Ready")
        main_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # Progress text
        self.progress_text = QLabel("0/0 files processed")
        main_layout.addWidget(self.progress_text)
        
        # Separator
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.HLine)
        separator5.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator5)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_changes)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setVisible(False)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.convert_button)
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(buttons_layout)
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path.setText(folder_path)
            self.files_path.clear()  # Clear files selection
            
            try:
                self.files = [
                    os.path.join(folder_path, f) 
                    for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))
                ]
                self.update_extension_list()
                self.status_label.setText(f"Status: Found {len(self.files)} files in folder")
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Error accessing folder: {e}")
    
    def browse_files(self):
        """Open file browser dialog"""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            self.files = files
            self.files_path.setText(f"{len(files)} files selected")
            self.folder_path.clear()  # Clear folder selection
            
            self.update_extension_list()
            self.status_label.setText(f"Status: Selected {len(self.files)} files")
    
    def update_extension_list(self):
        """Update the extension dropdown with available extensions"""
        self.extensions = set()
        
        for file in self.files:
            ext = pathlib.Path(file).suffix
            if ext:
                self.extensions.add(ext)
        
        self.from_ext.clear()
        ext_list = sorted(list(self.extensions))
        self.from_ext.addItems(ext_list)
        
        if ext_list:
            self.from_ext.setCurrentIndex(0)
    
    def update_matching_files(self):
        """Update count of matching files"""
        current_ext = self.from_ext.currentText()
        if current_ext:
            matching_files = self.get_files_with_extension(current_ext)
            self.status_label.setText(f"Status: {len(matching_files)} files match the selected extension")
    
    def get_files_with_extension(self, extension):
        """Filter files by extension"""
        return [f for f in self.files if f.endswith(extension)]
    
    @staticmethod
    def rename_file(file_path, from_ext, to_ext, keep_original):
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
    
    def preview_changes(self):
        """Show preview of changes"""
        from_ext = self.from_ext.currentText()
        to_ext = self.to_ext.text()
        
        if not from_ext:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a source extension first")
            return
            
        if not to_ext:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please enter a destination extension")
            return
        
        matching_files = self.get_files_with_extension(from_ext)
        if not matching_files:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Info", "No files match the selected extension")
            return
        
        preview_dialog = PreviewDialog(matching_files, from_ext, to_ext, self)
        preview_dialog.exec()
    
    def start_conversion(self):
        """Start the conversion process"""
        from_ext = self.from_ext.currentText()
        to_ext = self.to_ext.text()
        
        if not from_ext:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a source extension first")
            return
            
        if not to_ext:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please enter a destination extension")
            return
        
        matching_files = self.get_files_with_extension(from_ext)
        
        if not matching_files:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Info", "No files match the selected extension")
            return
        
        # Ask for confirmation
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "Confirm Conversion", 
            f"Convert {len(matching_files)} files from {from_ext} to {to_ext}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Update UI for processing
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(matching_files))
            self.progress_text.setText(f"0/{len(matching_files)} files processed")
            
            self.convert_button.setVisible(False)
            self.preview_button.setVisible(False)
            self.cancel_button.setVisible(True)
            self.exit_button.setEnabled(False)
            
            # Create and start worker thread
            self.worker_thread = ConversionThread(
                matching_files,
                from_ext,
                to_ext,
                self.keep_original.isChecked(),
                self.use_mp.isChecked(),
                self.cpu_cores.value(),
                self.rename_file
            )
            
            # Connect signals
            self.worker_thread.progress_updated.connect(self.update_progress)
            self.worker_thread.status_updated.connect(self.update_status)
            self.worker_thread.conversion_finished.connect(self.conversion_finished)
            
            self.worker_thread.start()
            self.processing = True
    
    def cancel_operation(self):
        """Cancel the current operation"""
        if self.processing and self.worker_thread:
            self.worker_thread.cancel = True
            self.status_label.setText("Status: Cancelling...")
    
    @Slot(int, int)
    def update_progress(self, current, total):
        """Update progress bar and text"""
        self.progress_bar.setValue(current)
        self.progress_bar.setMaximum(total)
        self.progress_text.setText(f"{current}/{total} files processed")
    
    @Slot(str)
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(f"Status: {status}")
    
    @Slot(int, int)
    def conversion_finished(self, success_count, total_count):
        """Handle conversion completion"""
        self.convert_button.setVisible(True)
        self.preview_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.exit_button.setEnabled(True)
        self.processing = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for a consistent look
    
    window = ExtensionChanger()
    window.show()
    
    sys.exit(app.exec())