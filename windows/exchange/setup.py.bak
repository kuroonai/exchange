from setuptools import setup

APP=['kcctext.py']
OPTIONS={'argv_emulation':True, 'iconfile':'/Users/kuroonai/Downloads/macos/kcc.icns'}
setup(
   name='kcctext',
   version='1.0',
   description="Kuroonai's Caesar cipher for text",
   author='Naveen Vasudevan',
   author_email='naveenovan@gmail.com',
   packages=['kcctext'],  #same as name
   install_requires=['PySimpleGUI','clipboard'], #external packages as dependencies
   app=APP,
   options={'py2app':OPTIONS},
   setup_requires=['py2app']
)