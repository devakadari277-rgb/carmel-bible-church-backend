from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# REST API Router
router = DefaultRouter()
router.register(r'members', api_views.UserViewSet, basename='api_members')
router.register(r'settings', api_views.ChurchSettingViewSet, basename='api_settings')
router.register(r'events', api_views.EventViewSet, basename='api_events')
router.register(r'prayers', api_views.PrayerRequestViewSet, basename='api_prayers')
router.register(r'announcements', api_views.AnnouncementViewSet, basename='api_announcements')
router.register(r'live-streams', api_views.LiveStreamViewSet, basename='api_streams')
router.register(r'gallery', api_views.GalleryViewSet, basename='api_gallery')
router.register(r'contact-messages', api_views.ContactMessageViewSet, basename='api_messages')
router.register(r'activities', api_views.ActivityLogViewSet, basename='api_activities')
router.register(r'notifications', api_views.UserNotificationViewSet, basename='api_notifications')

urlpatterns = [
    # Public & Member Routes (Traditional HTML Views)
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('prayer-requests/', views.prayer_requests_view, name='prayer_requests'),
    path('events/', views.events_view, name='events'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('live-stream/', views.live_stream_view, name='live_stream'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('portal/', views.admin_portal_login_view, name='admin_portal_login'),

    # Admin Dashboard Routes (Strictly protected by RoleBasedAccessMiddleware)
    path('admin-dashboard/', views.admin_dashboard_overview, name='admin_dashboard'),
    path('admin-dashboard/members/', views.admin_manage_members, name='admin_members'),
    path('admin-dashboard/prayers/', views.admin_manage_prayers, name='admin_prayers'),
    path('admin-dashboard/events/', views.admin_manage_events, name='admin_events'),
    path('admin-dashboard/announcements/', views.admin_manage_announcements, name='admin_announcements'),
    path('admin-dashboard/live-streams/', views.admin_manage_live_streams, name='admin_streams'),
    path('admin-dashboard/gallery/', views.admin_manage_gallery, name='admin_gallery'),
    path('admin-dashboard/church-info/', views.admin_manage_church_info, name='admin_church_info'),
    path('admin-dashboard/messages/', views.admin_manage_messages, name='admin_messages'),

    # --- REST API Endpoints ---
    path('api/', include(router.urls)),
    path('api/auth/register/', api_views.RegisterView.as_view(), name='api_register'),
    path('api/auth/login/', api_views.LoginView.as_view(), name='api_login'),
    path('api/auth/admin-login/', api_views.AdminLoginView.as_view(), name='api_admin_login'),

    path('api/profile/', api_views.ProfileView.as_view(), name='api_profile'),
    path('api/admin/stats/', api_views.AdminStatsView.as_view(), name='api_admin_stats'),
]

