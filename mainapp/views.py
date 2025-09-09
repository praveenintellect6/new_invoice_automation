from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from .utils import *
import os
from dotenv import load_dotenv
from .calculation import *
from django.conf import settings
from datetime import datetime
from .purchase_report import *
load_dotenv()
from openpyxl import load_workbook
import time 

# print(os.getenv("DB_PORT"))
# supp=NewSupplier.objects.get(id=23)
# print(supp.supplier_mapp_col)


# rr=NewSupplier.objects.get(supplier_name='wurth')
# print(rr.supplier_mapp_col)

@csrf_exempt
def submit_edit_excel_files(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        excel_date = request.POST.get("date")
        folder_path = PurchaseReportClass().createFolderByDate(excel_date)
        print(excel_date)
        for i in files:
            print(i.name)
        if files:
            for f in files:
                if f.name.endswith('.xlsx'):
                    path = os.path.join(folder_path, f.name)
                if os.path.exists(path):
                            os.remove(path)
                with open(path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
        try:
            report_file = os.path.join(folder_path, f"{excel_date}_PurchaseReport.xlsx")
            if os.path.exists(report_file):
                os.remove(report_file)
                print(f" Removed old report: {report_file}")
        except Exception as e:
            print(f" Could not remove old report: {e}")

        xlsx_files = [ f for f in os.listdir(folder_path) if f.endswith(".xlsx") and not f.endswith("PurchaseReport.xlsx")]

        for file in xlsx_files:
            file_path = os.path.join(folder_path, file)
            try:
                df=pd.read_excel(file_path, dtype=str)
                supplier_name = df['supplier'].iloc[0]
                supp = NewSupplier.objects.filter(supplier_name=supplier_name).first()
                if not supp:
                    print(f" Supplier not found for {file}, skipping...")
                    continue
                rr = ReportCalculation(df=df, file=folder_path, excel_date=excel_date, supp=supp)
                rr.MappToPurchaseReport()
                p_df=rr.exportToExcel()
                print(f" Processed {file}")
                folder_path = PurchaseReportClass().createFolderByDate(excel_date)
                PurchaseReportClass.copy_folder_contents(source_folder=folder_path)
            except Exception as e:
                print(f" Failed to process {file}: {e}")

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Invalid request"}, status=400)


@csrf_exempt 
def submit_excel_files(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        excel_date = request.POST.get("date")
        for f in files:
            df=pd.read_excel(f, dtype=str)
            supplier_name = df['supplier'].iloc[0]
            print(supplier_name)
            exist = NewSupplier.objects.filter(supplier_name=supplier_name).exists()
            if not exist:
                break
            else:
                supp = NewSupplier.objects.filter(supplier_name=supplier_name).first()
                folder_path = PurchaseReportClass().createFolderByDate(excel_date)
                if os.path.exists(os.path.join(folder_path, f.name)):
                    print("file exist")
                else:
                    rr = ReportCalculation(df=df,file=folder_path,excel_date=excel_date,supp=supp) 
                    rr.MappToPurchaseReport()
                    p_df=rr.exportToExcel()
                    save_path=os.path.join(folder_path, f.name)
                    with open(save_path, "wb+") as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
            folder_path = PurchaseReportClass().createFolderByDate(excel_date)
            PurchaseReportClass.copy_folder_contents(source_folder=folder_path)

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Invalid request"}, status=400)


@csrf_exempt
def home_view(request):
    return render(request, "index.html")

@csrf_exempt
def save_edited_case(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        gst= request.POST.get("gst")
        gst_mapp= request.POST.get("gst_mapp")
        profit_mapp= request.POST.get("profit_mapp")

        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            add_case_list_raw = request.POST.get("add_case_list", "[]")
            edit_case_list = json.loads(add_case_list_raw)
            # print("edit_case_list===", edit_case_list)
            case_edit=CaseEditing(lst_array=edit_case_list,supplier_id=supplier_id,gst=gst,gst_mapp=gst_mapp,profit_mapp=profit_mapp)
            return JsonResponse({
                    "status": "success",
                })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "invalid request"}, status=400)

@csrf_exempt
def save_edited_columns(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            edit_column_list_raw = request.POST.get("edit_column_list", "[]")
            try:
                edit_column_list = json.loads(edit_column_list_raw)

            except json.JSONDecodeError:
                edit_column_list = []

            col_edit=ColumnEditing(edit_column_list,supplier_id)

            return JsonResponse({
                "status": "success",
            })
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "invalid request"}, status=400)

@csrf_exempt
def add_update_columns(request):
    
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        supplier_cols_raw = request.POST.get("supplierCols") 

        if not supplier_id :
            return JsonResponse({"status": "error", "message": "supplier_id required"}, status=400)
        
        try:
            supplier_cols = json.loads(supplier_cols_raw)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid supplierCols format"}, status=400)
        
        try:
            supplier = NewSupplier.objects.get(id=supplier_id)
        except NewSupplier.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Supplier not found"}, status=404)
        
        supplier.supplier_col = supplier_cols
        supplier.save()
        return JsonResponse({
            "status": "success",
            "message": "Supplier columns updated successfully",
            "columns": supplier.supplier_col
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def fetch_case(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            supplier = NewSupplier.objects.get(id=supplier_id)
            # supplier_col_map=supplier.supplier_mapp_col or {}
            mapping_columns = list(default_mapping().keys())
            col_state = ColumnEditingState.objects.filter(supplier=supplier).first()

            if col_state:
                state_data = col_state.column_state
            else:
                state_data = []
            case = CaseEditingState.objects.filter(supplier=supplier).first()

            if case:
                case_state = case.case_state
                gst=case.gst
                gst_mapp=case.gst_mapp
                profit_mapp=case.profit_mapp
            else:
                case_state=[]
                gst=''
                gst_mapp=''
                profit_mapp=''

            return JsonResponse({'status': 'success','mapping_columns': mapping_columns,'column_state': state_data,'case_state': case_state,'gst':gst,
                                 'gst_mapp':gst_mapp,'profit_mapp':profit_mapp}, status=200)
        
        except NewSupplier.DoesNotExist:

            return JsonResponse({'status': 'error', 'message': 'Supplier not found'}, status=404)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def fetch_columns(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        print("supplier_id:",supplier_id)
        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            supplier = NewSupplier.objects.get(id=supplier_id)
            # supplier_col_map=supplier.supplier_mapp_col or {}
            mapping_columns = list(default_mapping().keys())
            col_state = ColumnEditingState.objects.filter(supplier=supplier).first()
            if col_state:
                state_data = col_state.column_state
            else:
                state_data = []
            case = CaseEditingState.objects.filter(supplier=supplier).first()
            if case:
                case_state = case.case_state
                gst=case.gst
            else:
                case_state=[]
                gst=''
            return JsonResponse({'status': 'success','mapping_columns': mapping_columns,'column_state': state_data,'case_state': case_state,'gst':gst}, status=200)
        except NewSupplier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Supplier not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_supplier(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            supplier = NewSupplier.objects.get(id=supplier_id)
            supplier_name = supplier.supplier_name
            supplier.delete()
            return JsonResponse({'status': 'success', 'message': f"Supplier '{supplier_name}' deleted."}, status=200)
        except NewSupplier.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Supplier not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def add_supplier(request):
    if request.method == "POST":
        supplier_name = request.POST.get("supplier_name")
        if not supplier_name:
            return JsonResponse({'error': 'Missing supplier_name'}, status=400)
        if NewSupplier.objects.filter(supplier_name=supplier_name).exists():
            return JsonResponse({'error': 'Supplier already exists'}, status=409)
        supplier = NewSupplier.objects.create(supplier_name=supplier_name)
        return JsonResponse({'status': 'success','message': 'Supplier created'}, status=201)

@csrf_exempt
def get_suppliers(request):
    suppliers = NewSupplier.objects.all().values('id', 'supplier_name')
    return JsonResponse(list(suppliers), safe=False)


