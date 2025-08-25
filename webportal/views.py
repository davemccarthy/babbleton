from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.conf import settings
import requests
import json
from datetime import date
from .models import Centres, Operators, Administrators, Calls, Sessions, Languages, Payplan

# Create your views here.

def live_traffic(request):
    """Live traffic monitoring"""
    context = {
        'page_title': 'Live Traffic',
        'active_section': 'live',
        'active_subsection': 'traffic'
    }
    return render(request, 'live-traffic.html', context)

def live_traffic_data(request):
    """AJAX endpoint to get traffic data from ANDROMEDA server"""
    try:
        # Get the ANDROMEDA server URL from settings
        andromeda_url = f"http://{settings.ANDROMEDA_SERVER}/globaldata"
        
        # Make HTTP request to ANDROMEDA server
        response = requests.get(andromeda_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse JSON response
        traffic_data = response.json()
        
        # Process the data to extract summary information
        summary_data = process_traffic_summary(traffic_data)
        
        # Process centres data for the chart
        centres_data = process_traffic_centres(traffic_data)
        
        # Combine summary and centres data
        response_data = {
            'summary': summary_data['summary'],
            'centres': centres_data
        }
        
        return JsonResponse(response_data)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from ANDROMEDA: {e}")
        return JsonResponse({
            'error': 'Failed to fetch data from ANDROMEDA server',
            'summary': {
                'traffic': 0,
                'operators': 0,
                'waiting': 0,
                'calls': 0,
                'minutes': 0,
                'acd': 0
            },
            'centres': []
        }, status=500)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from ANDROMEDA: {e}")
        return JsonResponse({
            'error': 'Invalid JSON response from ANDROMEDA server',
            'summary': {
                'traffic': 0,
                'operators': 0,
                'waiting': 0,
                'calls': 0,
                'minutes': 0,
                'acd': 0
            },
            'centres': []
        }, status=500)
    except Exception as e:
        print(f"Unexpected error in live_traffic_data: {e}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'summary': {
                'traffic': 0,
                'operators': 0,
                'waiting': 0,
                'calls': 0,
                'minutes': 0,
                'acd': 0
            },
            'centres': []
        }, status=500)

def process_traffic_summary(raw_data):
    """Process raw data from ANDROMEDA to extract summary information"""
    try:
        # Based on your JSON structure, the first object contains the summary data
        if len(raw_data) >= 1:
            summary_object = raw_data[0]
            
            # Extract the summary row data
            if 'rows' in summary_object and len(summary_object['rows']) > 0:
                summary_row = summary_object['rows'][0]
                
                # Based on current data: ["7", "7", "9", "", "", "", "0"]
                # Mapping: Traffic, Agents, Waiting, Calls, Minutes, ACD, (unused)
                summary = {
                    'traffic': int(summary_row[0]) if summary_row[0] and summary_row[0].isdigit() else 0,
                    'operators': int(summary_row[1]) if summary_row[1] and summary_row[1].isdigit() else 0,
                    'waiting': int(summary_row[2]) if summary_row[2] and summary_row[2].isdigit() else 0,
                    'calls': int(summary_row[3]) if summary_row[3] and summary_row[3].isdigit() else 0,
                    'minutes': int(summary_row[4]) if summary_row[4] and summary_row[4].isdigit() else 0,
                    'acd': int(summary_row[5]) if summary_row[5] and summary_row[5].isdigit() else 0
                }
                
                return {
                    'summary': summary
                }
        
        # Fallback if data structure is unexpected
        return {
            'summary': {
                'traffic': 0,
                'operators': 0,
                'waiting': 0,
                'calls': 0,
                'minutes': 0,
                'acd': 0
            }
        }
        
    except Exception as e:
        print(f"Error processing traffic summary: {e}")
        return {
            'summary': {
                'traffic': 0,
                'operators': 0,
                'waiting': 0,
                'calls': 0,
                'minutes': 0,
                'acd': 0
            }
        }

def process_traffic_centres(raw_data):
    """Process raw data from ANDROMEDA to extract centres data for chart"""
    try:
        centres = []
        
        print(f"Processing centres from {len(raw_data)} objects")
        
        # Skip the first object (summary) and process the rest as centres
        for i, centre_object in enumerate(raw_data[1:], 1):
            print(f"Processing centre object {i}: {centre_object}")
            
            if 'rows' in centre_object and len(centre_object['rows']) > 0:
                # Process all rows in this centre object (in case there are multiple centres in one object)
                for row_index, centre_row in enumerate(centre_object['rows']):
                    print(f"  Processing row {row_index}: {centre_row}")
                    
                    # Based on the JSON structure, extract centre data
                    # Columns: ['centre', 'id', 'operators', 'languages', 'calls', 'minutes', 'acd', 'traffic']
                    if len(centre_row) >= 8:
                        centre_data = {
                            'id': len(centres) + 1,  # Use sequential IDs
                            'name': centre_row[0] if centre_row[0] else f'Centre {len(centres) + 1}',
                            'operators': int(centre_row[2]) if centre_row[2] and centre_row[2].isdigit() else 0,  # operators is at index 2
                            'traffic': int(centre_row[7]) if centre_row[7] and centre_row[7].isdigit() else 0,   # traffic is at index 7
                            'languages': int(centre_row[3]) if centre_row[3] and centre_row[3].isdigit() else 0,  # languages is at index 3
                            'calls': int(centre_row[4]) if centre_row[4] and centre_row[4].isdigit() else 0,      # calls is at index 4
                            'minutes': int(centre_row[5]) if centre_row[5] and centre_row[5].isdigit() else 0,   # minutes is at index 5
                            'acd': int(centre_row[6]) if centre_row[6] and centre_row[6].isdigit() else 0        # acd is at index 6
                        }
                        centres.append(centre_data)
                        print(f"  Added centre: {centre_data}")
        
        print(f"Total centres processed: {len(centres)}")
        return centres
        
    except Exception as e:
        print(f"Error processing traffic centres: {e}")
        return []

def live_sessions(request):
    """Live sessions monitoring"""
    try:
        # Use raw SQL to get sessions with joins and calculated fields
        # Only show sessions where duration is null (active sessions)
        sessions_data = Sessions.objects.raw("""
            SELECT 
                s.id,
                s.operid,
                s.start,
                s.duration,
                s.callduration,
                s.calltotal,
                s.external,
                CONCAT(o.fname, ' ', o.sname) as agent_name,
                l.name as language_name,
                EXTRACT(EPOCH FROM (NOW() - s.start)) as duration_seconds
            FROM sessions s
            INNER JOIN operators o ON s.operid = o.id
            INNER JOIN languages l ON o.langid = l.id
            WHERE s.duration IS NULL
            ORDER BY s.start DESC
        """)
        
        context = {
            'page_title': 'Live Sessions',
            'active_section': 'live',
            'active_subsection': 'sessions',
            'sessions': sessions_data
        }
        return render(request, 'live-sessions.html', context)
    except Exception as e:
        print(f"Error in live_sessions view: {e}")
        messages.error(request, f'Error loading sessions: {str(e)}')
        context = {
            'page_title': 'Live Sessions',
            'active_section': 'live',
            'active_subsection': 'sessions',
            'sessions': []
        }
        return render(request, 'live-sessions.html', context)

def live_sessions_data(request):
    """AJAX endpoint to get sessions data"""
    try:
        # Use raw SQL to get sessions with joins and calculated fields
        # Only show sessions where duration is null (active sessions)
        sessions_data = Sessions.objects.raw("""
            SELECT 
                s.id,
                s.operid,
                s.start,
                s.duration,
                s.callduration,
                s.calltotal,
                s.external,
                CONCAT(o.fname, ' ', o.sname) as agent_name,
                l.name as language_name,
                EXTRACT(EPOCH FROM (NOW() - s.start)) as duration_seconds
            FROM sessions s
            INNER JOIN operators o ON s.operid = o.id
            INNER JOIN languages l ON o.langid = l.id
            WHERE s.duration IS NULL
            ORDER BY s.start DESC
        """)
        
        # Convert sessions to JSON-serializable format
        sessions_list = []
        for session in sessions_data:
            sessions_list.append({
                'id': session.id,
                'agent_name': session.agent_name,
                'start': session.start.strftime('%Y-%m-%d %H:%M:%S') if session.start else '',
                'duration_seconds': session.duration_seconds,
                'language_name': session.language_name,
                'calltotal': session.calltotal or 0,
                'callduration': session.callduration.total_seconds() if session.callduration else 0,
                'external': session.external
            })
        
        return JsonResponse({
            'sessions': sessions_list,
            'count': len(sessions_list)
        })
    except Exception as e:
        print(f"Error in live_sessions_data view: {e}")
        return JsonResponse({
            'error': str(e),
            'sessions': [],
            'count': 0
        }, status=500)

def reports_centres(request):
    """Centres reports with date range filtering"""
    from datetime import date, datetime
    
    # Get date range from request or use today as default
    start_date = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    try:
        # Convert string dates to datetime objects for the query
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        # Use raw SQL to get aggregated data grouped by centre
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.id as centre_id,
                    c.name as centre_name,
                    COUNT(DISTINCT o.langid) as languages_count,
                    COUNT(DISTINCT s.operid) as agents_count,
                    COUNT(s.id) as sessions_count,
                    COALESCE(SUM(s.calltotal), 0) as total_calls,
                    COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) as total_minutes_seconds,
                    CASE 
                        WHEN COALESCE(SUM(s.calltotal), 0) > 0 
                        THEN COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) / COALESCE(SUM(s.calltotal), 1)
                        ELSE 0 
                    END as acd_seconds
                FROM sessions s
                INNER JOIN operators o ON s.operid = o.id
                INNER JOIN centres c ON o.centreid = c.id
                WHERE s.duration IS NOT NULL
                    AND s.start >= %s
                    AND s.start <= %s
                GROUP BY c.id, c.name
                ORDER BY c.name
            """, [start_datetime, end_datetime])
            
            centres_data = []
            for row in cursor.fetchall():
                centres_data.append({
                    'centre_id': row[0],
                    'centre_name': row[1],
                    'languages_count': row[2],
                    'agents_count': row[3],
                    'sessions_count': row[4],
                    'total_calls': row[5],
                    'total_minutes_seconds': row[6],
                    'acd_seconds': row[7]
                })
        
        # Calculate summary totals
        total_sessions = sum(centre['sessions_count'] for centre in centres_data)
        total_calls = sum(centre['total_calls'] for centre in centres_data)
        total_minutes = sum(centre['total_minutes_seconds'] for centre in centres_data)
        
        context = {
            'page_title': 'Centres Reports',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centres_data': centres_data,
            'start_date': start_date,
            'end_date': end_date,
            'has_data': len(centres_data) > 0,
            'total_sessions': total_sessions,
            'total_calls': total_calls,
            'total_minutes': total_minutes
        }
        return render(request, 'reports-centres.html', context)
    except Exception as e:
        print(f"Error in reports_centres view: {e}")
        messages.error(request, f'Error loading centres report: {str(e)}')
        context = {
            'page_title': 'Centres Reports',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centres_data': [],
            'start_date': start_date,
            'end_date': end_date,
            'has_data': False
        }
        return render(request, 'reports-centres.html', context)

def reports_centre_detail(request, centre_id):
    """Centre detail report with language breakdown"""
    from datetime import date, datetime
    
    # Get date range from request or use today as default
    start_date = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    try:
        # Convert string dates to datetime objects for the query
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        # Get centre name first
        centre = Centres.objects.get(id=centre_id)
        
        # Use raw SQL to get aggregated data grouped by language for the specific centre
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    l.id as language_id,
                    l.name as language_name,
                    COUNT(DISTINCT s.operid) as agents_count,
                    COUNT(s.id) as sessions_count,
                    COALESCE(SUM(s.calltotal), 0) as total_calls,
                    COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) as total_minutes_seconds,
                    CASE 
                        WHEN COALESCE(SUM(s.calltotal), 0) > 0 
                        THEN COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) / COALESCE(SUM(s.calltotal), 1)
                        ELSE 0 
                    END as acd_seconds
                FROM sessions s
                INNER JOIN operators o ON s.operid = o.id
                INNER JOIN languages l ON o.langid = l.id
                WHERE s.duration IS NOT NULL
                    AND s.start >= %s
                    AND s.start <= %s
                    AND o.centreid = %s
                GROUP BY l.id, l.name
                ORDER BY l.name
            """, [start_datetime, end_datetime, centre_id])
            
            languages_data = []
            for row in cursor.fetchall():
                languages_data.append({
                    'language_id': row[0],
                    'language_name': row[1],
                    'agents_count': row[2],
                    'sessions_count': row[3],
                    'total_calls': row[4],
                    'total_minutes_seconds': row[5],
                    'acd_seconds': row[6]
                })
        
        # Calculate Rate and Due for each language
        for lang_data in languages_data:
            lang_id = lang_data['language_id']
            acd_minutes = lang_data['acd_seconds'] / 60  # Convert seconds to minutes
            
            # Find appropriate payplan rate
            rate = None
            due = None
            
            if acd_minutes > 0:  # Only calculate if we have ACD
                # Convert ACD to seconds for payplan comparison (payplan.acd is in seconds)
                acd_seconds = lang_data['acd_seconds']
                
                # First try to find centre-specific payplan
                centre_payplans = Payplan.objects.filter(
                    langid=lang_id,
                    centreid=centre_id
                ).order_by('acd')
                
                # If no centre-specific, try global payplan (centreid=0)
                if not centre_payplans.exists():
                    centre_payplans = Payplan.objects.filter(
                        langid=lang_id,
                        centreid=0
                    ).order_by('acd')
                
                if centre_payplans.exists():
                    # Find the payplan where payplan.acd <= language_acd_seconds < next_payplan.acd
                    payplans_list = list(centre_payplans)
                    
                    for i, payplan in enumerate(payplans_list):
                        if i == len(payplans_list) - 1:
                            # Last payplan - use it if acd_seconds >= payplan.acd
                            if acd_seconds >= payplan.acd:
                                rate = payplan.rate
                                break
                        else:
                            # Check if acd_seconds is in this range
                            next_payplan = payplans_list[i + 1]
                            if payplan.acd <= acd_seconds < next_payplan.acd:
                                rate = payplan.rate
                                break
                    
                    # If no range found, use the first payplan if acd_seconds >= its acd
                    if rate is None and payplans_list and acd_seconds >= payplans_list[0].acd:
                        rate = payplans_list[0].rate
                
                # Calculate Due amount (rate is per minute, so multiply total minutes by rate)
                if rate is not None:
                    total_minutes_for_lang = lang_data['total_minutes_seconds'] / 60  # Convert total seconds to minutes
                    due = float(total_minutes_for_lang) * float(rate)
            
            lang_data['rate'] = rate
            lang_data['due'] = due
        
        # Calculate summary totals
        total_sessions = sum(lang['sessions_count'] for lang in languages_data)
        total_calls = sum(lang['total_calls'] for lang in languages_data)
        total_minutes = sum(lang['total_minutes_seconds'] for lang in languages_data)
        total_due = sum(lang['due'] or 0 for lang in languages_data)
        
        context = {
            'page_title': f'Centre Detail - {centre.name}',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centre': centre,
            'languages_data': languages_data,
            'start_date': start_date,
            'end_date': end_date,
            'has_data': len(languages_data) > 0,
            'total_sessions': total_sessions,
            'total_calls': total_calls,
            'total_minutes': total_minutes,
            'total_due': total_due
        }
        return render(request, 'reports-centre-detail.html', context)
    except Centres.DoesNotExist:
        messages.error(request, 'Centre not found.')
        return redirect('reports-centres')
    except Exception as e:
        print(f"Error in reports_centre_detail view: {e}")
        messages.error(request, f'Error loading centre detail: {str(e)}')
        context = {
            'page_title': 'Centre Detail',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centre': None,
            'languages_data': [],
            'start_date': start_date,
            'end_date': end_date,
            'has_data': False,
            'total_sessions': 0,
            'total_calls': 0,
            'total_minutes': 0,
            'total_due': 0
        }
        return render(request, 'reports-centre-detail.html', context)

def reports_friends(request):
    """Friends reports"""
    context = {
        'page_title': 'Friends Reports',
        'active_section': 'reports',
        'active_subsection': 'friends'
    }
    return render(request, 'reports-friends.html', context)

def reports_historical(request):
    """Historical reports"""
    context = {
        'page_title': 'Historical Reports',
        'active_section': 'reports',
        'active_subsection': 'historical'
    }
    return render(request, 'reports-historical.html', context)

def reports_language_detail(request, centre_id, language_id):
    """Detailed report for a specific language within a centre, showing agents"""
    try:
        # Get date range from query parameters
        start_date = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
        end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        # Get centre and language details
        centre = get_object_or_404(Centres, id=centre_id)
        language = get_object_or_404(Languages, id=language_id)
        
        # Use raw SQL to get aggregated data grouped by operatorid
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    o.id as operator_id,
                    o.fname,
                    o.sname,
                    COUNT(s.id) as sessions_count,
                    COALESCE(SUM(s.calltotal), 0) as total_calls,
                    COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) as total_minutes_seconds,
                    CASE 
                        WHEN COALESCE(SUM(s.calltotal), 0) > 0 
                        THEN COALESCE(SUM(EXTRACT(EPOCH FROM s.callduration)), 0) / COALESCE(SUM(s.calltotal), 1)
                        ELSE 0 
                    END as acd_seconds
                FROM sessions s
                INNER JOIN operators o ON s.operid = o.id
                WHERE o.centreid = %s 
                AND o.langid = %s
                AND s.duration IS NOT NULL
                AND DATE(s.start) BETWEEN %s AND %s
                GROUP BY o.id, o.fname, o.sname
                ORDER BY o.fname, o.sname
            """, [centre_id, language_id, start_date, end_date])
            
            agents_data = []
            total_sessions = 0
            total_calls = 0
            total_minutes = 0
            
            for row in cursor.fetchall():
                agent_data = {
                    'operator_id': row[0],
                    'fname': row[1],
                    'sname': row[2],
                    'sessions_count': row[3],
                    'total_calls': row[4],
                    'total_minutes_seconds': row[5],
                    'acd_seconds': row[6]
                }
                agents_data.append(agent_data)
                
                total_sessions += row[3]
                total_calls += row[4]
                total_minutes += row[5]
        
        # Calculate overall ACD
        overall_acd = total_minutes / total_calls if total_calls > 0 else 0
        
        context = {
            'page_title': f'Agent Report - {centre.name} - {language.name}',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centre': centre,
            'language': language,
            'agents_data': agents_data,
            'start_date': start_date,
            'end_date': end_date,
            'total_sessions': total_sessions,
            'total_calls': total_calls,
            'total_minutes': total_minutes,
            'overall_acd': overall_acd
        }
        
        return render(request, 'reports-language-detail.html', context)
        
    except Exception as e:
        print(f"Error in reports_language_detail view: {e}")
        messages.error(request, f'Error loading report: {str(e)}')
        return redirect('reports-centres')

def reports_agent_detail(request, centre_id, language_id, operator_id):
    """Detailed report for a specific agent, showing individual sessions"""
    try:
        # Get date range from query parameters
        start_date = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
        end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        # Get centre, language, and operator details
        centre = get_object_or_404(Centres, id=centre_id)
        language = get_object_or_404(Languages, id=language_id)
        operator = get_object_or_404(Operators, id=operator_id)
        
        # Use raw SQL to get individual sessions for the agent
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.id as session_id,
                    s.start,
                    EXTRACT(EPOCH FROM s.duration) as duration_seconds,
                    COALESCE(d.username, 'Unknown Device') as device_name,
                    s.calltotal,
                    EXTRACT(EPOCH FROM s.callduration) as callduration_seconds,
                    CASE 
                        WHEN s.calltotal > 0 
                        THEN EXTRACT(EPOCH FROM s.callduration) / s.calltotal
                        ELSE 0 
                    END as acd_seconds
                FROM sessions s
                LEFT JOIN devices d ON s.devid = d.id
                WHERE s.operid = %s 
                AND s.duration IS NOT NULL
                AND DATE(s.start) BETWEEN %s AND %s
                ORDER BY s.start DESC
            """, [operator_id, start_date, end_date])
            
            sessions_data = []
            total_calls = 0
            total_minutes = 0
            
            for row in cursor.fetchall():
                session_data = {
                    'session_id': row[0],
                    'start': row[1],
                    'duration_seconds': row[2],
                    'device_name': row[3],
                    'calltotal': row[4],
                    'callduration_seconds': row[5],
                    'acd_seconds': row[6]
                }
                sessions_data.append(session_data)
                
                total_calls += row[4] if row[4] else 0
                total_minutes += row[5] if row[5] else 0
        
        # Calculate overall ACD
        overall_acd = total_minutes / total_calls if total_calls > 0 else 0
        
        context = {
            'page_title': f'Session Report - {operator.fname} {operator.sname}',
            'active_section': 'reports',
            'active_subsection': 'centres',
            'centre': centre,
            'language': language,
            'operator': operator,
            'sessions_data': sessions_data,
            'start_date': start_date,
            'end_date': end_date,
            'total_calls': total_calls,
            'total_minutes': total_minutes,
            'overall_acd': overall_acd
        }
        
        return render(request, 'reports-agent-detail.html', context)
        
    except Exception as e:
        print(f"Error in reports_agent_detail view: {e}")
        messages.error(request, f'Error loading report: {str(e)}')
        return redirect('reports-centres')

def admin_centres(request):
    """Centres administration - list view"""
    try:
        centres = Centres.objects.all().order_by('name')
        
        # Handle search
        search_query = request.GET.get('search', '')
        if search_query:
            centres = centres.filter(name__icontains=search_query)
        
        # Handle status filter
        status_filter = request.GET.get('status', '')
        if status_filter == 'active':
            centres = centres.filter(disabled=False)
        elif status_filter == 'disabled':
            centres = centres.filter(disabled=True)
        
        context = {
            'page_title': 'Centres Administration',
            'active_section': 'admin',
            'active_subsection': 'centres',
            'centres': centres,
            'search_query': search_query,
            'status_filter': status_filter
        }
        return render(request, 'admin-centres.html', context)
    except Exception as e:
        print(f"Error in admin_centres view: {e}")
        raise

def admin_centres_create(request):
    """Create new centre"""
    if request.method == 'POST':
        try:
            centre = Centres(
                name=request.POST.get('name'),
                abbreviation=request.POST.get('abbreviation'),
                contact=request.POST.get('contact'),
                email=request.POST.get('email'),
                mobile=request.POST.get('mobile'),
                disabled=request.POST.get('disabled') == 'on',
                dedicated=request.POST.get('dedicated') == 'on',
                billname=request.POST.get('billname'),
                address1=request.POST.get('address1'),
                address2=request.POST.get('address2'),
                address3=request.POST.get('address3'),
                address4=request.POST.get('address4')
            )
            centre.save()
            messages.success(request, f'Centre "{centre.name}" created successfully.')
            return redirect('admin-centres')
        except Exception as e:
            messages.error(request, f'Error creating centre: {str(e)}')
    
    context = {
        'page_title': 'Create New Centre',
        'active_section': 'admin',
        'active_subsection': 'centres'
    }
    return render(request, 'admin-centres-form.html', context)

def admin_centres_edit(request, centre_id):
    """Edit existing centre"""
    centre = get_object_or_404(Centres, id=centre_id)
    
    if request.method == 'POST':
        try:
            centre.name = request.POST.get('name')
            centre.abbreviation = request.POST.get('abbreviation')
            centre.contact = request.POST.get('contact')
            centre.email = request.POST.get('email')
            centre.mobile = request.POST.get('mobile')
            centre.disabled = request.POST.get('disabled') == 'on'
            centre.dedicated = request.POST.get('dedicated') == 'on'
            centre.billname = request.POST.get('billname')
            centre.address1 = request.POST.get('address1')
            centre.address2 = request.POST.get('address2')
            centre.address3 = request.POST.get('address3')
            centre.address4 = request.POST.get('address4')
            centre.save()
            messages.success(request, f'Centre "{centre.name}" updated successfully.')
            return redirect('admin-centres')
        except Exception as e:
            messages.error(request, f'Error updating centre: {str(e)}')
    
    context = {
        'page_title': f'Edit Centre - {centre.name}',
        'active_section': 'admin',
        'active_subsection': 'centres',
        'centre': centre
    }
    return render(request, 'admin-centres-form.html', context)

def admin_centres_delete(request, centre_id):
    """Delete centre with confirmation"""
    centre = get_object_or_404(Centres, id=centre_id)
    
    if request.method == 'POST':
        try:
            centre_name = centre.name
            centre.delete()
            messages.success(request, f'Centre "{centre_name}" deleted successfully.')
            return redirect('admin-centres')
        except Exception as e:
            messages.error(request, f'Error deleting centre: {str(e)}')
            return redirect('admin-centres')
    
    context = {
        'page_title': f'Delete Centre - {centre.name}',
        'active_section': 'admin',
        'active_subsection': 'centres',
        'centre': centre
    }
    return render(request, 'admin-centres-delete.html', context)

def admin_operators(request):
    """Operators administration with inner joins"""
    try:
        # Use raw SQL for complex inner joins with aggregated data
        operators_data = Operators.objects.raw("""
            SELECT 
                o.id,
                o.identifier,
                CONCAT(o.fname, ' ', o.sname) as full_name,
                c.name as centre_name,
                l.name as language_name,
                o.calltotal,
                o.callduration
            FROM operators o
            INNER JOIN centres c ON o.centreid = c.id
            INNER JOIN languages l ON o.langid = l.id
            ORDER BY o.id DESC
        """)
        
        # Handle search
        search_query = request.GET.get('search', '')
        if search_query:
            operators_data = Operators.objects.raw("""
                SELECT 
                    o.id,
                    o.identifier,
                    CONCAT(o.fname, ' ', o.sname) as full_name,
                    c.name as centre_name,
                    l.name as language_name,
                    o.calltotal,
                    o.callduration
                FROM operators o
                INNER JOIN centres c ON o.centreid = c.id
                INNER JOIN languages l ON o.langid = l.id
                WHERE o.fname LIKE %s OR o.sname LIKE %s OR o.identifier LIKE %s
                ORDER BY o.id DESC
            """, [f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
        
        # Handle centre filter
        centre_filter = request.GET.get('centre', '')
        if centre_filter:
            operators_data = Operators.objects.raw("""
                SELECT 
                    o.id,
                    o.identifier,
                    CONCAT(o.fname, ' ', o.sname) as full_name,
                    c.name as centre_name,
                    l.name as language_name,
                    o.calltotal,
                    o.callduration
                FROM operators o
                INNER JOIN centres c ON o.centreid = c.id
                INNER JOIN languages l ON o.langid = l.id
                WHERE c.id = %s
                ORDER BY o.id DESC
            """, [centre_filter])
        
        # Get all centres for filter dropdown
        centres = Centres.objects.all().order_by('name')
        
        context = {
            'page_title': 'Agents Administration',
            'active_section': 'admin',
            'active_subsection': 'operators',
            'operators': operators_data,
            'centres': centres,
            'search_query': search_query,
            'centre_filter': centre_filter
        }
        return render(request, 'admin-operators.html', context)
    except Exception as e:
        print(f"Error in admin_operators view: {e}")
        messages.error(request, f'Error loading operators: {str(e)}')
        context = {
            'page_title': 'Agents Administration',
            'active_section': 'admin',
            'active_subsection': 'operators',
            'operators': [],
            'centres': [],
            'search_query': '',
            'centre_filter': ''
        }
        return render(request, 'admin-operators.html', context)

def admin_administrators(request):
    """Administrators administration"""
    # Fetch administrators with centre information using raw SQL
    administrators = Administrators.objects.raw("""
        SELECT a.id, a.centreid, a.name, a.username, a.email, a.mobile,
               COALESCE(c.name, 'Unknown Centre') as centre_name
        FROM administrators a
        LEFT JOIN centres c ON a.centreid = c.id
        ORDER BY a.id DESC
    """)
    
    context = {
        'page_title': 'Administrators Administration',
        'active_section': 'admin',
        'active_subsection': 'administrators',
        'administrators': administrators
    }
    return render(request, 'admin-administrators.html', context)

def admin_payments(request):
    """Payments administration with grouped data"""
    try:
        # Use raw SQL to get payplan data grouped by language and centre
        payplan_data = Payplan.objects.raw("""
            SELECT 
                p.id,
                p.centreid,
                p.langid,
                p.acd,
                p.rate,
                l.name as language_name,
                CASE 
                    WHEN p.centreid = 0 THEN 'Global'
                    ELSE c.name 
                END as centre_name,
                CASE 
                    WHEN p.centreid = 0 THEN 'Language Only'
                    ELSE 'Centre Specific'
                END as plan_type
            FROM payplan p
            INNER JOIN languages l ON p.langid = l.id
            LEFT JOIN centres c ON p.centreid = c.id
            ORDER BY l.name, 
                     CASE WHEN p.centreid = 0 THEN 0 ELSE 1 END,
                     c.name,
                     p.acd DESC
        """)
        
        # Handle search
        search_query = request.GET.get('search', '')
        if search_query:
            payplan_data = Payplan.objects.raw("""
                SELECT 
                    p.id,
                    p.centreid,
                    p.langid,
                    p.acd,
                    p.rate,
                    l.name as language_name,
                    CASE 
                        WHEN p.centreid = 0 THEN 'Global'
                        ELSE c.name 
                    END as centre_name,
                    CASE 
                        WHEN p.centreid = 0 THEN 'Language Only'
                        ELSE 'Centre Specific'
                    END as plan_type
                FROM payplan p
                INNER JOIN languages l ON p.langid = l.id
                LEFT JOIN centres c ON p.centreid = c.id
                WHERE l.name LIKE %s OR c.name LIKE %s
                ORDER BY l.name, 
                         CASE WHEN p.centreid = 0 THEN 0 ELSE 1 END,
                         c.name,
                         p.acd DESC
            """, [f'%{search_query}%', f'%{search_query}%'])
        
        # Handle language filter
        language_filter = request.GET.get('language', '')
        if language_filter:
            payplan_data = Payplan.objects.raw("""
                SELECT 
                    p.id,
                    p.centreid,
                    p.langid,
                    p.acd,
                    p.rate,
                    l.name as language_name,
                    CASE 
                        WHEN p.centreid = 0 THEN 'Global'
                        ELSE c.name 
                    END as centre_name,
                    CASE 
                        WHEN p.centreid = 0 THEN 'Language Only'
                        ELSE 'Centre Specific'
                    END as plan_type
                FROM payplan p
                INNER JOIN languages l ON p.langid = l.id
                LEFT JOIN centres c ON p.centreid = c.id
                WHERE l.id = %s
                ORDER BY l.name, 
                         CASE WHEN p.centreid = 0 THEN 0 ELSE 1 END,
                         c.name,
                         p.acd DESC
            """, [language_filter])
        
        # Get all languages for filter dropdown
        languages = Languages.objects.all().order_by('name')
        
        context = {
            'page_title': 'Payments Administration',
            'active_section': 'admin',
            'active_subsection': 'payments',
            'payplans': payplan_data,
            'languages': languages,
            'search_query': search_query,
            'language_filter': language_filter
        }
        return render(request, 'admin-payments.html', context)
    except Exception as e:
        print(f"Error in admin_payments view: {e}")
        messages.error(request, f'Error loading payments: {str(e)}')
        context = {
            'page_title': 'Payments Administration',
            'active_section': 'admin',
            'active_subsection': 'payments',
            'payplans': [],
            'languages': [],
            'search_query': '',
            'language_filter': ''
        }
        return render(request, 'admin-payments.html', context)

def admin_payments_create(request):
    """Create new payplan"""
    if request.method == 'POST':
        try:
            payplan = Payplan(
                centreid=request.POST.get('centreid') or 0,
                langid=request.POST.get('langid'),
                acd=request.POST.get('acd') or 0,
                rate=request.POST.get('rate') or 0.0
            )
            payplan.save()
            messages.success(request, f'Payplan created successfully.')
            return redirect('admin-payments')
        except Exception as e:
            messages.error(request, f'Error creating payplan: {str(e)}')
    
    # Get centres and languages for dropdowns
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    context = {
        'page_title': 'Create New Payplan',
        'active_section': 'admin',
        'active_subsection': 'payments',
        'centres': centres,
        'languages': languages
    }
    return render(request, 'admin-payments-form.html', context)

def admin_payments_edit(request, payplan_id):
    """Edit existing payplan"""
    payplan = get_object_or_404(Payplan, id=payplan_id)
    
    if request.method == 'POST':
        try:
            payplan.centreid = request.POST.get('centreid') or 0
            payplan.langid = request.POST.get('langid')
            payplan.acd = request.POST.get('acd') or 0
            payplan.rate = request.POST.get('rate') or 0.0
            payplan.save()
            messages.success(request, f'Payplan updated successfully.')
            return redirect('admin-payments')
        except Exception as e:
            messages.error(request, f'Error updating payplan: {str(e)}')
    
    # Get centres and languages for dropdowns
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    context = {
        'page_title': f'Edit Payplan',
        'active_section': 'admin',
        'active_subsection': 'payments',
        'payplan': payplan,
        'centres': centres,
        'languages': languages
    }
    return render(request, 'admin-payments-form.html', context)

def admin_payments_delete(request, payplan_id):
    """Delete payplan with confirmation"""
    # Get payplan with related data for display
    payplan_data = Payplan.objects.raw("""
        SELECT 
            p.id,
            p.centreid,
            p.langid,
            p.acd,
            p.rate,
            l.name as language_name,
            CASE 
                WHEN p.centreid = 0 THEN 'Global'
                ELSE c.name 
            END as centre_name
        FROM payplan p
        INNER JOIN languages l ON p.langid = l.id
        LEFT JOIN centres c ON p.centreid = c.id
        WHERE p.id = %s
    """, [payplan_id])
    
    if not payplan_data:
        messages.error(request, 'Payplan not found.')
        return redirect('admin-payments')
    
    payplan = payplan_data[0]
    
    if request.method == 'POST':
        try:
            # Delete the payplan
            Payplan.objects.filter(id=payplan_id).delete()
            
            messages.success(request, f'Payplan deleted successfully.')
            return redirect('admin-payments')
        except Exception as e:
            messages.error(request, f'Error deleting payplan: {str(e)}')
            return redirect('admin-payments')
    
    context = {
        'page_title': f'Delete Payplan',
        'active_section': 'admin',
        'active_subsection': 'payments',
        'payplan': payplan
    }
    return render(request, 'admin-payments-delete.html', context)

def generate_unique_identifier():
    """Generate a unique 4-digit numeric identifier for new agents"""
    import random
    
    # Get all existing identifiers to avoid duplicates
    existing_identifiers = set(Operators.objects.values_list('identifier', flat=True))
    
    # Generate a unique 4-digit number
    max_attempts = 1000  # Prevent infinite loop
    attempts = 0
    
    while attempts < max_attempts:
        # Generate a 4-digit numeric identifier (1000-9999)
        identifier = str(random.randint(1000, 9999))
        
        # Check if it already exists
        if identifier not in existing_identifiers:
            return identifier
        
        attempts += 1
    
    # If we can't find a unique number after many attempts, raise an error
    raise ValueError("Unable to generate unique identifier after 1000 attempts")

def admin_operators_create(request):
    """Create new agent"""
    if request.method == 'POST':
        try:
            # Generate unique identifier
            identifier = generate_unique_identifier()
            
            # Create new operator (ID will be auto-generated by database)
            operator = Operators(
                fname=request.POST.get('fname'),
                sname=request.POST.get('sname'),
                centreid=request.POST.get('centreid'),
                langid=request.POST.get('langid'),
                email=request.POST.get('email') or None,
                mobile=request.POST.get('mobile') or None,
                identifier=identifier,
                calltotal=0,
                callduration=None
            )
            operator.save()
            
            messages.success(request, f'Agent "{operator.fname} {operator.sname}" created successfully with ID {identifier}.')
            return redirect('admin-operators')
        except Exception as e:
            messages.error(request, f'Error creating agent: {str(e)}')
    
    # Get centres and languages for dropdowns
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    context = {
        'page_title': 'Add New Agent',
        'active_section': 'admin',
        'active_subsection': 'operators',
        'centres': centres,
        'languages': languages
    }
    return render(request, 'admin-operators-form.html', context)

def admin_operators_edit(request, operator_id):
    """Edit existing agent"""
    operator = get_object_or_404(Operators, id=operator_id)
    
    if request.method == 'POST':
        try:
            operator.fname = request.POST.get('fname')
            operator.sname = request.POST.get('sname')
            operator.centreid = request.POST.get('centreid')
            operator.langid = request.POST.get('langid')
            operator.email = request.POST.get('email') or None
            operator.mobile = request.POST.get('mobile') or None
            operator.save()
            
            messages.success(request, f'Agent "{operator.fname} {operator.sname}" updated successfully.')
            return redirect('admin-operators')
        except Exception as e:
            messages.error(request, f'Error updating agent: {str(e)}')
    
    # Get centres and languages for dropdowns
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    context = {
        'page_title': f'Edit Agent - {operator.fname} {operator.sname}',
        'active_section': 'admin',
        'active_subsection': 'operators',
        'operator': operator,
        'centres': centres,
        'languages': languages
    }
    return render(request, 'admin-operators-form.html', context)

def admin_operators_delete(request, operator_id):
    """Delete agent with confirmation"""
    # Get operator with related data for display
    operator_data = Operators.objects.raw("""
        SELECT 
            o.id,
            o.identifier,
            CONCAT(o.fname, ' ', o.sname) as full_name,
            o.fname,
            o.sname,
            c.name as centre_name,
            l.name as language_name
        FROM operators o
        INNER JOIN centres c ON o.centreid = c.id
        INNER JOIN languages l ON o.langid = l.id
        WHERE o.id = %s
    """, [operator_id])
    
    if not operator_data:
        messages.error(request, 'Agent not found.')
        return redirect('admin-operators')
    
    operator = operator_data[0]
    
    if request.method == 'POST':
        try:
            operator_name = f"{operator.fname} {operator.sname}"
            operator_identifier = operator.identifier
            
            # Delete the operator
            Operators.objects.filter(id=operator_id).delete()
            
            messages.success(request, f'Agent "{operator_name}" (ID: {operator_identifier}) deleted successfully.')
            return redirect('admin-operators')
        except Exception as e:
            messages.error(request, f'Error deleting agent: {str(e)}')
            return redirect('admin-operators')
    
    context = {
        'page_title': f'Delete Agent - {operator.fname} {operator.sname}',
        'active_section': 'admin',
        'active_subsection': 'operators',
        'operator': operator
    }
    return render(request, 'admin-operators-delete.html', context)

def admin_administrators_create(request):
    """Create new administrator"""
    if request.method == 'POST':
        try:
            # Use raw SQL to reset the sequence and let the database handle auto-increment properly
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Reset the auto-increment sequence to the correct value
                cursor.execute("SELECT setval('administrators_id_seq', (SELECT COALESCE(MAX(id), 0) FROM administrators))")
                
                # Now insert without specifying ID - let the database handle it
                cursor.execute("""
                    INSERT INTO administrators (name, centreid, username, email, mobile, password, accessed, restricted, notifications)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    request.POST.get('name'),
                    request.POST.get('centreid'),
                    request.POST.get('username'),
                    request.POST.get('email') or None,
                    request.POST.get('mobile') or None,
                    request.POST.get('password'),  # password from form
                    None,  # accessed
                    False,  # restricted
                    True   # notifications
                ])
            
            messages.success(request, f'Administrator "{request.POST.get("name")}" created successfully.')
            return redirect('admin-administrators')
        except Exception as e:
            messages.error(request, f'Error creating administrator: {str(e)}')
    
    # Get centres for dropdown
    centres = Centres.objects.all().order_by('name')
    
    context = {
        'page_title': 'Add New Administrator',
        'active_section': 'admin',
        'active_subsection': 'administrators',
        'centres': centres
    }
    return render(request, 'admin-administrators-form.html', context)

def admin_administrators_edit(request, administrator_id):
    """Edit existing administrator"""
    administrator = get_object_or_404(Administrators, id=administrator_id)
    
    if request.method == 'POST':
        try:
            administrator.name = request.POST.get('name')
            administrator.centreid = request.POST.get('centreid')
            administrator.username = request.POST.get('username')
            administrator.password = request.POST.get('password')
            administrator.email = request.POST.get('email') or None
            administrator.mobile = request.POST.get('mobile') or None
            administrator.save()
            
            messages.success(request, f'Administrator "{administrator.name}" updated successfully.')
            return redirect('admin-administrators')
        except Exception as e:
            messages.error(request, f'Error updating administrator: {str(e)}')
    
    # Get centres for dropdown
    centres = Centres.objects.all().order_by('name')
    
    context = {
        'page_title': f'Edit Administrator - {administrator.name}',
        'active_section': 'admin',
        'active_subsection': 'administrators',
        'administrator': administrator,
        'centres': centres
    }
    return render(request, 'admin-administrators-form.html', context)

def admin_administrators_delete(request, administrator_id):
    """Delete administrator with confirmation"""
    # Get administrator with related data for display
    administrator_data = Administrators.objects.raw("""
        SELECT 
            a.id,
            a.name,
            a.username,
            a.email,
            a.mobile,
            COALESCE(c.name, 'Unknown Centre') as centre_name
        FROM administrators a
        LEFT JOIN centres c ON a.centreid = c.id
        WHERE a.id = %s
    """, [administrator_id])
    
    if not administrator_data:
        messages.error(request, 'Administrator not found.')
        return redirect('admin-administrators')
    
    administrator = administrator_data[0]
    
    if request.method == 'POST':
        try:
            administrator_name = administrator.name
            
            # Delete the administrator
            Administrators.objects.filter(id=administrator_id).delete()
            
            messages.success(request, f'Administrator "{administrator_name}" deleted successfully.')
            return redirect('admin-administrators')
        except Exception as e:
            messages.error(request, f'Error deleting administrator: {str(e)}')
            return redirect('admin-administrators')
    
    context = {
        'page_title': f'Delete Administrator - {administrator.name}',
        'active_section': 'admin',
        'active_subsection': 'administrators',
        'administrator': administrator
    }
    return render(request, 'admin-administrators-delete.html', context)

def centre_detail(request, centre_id):
    """Placeholder view for centre detail - redirects to reports"""
    return redirect('reports-centres')
