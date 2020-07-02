from django import forms
from datetime import date


class GetTokenForm(forms.Form):
    email = forms.CharField(max_length=20, required=True)
    password = forms.CharField(max_length=30, required=True)


class CreateLinkForm(forms.Form):
    link = forms.URLField(max_length=300, required=True)


class AnalyticForm(forms.Form):
    date_from = forms.DateField(required=True)
    date_to = forms.DateField()
    order_by = forms.CharField()

    def clean(self):

        super(AnalyticForm, self).clean()

        date_to = self.cleaned_data.get('date_to')
        order_by = self.cleaned_data.get('order_by')
        if not date_to:
            self.cleaned_data['date_to'] = date.today()

        if order_by and order_by not in ['ASC', 'DESC']:
            self._errors['order_by'] = self.error_class([
                'Wrong order_by parameter. Choose "ASC" or "DESC"'])
        return self.cleaned_data
