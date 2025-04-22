from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.conf import settings
import requests
import pandas as pd
from django.shortcuts import render
from .forms import ReportForm, UserAdRevenueForm
from io import StringIO
import concurrent.futures

# Cache timeout in seconds (e.g., 5 minutes)
CACHE_TIMEOUT = 300

def get_cached_report(cache_key, params, url):
    """Helper function to get or fetch report data"""
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    response = requests.get(url, params=params, timeout=120)
    if response.status_code == 200:
        cache.set(cache_key, response.content, CACHE_TIMEOUT)
        return response.content
    return None

@require_http_methods(["GET", "POST"])
def report_view(request):
    api_key = settings.APPLOVIN_API_KEY  # Move API key to settings.py
    context = {
        'max_form': ReportForm(initial={'api_key': api_key}),
        'user_ad_form': UserAdRevenueForm(initial={'api_key': api_key}),
        'show_preview': request.POST.get('show_preview', False)
    }

    if request.method == 'POST':
        if 'max_report' in request.POST:
            context.update(handle_max_report(request, api_key))
        elif 'user_ad_report' in request.POST:
            context.update(handle_user_ad_report(request, api_key))

    return render(request, 'report_dashboard/report.html', context)

def handle_max_report(request, api_key):
    """Separate function to handle MAX report generation"""
    post_data = request.POST.copy()
    post_data['api_key'] = api_key
    form = ReportForm(post_data)
    
    if not form.is_valid():
        return {'error': 'Invalid form data'}

    params = prepare_max_report_params(form, api_key)
    cache_key = f"max_report_{params['start']}_{params['end']}_{params['columns']}"
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                get_cached_report, 
                cache_key, 
                params, 
                'https://r.applovin.com/maxReport'
            )
            response_content = future.result(timeout=180)
            
        if response_content:
            return process_max_report_response(response_content)
        return {'error': 'Failed to fetch report data'}
            
    except concurrent.futures.TimeoutError:
        return {'error': 'Request timed out. Please try with a shorter date range.'}
    except Exception as e:
        return {'error': f'Error: {str(e)}'}

def handle_user_ad_report(request, api_key):
    """Separate function to handle user ad report generation"""
    post_data = request.POST.copy()
    post_data['api_key'] = api_key
    form = UserAdRevenueForm(post_data)
    
    if not form.is_valid():
        return {'error': 'Invalid form data'}

    params = prepare_user_ad_report_params(form, api_key)
    cache_key = f"user_ad_report_{params['date']}_{params['platform']}_{params['application']}"
    
    try:
        response = requests.get(
            'https://r.applovin.com/max/userAdRevenueReport',
            params=params,
            timeout=180
        )
        
        if response.status_code == 200:
            return process_user_ad_report_response(response.json())
        return {'error': f'API Error: {response.status_code}'}
            
    except requests.Timeout:
        return {'error': 'Request timed out. Please try again.'}
    except Exception as e:
        return {'error': f'Error: {str(e)}'}

def prepare_max_report_params(form, api_key):
    """Prepare parameters for MAX report API"""
    return {
        'api_key': api_key,
        'start': form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
        'end': form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
        'columns': ','.join(form.cleaned_data['columns']),
        'format': 'csv',
        'report_type': form.cleaned_data['report_type']
    }

def process_max_report_response(response_content):
    """Process MAX report response"""
    try:
        csv_content = response_content.decode('utf-8', errors='ignore')
        df = pd.read_csv(
            StringIO(csv_content),
            chunksize=10000
        )
        df_complete = pd.concat(df, ignore_index=True)
        
        return {
            'csv_url_max': response_content,
            'max_success': True,
            'csv_data': df_complete.to_html(
                classes='table table-striped table-bordered',
                index=False,
                float_format=lambda x: '{:.2f}'.format(x) if pd.notnull(x) else '',
                na_rep=''
            )
        }
    except Exception as e:
        return {'error': f"Error processing CSV data: {str(e)}"}

def prepare_user_ad_report_params(form, api_key):
    """Prepare parameters for user ad report API"""
    return {
        'api_key': api_key,
        'date': form.cleaned_data['date'].strftime('%Y-%m-%d'),
        'platform': form.cleaned_data['platform'],
        'application': form.cleaned_data['application'],
        'aggregated': form.cleaned_data['aggregated']
    }

def process_user_ad_report_response(data):
    """Process user ad report response"""
    if data.get('status') == 200:
        return {
            'csv_url_1': data.get('url'),
            'csv_url_2': data.get('ad_revenue_report_url'),
            'user_ad_success': True
        }
    return {'error': f"API Error: {data.get('message', 'Unknown error')}"}
