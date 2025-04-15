from django import forms

class ReportForm(forms.Form):
    api_key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
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
