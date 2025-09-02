from .models import *

class CaseEditing:
    def __init__(self, lst_array,supplier_id,gst):
        self.supplier=NewSupplier.objects.get(id=supplier_id)
        deleted_count, _ = Cases.objects.filter(supplier_id=supplier_id).delete()
        self.lst_array=lst_array
        self.gst=gst
        self.editcase()
        self.storeCaseState()

    def editcase(self):
        for i in self.lst_array:
            min=i[0]
            max=i[1]
            profit=[2]
            Cases.objects.create(supplier=self.supplier, min=min, max=max, profit=profit,gst=self.gst)  

    def storeCaseState(self):
        state, created = CaseEditingState.objects.update_or_create(
            supplier=self.supplier,
            gst=self.gst,
            defaults={"case_state": self.lst_array}
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
    

