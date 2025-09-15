from .models import *
from datetime import datetime
import random
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv
import os
from .purchase_report import PurchaseReportClass
from .extraction import Extraction
from .calculation import ReportCalculation


class MailAutomation:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("praveen_mail")
        self.password = os.getenv("praveen_password")
        pass

    def printTime(self):
        print("Time:",datetime.now())
    
    def generate_random_3_digit(self):
        return random.randint(100, 999)

    def mailExtraction(self):
        try:
            self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
            load_dotenv()
            self.mail.login(self.username, self.password)
            print("✅ IMAP connection successful")
            self.mail.select("inbox")
            self.mail.select('"[Gmail]/All Mail"')
            status, messages = self.mail.search(None, 'X-GM-RAW', 'is:unread')
            print("status",status)
            if status != "OK":
                print("No emails found.")
                self.mail.logout()
            else:
                for num in messages[0].split():
                    res, data = self.mail.fetch(num, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    subject = decode_header(msg["Subject"])[0][0]
                    _, msg_data = self.mail.fetch(num, '(RFC822)')
                    if not msg_data or not msg_data[0]:
                        continue
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    body = ""
                    if msg.is_multipart():
                        if "invoice" in msg.get("Subject", "").lower():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition", "")).lower()
                                if content_disposition and "attachment" in content_disposition:
                                    raw_date = msg.get("Date")
                                    filename = str(self.generate_random_3_digit())+"_"+part.get_filename()
                                    invoice_date = parsedate_to_datetime(raw_date).date()
                                    invoice_date=str(invoice_date)
                                    folder_path = PurchaseReportClass().createFolderByDate(invoice_date)
                                    if not filename:
                                            ext = mimetypes.guess_extension(content_type) or ".bin"
                                            filename = f"attachment_{uuid.uuid4().hex}{ext}"    
                                    filepath = os.path.join(folder_path, filename)
                                    try:
                                        with open(filepath, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                                    except Exception as save_error:
                                        print(f"Failed to save attachment {filename}: {save_error}")
                                    try:
                                        extra= Extraction()
                                        df= extra.scrapping(filepath=filepath,maildate=invoice_date)
                                        supplier_name = df['supplier'].iloc[0]
                                        print("supplier name:",supplier_name)
                                        supp = NewSupplier.objects.get(supplier_name__iexact=supplier_name)
                                        if not supp:
                                            print(f" Supplier not found for {f.name}, skipping...")
                                            continue
                                        rr = ReportCalculation(df=df, file=folder_path,filename=filename,excel_date=invoice_date, supp=supp)
                                        rr.MappToPurchaseReport()
                                        p_df= rr.exportToExcel()
                                        PurchaseReportClass.copy_folder_contents(source_folder=folder_path)
                                    except Exception as e:
                                        print(f" Failed to process : {e}")
                                    
            self.mail.logout()                        
        except Exception as e:
            print("imap connection failed")
            self.mail.logout()
            print(e)


class CaseEditing:

    def __init__(self, lst_array=None,supplier_id=None,gst=None,gst_mapp=None,profit_mapp=None):
        self.supplier=NewSupplier.objects.get(id=supplier_id)
        deleted_count, _ = Cases.objects.filter(supplier_id=supplier_id).delete()
        self.lst_array=lst_array
        self.gst=gst
        self.gst_mapp=gst_mapp
        self.profit_mapp=profit_mapp
        self.editcase()
        self.storeCaseState()

    def editcase(self):
        for i in self.lst_array:
            min=i[0]
            max=i[1]
            profit=i[2]
            case=Cases.objects.create(supplier=self.supplier, min=min, max=max, profit=profit,gst=self.gst,gst_mapp=self.gst_mapp,profit_mapp=self.profit_mapp)
            case.save()

    def storeCaseState(self):
       
        state, created = CaseEditingState.objects.update_or_create(
            supplier=self.supplier,
            defaults={"case_state": self.lst_array,
                      "gst": self.gst,
                      "gst_mapp": self.gst_mapp,
                      "profit_mapp": self.profit_mapp}
        )
        self.state=state
    
    
class ColumnEditing:

    def __init__(self, lst_array,supplier_id):
        self.lst_array=lst_array
        self.supplier=NewSupplier.objects.get(id=supplier_id)
        self.col_map_tem=default_mapping()
        self.col_calc_temp=default_mapping()
        self.__column_dict= {}
        self.__column_list= []
        self.edit_column()
        self.storeColumnState()
        self.supplier.supplier_col= self.get_column_list()
        self.supplier.save()
        self.__column_dict= self.combine_mapp_col()
        self.supplier.supplier_mapp_col= self.__column_dict
        self.supplier.save()

    def get_column_list(self):
        self.__column_list=list(set(self.__column_list))
        return self.__column_list
    
    def combine_mapp_col(self):
        self.__column_dict = {k: self.col_map_tem.get(k) or self.col_calc_temp.get(k) for k in set(self.col_map_tem) | set(self.col_calc_temp)}
        return self.__column_dict

    def get_supplier(self):
        return self.supplier
    
    def edit_column(self):
        for i in self.lst_array:
            if '' != i[0] and '' == i[1] and '' == i[2]:
                self.case_col_add(i)
            if '' != i[0] and '' != i[1] and '' == i[2]:
                self.case_col_map(i)
            if '' == i[0] and ''!= i[1] and '' != i[2]:
                self.case_calculation(i)
    
    def case_col_add(self,lst):
        self.__column_list.append(lst[0])
    
    def case_col_map(self,lst):
        for i in lst:
            self.col_map_tem[lst[1]]=lst[0]
            self.__column_list.append(lst[0])
    
    def case_calculation(self,lst):
        for i in lst:
            self.col_calc_temp[lst[1]]=lst[2]
    
    def storeColumnState(self):
        filtered = [row for row in self.lst_array if any(cell.strip() for cell in row)]
        state, created = ColumnEditingState.objects.update_or_create(
            supplier=self.supplier,
            defaults={"column_state": filtered}
        )
        self.state=state
    
