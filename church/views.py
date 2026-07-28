from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    User, Profile, ChurchSetting, PrayerRequest, 
    Event, Announcement, LiveStream, Gallery, ContactMessage
)
from .forms import (
    UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm,
    PrayerRequestForm, EventForm, AnnouncementForm, LiveStreamForm, 
    GalleryForm, ChurchSettingForm
)

# ==========================================
# PUBLIC / MEMBER VIEWS
# ==========================================

def home_view(request):
    """
    Renders the church website Home Page with Welcome message, Pastor Profile,
    Vision/Mission, Latest Events, Pinned & Approved Prayers, and Live Stream.
    Includes the contact form submission handler inline.
    """
    settings = ChurchSetting.get_settings()
    
    # Get active live stream
    live_stream = LiveStream.objects.filter(is_active=True).order_by('-created_at').first()
    
    # Get latest 3 events (future events preferred)
    events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:3]
    if not events.exists():
        events = Event.objects.order_by('-event_date')[:3]
        
    # Get latest 3 announcements
    announcements = Announcement.objects.order_by('-created_at')[:3]
    
    # Get pinned and approved prayer requests
    pinned_prayers = PrayerRequest.objects.filter(status='approved', is_pinned=True).order_by('-created_at')
    recent_prayers = PrayerRequest.objects.filter(status='approved', is_pinned=False).order_by('-created_at')[:4]
    
    # Contact Form Handler
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Your contact message has been sent successfully. We will get back to you shortly.")
            return redirect('home')
        else:
            messages.error(request, "Please fill out all fields in the contact form.")
            
    context = {
        'church_settings': settings,
        'live_stream': live_stream,
        'events': events,
        'announcements': announcements,
        'pinned_prayers': pinned_prayers,
        'recent_prayers': recent_prayers,
    }
    return render(request, 'church/home.html', context)

def register_view(request):
    """
    Registers a new member account. Standard users become Members;
    specifically designated admin emails are automatically elevated.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()  # Triggers save() logic where email checks occur
            login(request, user)
            messages.success(request, f"Welcome to Carmel Bible Church, {user.username}! Your account has been registered.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'church/register.html', {'form': form})

def login_view(request):
    """
    Authenticates both Members and Admins.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'church/login.html', {'form': form})

def admin_portal_login_view(request):
    """
    Dedicated, hidden Admin Portal Login page.
    Only allows access to the Admin Dashboard upon successful authentication.
    """
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    messages.success(request, f"Welcome to the Admin Dashboard, {user.username}!")
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Access Denied. You do not have permission to access this page.")
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'church/admin/portal_login.html', {'form': form})


def logout_view(request):
    """
    Logs the user out of their session.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def profile_view(request):
    """
    Allows a Member or Admin to edit their OWN profile information only.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'church/profile.html', context)

def prayer_requests_view(request):
    """
    View to list approved prayer requests. Authenticated users can submit a new
    prayer request which enters a 'pending' state awaiting Admin approval.
    """
    pinned_prayers = PrayerRequest.objects.filter(status='approved', is_pinned=True).order_by('-created_at')
    recent_prayers = PrayerRequest.objects.filter(status='approved', is_pinned=False).order_by('-created_at')
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PrayerRequestForm(request.POST)
            if form.is_valid():
                prayer = form.save(commit=False)
                prayer.user = request.user
                prayer.status = 'pending'  # Force pending approval status
                prayer.save()
                messages.success(request, "Your prayer request has been submitted successfully and is awaiting review from an administrator.")
                return redirect('prayer_requests')
        else:
            form = PrayerRequestForm()
    else:
        form = None

    context = {
        'pinned_prayers': pinned_prayers,
        'recent_prayers': recent_prayers,
        'form': form
    }
    return render(request, 'church/prayer_requests.html', context)

def events_view(request):
    """
    Displays the timeline list of all events. Members have read-only access.
    """
    events = Event.objects.order_by('event_date')
    return render(request, 'church/events.html', {'events': events})

def announcements_view(request):
    """
    Displays a list of all announcements. Members have read-only access.
    """
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'church/announcements.html', {'announcements': announcements})

def gallery_view(request):
    """
    Displays the photo gallery. Members have read-only access.
    """
    photos = Gallery.objects.order_by('-uploaded_at')
    return render(request, 'church/gallery.html', {'photos': photos})

def live_stream_view(request):
    """
    Allows members to watch the latest active live stream.
    """
    live_stream = LiveStream.objects.filter(is_active=True).order_by('-created_at').first()
    archive_streams = LiveStream.objects.filter(is_active=False).order_by('-created_at')[:6]
    context = {
        'live_stream': live_stream,
        'archive_streams': archive_streams,
    }
    return render(request, 'church/live_stream.html', context)


# ==========================================
# ADMIN DASHBOARD VIEWS
# ==========================================

@login_required
def admin_dashboard_overview(request):
    """
    Overview statistics and numbers for Admin Dashboard.
    """
    total_members = User.objects.filter(role='member').count()
    total_prayers = PrayerRequest.objects.count()
    pending_prayers = PrayerRequest.objects.filter(status='pending').count()
    total_events = Event.objects.count()
    total_live_videos = LiveStream.objects.count()
    total_announcements = Announcement.objects.count()
    total_messages = ContactMessage.objects.count()

    context = {
        'total_members': total_members,
        'total_prayers': total_prayers,
        'pending_prayers': pending_prayers,
        'total_events': total_events,
        'total_live_videos': total_live_videos,
        'total_announcements': total_announcements,
        'total_messages': total_messages,
    }
    return render(request, 'church/admin/dashboard.html', context)

@login_required
def admin_manage_members(request):
    """
    Lists users registered as Members. Admin can view details and delete users.
    """
    members_list = User.objects.filter(role='member').order_by('-date_joined')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        if action == 'delete' and user_id:
            member = get_object_or_404(User, id=user_id, role='member')
            member.delete()
            messages.success(request, f"Member '{member.username}' has been deleted successfully.")
            return redirect('admin_members')
            
    return render(request, 'church/admin/members.html', {'members': members_list})

@login_required
def admin_manage_prayers(request):
    """
    Approves, rejects, pins, or deletes prayer requests.
    """
    prayers = PrayerRequest.objects.order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        prayer_id = request.POST.get('prayer_id')
        prayer = get_object_or_404(PrayerRequest, id=prayer_id)
        
        if action == 'approve':
            prayer.status = 'approved'
            prayer.save()
            messages.success(request, f"Prayer Request '{prayer.title}' approved.")
        elif action == 'reject':
            prayer.status = 'rejected'
            prayer.save()
            messages.success(request, f"Prayer Request '{prayer.title}' rejected.")
        elif action == 'pin':
            prayer.is_pinned = True
            prayer.save()
            messages.success(request, f"Prayer Request '{prayer.title}' pinned to top.")
        elif action == 'unpin':
            prayer.is_pinned = False
            prayer.save()
            messages.success(request, f"Prayer Request '{prayer.title}' unpinned.")
        elif action == 'delete':
            prayer.delete()
            messages.success(request, f"Prayer Request '{prayer.title}' deleted.")
            
        return redirect('admin_prayers')
        
    return render(request, 'church/admin/prayers.html', {'prayers': prayers})

@login_required
def admin_manage_events(request):
    """
    CRUD panel for Events.
    """
    events = Event.objects.order_by('-event_date')
    form = EventForm()
    edit_event = None

    event_id = request.GET.get('edit')
    if event_id:
        edit_event = get_object_or_404(Event, id=event_id)
        form = EventForm(instance=edit_event)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Event created successfully.")
                return redirect('admin_events')
        elif action == 'update':
            ev_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=ev_id)
            form = EventForm(request.POST, request.FILES, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, "Event updated successfully.")
                return redirect('admin_events')
        elif action == 'delete':
            ev_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=ev_id)
            event.delete()
            messages.success(request, "Event deleted successfully.")
            return redirect('admin_events')

    context = {
        'events': events,
        'form': form,
        'edit_event': edit_event
    }
    return render(request, 'church/admin/events.html', context)

@login_required
def admin_manage_announcements(request):
    """
    CRUD panel for Announcements.
    """
    announcements = Announcement.objects.order_by('-created_at')
    form = AnnouncementForm()
    edit_announcement = None

    ann_id = request.GET.get('edit')
    if ann_id:
        edit_announcement = get_object_or_404(Announcement, id=ann_id)
        form = AnnouncementForm(instance=edit_announcement)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Announcement published.")
                return redirect('admin_announcements')
        elif action == 'update':
            a_id = request.POST.get('announcement_id')
            announcement = get_object_or_404(Announcement, id=a_id)
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                messages.success(request, "Announcement updated.")
                return redirect('admin_announcements')
        elif action == 'delete':
            a_id = request.POST.get('announcement_id')
            announcement = get_object_or_404(Announcement, id=a_id)
            announcement.delete()
            messages.success(request, "Announcement deleted.")
            return redirect('admin_announcements')

    context = {
        'announcements': announcements,
        'form': form,
        'edit_announcement': edit_announcement
    }
    return render(request, 'church/admin/announcements.html', context)

@login_required
def admin_manage_live_streams(request):
    """
    CRUD panel for YouTube Live streams.
    """
    streams = LiveStream.objects.order_by('-created_at')
    form = LiveStreamForm()
    edit_stream = None

    stream_id = request.GET.get('edit')
    if stream_id:
        edit_stream = get_object_or_404(LiveStream, id=stream_id)
        form = LiveStreamForm(instance=edit_stream)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = LiveStreamForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Live Stream link saved.")
                return redirect('admin_streams')
        elif action == 'update':
            s_id = request.POST.get('stream_id')
            stream = get_object_or_404(LiveStream, id=s_id)
            form = LiveStreamForm(request.POST, instance=stream)
            if form.is_valid():
                form.save()
                messages.success(request, "Live Stream link updated.")
                return redirect('admin_streams')
        elif action == 'delete':
            s_id = request.POST.get('stream_id')
            stream = get_object_or_404(LiveStream, id=s_id)
            stream.delete()
            messages.success(request, "Live Stream link deleted.")
            return redirect('admin_streams')

    context = {
        'streams': streams,
        'form': form,
        'edit_stream': edit_stream
    }
    return render(request, 'church/admin/live_streams.html', context)

@login_required
def admin_manage_gallery(request):
    """
    CRUD panel for Photo Gallery.
    """
    photos = Gallery.objects.order_by('-uploaded_at')
    form = GalleryForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = GalleryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Photo uploaded to gallery.")
                return redirect('admin_gallery')
        elif action == 'delete':
            photo_id = request.POST.get('photo_id')
            photo = get_object_or_404(Gallery, id=photo_id)
            photo.delete()
            messages.success(request, "Photo removed from gallery.")
            return redirect('admin_gallery')

    context = {
        'photos': photos,
        'form': form
    }
    return render(request, 'church/admin/gallery.html', context)

@login_required
def admin_manage_church_info(request):
    """
    Form view editing the global ChurchSetting (Website Customizer & Pastor profile details).
    """
    settings = ChurchSetting.get_settings()
    form = ChurchSettingForm(instance=settings)

    if request.method == 'POST':
        form = ChurchSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Website layout and Church details updated successfully.")
            return redirect('admin_church_info')

    return render(request, 'church/admin/church_info.html', {'form': form, 'settings': settings})

@login_required
def admin_manage_messages(request):
    """
    View messages submitted via Contact Us form.
    """
    contact_messages = ContactMessage.objects.order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        msg_id = request.POST.get('message_id')
        if action == 'delete' and msg_id:
            message = get_object_or_404(ContactMessage, id=msg_id)
            message.delete()
            messages.success(request, "Contact message deleted.")
            return redirect('admin_messages')
            
    return render(request, 'church/admin/messages.html', {'messages': contact_messages})
