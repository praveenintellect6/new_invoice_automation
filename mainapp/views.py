from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *

def home_view(request): 
    return render(request, "index.html")


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


