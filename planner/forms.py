# -*- encoding: utf-8 -*-
from django import forms
from .models import User, Task, Customer, Execution, Order, Sending, Deal, Employee, Project, Company, News, Event
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django_select2.forms import Select2Widget
from django.contrib.admin.widgets import AdminDateWidget
from crum import get_current_user
from .formatChecker import NotClearableFileInput
from .fotoUpload import AvatarInput
from .btnWidget import BtnWidget


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {'password': forms.PasswordInput}

    def is_valid(self):
        username_ = self.data["username"]
        try:
            User._default_manager.get(username=username_)
            self.errors.clear()
            self.cleaned_data["username"] = username_
            return True
        except:
            return False


class DealFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DealFilterForm, self).__init__(*args, **kwargs)

        customer = [(customer.id, customer.name) for customer in Customer.objects.all()]
        customer.insert(0, (0, "Всі"))

        company = [(company.id, company.name) for company in Company.objects.all()]
        company.insert(0, (0, "Всі"))

        act_status = []
        act_status.insert(0, (0, "Всі"))
        act_status.insert(1, ('NI', "Не виписаний"))
        act_status.insert(2, ('PI', "Виписаний частково"))
        act_status.insert(3, ('IS', "Виписаний"))

        pay_status = []
        pay_status.insert(0, (0, "Всі"))
        pay_status.insert(1, ('NP', "Не оплачений"))
        pay_status.insert(2, ('AP', "Оплачений аванс"))
        pay_status.insert(3, ('PU', "Оплачений"))

        self.fields['customer'].choices = customer
        self.fields['company'].choices = company
        self.fields['act_status'].choices = act_status
        self.fields['pay_status'].choices = pay_status

    customer = forms.ChoiceField(label='Замовник', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    company = forms.ChoiceField(label='Компанія', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    act_status = forms.ChoiceField(label='Акт виконаних робіт', required=False,
                                   widget=forms.Select(attrs={"onChange": 'submit()'}))
    pay_status = forms.ChoiceField(label='Статус оплати', required=False,
                                   widget=forms.Select(attrs={"onChange": 'submit()'}))
    filter = forms.CharField(label='Слово пошуку', max_length=255, required=False)


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['number', 'date', 'customer', 'company', 'value', 'advance',
                  'pay_status', 'pay_date', 'expire_date', 'act_status',
                  'act_date', 'act_value', 'pdf_copy', 'value_correction', 'comment']
        widgets = {
            'date': AdminDateWidget,
            'customer': Select2Widget,
            'pay_date': AdminDateWidget,
            'expire_date': AdminDateWidget,
            'act_date': AdminDateWidget,
            'pdf_copy': NotClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'style': 'width:400px;'})
        self.fields['comment'].widget.attrs.update({'style': 'width:100%; height:44px;'})

    def clean(self):
        cleaned_data = super(DealForm, self).clean()
        value = cleaned_data.get("value")
        pay_status = cleaned_data.get("pay_status")
        pay_date = cleaned_data.get("pay_date")
        advance = cleaned_data.get("advance")
        act_status = cleaned_data.get("act_status")
        act_date = cleaned_data.get("act_date")
        act_value = cleaned_data.get("act_value")
        pdf_copy = cleaned_data.get("pdf_copy")
        self.data.__customer__ = cleaned_data.get("customer")
        self.data.__expire_date__ = cleaned_data.get("expire_date")

        if pay_status == Deal.PaidUp:
            if not value or value == 0:
                self.add_error('value', "Вкажіть Вартість робіт")
            if not pay_date:
                self.add_error('pay_date', "Вкажіть Дату оплати")
        if pay_status == Deal.AdvancePaid:
            if not advance or advance == 0:
                self.add_error('advance', "Вкажіть Аванс")
            if not pay_date:
                self.add_error('pay_date', "Вкажіть Дату оплати")
        if act_status != Deal.NotIssued:
            if not value or value == 0:
                self.add_error('value', "Вкажіть Вартість робіт")
            if not act_date:
                self.add_error('act_date', "Вкажіть Дату акту виконаних робіт")
            if not act_value or act_value == 0:
                self.add_error('act_value', "Вкажіть Суму акту виконаних робіт")
            if not pdf_copy:
                self.add_error('pdf_copy', "Підвантажте будь ласка електронний примірник")
        return cleaned_data


class TasksInlineForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['object_code', 'object_address', 'project_type', 'owner', 'planned_finish', 'exec_status']
        widgets = {
            'object_code': BtnWidget(),
            'project_type': Select2Widget(),
            'planned_finish': AdminDateWidget(),
            'DELETION_FIELD_NAME': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TasksInlineForm, self).__init__(*args, **kwargs)
        self.fields['object_address'].widget.attrs.update({'style': 'width:100%;'})
        self.fields['owner'].queryset = Employee.objects.filter(user__groups__name__contains="ГІПи",
                                                                user__is_active=True)
        self.fields['object_code'].widget.attrs.update({'task_id': self.instance.id})
        if self.instance.pk is None or self.instance.project_type.active:
            self.fields['project_type'].queryset = Project.objects.filter(active=True)


    def clean(self):
        super(TasksInlineForm, self).clean()
        project_type = self.cleaned_data.get("project_type")
        planned_finish = self.cleaned_data.get("planned_finish")
        if project_type and self.data.__customer__:
            if self.data.__customer__ != project_type.customer:
                self.add_error('project_type', "Тип проекту не входить до можливих значень Замовника Договору")
        if planned_finish and self.data.__expire_date__:
            if planned_finish > self.data.__expire_date__:
                self.add_error('planned_finish', "Планова дата закінчення повинна бути меншою дати закінчення договору")


TasksFormSet = inlineformset_factory(Deal, Task, form=TasksInlineForm, extra=1)


class TaskFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        exec_status = []
        exec_status.insert(0, (0, "Всі"))
        exec_status.insert(1, ('IW', "В черзі"))
        exec_status.insert(2, ('IP', "Виконується"))
        exec_status.insert(3, ('HD', "Виконано"))
        exec_status.insert(4, ('ST', "Надіслано"))

        owners = [(owner[0], owner[1]) for owner in Task.objects.values_list('owner__id', 'owner__name').order_by().distinct()]
        owners.insert(0, (0, "Всі"))
        customers = [(customer.id, customer.name) for customer in Customer.objects.all()]
        customers.insert(0, (0, "Всі"))

        self.fields['exec_status'].choices = exec_status
        self.fields['owner'].choices = owners
        self.fields['customer'].choices = customers

    exec_status = forms.ChoiceField(label='Статус', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    owner = forms.ChoiceField(label='Керівник проекту', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    customer = forms.ChoiceField(label='Замовник', required=False, widget=forms.Select(attrs={"onChange": 'submit()'}))
    filter = forms.CharField(label='Слово пошуку', max_length=255, required=False)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['object_code', 'object_address', 'project_type', 'deal', 'exec_status', 'owner',
                  'planned_start', 'planned_finish', 'actual_start', 'actual_finish',
                  'tc_received', 'tc_upload', 'pdf_copy', 'project_code', 'comment']
        widgets = {
            'project_type': Select2Widget,
            'deal': Select2Widget,
            'planned_start': AdminDateWidget,
            'planned_finish': AdminDateWidget,
            'actual_start': AdminDateWidget,
            'actual_finish': AdminDateWidget,
            'tc_received': AdminDateWidget,
            'pdf_copy': NotClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['object_address'].widget.attrs.update({'style': 'width:100%;'})
        self.fields['comment'].widget.attrs.update({'style': 'width:100%; height:63px;'})

        if get_current_user().is_superuser:
            self.fields['owner'].queryset = Employee.objects.filter(user__groups__name__contains="ГІПи",
                                                                    user__is_active=True)
        elif self.instance.pk is None or self.instance.owner.user == get_current_user():
            self.fields['owner'].queryset = Employee.objects.filter(user=get_current_user())

        if self.instance.pk is None or self.instance.deal.act_status == Deal.NotIssued:
            self.fields['deal'].queryset = Deal.objects.filter(act_status=Deal.NotIssued)
        else:
            self.fields['deal'].widget.attrs['disabled'] = True
            self.fields['deal'].required = False

        if self.instance.pk is None or self.instance.project_type.active:
            self.fields['project_type'].queryset = Project.objects.filter(active=True)
        else:
            self.fields['project_type'].widget.attrs['disabled'] = True
            self.fields['deal'].required = False

    def clean_deal(self):
        if self.cleaned_data['deal']:
            return self.cleaned_data['deal']
        else:
            return self.instance.deal

    def clean_project_type(self):
        if self.cleaned_data['project_type']:
            return self.cleaned_data['project_type']
        else:
            return self.instance.project_type

    def clean(self):
        cleaned_data = super(TaskForm, self).clean()
        project_type = cleaned_data.get("project_type")
        deal = cleaned_data.get("deal")
        exec_status = cleaned_data.get("exec_status")
        actual_finish = cleaned_data.get("actual_finish")
        planned_finish = cleaned_data.get("planned_finish")
        pdf_copy = cleaned_data.get("pdf_copy")
        self.instance.__project_type__ = project_type
        self.instance.__exec_status__ = exec_status

        if not get_current_user().is_superuser and (not deal or deal.act_status != Deal.NotIssued):
            raise ValidationError("Договір закрито, зверніться до керівника")
        if not project_type or project_type.active is False:
            raise ValidationError("Даний Тип проекту не активний")
        if project_type and deal:
            if deal.customer != project_type.customer:
                self.add_error('project_type', "Тип проекту не відповідає Замовнику Договору")
        if exec_status in [Task.Done, Task.Sent]:
            if not actual_finish:
                self.add_error('actual_finish', "Вкажіть будь ласка Фактичне закінчення робіт")
            elif not pdf_copy:
                self.add_error('pdf_copy', "Підвантажте будь ласка електронний примірник")
        if actual_finish and exec_status not in [Task.Done, Task.Sent]:
            self.add_error('exec_status', "Будь ласка відмітьте Статус виконання або видаліть Дату виконання")
        if planned_finish and planned_finish > deal.expire_date:
            self.add_error('planned_finish', "Планова дата закінчення повинна бути меншою дати закінчення договору")
        return cleaned_data


class ExecutorInlineForm(forms.ModelForm):
    class Meta:
        model = Execution
        fields = ['executor', 'part_name', 'part', 'exec_status', 'finish_date']
        widgets = {
            'executor': Select2Widget(),
            'finish_date': AdminDateWidget(),
            'DELETION_FIELD_NAME': forms.HiddenInput()
        }

    def clean(self):
        super(ExecutorInlineForm, self).clean()
        exec_status = self.cleaned_data.get('exec_status')
        finish_date = self.cleaned_data.get('finish_date')
        if finish_date and exec_status != Execution.Done:
            self.add_error('exec_status', "Будь ласка відмітьте Статус виконання або видаліть Дату виконання")
        elif exec_status == Execution.Done and not finish_date:
            self.add_error('finish_date', "Вкажіть будь ласка Дату виконання робіт")


class ExecutorsInlineFormset(BaseInlineFormSet):
    """used to pass in the constructor of inlineformset_factory"""
    def clean(self):
        """forces each clean() method on the ChildCounts to be called"""
        super(ExecutorsInlineFormset, self).clean()
        percent = 0
        outsourcing_part = 0
        self.instance.__outsourcing_part__ = 0
        for form in self.forms:
            part = form.cleaned_data.get('part', 0)
            executor = form.cleaned_data.get('executor')
            if not form.cleaned_data.get('DELETE', False):
                percent += part
                if executor and executor.user.username.startswith('outsourcing'):
                    outsourcing_part += part
        self.instance.__outsourcing_part__ = outsourcing_part
        if self.instance.pk:
            if self.instance.__exec_status__ in [Task.Done, Task.Sent] and percent < 100:
                raise ValidationError(('Вкажіть 100%% часток виконавців. Зараз : %(percent).0f%%') % {'percent': percent})
            if self.instance.__project_type__.executors_bonus > 0:
                bonuses_max = 100 + 100 * self.instance.__project_type__.owner_bonus /\
                              self.instance.__project_type__.executors_bonus
            else:
                bonuses_max = 100
            if percent > bonuses_max:
                raise ValidationError(('Сума часток виконавців не має перевищувати %(bonuses_max).0f%%. '
                                       'Зараз : %(percent).0f%%') % {'bonuses_max': bonuses_max, 'percent': percent})


ExecutorsFormSet = inlineformset_factory(Task, Execution, form=ExecutorInlineForm, extra=1, formset=ExecutorsInlineFormset)


class OrderInlineForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['contractor', 'deal_number', 'value', 'advance', 'pay_status', 'pay_date']
        widgets = {
            'contractor': Select2Widget(),
            'pay_date': AdminDateWidget(),
            'DELETION_FIELD_NAME': forms.HiddenInput()
        }

    def clean(self):
        super(OrderInlineForm, self).clean()
        pay_status = self.cleaned_data.get("pay_status")
        pay_date = self.cleaned_data.get("pay_date")
        value = self.cleaned_data.get("value")
        if pay_status and pay_status != Order.NotPaid:
            if not pay_date:
                self.add_error('pay_date', "Вкажіть будь ласка Дату оплати")
            if not value or value == 0:
                self.add_error('value', "Вкажіть будь ласка Вартість робіт")
        if pay_date and pay_status == Order.NotPaid:
            self.add_error('pay_status', "Відмітьте Статус оплати або видаліть Дату оплати")


class CostsInlineFormset(BaseInlineFormSet):
    """used to pass in the constructor of inlineformset_factory"""
    def clean(self):
        """forces each clean() method on the ChildCounts to be called"""
        super(CostsInlineFormset, self).clean()
        outsourcing = 0
        for form in self.forms:
            if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                outsourcing += form.cleaned_data.get('value', 0)
        if self.instance.pk:
            if self.instance.__exec_status__ in [Task.Done, Task.Sent]:
                if self.instance.__project_type__.net_price() > 0 and hasattr(self.instance, '__outsourcing_part__'):
                    costs_part = outsourcing / self.instance.__project_type__.net_price() * 100
                    if self.instance.__outsourcing_part__ > 0 and costs_part == 0:
                        raise ValidationError("Добавте будь ласка витрати по аутсорсингу")
                    if self.instance.__outsourcing_part__ < costs_part:
                        raise ValidationError("Відсоток витрат на аутсорсинг перевищує відсоток виконання робіт аутсорсингом")
                elif self.instance.__project_type__.net_price() == 0 and outsourcing > 0:
                    raise ValidationError("У проекту вартість якого дорівнює нулю не може бути витрат")


CostsFormSet = inlineformset_factory(Task, Order, form=OrderInlineForm, extra=1, formset=CostsInlineFormset)


class SendingInlineForm(forms.ModelForm):
    class Meta:
        model = Sending
        fields = ['receiver', 'receipt_date', 'copies_count', 'register_num']
        widgets = {
            'receiver': Select2Widget(),
            'receipt_date': AdminDateWidget(),
            'DELETION_FIELD_NAME': forms.HiddenInput()
        }


class SendingInlineFormset(BaseInlineFormSet):
    """used to pass in the constructor of inlineformset_factory"""
    def clean(self):
        """forces each clean() method on the ChildCounts to be called"""
        super(SendingInlineFormset, self).clean()
        if self.instance.pk:
            if self.instance.__exec_status__ == Task.Sent and self.instance.__project_type__.copies_count > 0:
                sending = 0
                for form in self.forms:
                    if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                        sending += form.cleaned_data.get('copies_count', 0)
                if sending == 0:
                    raise ValidationError("Ви не можете закрити цей проект без відправки")


SendingFormSet = inlineformset_factory(Task, Sending, form=SendingInlineForm, extra=1, formset=SendingInlineFormset)


class TaskExchangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.tasks_ids = kwargs.pop('tasks_ids')
        super(TaskExchangeForm, self).__init__(*args, **kwargs)
        deal = [(deal.id, deal.number) for deal in Deal.objects.filter(act_status=Deal.NotIssued)]
        self.fields['deal'].choices = deal

    deal = forms.ChoiceField(label='Оберіть договір', widget=Select2Widget())

    def clean(self):
        super(TaskExchangeForm, self).clean()
        deal_id = self.cleaned_data.get("deal")
        tasks = Task.objects.filter(id__in=self.tasks_ids)
        if not self.tasks_ids:
            raise ValidationError("Ви не обрали жодного проекту")
        if deal_id:
            deal = Deal.objects.get(pk=deal_id)
            for task in tasks:
                if deal.customer != task.project_type.customer:
                    self.add_error('deal', "{} - тип проекту не відповідає Замовнику Договору".format(task))
                if task.deal.act_status != Deal.NotIssued:
                    self.add_error('deal', "{} - договір закрито, зверніться до керівника".format(task))


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'text', 'news_type', 'actual_from', 'actual_to']

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.fields['actual_from'].widget = AdminDateWidget()
        self.fields['actual_to'].widget = AdminDateWidget()
        self.fields['title'].widget.attrs.update({'style': 'width:100%;'})
        self.fields['text'].widget.attrs.update({'style': 'width:100%; height:63px;'})


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'repeat', 'description']

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = AdminDateWidget()
        self.fields['title'].widget.attrs.update({'style': 'width:100%;'})
        self.fields['description'].widget.attrs.update({'style': 'width:100%; height:63px;'})


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['mobile_phone', 'avatar']
        widgets = {
            'avatar': AvatarInput,
        }
