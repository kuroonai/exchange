# Building Extension Changer

This document contains instructions for building standalone executables of Extension Changer for Windows, macOS, and Linux (AppImage).

## Prerequisites

- Python 3.7 or higher
- Git (for cloning the repository)
- Internet connection (for downloading dependencies)

## Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Additionally, you'll need platform-specific packaging tools:

- Windows: PyInstaller
- macOS: PyInstaller, create-dmg (optional, for DMG creation)
- Linux: PyInstaller, appimagetool

## Project Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/extension-changer.git
cd extension-changer
```

2. Create a `requirements.txt` file with the following content:
```
PySide6>=6.0.0
```

3. Make sure you have a proper application icon:
   - Windows: `icon.ico` (ICO format)
   - macOS: `icon.icns` (ICNS format)
   - Linux: `icon.png` (PNG format, at least 256x256 pixels)

## Building for Windows

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the executable:
```bash
pyinstaller --name="Extension Changer" --windowed --icon=icon.ico --add-data="icon.ico;." extension_changer.py
```

3. The executable will be in the `dist/Extension Changer` directory.

4. (Optional) Create an installer using NSIS:
   - Install NSIS (Nullsoft Scriptable Install System) from https://nsis.sourceforge.io/
   - Use the provided `installer.nsi` script or create one:
   ```bash
   makensis installer.nsi
   ```

## Building for macOS

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the macOS app bundle:
```bash
pyinstaller --name="Extension Changer" --windowed --icon=icon.icns --add-data="icon.icns:." extension_changer.py
```

3. The app will be in the `dist` directory as `Extension Changer.app`.

4. (Optional) Create a DMG installer:
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Extension Changer" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Extension Changer.app" 200 190 \
  --hide-extension "Extension Changer.app" \
  --app-drop-link 600 185 \
  "Extension Changer.dmg" \
  "dist/Extension Changer.app"
```

## Building for Linux (AppImage)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create a spec file named `extension_changer.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(['extension_changer.py'],
             pathex=[],
             binaries=[],
             datas=[('icon.png', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='extension_changer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='icon.png')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='extension_changer')
```

3. Build with PyInstaller:
```bash
pyinstaller extension_changer.spec
```

4. Create AppDir structure:
```bash
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy application
cp -r dist/extension_changer/* AppDir/usr/bin/

# Create desktop file
cat > AppDir/usr/share/applications/extension-changer.desktop << EOF
[Desktop Entry]
Name=Extension Changer
Exec=extension_changer
Icon=extension-changer
Type=Application
Categories=Utility;
EOF

# Copy icon
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/extension-changer.png
cp icon.png AppDir/extension-changer.png

# Create AppRun file
cat > AppDir/AppRun << EOF
#!/bin/bash
SELF=\$(readlink -f "\$0")
HERE=\${SELF%/*}
export PATH="\${HERE}/usr/bin/:\${PATH}"
"\${HERE}/usr/bin/extension_changer" "\$@"
EOF
chmod +x AppDir/AppRun
```

5. Download and use appimagetool:
```bash
# Download appimagetool
wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
chmod +x appimagetool-x86_64.AppImage

# Create AppImage
./appimagetool-x86_64.AppImage AppDir/ Extension_Changer-x86_64.AppImage
```

6. The AppImage will be created as `Extension_Changer-x86_64.AppImage`.

## Cross-Platform Release Preparation

For a complete release, organize your files as follows:

```
releases/
├── windows/
│   ├── Extension Changer.exe (standalone executable)
│   └── Extension_Changer_Setup.exe (optional installer)
├── macos/
│   ├── Extension Changer.app (app bundle)
│   └── Extension Changer.dmg (optional disk image)
└── linux/
    └── Extension_Changer-x86_64.AppImage
```

## Additional Packaging Options

- **Windows**: Consider using [Inno Setup](https://jrsoftware.org/isinfo.php) as an alternative to NSIS for creating installers.
- **macOS**: Sign your application using `codesign` for distribution.
- **Linux**: Consider creating Debian `.deb` packages or RPM packages for specific distributions.

## Troubleshooting

### Missing Libraries
If you encounter missing library errors when running the built application:

1. Use `--hidden-import` to include missing modules:
```bash
pyinstaller --hidden-import=<module_name> ...
```

2. For Qt-specific issues, ensure PySide6 plugins are included:
```bash
pyinstaller --add-data="<path_to_site-packages>/PySide6/plugins:PySide6/plugins" ...
```

### macOS Code Signing
For distributing on macOS, sign your application:
```bash
codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" "dist/Extension Changer.app"
```

### Linux Dependencies
If your AppImage doesn't run on some Linux distributions, include common libraries in your AppDir:
```bash
mkdir -p AppDir/usr/lib
cp /path/to/needed/library.so AppDir/usr/lib/
```