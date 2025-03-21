# Enhanced Extension Changer

A GUI application for batch changing file extensions with additional advanced features.

## Overview

Enhanced Extension Changer is a Python application that allows you to easily change file extensions for multiple files at once. It combines the functionality of command-line batch processing with the ease of use of a graphical interface.

## Features

- **User-friendly GUI**: Simple, intuitive interface for managing file extensions
- **Multiple Selection Methods**:
  - Select a folder to process all files within it
  - Select specific files individually
- **Smart Extension Detection**: Automatically identifies available extensions from selected files
- **Preview Changes**: See what will happen before applying any changes
- **Advanced Options**:
  - Keep original files (create copies instead of renaming)
  - Configurable multiprocessing with CPU core selection for faster processing
- **Real-time Progress Tracking**: Detailed progress bar and status updates
- **Cancel Operation**: Ability to cancel ongoing operations

## Screenshots

[Add screenshots here once the app is complete]

## Installation

### Requirements

- Python 3.6 or higher
- PySimpleGUI
- tqdm

### Install Dependencies

```bash
# Using pip
pip install PySimpleGUI tqdm

# Or using conda
conda install conda-forge::pysimplegui
pip install tqdm
```

### Download the Application

Clone the repository:

```bash
git clone https://github.com/yourusername/enhanced-extension-changer.git
cd enhanced-extension-changer
```

## Usage

1. Run the application:

```bash
python enhanced_extension_changer.py
```

2. Select files using one of the two methods:
   - Click "Browse" next to "Source:" to select a folder containing files
   - Click "Browse" next to "Or select files:" to select individual files

3. Choose the source extension from the dropdown menu

4. Enter the desired target extension in the "To:" field

5. Optionally adjust advanced settings:
   - Check "Keep original files" to create copies instead of renaming
   - Enable/disable multiprocessing and adjust CPU core usage

6. Click "Preview" to see what changes will be made

7. Click "Convert" to process the files

## Files

- `exc.py` - Main application file
- `exc.ico` - Application icon (must be in the same directory as the script)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original work by Naveen Kumar Vasudevan (naveenovan@gmail.com)
- Enhanced and improved with additional features
