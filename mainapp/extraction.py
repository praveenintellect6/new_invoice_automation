import pdfplumber
import re
import pandas as pd
import os
from fileinput import filename
from .models import *
from .purchase_report import PurchaseReportClass

class Extarction:
    def __init__(self):
        self.supplier_obj=SupplierSelection()
        self.supplier=''
        self.filepath=''
        self.maildate=''
    
    def scrapping(self,filepath=None,maildate=None):
        self.filepath=filepath
        self.filename=os.path.basename(filepath)
        self.maildate=maildate
        start_point=False
        text_list = []
        with pdfplumber.open(filepath) as pdf:
                    count = 0
                    for i, page in enumerate(pdf.pages):
                        try:
                            text = page.extract_text()
                            if text:
                                for line in text.splitlines():

                                    if not self.supplier:
                                        self.supplier=self.supplier_obj.setSupplier(line)

                                    if self.supplier:
                                        if self.supplier.start_key in line:
                                            start_point=True
                                            continue

                                        if self.supplier.end_key in line:
                                            start_point=False
                                            break

                                        if start_point == True:
                                            text_list.append(line)
                                            
                        except Exception as e:
                            print(f"Error Extracting Text from Page {i + 1}: {e}\n\n")
        if self.supplier:
            df1=self.supplier.extractInvoice(text_list,filename=self.filename,maildate=self.maildate)
            return df1
        else:
            return None             
        
class SupplierSelection:
    def __init__(self):
        self.wuth=Wurth()
        self.mcgrath=JohnMcGrath()
        self.yhi=Yhi()
        self.repco=Repco()

    def setSupplier(self,line):
        if self.wuth.invoice_selection_key in line:
            return self.wuth
        if self.mcgrath.invoice_selection_key in line:
            return self.mcgrath
        if self.yhi.invoice_selection_key in line:
            return self.yhi
        if self.repco.invoice_selection_key in line:
            return self.repco
        
class Wurth:
    invoice_selection_key="SUA_BOS_F_DS/EUW/"
    start_key="Delivery address Provident Motors Pty Ltd"
    end_key="Your payment terms"

    def __init__(self):
        pass

    def extractInvoice(self,text_list=None,filename=None,maildate=None):
        if text_list is not None:
            self.text_list=text_list
            df1=self.extract(filename=filename,maildata=maildate)
            return df1
        
    def extract(self,filename=None,maildata=None):        
        supplier_name="Wurth"
        itemno=[]
        item_description=[]
        customer_part_no=[]
        Ext_Net_Price_AUD=[]
        Price_Unit=[]
        Price_AUD=[]
        Quantity=[]
        Pack_Unit=[]
        ttt=[i.split() for i in self.text_list]
        def filter_numeric_only(data):
                pattern =  re.compile(r'^\d+(\.\d+)?$')  # Match integer or decimal numbers
                result = []
                unknown= []
                for row in data:
                    filtered_row = [item for item in row if pattern.fullmatch(item)]
                    filtered_row2 = [item for item in row if not pattern.fullmatch(item)]
                    result.append(filtered_row)
                    result.append(filtered_row2)
                return result
        result=filter_numeric_only(ttt)
        result=[i for i in result if i]
        pattern = re.compile(r'^\d+(\.\d+)?$')
        newresult=[]
        for i in range(len(result)):
            if len(result[i])==1 and pattern.fullmatch(result[i][0]):
                pass
            else:
                newresult.append(result[i])

        numberlist=[]#list contain only numbers
        finalresult=[]#list contains itemdescription and customer parts no
        for i in range(len(newresult)):
            k = True
            for j in newresult[i]:
                if not pattern.fullmatch(j):
                    k = False
            if k == True:
                if len(newresult[i]) > 6:
                    del newresult[i][0]
                    numberlist.append(newresult[i])
                    finalresult.append(newresult[i+1])
                    finalresult.append(newresult[i+2])
        item_description=[' '.join(finalresult[i]) for i in range(0,len(finalresult),2)]
        customer_part_no=[' '.join(finalresult[i]) for i in range(1,len(finalresult),2)]
        Ext_Net_Price_AUD=[i[len(i)-1] for i in numberlist]
        Price_Unit=[i[len(i)-2] for i in numberlist]
        Price_AUD=[i[len(i)-3] for i in numberlist]
        Quantity=[i[len(i)-4] for i in numberlist]
        Pack_Unit=[i[len(i)-5] for i in numberlist]
        itemno=[i[0] for i in numberlist]
        max_len = max(len(itemno),len(item_description),len(customer_part_no),len(Pack_Unit),len(Quantity),len(Price_AUD),len(Price_Unit),len(Ext_Net_Price_AUD))
        def pad(lst):
            return lst + [""] * (max_len - len(lst))
        df1=pd.DataFrame({
            # "filePath":[filename for i  in range(len(pad(itemno)))],
            "supplier":[supplier_name for i in range(len(pad(itemno)))],
            "maildate":[maildata for i in range(len(pad(itemno)))],
            "Item Number":pad(itemno),
            "Item Description":pad(item_description),
            "customer_part_no":pad(customer_part_no),
            "Ext. Net Price AUD":pad(Ext_Net_Price_AUD),
            "Price_Unit":pad(Price_Unit),
            "Price AUD":pad(Price_AUD),
            "Quantity":pad(Quantity),
            "Pack_Unit":pad(Pack_Unit)
        })
        name, ext = os.path.splitext(filename)
        folder_path = PurchaseReportClass().createFolderByDate(maildata)
        real_path=os.path.join(folder_path,name)
        df1.to_excel(f"{real_path}.xlsx", index=False)
        return df1
        
class JohnMcGrath:
    invoice_selection_key="McGrath Canberra Pty Ltd"
    start_key="Ordered B.O. Supplied"
    end_key="CONDITIONS OF SALE"

    def __init__(self):
        pass

    def extractInvoice(self,text_list=None,filename=None,maildate=None):
        if text_list is not None:
            self.text_list=text_list
            df1=self.extract(filename=filename,maildata=maildate)
            return df1

    def extract(self,filename=None,maildata=None): 
        mmm=self.text_list
        supplier_name="John McGrath"
        location= []
        part_Number= []
        description= []
        ordered= []
        supplied= []
        unit_List= []
        unit_Net= []
        GST_Code= []
        total= []
        def filter_numeric_only(data):
            pattern = re.compile(r'^\d+(\.\d+)?$')  # Match integer or decimal numbers
            result = []
            unknown= []
            for row in data:
                filtered_row = [item for item in row if pattern.fullmatch(item)]
                filtered_row2 = [item for item in row if not pattern.fullmatch(item)]
                result.append(filtered_row)
                unknown.append(filtered_row2)
            return result,unknown
        # mmm=mmm[1:len(mmm)-1]
        print(mmm)
        mmm=[i.split() for i in mmm]
        
       
        classified_data,unknown = filter_numeric_only(mmm)
        classified_data2= []
        for i in classified_data:
            if len(i)==7:
                del i[3]
            if not i:
                i=[0,0,0,0,0,0]
            classified_data2.append(i)
        classified_data=classified_data2
        classified_data=[ i[1:] for i in classified_data]
        unknown=[i for i in unknown]
        ordered=[i[0] for i in classified_data]
        supplied=[i[1] for i in classified_data]
        unit_List= [i[2] for i in classified_data]
        unit_Net=[i[3] for i in classified_data]
        total=[i[4] for i in classified_data]
        location=[i[0] for i in unknown]
        part_Number=[i[1] for i in unknown]
        GST_Code=[i[len(i)-1] for i in unknown]
        description=[' '.join(i[2:len(i)-1]) for i in unknown]
        max_len = max(len(location),len(part_Number),len(description),len(ordered),len(supplied),len(unit_List),len(unit_Net),len(GST_Code),len(total))
        def pad(lst):
            return lst + [""] * (max_len - len(lst))
        df1=pd.DataFrame({
            # "filePath":[f'{filename}' for i  in range(len(pad(location)))],
            "supplier":[f'{supplier_name}' for i in range(len(pad(location)))],
            "maildate":[maildata for i in range(len(pad(location)))],
            "location": pad(location),
            "Part Number": pad(part_Number),
            "Description":pad(description),
            "Quantity Ordered":pad(ordered),
            "Quantity Supplied":pad(supplied),
            "Unit List":pad(unit_List),
            "unit_Net":pad(unit_Net),
            "GST_Code":pad(GST_Code),
            "Total":pad(total)
        })
        name, ext = os.path.splitext(filename)
        folder_path = PurchaseReportClass().createFolderByDate(maildata)
        real_path=os.path.join(folder_path,name)
        df1.to_excel(f"{real_path}.xlsx", index=False)
        return df1

class Yhi:
    invoice_selection_key="Aust Capital Terr Australia"
    start_key="S/N CODE DESCRIPTION QUANTITY UNIT PRICE AMOUNT"
    end_key="SUBTOTAL"

    def __init__(self):
        pass

    def extractInvoice(self,text_list=None,filename=None,maildate=None):
        if text_list is not None:
            self.text_list=text_list
            df1=self.extract(filename=filename,maildata=maildate)
            return df1

    def extract(self,filename=None,maildata=None): 
        aaa=self.text_list 
        supplier_name="YHI"
        CODE= []
        DESCRIPTION= []
        QUANTITY= []
        UNIT_PRICE= []
        AMOUNT= []
        aaa=[i.split() for i in aaa]
        aaa_dict_list=[]
        extra=0
        pos=[]
        for i in range(1,len(aaa)):
            if len(aaa[i])< 7:
                aaa[i-1].insert(2,''.join(aaa[i]))
                pos.append(i)
        for i in pos:
            if i in aaa:
                aaa.remove(i)
        aaa = [i for i in aaa if len(i) >= 6]

        def filter_numeric_only(data):
                pattern = re.compile(r'^\d+(\.\d+)?$')  # Match integer or decimal numbers
                result = []
                unknown= []
                for row in data:
                    filtered_row = [item for item in row if pattern.fullmatch(item)]
                    filtered_row2 = [item for item in row if not pattern.fullmatch(item)]
                    result.append(filtered_row)
                    unknown.append(filtered_row2)
                return result,unknown
        
        numbers,texts=filter_numeric_only(aaa)
        CODE=[i[0] for i in texts]
        DESCRIPTION=[' '.join(i[1:]) for i in texts]
        AMOUNT=[i[3] for i in numbers]
        UNIT_PRICE=[i[2] for i in numbers]
        QUANTITY=[i[1] for i in numbers]
        max_len = max(len(CODE),len(DESCRIPTION),len(AMOUNT),len(UNIT_PRICE),len(QUANTITY))
        def pad(lst):
            return lst + [""] * (max_len - len(lst))
        df1=pd.DataFrame({
                        # "filePath":[f'{filename}' for i  in range(len(pad(CODE)))],
                        "supplier":[f'{supplier_name}' for i in range(len(pad(CODE)))],
                        "maildate":[f'{maildata}' for i in range(len(pad(CODE)))],          
                        "CODE":pad(CODE),
                        "DESCRIPTION":pad(DESCRIPTION),
                        "QUANTITY":pad(QUANTITY),
                        "UNIT PRICE":pad(UNIT_PRICE),
                        "AMOUNT":pad(AMOUNT)
                        })
        name, ext = os.path.splitext(filename)
        folder_path = PurchaseReportClass().createFolderByDate(maildata)
        real_path=os.path.join(folder_path,name)
        df1.to_excel(f"{real_path}.xlsx", index=False)
        return df1

class Repco:
    invoice_selection_key="A DIVISION OF GPC ASIA PACIFIC PTY LTD"
    start_key="INCL GST EXCL GST TOTAL"
    end_key="PAYABLE"

    def __init__(self):
        pass

    def extractInvoice(self,text_list=None,filename=None,maildate=None):
        if text_list is not None:
            self.text_list=text_list
            df1=self.extract(filename=filename,maildata=maildate)
            return df1

    def extract(self,filename=None,maildata=None):  
        supplier_name="Repco"
        rrr=self.text_list
        rrr=rrr[:len(rrr)-1]
        rrr=[i.split() for i in rrr]
        rrr=[i[1:] for i in rrr]
        part_number=[]
        description=[]
        retail_incl_gst=[]
        uom=[]
        qty_supplied=[]
        unit_price_excl_gst=[]
        s=[]
        total_gst=[]
        total_incl_gst=[]
        numbers=[]
        for r in rrr:
            found=[re.findall(r'\d+\.?\d*', i) for i in r]
            found=[i for i in found if i]
            numbers.append(found)
        numeric_list = []
        alphabet_list = []
        for row in rrr:
            row_numeric = []
            row_alpha = []
            for item in row:
                clean_item = item.replace(',', '')
                try:
                    row_numeric.append(float(clean_item))
                except ValueError:
                    row_alpha.append(item)
            numeric_list.append(row_numeric)
            alphabet_list.append(row_alpha)
        alphabet_list=[i[:len(i)-1] if "S" in i else i for i in alphabet_list]        
        total_incl_gst=[i[len(i)-1] if len(i) >= 1 else None for i in numeric_list]
        total_gst=[i[len(i)-2] if len(i) >= 2 else None for i in numeric_list]
        s=[i[len(i)-3] if len(i) >= 3 else None for i in numeric_list]
        unit_price_excl_gst=[i[len(i)-4] if len(i) >= 4 else None for i in numeric_list]
        qty_supplied=[i[len(i)-5] if len(i) >= 5 else None for i in numeric_list]
        retail_incl_gst=[i[len(i)-6] if len(i) >= 6 else None for i in numeric_list]
        part_number = [i.pop(0) for i in alphabet_list]
        uom=[i.pop(len(i)-1) for i in alphabet_list]
        description=[' '.join(i) for i in alphabet_list]
        max_len = max(len(total_incl_gst),len(total_gst),len(unit_price_excl_gst),len(qty_supplied),len(part_number))
        def pad(lst):
            return lst + [""] * (max_len - len(lst))
        df1=pd.DataFrame({
                            # "filePath":[f'{filename}' for i  in range(len(pad(part_number)))],
                            "supplier":[f'{supplier_name}' for i in range(len(pad(part_number)))],
                            "maildate":[f'{maildata}' for i in range(len(pad(part_number)))],
                            "Part Number":pad(part_number),
                            "Description":pad(description),
                            "uom":pad(uom),
                            "RETAIL INCL GST":pad(retail_incl_gst),
                            "unit_price_excl_gst":pad(unit_price_excl_gst),
                            "QTY Supplied":pad(qty_supplied),
                            "total_gst":pad(total_gst),
                            "s":pad(s),
                            "TOTAL INCL GST":pad(total_incl_gst)
                            })
        name, ext = os.path.splitext(filename)
        folder_path = PurchaseReportClass().createFolderByDate(maildata)
        real_path=os.path.join(folder_path,name)
        df1.to_excel(f"{real_path}.xlsx", index=False)
        return df1


