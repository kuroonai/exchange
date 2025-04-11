# Extension Changer (extension_changer)

A cross-platform utility for batch changing file extensions with a modern Qt interface.

![Extension Changer Screenshot](https://raw.githubusercontent.com/kuroonai/exchange/main/screenshots/screenshot.png)

## Features

- Batch rename file extensions
- Option to create copies instead of renaming files
- Preview changes before executing
- Multi-processing support for faster operations
- Advanced options for CPU usage control
- Modern Qt-based interface
- Cross-platform (Windows, macOS, Linux)

## Installation

### Using pip (Recommended)

```bash
pip install extension_changer
```

### Manual Installation

```bash
git clone https://github.com/kuroonai/exchange.git
cd exchange
pip install -e .
```

## Usage

### Command Line

Once installed, you can start the application from the command line:

```bash
extension_changer
```

### Basic Workflow

1. Select a folder or individual files
2. Choose the source extension from the dropdown
3. Specify the target extension
4. Optionally, check "Keep original files" to create copies
5. Click "Preview" to see the changes before applying
6. Click "Convert" to execute the extension change

### Advanced Options

- **Use multiprocessing**: Enable for faster processing of many files
- **CPU cores to use**: Control how many CPU cores to dedicate to the task

## Development

### Requirements

- Python 3.7+
- PySide6 (or PyQt6)

### Setup Development Environment

```bash
git clone https://github.com/kuroonai/exchange.git
cd exchange
pip install -e .
```

## Author

Created by Naveen Vasudevan ([@kuroonai](https://github.com/kuroonai))

## Building from Source

See [BUILDING.md](BUILDING.md) for instructions on building standalone executables for Windows, macOS, and Linux.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.