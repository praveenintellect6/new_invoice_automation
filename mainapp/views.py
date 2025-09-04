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

# print(os.getenv("DB_PORT"))
# supp=NewSupplier.objects.get(id=23)
# print(supp.supplier_mapp_col)


# rr=ReportCalculation()

# @csrf_exempt
# def submit_excel_files(request):
#     if request.method == "POST":
#         files = request.FILES.getlist("files")
#         saved_files = []
#         for f in files:
#             save_path=os.path.join(settings.MEDIA_ROOT, f.name)
#             with open(save_path, "wb+") as destination:
#                 for chunk in f.chunks():
#                     destination.write(chunk)
#             saved_files.append(f.name)
#         return JsonResponse({"status": "success", "files": saved_files})
#     return JsonResponse({"status": "failed"}, status=400)


@csrf_exempt 
def submit_excel_files(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        excel_date = request.POST.get("date")
        saved_files = []
        for f in files:
            df=pd.read_excel(f)
            supplier_name = df['supplier'].iloc[0]
            print(supplier_name)
            exists = NewSupplier.objects.filter(supplier_name=supplier_name).exists()
            if not exists:
                break
            else:
                rr = ReportCalculation(df=df) 
                rr.MappToPurchaseReport()
                p_df=rr.exportToExcel()
                
                folder_path = PurchaseReportClass().createFolderByDate(excel_date)
                save_path=os.path.join(folder_path, f.name)
                with open(save_path, "wb+") as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                excel_path=os.path.join(folder_path,f"{excel_date}_PurchaseReport.xlsx")
                if os.path.exists(excel_path): 
                    print("File already exists:", excel_path)
                else:
                    print("File does not exist, safe to create:", excel_path)
                    p_df.to_excel(excel_path, index=False)
                saved_files.append(f.name)
        return JsonResponse({"status": "success", "files": saved_files})
    return JsonResponse({"status": "failed", "message": "Invalid request"}, status=400)


@csrf_exempt
def home_view(request):
    return render(request, "index.html")

@csrf_exempt
def save_edited_case(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        gst=request.POST.get("gst")
        # print("supplier_id===",supplier_id)
        # print("gst===",gst)
        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Missing supplier_id'}, status=400)
        try:
            add_case_list_raw = request.POST.get("add_case_list", "[]")
            edit_case_list = json.loads(add_case_list_raw)
            # print("edit_case_list===", edit_case_list)
            case_edit=CaseEditing(edit_case_list,supplier_id,gst)
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
            else:
                case_state=[]
                gst=''
         
            return JsonResponse({'status': 'success','mapping_columns': mapping_columns,'column_state': state_data,'case_state': case_state,'gst':gst}, status=200)
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


