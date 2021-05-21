# -*- coding: utf-8 -*-
"""
Created on Fri May 21 12:15:59 2021

@author:Naveen Kumar Vasudevan, 
        Doctoral Candidate, 
        The Xi Research Group, 
        Department of Chemical Engineering,
        McMaster University, 
        Hamilton, 
        Canada.
        
        naveenovan@gmail.com
        https://naveenovan.wixsite.com/kuroonai
"""


import PySimpleGUI as sg
import pathlib


firstcolumn = [
    [sg.Text("Input files")],
    [sg.Text("From")],
    [sg.Text("To  ", justification='right')],
    [sg.Text('Progress')],
    ]

secondcolumn = [
    [sg.In(size=(40, 1), enable_events=True, key="IN-files"), sg.FilesBrowse(key="IN-file-browser")],
    [sg.Combo(['from extension'], size=(10,4), key='fromexts')],
    [sg.In(size=(10,4), key='toexts', justification='left')],
    [sg.ProgressBar(1, orientation='h', size=(40, 20), key='progress'), sg.Text( size=(10,1), key='progper')],
    ]

thirdcolumn = [
    [sg.Button('exchange', size=(10,1), key='exchange'),sg.Button('Done', size=(10,1), key='Done')]
    ]


layout = [
    [
        sg.Column(firstcolumn),
        sg.Column(secondcolumn),
        sg.Column(thirdcolumn),
    ]
]



window = sg.Window("Kuroonai's extension changer", layout, icon='Images/logo.ico')

if __name__ == "__main__":
    
    while True:
        event, values = window.read()
        
        if event == "Exit" or event == sg.WIN_CLOSED or event == 'Done':
            break
        
        elif event == "IN-files":
            allfiles = values["IN-files"]
            files = allfiles.split(';')
            extlist = []
            for f in files:
                extlist.append(pathlib.Path(f).suffix)
            extlist = set(extlist)
            extlistback = []
            for ext in extlist:
                extlistback.append(ext)
                window.Element('fromexts').Update(values=extlistback, value=ext, size=(10,4))      
     
        elif event=='exchange':
            fromext = values['fromexts']
            toext = values['toexts']
            
            if not toext.startswith('.') : toext = '.'+toext
            
            progress_bar = window.FindElement('progress')
            progper = window.FindElement('progper')
            
            files = [f for f in files if f.endswith(fromext)]
            for i, f in enumerate(files):
                p = pathlib.Path(f)
                p.rename(p.with_suffix(toext))
                progress_bar.UpdateBar(i+1)
                progper.update('{} of {} done'.format(i+1,len(files)))            
                
    window.close()

