
from .models import *
import pandas as pd
import operator
import re 
import numpy as np
from openpyxl import load_workbook
from dotenv import load_dotenv
import os
import shutil
from .purchase_report import PurchaseReportClass
class ReportCalculation:
    #*kwargs(df=df)
    def __init__(self, file=None, df=None,excel_date=None,supp=None):
        self.supp=supp
        self.operator=["+", "-", "*", "/"]
        #'0','1','2','3','4','5','6','7','8','9'
        # self.supp=NewSupplier.objects.get(id=24)
        self.cases=Cases.objects.filter(supplier=self.supp).values('min','max','profit')
        self.gst=Cases.objects.filter(supplier=self.supp).first()
        self.gst=self.gst.gst
        self.supplier_name=self.supp.supplier_name
        self.mapped_col = self.supp.supplier_mapp_col
        self.col_list = self.supp.supplier_col
        self.equation=[]
        self.direct=[]
        load_dotenv()
        self.template_path=os.getenv("workbook_path")
        self.equation_token_mapp={}
        self.extractExpression()
        #---------------------------
        #self.read_excel()
        if df is not None:
            self.df=df
        if file is not None:
            self.filepath=file
        if excel_date is not None:
            self.excel_date=excel_date

    def get_equation(self):
        return self.equation
    
    def get_direct(self):
        return self.direct
    
    def extractExpression(self):
        self.sorted_data = {key: self.mapped_col.get(key, "") for key in default_mapping().keys()}
        for key, value in self.sorted_data.items():
            if any(op in value for op in self.operator):
                self.equation.append(key)
            else:
                self.direct.append(key)
    
    def read_excel(self,):
        df = pd.read_excel("196_Invoice_4321420874.xlsx")
        self.df=df

    def exportToExcel(self):
        self.sample=pd.DataFrame()
        for key,value in default_mapping().items():
            self.sample[key] = self.combine_report[key]
        self.sample['Supplier'] = self.combine_report['supplier']
        self.sample['DATE'] = self.combine_report['maildate']
        self.sample['PROFIT%'] = self.combine_report['PROFIT_per']


        filepathname = os.path.join(self.filepath, f"{self.excel_date}_PurchaseReport.xlsx")
        if os.path.exists(filepathname):
            self.wb = load_workbook(filepathname)
           
        else:
            self.wb = load_workbook(self.template_path, data_only=True)

        ws = self.wb.active
        headers = [cell.value for cell in ws[4]] 
        # print("Columns ", headers)
        start_row = ws.max_row + 1
        for r_idx, row in enumerate(self.sample.to_dict('records'), start=start_row):
            for c_idx, header in enumerate(headers, start=1):
                if header == "S.NO":
                    ws.cell(row=r_idx, column=c_idx, value=r_idx - 4)
                elif header in row:
                    ws.cell(row=r_idx, column=c_idx, value=row[header])

        self.wb.save(filepathname)
        self.wb.close()
        # PurchaseReportClass.copyToRemoteFolder(source_folder=self.filepath)
        return self.sample
        #return self.wb
        #self.sample.to_excel(f"{self.supplier_name}.xlsx", index=False)
    
    def getProcessedReport(self):
        return self.sample

    def findProfit(self):
        self.combine_report['ACTUAL PRICE']

        def findpro(value):     
            for i in self.cases:
                if int(i['min']) < value <=int(i['max']):
                    return round(float(i['profit'])/100 * value,2)
            return None
        
        def findper(value):
            for i in self.cases:
                if int(i['min']) < value <=int(i['max']):
                    return i['profit']+' %'
            return None
        
        self.combine_report["PROFIT%"] = self.combine_report["ACTUAL PRICE"].apply(findpro)

        self.combine_report["PROFIT_per"] = self.combine_report["ACTUAL PRICE"].apply(findper)

    def findGst(self):
        def findgst(value):
            gst=float(self.gst)/100
            return round((value * gst),2)
        
        self.combine_report["GST"] = self.combine_report["SELLING PRICE(Exc.GST)"].apply(findgst)


    def split_formula(self,formula, columns):
        # Sort columns by length (to avoid partial matches, e.g., PRICE inside TOTAL PRICE)
        sorted_cols = sorted(columns, key=len, reverse=True)
        # Escape regex special characters in column names
        escaped_cols = [re.escape(col) for col in sorted_cols]
        # Regex: match column OR operator (+, -, *, /, parentheses, %)
        pattern = r'(' + '|'.join(escaped_cols) + r'|\+|\-|\*|\/|\(|\)|%)'
        tokens = [t.strip() for t in re.findall(pattern, formula) if t.strip()]
        return tokens


    def MappToPurchaseReport(self):
        #create purachase report dataframe
        self.report=pd.DataFrame(columns=list(self.mapped_col.keys()))
        mergelst=list(self.mapped_col.keys()) + (list(self.df.columns))
        #create comined columns of supplier report and purchase report 
        self.combine_report=pd.DataFrame(columns=mergelst)
        #insert data from supplier df into combined df
        for i in list(self.df.columns):
            self.combine_report[i]=self.df[i]
        
        for key,value in self.sorted_data.items():

            if key in self.direct:
                    if value in self.df.columns:
                        self.report[key] = self.df[value]
                        #insert data from purchase report df to combined df
                        self.combine_report[key]=self.df[value]

                        if key == 'ACTUAL PRICE':
                            self.findProfit()

                        if key == 'SELLING PRICE(Exc.GST)':
                            self.findGst()
            
            if key in self.equation:
                #for i in sorted(self.combine_report.columns, key=len,reverse=True):
                sorted_cols = sorted(list(self.combine_report.columns), key=len, reverse=True)
                escaped_cols = [re.escape(col) for col in sorted_cols]

                # Add regex for numbers: \d+(?:\.\d+)?  (matches 10, 3.5, etc.)
                pattern = r'(' + '|'.join(escaped_cols) + r'|\+|\-|\*|\/|\(|\)|%|\d+(?:\.\d+)?)'
                tokens = [t.strip() for t in re.findall(pattern, value) if t.strip()]
                tokens = ' '.join([f"pd.to_numeric(self.combine_report['{i}'], errors='coerce')" if i in list(self.combine_report.columns) else i for i in tokens])
                self.equation_token_mapp[key]=tokens
                self.combine_report[key] =  eval(self.equation_token_mapp[key]).round(2)

                if key == 'ACTUAL PRICE':
                        self.findProfit()

                if key == 'SELLING PRICE(Exc.GST)':
                        self.findGst()

                # for i in tokens:
                #     if i in list(self.combine_report.columns):
                #         value=value.replace(i,f"df['{i}']")
                
            
        #print(self.equation)
            # if key in self.equation:
            #     print("value",key)
                
            #     print("Add:", self.ops["+"](a, b))  
                
            #     print("operant:",[i for i in self.report.columns if i in value])
            #     print("operator:",[i for i in self.operator if i in value])
        #self.report.to_excel("output.xlsx", index=False)
        #self.combine_report.to_excel("output2.xlsx", index=False)
        #print(self.equation_token_mapp)
        # print(self.combine_report['ACTUAL PRICE'])
        print("--------------------------------------------------")
    

