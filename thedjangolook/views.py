from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Operators, Centres, Languages


def agent_list(request):
    """List all agents with search and filtering capabilities"""
    agents = Operators.objects.all().order_by('fname', 'sname')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        agents = agents.filter(
            Q(fname__icontains=search_query) |
            Q(sname__icontains=search_query) |
            Q(identifier__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Get centres and languages for display
    centres = Centres.objects.all()
    languages = Languages.objects.all()
    
    # Create lookup dictionaries for efficient display
    centre_lookup = {centre.id: centre.name for centre in centres}
    language_lookup = {lang.id: lang.name for lang in languages}
    
    # Pagination
    paginator = Paginator(agents, 50)  # Show 50 agents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add display names to agents on the current page
    for agent in page_obj:
        agent.centre_name = centre_lookup.get(agent.centreid, 'Unknown Centre')
        agent.language_name = language_lookup.get(agent.langid, 'Unknown Language')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'thedjangolook/agent_list.html', context)


def agent_create(request):
    """Create a new agent"""
    if request.method == 'POST':
        try:
            # Get form data
            centre_name = request.POST.get('centre_name')
            language_name = request.POST.get('language_name')
            
            # Find centre and language IDs
            centre = Centres.objects.filter(name=centre_name).first()
            language = Languages.objects.filter(name=language_name).first()
            
            if not centre:
                messages.error(request, f'Centre "{centre_name}" not found.')
                return redirect('thedjangolook:agent_create')
            
            if not language:
                messages.error(request, f'Language "{language_name}" not found.')
                return redirect('thedjangolook:agent_create')
            
            # Create the agent
            agent = Operators.objects.create(
                centreid=centre.id,
                langid=language.id,
                status=request.POST.get('status', 'ins'),
                identifier=request.POST.get('identifier'),
                fname=request.POST.get('fname'),
                sname=request.POST.get('sname'),
                mobile=request.POST.get('mobile'),
                email=request.POST.get('email'),
            )
            
            messages.success(request, f'Agent "{agent.fname} {agent.sname}" created successfully.')
            return redirect('thedjangolook:agent_list')
            
        except Exception as e:
            messages.error(request, f'Error creating agent: {str(e)}')
            return redirect('thedjangolook:agent_create')
    
    # GET request - show form
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    context = {
        'centres': centres,
        'languages': languages,
        'status_choices': ['ins', 'sus', 'oos'],
    }
    return render(request, 'thedjangolook/agent_form.html', context)


def agent_update(request, agent_id):
    """Update an existing agent"""
    agent = get_object_or_404(Operators, id=agent_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            centre_name = request.POST.get('centre_name')
            language_name = request.POST.get('language_name')
            
            # Find centre and language IDs
            centre = Centres.objects.filter(name=centre_name).first()
            language = Languages.objects.filter(name=language_name).first()
            
            if not centre:
                messages.error(request, f'Centre "{centre_name}" not found.')
                return redirect('thedjangolook:agent_update', agent_id=agent_id)
            
            if not language:
                messages.error(request, f'Language "{language_name}" not found.')
                return redirect('thedjangolook:agent_update', agent_id=agent_id)
            
            # Update the agent
            agent.centreid = centre.id
            agent.langid = language.id
            agent.status = request.POST.get('status')
            agent.identifier = request.POST.get('identifier')
            agent.fname = request.POST.get('fname')
            agent.sname = request.POST.get('sname')
            agent.mobile = request.POST.get('mobile')
            agent.email = request.POST.get('email')
            agent.save()
            
            messages.success(request, f'Agent "{agent.fname} {agent.sname}" updated successfully.')
            return redirect('thedjangolook:agent_list')
            
        except Exception as e:
            messages.error(request, f'Error updating agent: {str(e)}')
            return redirect('thedjangolook:agent_update', agent_id=agent_id)
    
    # GET request - show form with current data
    centres = Centres.objects.all().order_by('name')
    languages = Languages.objects.all().order_by('name')
    
    # Get current centre and language names
    current_centre = Centres.objects.filter(id=agent.centreid).first()
    current_language = Languages.objects.filter(id=agent.langid).first()
    
    context = {
        'agent': agent,
        'centres': centres,
        'languages': languages,
        'current_centre_name': current_centre.name if current_centre else '',
        'current_language_name': current_language.name if current_language else '',
        'status_choices': ['ins', 'sus', 'oos'],
    }
    return render(request, 'thedjangolook/agent_form.html', context)


def agent_delete(request, agent_id):
    """Delete an agent"""
    agent = get_object_or_404(Operators, id=agent_id)
    
    if request.method == 'POST':
        try:
            agent_name = f"{agent.fname} {agent.sname}"
            agent.delete()
            messages.success(request, f'Agent "{agent_name}" deleted successfully.')
            return redirect('thedjangolook:agent_list')
        except Exception as e:
            messages.error(request, f'Error deleting agent: {str(e)}')
            return redirect('thedjangolook:agent_list')
    
    # GET request - show confirmation
    context = {
        'agent': agent,
    }
    return render(request, 'thedjangolook/agent_confirm_delete.html', context)


def agent_detail(request, agent_id):
    """Show detailed information about an agent"""
    agent = get_object_or_404(Operators, id=agent_id)
    
    # Get related information
    centre = Centres.objects.filter(id=agent.centreid).first()
    language = Languages.objects.filter(id=agent.langid).first()
    
    context = {
        'agent': agent,
        'centre': centre,
        'language': language,
    }
    return render(request, 'thedjangolook/agent_detail.html', context)
