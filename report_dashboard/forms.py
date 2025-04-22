from django import forms
from django.core.validators import MinValueValidator
from datetime import date, timedelta

class ReportForm(forms.Form):
    # Add validation for date range
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        validators=[MinValueValidator(limit_value=date.today() - timedelta(days=90))]
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date must be after start date")
            if (end_date - start_date).days > 31:
                raise forms.ValidationError("Date range cannot exceed 31 days")

        return cleaned_data
    columns = forms.MultipleChoiceField(
        choices=[
            ('day', 'Day'),
            ('hour', 'Hour'),
            ('country', 'Country'),
            ('platform', 'Platform'),
            ('application', 'Application'),
            ('network', 'Network'),
            ('adformat', 'Ad Format'),
            ('placement', 'Placement'),
            ('estimated_revenue', 'Estimated Revenue'),
            ('impressions', 'Impressions'),
            ('ecpm', 'eCPM'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'})
    )
    report_type = forms.ChoiceField(
        choices=[
            ('network', 'Network'),
            ('country', 'Country'),
            ('placement', 'Placement'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class UserAdRevenueForm(forms.Form):
    api_key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    platform = forms.ChoiceField(
        choices=[
            ('android', 'Android'),
            ('ios', 'iOS'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    application = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    aggregated = forms.ChoiceField(
        choices=[
            ('0', 'No'),
            ('1', 'Yes'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
