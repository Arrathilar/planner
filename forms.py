# -*- encoding: utf-8 -*-
from django import forms
from planner.models import User, Task, Customer, Execution, Order, Sending, Deal, Employee
from django.forms import inlineformset_factory
from django_select2.forms import Select2Widget
from django.contrib.admin.widgets import AdminDateWidget


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def is_valid(self):
        username_ = self.data["username"]
        try:
            User._default_manager.get(username=username_)
            self.errors.clear()
            self.cleaned_data["username"] = username_
            return True
        except:
            return False


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['object_code', 'object_address', 'project_type', 'deal', 'exec_status', 'owner',
                  'planned_start', 'planned_finish', 'actual_start', 'actual_finish',
                  'tc_received', 'tc_upload', 'pdf_copy', 'project_code', 'comment']
        widgets = {
            'project_type': Select2Widget,
            'deal': Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['deal'].queryset = Deal.objects.all()
        self.fields['owner'].queryset = Employee.objects.filter(user__groups__name__contains="ГІПи", user__is_active=True)

ExecutorsFormSet = inlineformset_factory(Task, Execution, fields=('executor', 'part_name', 'part'),
                                         extra=2, widgets={'executor': Select2Widget()})
CostsFormSet = inlineformset_factory(Task, Order, fields=('contractor', 'deal_number', 'value', 'advance', 'pay_status', 'pay_date'),
                                     extra=2, widgets={'contractor': Select2Widget(attrs={'data-width': 'auto'}), 'pay_date': AdminDateWidget()})
SendingFormSet = inlineformset_factory(Task, Sending, fields=('receiver', 'receipt_date', 'copies_count', 'register_num'),
                                       extra=2, widgets={'receiver': Select2Widget(attrs={'data-width': '20em'}), 'receipt_date': AdminDateWidget()})


class TaskFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        exec_status = []
        exec_status.insert(0, (0, "Всі"))
        exec_status.insert(1, ('IW', "В черзі"))
        exec_status.insert(2, ('IP', "Виконується"))
        exec_status.insert(3, ('HD', "Виконано"))

        owners = [(owner[0], owner[1]) for owner in Task.objects.values_list('owner__id', 'owner__name').distinct()]
        owners.insert(0, (0, "Всі"))
        customers = [(customer.id, customer.name) for customer in Customer.objects.all()]
        customers.insert(0, (0, "Всі"))

        self.fields['exec_status'].choices = exec_status
        self.fields['owner'].choices = owners
        self.fields['customer'].choices = customers

    exec_status = forms.ChoiceField(label='Статус виконання', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    owner = forms.ChoiceField(label='Керівник проекту', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    customer = forms.ChoiceField(label='Замовник', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    filter = forms.CharField(label='Слово пошуку', max_length=255, required=False)
