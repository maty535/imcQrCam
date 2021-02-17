#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from requests.structures import CaseInsensitiveDict
import datetime
import os
import pprint as pp 
import csv


api_url  = "https://ekasa.financnasprava.sk/mdu/api/v1/opd/receipt/find"

def getBillInfoFromEkasa(inFileName):
    out = {}
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Connection"]   = "Keep-Alive"
    
    s = requests.Session()
    s.headers.update({"Content-Type":"application/json",
                      "Connection":"Keep-Alive"})
    
    res = None

    with open(inFileName,'r', encoding='utf-8', errors='ignore') as jsonFile:
        data  = json.load(jsonFile)
        rowCount=0
        for q in data:
            v = data[q]
            rowCount+=1
            print("== PROCESSING CODE {}: {}".format(rowCount,v))
            
            reqData = {"receiptId": v}
            try:
                response = s.post(api_url, data=json.dumps(reqData) )
                print("== GOT RESPONSE, STATUS: ",response.status_code)
                if response.status_code == 200:
                    res = json.loads(response.content.decode('utf-8'))
            except Exception as e:
                print(e)
                print("=== Retrying request")
                response = s.post(api_url,  data=json.dumps(reqData))
                print("== GOT RESPONSE, STATUS: ",response.status_code)
                if response.status_code == 200:
                    res = json.loads(response.content.decode('utf-8'))

            if response is not None and response.status_code == 200 and res is not None:
                
                billInfo = res['receipt']
                out[v] = {
                        "ico": billInfo['ico'],
                        "icdph": billInfo['icDph'],
                        "date": billInfo['issueDate'],
                        "totalPrice":billInfo['totalPrice'],
                        "vatAmountBasic":billInfo['vatAmountBasic'],
                        "taxBaseBasic":billInfo['taxBaseBasic'],
                        "vatAmountReduced": billInfo['vatAmountReduced'],
                        "vatRateReduced":billInfo['vatRateReduced']
                }
            elif response.status_code == 739:
                pp.pprint(response.content.decode('utf-8'))
                break
            else:
                pp.pprint(response.content.decode('utf-8'))
                break
                
    s.close()
        
    return out


if __name__ == '__main__':
    outBilllingData = {}
    outBilllingData = getBillInfoFromEkasa('billingData.json')
    with open("billData-output-2.json",'w+') as of:
        json.dump(outBilllingData, of, ensure_ascii=False, indent=4)
        
    with open("billData-output-2.csv",'w+') as of2:
        billCsvWriter = csv.writer(of2, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='"')
        for b in outBilllingData:
            billCsvWriter.writerow(b, outBilllingData[b])
    of.close()    
