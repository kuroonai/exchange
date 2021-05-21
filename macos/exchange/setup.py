from setuptools import setup

APP=['exchange.py']
OPTIONS={'argv_emulation':True, 'iconfile':'/Users/kuroonai/Downloads/macos/kcc.icns'}
setup(
   name='exchange',
   version='1.0',
   description="Kuroonai's Caesar cipher for text",
   author='Naveen Vasudevan',
   author_email='naveenovan@gmail.com',
   packages=['exchange'],  #same as name
   install_requires=['PySimpleGUI','pathlib'], #external packages as dependencies
   app=APP,
   options={'py2app':OPTIONS},
   setup_requires=['py2app']
)