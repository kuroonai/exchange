#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extension Changer main entry point
"""

import sys
import os
import importlib.resources
from pathlib import Path
from PySide6.QtWidgets import QApplication

from .extension_changer import ExtensionChanger


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for a consistent look
    
    # Get resource paths - multiple approaches to ensure icon is found
    icon_path = None
    
    # Approach 1: Using importlib.resources (Python 3.7+)
    try:
        # For Python 3.9+
        if hasattr(importlib.resources, 'files'):
            if sys.platform == 'darwin':
                icon_path = importlib.resources.files('extension_changer.resources').joinpath('icon.icns')
            elif sys.platform == 'win32':
                icon_path = importlib.resources.files('extension_changer.resources').joinpath('icon.ico')
            else:
                icon_path = importlib.resources.files('extension_changer.resources').joinpath('icon.png')
        # For Python 3.7-3.8
        else:
            if sys.platform == 'darwin':
                with importlib.resources.path('extension_changer.resources', 'icon.icns') as path:
                    icon_path = path
            elif sys.platform == 'win32':
                with importlib.resources.path('extension_changer.resources', 'icon.ico') as path:
                    icon_path = path
            else:
                with importlib.resources.path('extension_changer.resources', 'icon.png') as path:
                    icon_path = path
    except (ModuleNotFoundError, ImportError, FileNotFoundError) as e:
        print(f"Could not load icon using importlib.resources: {e}")
    
    # Approach 2: Check in current package directory
    if not icon_path or not os.path.exists(str(icon_path)):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resource_dir = os.path.join(current_dir, 'resources')
        
        if sys.platform == 'darwin' and os.path.exists(os.path.join(resource_dir, 'icon.icns')):
            icon_path = os.path.join(resource_dir, 'icon.icns')
        elif sys.platform == 'win32' and os.path.exists(os.path.join(resource_dir, 'icon.ico')):
            icon_path = os.path.join(resource_dir, 'icon.ico')
        elif os.path.exists(os.path.join(resource_dir, 'icon.png')):
            icon_path = os.path.join(resource_dir, 'icon.png')
        else:
            # Try any icon format as last resort
            for icon_name in ['icon.ico', 'icon.png', 'icon.icns']:
                if os.path.exists(os.path.join(resource_dir, icon_name)):
                    icon_path = os.path.join(resource_dir, icon_name)
                    break
    
    # Debug info
    if icon_path:
        print(f"Using icon: {icon_path}")
    else:
        print("No icon found")
    
    window = ExtensionChanger(icon_path)
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())