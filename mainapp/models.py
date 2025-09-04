from django.db import models

def default_mapping():
    return {
        "Supplier": "",
        "DATE": "",
        "PART DESCRIPTION": "",
        "PART NUMBER": "",
        "TRADE PRICE": "",
        "TOTAL COUNT": "",
        "PURCHASED COUNT": "",
        "TOTAL PRICE": "",
        "ACTUAL PRICE": "",
        "PROFIT%":"",
        "SELLING PRICE(Exc.GST)":"",
        "GST":"",
        "SELLING PRICE(Inc.GST)":"",
        }

class NewSupplier(models.Model):
    supplier_name=models.CharField(max_length=100,unique=True)
    supplier_col=models.JSONField(default=list, blank=True)
    supplier_mapp_col=models.JSONField(default=default_mapping, blank=True)

class SingleInvoice(models.Model):
    supplier=models.ForeignKey(NewSupplier, on_delete=models.CASCADE)
    invoice_date=models.CharField(max_length=10)
    invoice_filepath=models.CharField(max_length=155,unique=True)

class PurchaseReport(models.Model):
    invoice_date=models.CharField(max_length=10)
    supplier=models.CharField(max_length=100)
    date=models.CharField(max_length=10)
    part_description=models.CharField(max_length=100)
    part_number=models.CharField(max_length=100)
    trade_price=models.CharField(max_length=10)
    total_count=models.CharField(max_length=10)
    purchase_count=models.CharField(max_length=10)
    total_price=models.CharField(max_length=10)
    actual_price=models.CharField(max_length=10)
    profit=models.CharField(max_length=10)
    selling_price_exc_gst=models.CharField(max_length=10)
    gst=models.CharField(max_length=10)
    selling_price_inc_gst=models.CharField(max_length=10)

class ColumnEditingState(models.Model):
    supplier=models.ForeignKey(NewSupplier, on_delete=models.CASCADE)
    column_state=models.JSONField(default=list, blank=True)

class Cases(models.Model):
    supplier=models.ForeignKey(NewSupplier, on_delete=models.CASCADE)
    profit=models.CharField(max_length=10)
    gst=models.CharField(max_length=10)
    min=models.CharField(max_length=10)
    max=models.CharField(max_length=10)

class CaseEditingState(models.Model):
    supplier=models.ForeignKey(NewSupplier, on_delete=models.CASCADE)
    case_state=models.JSONField(default=list, blank=True)
    gst=models.CharField(max_length=10)






