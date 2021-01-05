#!/usr/bin/env python
"""
This demo can be ran from the project root directory via:
```sh
python src/main.py
```
It can also be ran via p4a/buildozer.
"""
from kivy.app import App
from kivy.lang import Builder
import json
import os

DEMO_APP_KV_LANG = """
#:import ZBarCam kivy_garden.zbarcam.ZBarCam
#:import json json
#:import pp pprint 

BoxLayout:
    orientation: 'vertical'
    ZBarCam:
        id: zbarcam
        # optional, by default checks all types
        code_types: 'QRCODE', 'EAN13' 
    Label:
        size_hint: None, None
        size: self.texture_size[0], 50
        text: ', '.join([str(symbol.data) for symbol in zbarcam.symbols])   
    Label:
        size_hint: None, None
        size: self.texture_size[0], 50
        text: ''.join(json.dumps(zbarcam.allScannedQR, indent=1) )   
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        Button:
            id: scanButton
            text: 'Scan a qrcode'
            disabled: True
            on_release: 
                zbarcam.start()
                scanButton.disabled = True
                stopButton.disabled = False
        Button:
            id: stopButton
            text: 'Stop detection'
            on_release: 
                zbarcam.stop()
                scanButton.disabled = False
                stopButton.disabled = True
        Button:
            id: listButton
            text: 'List'
            disabled: False
            on_release: 
                pass
"""


class DemoApp(App):

    def build(self):
        return Builder.load_string(DEMO_APP_KV_LANG)
    
    def on_start(self):
        try:
            with open("billingData.json",'r') as jsonFile:
                self.root.ids.zbarcam.allScannedQR = json.load(jsonFile)
                jsonFile.close()
        except :
            pass
    
    def on_stop(self):
        #app_folder = os.path.dirname(os.path.abspath(__file__))
        with open("billingData.json",'w+') as of:
            json.dump(self.root.ids.zbarcam.allScannedQR, of, ensure_ascii=False, indent=4)
            of.close()



if __name__ == '__main__':
    DemoApp().run()
