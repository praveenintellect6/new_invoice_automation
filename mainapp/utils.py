from .models import *

class ColumnEditing:

    def __init__(self, lst_array,supplier_id):
        self.lst_array=lst_array
        self.supplier=NewSupplier.objects.get(id=supplier_id)
        self.__column_list=[]
        self.__column_dict=default_mapping()
        self.edit_column()
        self.storeColumnState()

    def get_column_list(self):
        self.__column_list=list(set(self.__column_list))
        return self.__column_list
    
    def get_column_dict(self):
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
            if '' not in i:
                self.case_all(i)
    
    def case_col_add(self,lst):
        self.__column_list.append(lst[0])
    
    def case_col_map(self,lst):
        for i in lst:
            self.__column_dict[lst[1]]=lst[0]
    
    def case_calculation(self,lst):
        print("calculation====",lst)
    
    def case_all(self,lst):
        print("all====",lst)
    
    def storeColumnState(self):
        state, created = ColumnEditingState.objects.update_or_create(
            supplier=self.supplier,
            defaults={"column_state": self.lst_array}
        )
        print("state=====", state.column_state, "created:", created)
