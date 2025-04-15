import requests
import pandas as pd
from django.shortcuts import render
from .forms import ReportForm, UserAdRevenueForm
from io import StringIO

def report_view(request):
    api_key = "veXCVvRUzwWHzmcXlSCUOHaxEvlhCk26MaJsUlLSetkccK9MoLsBcQ6sJsXWZadw9xndg64Kzpxa84ywQo61DD"
    # Initialize forms without api_key requirement
    max_form = ReportForm(initial={'api_key': api_key})  # Add initial api_key
    user_ad_form = UserAdRevenueForm(initial={'api_key': api_key})  # Add initial api_key
    context = {
        'max_form': max_form,
        'user_ad_form': user_ad_form,
        'show_preview': request.POST.get('show_preview', False)  # Add this line
    }

    if request.method == 'POST':
        if 'max_report' in request.POST:
            # Include api_key in POST data
            post_data = request.POST.copy()
            post_data['api_key'] = api_key
            form = ReportForm(post_data)
            print("\n=== MAX Report Form Data ===")
            print("POST data:", post_data)
            print("Form valid:", form.is_valid())
            print("Form errors:", form.errors)
            
            if form.is_valid():
                start_date = form.cleaned_data['start_date'].strftime('%Y-%m-%d')
                end_date = form.cleaned_data['end_date'].strftime('%Y-%m-%d')
                selected_columns = form.cleaned_data['columns']
                report_type = form.cleaned_data['report_type']  # Move this up
                
                print("\n=== API Request Details ===")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                print(f"Selected Columns: {selected_columns}")
                print(f"Report Type: {report_type}")
                
                params = {
                    'api_key': api_key,
                    'start': start_date,
                    'end': end_date,
                    'columns': ','.join(selected_columns),
                    'format': 'csv',
                    'report_type': report_type  # Include report_type in initial params
                }
                
                url = 'https://r.applovin.com/maxReport'
                print("\n=== API Call ===")
                print(f"URL: {url}")
                print("Parameters:", {k: v for k, v in params.items() if k != 'api_key'})
                
                try:
                    response = requests.get(url, params=params, timeout=120)
                    print("\n=== API Response ===")
                    print(f"Status Code: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    print(f"Response URL: {response.url}")
                    if response.status_code != 200:
                        print(f"Error Response: {response.text[:500]}")
                except Exception as e:
                    print(f"Request Error: {str(e)}")

                # Debug print statements
                print("\nForm Data:")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                print(f"Selected Columns: {selected_columns}")
                print(f"Report Type: {report_type}")

                params = {
                    'api_key': api_key,
                    'start': start_date,
                    'end': end_date,
                    'columns': ','.join(selected_columns),
                    'format': 'csv',
                    'report_type': report_type
                }

                print("\nAPI Request Parameters:")
                for key, value in params.items():
                    if key != 'api_key':  # Don't print API key
                        print(f"{key}: {value}")
                
                # Get selected columns from form
                selected_columns = form.cleaned_data['columns']
                
                # Map form column names to API expected names
                column_mapping = {
                    'adformat': 'ad_format',
                    'placement': 'network_placement',
                    'estimated_revenue': 'estimated_revenue',
                    'country': 'country',
                    'network_name': 'network_name',
                    'app_name': 'app_name'
                }
                
                # Convert selected column names to API format
                api_columns = [column_mapping.get(col, col) for col in selected_columns]
                columns_str = ','.join(api_columns) if api_columns else ''
                
                params = {
                    'api_key': api_key,
                    'start': start_date,
                    'end': end_date,
                    'columns': columns_str,
                    'format': 'csv'
                }
                
                url = 'https://r.applovin.com/maxReport'
                
                # Debug logging
                print("\nMAX Report Request Details:")
                print(f"URL: {url}")
                print(f"Full Request URL with params: {requests.Request('GET', url, params=params).prepare().url}")
                print(f"Parameters:")
                for key, value in params.items():
                    print(f"  {key}: {value}")
                
                try:
                    # Add headers for API request
                    headers = {
                        'Accept': 'text/csv',
                        'Content-Type': 'application/json',
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=120)
                    print(f"\nResponse Status Code: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        print("Response Content Type:", response.headers.get('content-type', 'Not specified'))
                        print("Response Content Preview (first 500 bytes):", response.content[:500])
                        context['csv_url_max'] = response.url
                        context['max_success'] = True
                        # Remove CSV processing and preview generation
                        
                        # Process CSV data in chunks for better memory management
                        try:
                            csv_content = response.content.decode('utf-8', errors='ignore')
                            df = pd.read_csv(
                                StringIO(csv_content),
                                chunksize=10000  # Process in chunks of 10000 rows
                            )
                            # Concatenate chunks
                            df_complete = pd.concat(df, ignore_index=True)
                            context['csv_data'] = df_complete.to_html(
                                classes='table table-striped table-bordered',
                                index=False,
                                float_format=lambda x: '{:.2f}'.format(x) if pd.notnull(x) else '',
                                na_rep=''  # Handle NaN values
                            )
                        except Exception as e:
                            context['error'] = f"Error processing CSV data: {str(e)}"
                            print(f"CSV Processing Error: {e}")
                    elif response.status_code == 504:
                        context['error'] = "The server took too long to respond. Please try with a shorter date range."
                    elif response.status_code == 429:
                        context['error'] = "Too many requests. Please wait a moment and try again."
                    else:
                        context['error'] = f"Server returned status code {response.status_code}. Please try again."
                except Exception as e:
                    context['error'] = f"Error fetching data: {str(e)}"

        elif 'user_ad_report' in request.POST:
            # Include api_key in POST data
            post_data = request.POST.copy()
            post_data['api_key'] = api_key
            form = UserAdRevenueForm(post_data)
            print("\n=== User Ad Revenue Form Data ===")
            print("POST data:", post_data)
            print("Form valid:", form.is_valid())
            print("Form errors:", form.errors)
            
            if form.is_valid():
                params = {
                    'api_key': api_key,
                    'date': form.cleaned_data['date'].strftime('%Y-%m-%d'),
                    'platform': form.cleaned_data['platform'],
                    'application': form.cleaned_data['application'],
                    'aggregated': str(form.cleaned_data['aggregated']).lower()
                }
                
                url = 'https://r.applovin.com/max/userAdRevenueReport'
                print("\n=== API Call ===")
                print(f"URL: {url}")
                print("Parameters:", {k: v for k, v in params.items() if k != 'api_key'})
                
                try:
                    # Add headers for API request
                    headers = {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=180)
                    print("\n=== API Response ===")
                    print(f"Status Code: {response.status_code}")
                    print(f"Response Headers: {dict(response.headers)}")
                    print(f"Response URL: {response.url}")
                    
                    if response.status_code == 200:
                        print("Response Content:", response.text[:500])  # Print first 500 chars of response
                        data = response.json()
                        if data.get('status') == 200:
                            # Store URLs for download
                            context['csv_url_1'] = data.get('url')
                            context['csv_url_2'] = data.get('ad_revenue_report_url')
                            context['user_ad_success'] = True
                            
                            # Only process preview if show_preview is True
                            if request.POST.get('show_preview'):
                                for report_url, context_key in [
                                    (data.get('url'), 'user_report_data'),
                                ]:
                                    try:
                                        report_response = requests.get(report_url, timeout=180)
                                        if report_response.status_code == 200:
                                            # Read only first 1000 rows for preview
                                            df = pd.read_csv(
                                                StringIO(report_response.content.decode('utf-8')),
                                                nrows=1000,  # Only read first 1000 rows
                                                low_memory=True
                                            )
                                            context[context_key] = df.to_html(
                                                classes='table table-striped table-bordered',
                                                index=False,
                                                float_format=lambda x: '{:.2f}'.format(x) if pd.notnull(x) else '',
                                                na_rep='',
                                                render_links=False,
                                                escape=False
                                            )
                                    except Exception as e:
                                        print(f"Error processing preview: {e}")
                        else:
                            context['error'] = f"API Error: {data.get('message', 'Unknown error')}"
                    else:
                        context['error'] = f"Error: API returned status code {response.status_code}"
                except requests.Timeout:
                    context['error'] = "Request timed out. Please try again."
                except Exception as e:
                    context['error'] = f"Error fetching data: {str(e)}"

    return render(request, 'report_dashboard/report.html', context)
