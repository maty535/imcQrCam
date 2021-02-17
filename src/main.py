#!/usr/bin/env python
"""
This demo can be ran from the project root directory via:
```sh
python src/main.py
```
It can also be ran via p4a/buildozer.
"""
import pprint as pp 
import json
import datetime
import os
import requests
from requests.structures import CaseInsensitiveDict

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.lang import Builder

from kivy.network.urlrequest import UrlRequest
from kivy.factory import Factory
from kivy.properties import (ObjectProperty, ListProperty, StringProperty,NumericProperty, DictProperty)

from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behaviour to the view. """
    pass

class CodeDetailButton(Button):
    
    def print_data(self, data):
        print(data)
    
    def print_data(self, qrCode):
        print("Qr id: {} ".format(qrCode))
        
    def on_press(self):
        try:
            QrScannerApp.get_running_app().root.show_qr_details(self.qrData)
        except AttributeError:
            details = QrScannerApp.get_running_app().root.read_qr_details(self.text)
            if details is not None:
                self.qrData =  details
                self.text = "{} ({}€)".format(details['orgName'], details['totalPrice'])
                self.totalPrice = details['totalPrice']
                self.date = details['date']
                QrScannerApp.get_running_app().root.qrCodesView.qrList.refresh_from_layout()
                QrScannerApp.get_running_app().root.show_qr_details(self.qrData)
            
            
        

class CamView(BoxLayout):
    pass

class CodeDetailView(BoxLayout):
    code =  DictProperty()
    items_container = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(CodeDetailView, self).__init__(**kwargs)
        self.code['orgName']     = ""
        self.code['totalPrice']  = ""
        self.code['date']        = ""
        self.code['unitName']    = ""    
        self.code['vatAmountBasic']  = ""
        self.code['vatAmountReduced'] = ""    
        
    
    def codeSelected(self):
        pass
        

        
class QRCodesView(BoxLayout):
    qrList = ObjectProperty()
    

class QrScannerRoot(BoxLayout):
    carousel     = ObjectProperty()
    qrCodesView  = ObjectProperty()
    camView      = ObjectProperty()
    detailView   = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(QrScannerRoot, self).__init__(**kwargs)
        self.qrcodesSet = set()
    
    def addNewScanedCode(self, code):
            
        self.qrCodesView.qrList.data.append(
                {'text': "{}".format(code)}
        )
        print("==== CODEs Saved: {}", len(self.qrCodesView.qrList.data) )
        
        self.qrCodesView.qrList.refresh_from_data()
    
    def show_qr_details(self, code):
        print("==== CODE: ", code)
        self.detailView.code = code
        self.detailView.items_container.clear_widgets()
        for i in code['items']:
            v = i['name']
            self.detailView.items_container.add_widget(Label(text=v, text_size=(250, 100)))
            v = "{} €".format(i['price'])
            self.detailView.items_container.add_widget(Label(text=v, text_size=(250, 100)))
        
        if self.carousel:
            self.carousel.load_slide(self.detailView)

    def read_qr_details(self, qrId):
        code = None
        print("==== READ DATA FOR CODE: ", qrId)
        respInfo = self.getBillInfoFromEkasa(qrId)
        print("==== READ DATA DONE: ", qrId)
        
        if respInfo is not None:
            billInfo = respInfo['receipt']
            code = {
                "orgName" : billInfo['organization']['name'],
                "unitName": "{} {},{} {}".format(billInfo['unit']['streetName'],billInfo['unit']['propertyRegistrationNumber'], 
                                                billInfo['unit']['postalCode'], billInfo['unit']['municipality'] ),
                "ico": billInfo['ico'],
                "icdph": billInfo['icDph'],
                "date": billInfo['issueDate'],
                "totalPrice":billInfo['totalPrice'],
                "vatAmountBasic":billInfo['vatAmountBasic'],
                "taxBaseBasic":billInfo['taxBaseBasic'],
                "vatAmountReduced": billInfo['vatAmountReduced'],
                "vatRateReduced":billInfo['vatRateReduced'],
                "items": billInfo['items']
            }
            return code 
        
            self.qrCodesView.qrList.data.remove(text=qrId)
            self.qrCodesView.qrList.data.append(
                {   'text': "{} ({}€)".format(code['orgName'], code['totalPrice']) ,
                    'totalPrice':   code['totalPrice'], 
                    'date':         code['date'],
                    'qrData':       code  
                }
            )
            self.qrCodesView.qrList.refresh_from_data()
        
        
    def getDetailsFromEkasa(self):
        print("==== START FETCHING not populated data from eKasa ====== ")
        for q in self.qrCodesView.qrList.data:
            q.qrData 
        
        # self.qrCodesView.qrList.data.append(
        #         {   'text': "{} ({}€)".format(code['orgName'], code['totalPrice']) ,
        #             'totalPrice':   code['totalPrice'], 
        #             'date':         code['date'],
        #             'qrData':       code  
        #         }
        # )
        # self.qrCodesView.qrList.refresh_from_data()
            
            
    def show_scannedCodes(self):
        self.qrCodesView.qrList.refresh_from_data() 
        if self.carousel:
            self.carousel.load_slide(self.qrCodesView)
            
    def show_camera(self):
        
        if self.carousel:
            self.carousel.load_slide(self.camView)
    
    def getBillInfoFromEkasa(self, qrId):
        out      = None
        config   = QrScannerApp.get_running_app().config
        api_url  = config.get("General", "ekasa_url").lower()
        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        reqData = {"receiptId": qrId}
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(reqData) )
            print("== RESPONSE STATUS: {}",response.status_code)
            if response.status_code == 200:
                out = json.loads(response.content.decode('utf-8'))
        except Exception as e:
            print(e)
            
        return out
        
    
    def billInfo_retrieved(self, req, data):
        billInfo = json.loads(data.decode()) if not isinstance(data, dict) else data    
        code = {
                "orgName" : billInfo['organization']['name'],
                "unitName": "{} {},{} {}".format(billInfo['unit']['streetName'],billInfo['unit']['propertyRegistrationNumber'], 
                                                billInfo['unit']['postalCode'], billInfo['unit']['municipality'] ),
                "ico": billInfo['ico'],
                "icdph": billInfo['icDph'],
                "date": billInfo['issueDate'],
                "totalPrice":billInfo['totalPrice'],
                "vatAmountBasic":billInfo['vatAmountBasic'],
                "taxBaseBasic":billInfo['taxBaseBasic'],
                "vatAmountReduced": billInfo['vatAmountReduced'],
                "vatRateReduced":billInfo['vatRateReduced'],
                "items": billInfo['items']
            }
        self.qrCodesView.qrList.data.append(
                {   'text': "{} ({}€)".format(code['orgName'], code['totalPrice']) ,
                    'totalPrice':   code['totalPrice'], 
                    'date':         code['date'],
                    'qrData':       code  
                }
        )
        self.qrCodesView.qrList.refresh_from_data()
        return data    

class QrScannerApp(App):
    title = 'Imcontec QR čítačka bločkov'

    def build_config(self, config):
        config.setdefaults('General', {'ekasa_mode': "Batch"})
        config.setdefaults('General', {'ekasa_url': "https://ekasa.financnasprava.sk/mdu/api/v1/opd/receipt/find"})
        
    def build_settings(self, settings):
        settings.add_json_panel("Finančná správa", self.config, data="""
            [
                {"type": "options",
                    "title": "Spôsob práce s eKasou Finančnej správy",
                    "section": "General",
                    "key": "ekasa_mode",
                    "options": ["Online", "Batch"]
                },
                {   "type": "string",
                    "title": "Url Finančnej správy pre eKasu",
                    "section": "General",
                    "key": "ekasa_url"
                }
            ]"""
            )
               

    def build(self):
        return QrScannerRoot()
    
    def on_start(self):
        data = {}
        
        try:
            with open("billingData.json",'r', encoding='utf-8', errors='ignore') as jsonFile:
                data  = json.load(jsonFile)
                for q in data:
                    v = data[q]
                    self.root.qrCodesView.qrList.data.append(
                        { 'text': v}
                    )
                    
                    # self.root.qrCodesView.qrList.data.append(
                    #     {   'text': "{} ({}€)".format(v['orgName'], v['totalPrice']) ,
                    #         'totalPrice':   v['totalPrice'], 
                    #         'date':         v['date'] ,
                    #         'qrData':       v
                    #     }
                    # )
                
                self.root.camView.ids.zbarcam.allScannedQR = data
                self.root.qrCodesView.qrList.refresh_from_data() 
                jsonFile.close()
        except Exception as e:
            print("==== Type error: " + str(e))
    
    def on_stop(self):
        #app_folder = os.path.dirname(os.path.abspath(__file__))
        with open("billingData.json",'w+') as of:
            cam = self.root.camView.ids.zbarcam
            if cam.allScannedQR and len(cam.allScannedQR) > 0:
                json.dump(cam.allScannedQR, of, ensure_ascii=False, indent=4)
            of.close()

if __name__ == '__main__':
    from kivy.config import Config
    QrScannerApp().run()


