from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from .models import Centres, Operators, Administrators, Calls, Sessions, Languages

# Create your views here.

def dashboard(request):
    """Main dashboard view"""
    context = {
        'page_title': 'Dashboard',
        'active_section': 'dashboard'
    }
    return render(request, 'dashboard.html', context)

def live_traffic(request):
    """Live traffic monitoring"""
    context = {
        'page_title': 'Live Traffic',
        'active_section': 'live',
        'active_subsection': 'traffic'
    }
    return render(request, 'live-traffic.html', context)

def live_sessions(request):
    """Live sessions monitoring"""
    context = {
        'page_title': 'Live Sessions',
        'active_section': 'live',
        'active_subsection': 'sessions'
    }
    return render(request, 'live-sessions.html', context)

def reports_centres(request):
    """Centres reports"""
    context = {
        'page_title': 'Centres Reports',
        'active_section': 'reports',
        'active_subsection': 'centres'
    }
    return render(request, 'reports-centres.html', context)

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
    context = {
        'page_title': 'Administrators Administration',
        'active_section': 'admin',
        'active_subsection': 'administrators'
    }
    return render(request, 'admin-administrators.html', context)

def admin_payments(request):
    """Payments administration"""
    context = {
        'page_title': 'Payments Administration',
        'active_section': 'admin',
        'active_subsection': 'payments'
    }
    return render(request, 'admin-payments.html', context)

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
