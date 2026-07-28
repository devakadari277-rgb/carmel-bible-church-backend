from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from .models import User, Profile, PrayerRequest, Event, Announcement, LiveStream, ChurchSetting

class RBACConstraintTests(TestCase):
    """
    Tests that only users with the specific admin emails can become Admin/Superusers,
    and all other registered users are strictly designated as Members.
    """
    def setUp(self):
        # Admin Emails are defined in settings.py. For testing, we ensure they are set.
        self.admin_emails = getattr(settings, 'ADMIN_EMAILS', [
            'pastor@carmelbiblechurch.org',
            'devakadari277@gmail.com',
            'brother@carmelbiblechurch.org'
        ])

    def test_admin_email_auto_elevation(self):
        """Users with designated admin emails must automatically become admins upon save."""
        for email in self.admin_emails:
            username = email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=email,
                password="SecurePassword123"
            )
            # Fetch from DB to ensure save logic ran and persisted
            user.refresh_from_db()
            self.assertEqual(user.role, 'admin')
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)

    def test_member_email_restrictions(self):
        """Users with other email addresses must strictly remain members with no staff/superuser access."""
        emails = [
            'normal_member@gmail.com',
            'another_user@carmelbiblechurch.org',
            'hack_attempt@carmelbiblechurch.org'
        ]
        for email in emails:
            username = email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=email,
                password="SecurePassword123"
            )
            user.refresh_from_db()
            self.assertEqual(user.role, 'member')
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    def test_privilege_escalation_prevention(self):
        """An existing member trying to promote themselves is blocked at the model save level."""
        user = User.objects.create_user(
            username="normalmember",
            email="member@gmail.com",
            password="SecurePassword123"
        )
        user.refresh_from_db()
        self.assertEqual(user.role, 'member')

        # Try to modify fields manually
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Check that model save reset them back to member
        user.refresh_from_db()
        self.assertEqual(user.role, 'member')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class AccessControlTests(TestCase):
    """
    Tests that non-admins (anonymous users and normal members) are strictly redirected
    with an access denied message if they attempt to request admin views.
    """
    def setUp(self):
        # Create a member
        self.member = User.objects.create_user(
            username="member1",
            email="member1@gmail.com",
            password="Password123"
        )
        
        # Create an admin
        self.admin = User.objects.create_user(
            username="pastor",
            email="pastor@carmelbiblechurch.org",
            password="Password123"
        )

        # URLs to protect
        self.protected_urls = [
            reverse('admin_dashboard'),
            reverse('admin_members'),
            reverse('admin_prayers'),
            reverse('admin_events'),
            reverse('admin_streams'),
            reverse('admin_gallery'),
            reverse('admin_announcements'),
            reverse('admin_church_info'),
            reverse('admin_messages'),
            '/admin/',
            '/admin/settings'
        ]

    def test_anonymous_user_blocked(self):
        """Unauthenticated requests to admin URLs must redirect to the home page with a message."""
        client = Client()
        for url in self.protected_urls:
            response = client.get(url, follow=True)
            # Redirect is expected
            self.assertRedirects(response, reverse('home'))
            
            # Message check
            messages = list(response.context['messages'])
            self.assertTrue(any("Access Denied. You do not have permission to access this page." in str(m) for m in messages))

    def test_member_user_blocked(self):
        """Authenticated Members must be blocked from accessing admin URLs and redirected to home."""
        client = Client()
        client.login(username="member1", password="Password123")
        
        for url in self.protected_urls:
            response = client.get(url, follow=True)
            self.assertRedirects(response, reverse('home'))
            
            messages = list(response.context['messages'])
            self.assertTrue(any("Access Denied. You do not have permission to access this page." in str(m) for m in messages))

    def test_admin_user_allowed(self):
        """Authenticated Admins must have successful access (200 OK) to the dashboard URLs."""
        client = Client()
        client.login(username="pastor", password="Password123")
        
        # Test custom admin dashboard
        response = client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = client.get(reverse('admin_members'))
        self.assertEqual(response.status_code, 200)


class PrayerRequestWorkflowTests(TestCase):
    """
    Tests the Prayer Request flow: submission (defaults to pending), visibility rules, and admin approval.
    """
    def setUp(self):
        self.member = User.objects.create_user(
            username="member1",
            email="member1@gmail.com",
            password="Password123"
        )
        self.admin = User.objects.create_user(
            username="deva",
            email="devakadari277@gmail.com",
            password="DEVA"
        )
        # Ensure single ChurchSetting exists
        ChurchSetting.get_settings()

    def test_prayer_submission_workflow(self):
        """Submitted prayer request defaults to pending and is hidden until approved."""
        client = Client()
        client.login(username="member1", password="Password123")
        
        # Submit a prayer request
        url = reverse('prayer_requests')
        post_data = {
            'title': 'Pray for family health',
            'description': 'Please pray for my mother who is currently recovering in the hospital.',
            'is_anonymous': False
        }
        response = client.post(url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirects on success

        # Check database entry
        prayer = PrayerRequest.objects.get(title='Pray for family health')
        self.assertEqual(prayer.status, 'pending')
        self.assertFalse(prayer.is_pinned)
        self.assertEqual(prayer.user, self.member)

        # Check public lists: it should not show up yet
        response_home = client.get(reverse('home'))
        self.assertNotContains(response_home, 'Pray for family health')
        
        response_wall = client.get(reverse('prayer_requests'))
        self.assertNotContains(response_wall, 'Pray for family health')

        # Admin logs in and approves
        client.login(username="deva", password="Password123")
        approve_url = reverse('admin_prayers')
        client.post(approve_url, {'action': 'approve', 'prayer_id': prayer.id})
        
        prayer.refresh_from_db()
        self.assertEqual(prayer.status, 'approved')

        # Check public lists: it should now show up
        client.logout()
        response_home_after = client.get(reverse('home'))
        self.assertContains(response_home_after, 'Pray for family health')
        
        response_wall_after = client.get(reverse('prayer_requests'))
        self.assertContains(response_wall_after, 'Pray for family health')
