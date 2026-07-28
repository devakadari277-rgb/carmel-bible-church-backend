from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    def save(self, *args, **kwargs):
        email_lower = self.email.strip().lower() if self.email else ''
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
        admin_emails_lower = [e.strip().lower() for e in admin_emails]

        # Enforce strict RBAC constraints at the database save level
        if email_lower and email_lower in admin_emails_lower:
            self.role = 'admin'
            self.is_staff = True
            self.is_superuser = True
        else:
            self.role = 'member'
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)

class ChurchSetting(models.Model):
    # Church Info
    church_name = models.CharField(max_length=200, default="Carmel Bible Church")
    church_logo = models.ImageField(upload_to='church/', blank=True, null=True)
    hero_title = models.CharField(max_length=200, default="Welcome to Carmel Bible Church")
    hero_subtitle = models.CharField(max_length=500, default="")
    hero_subtitle_telugu = models.CharField(max_length=500, default="దేవుని వాక్యము మా పాదములకు దీపమును, మా త్రోవకు వెలుగునై యున్నది.")
    hero_banner = models.ImageField(upload_to='church/', blank=True, null=True)
    
    welcome_message = models.TextField(default="We are glad you are here! Join us in fellowship and worship.")
    vision = models.TextField(default="To know Christ and to make Him known through sound biblical teaching, discipleship, and evangelism.")
    vision_telugu = models.TextField(default="క్రీస్తును తెలిసికొని, ఆయనను అందరికీ తెలియజేస్తూ, దేవుని వాక్యములో స్థిరపడిన విశ్వాసుల సమాజాన్ని నిర్మించుట.")
    mission = models.TextField(default="To preach the Gospel, make disciples of all nations, and serve our local community with the love of Christ.")
    mission_telugu = models.TextField(default="దేవుని వాక్యాన్ని విశ్వసనీయంగా బోధించుట, సువార్తను ప్రకటించుట, శిష్యులను చేయుట, ప్రార్థనలో ఎదుగుట, ప్రేమతో సంఘానికీ సమాజానికీ సేవ చేయుట.")
    
    # Pastor Profile
    pastor_name = models.CharField(max_length=100, default="Pastor Shyam Chevuri")
    pastor_designation = models.CharField(max_length=100, default="Pastor - Bible Teacher")
    pastor_photo = models.ImageField(upload_to='church/', blank=True, null=True)
    pastor_bio = models.TextField(default="Pastor Shyam Chevuri has been serving the community for over 13 years...")
    pastor_ministry_info = models.TextField(default="Focused on expository preaching and community outreach.")
    pastor_welcome_message = models.TextField(default="Welcome to our church home. I invite you to join us this Sunday!")

    # Contact Details
    contact_phone = models.CharField(max_length=20, default="+87908 73190")
    contact_email = models.EmailField(default="pastor@carmelbiblechurch.org")
    contact_address = models.TextField(default="Carmel Bible Church ,Rajam")
    map_embed_url = models.TextField(blank=True, default="https://www.google.com/maps?q=Carmel+Bible+Church,+Dolapeta,+Rajam,+Andhra+Pradesh+532127&output=embed", help_text="https://www.google.com/maps/place/Carmel+Bible+Church,+A+Center+for+Bible+Knowledge+and+Spiritual+Edification/@18.4619347,83.6622747,71m/data=!3m1!1e3!4m6!3m5!1s0x3a3c76d85527eaa5:0x793d3e9a54020aea!8m2!3d18.4620398!4d83.6622632!16s%2Fg%2F11f03szfzb?entry=ttu&g_ep=EgoyMDI2MDcxNS4wIKXMDSoASAFQAw%3D%3D")
    
    # Social links
    facebook_url = models.URLField(blank=True, default="https://www.facebook.com/syam.chevuri.9")
    youtube_url = models.URLField(blank=True, default="https://www.youtube.com/@Shyam_Chevuri")
    instagram_url = models.URLField(blank=True, default="https://www.instagram.com")

    def __str__(self):
        return self.church_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class PrayerRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    VISIBILITY_CHOICES = (
        ('all', 'All'),
        ('admin', 'Only Admin'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prayer_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_pinned = models.BooleanField(default=False)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.status})"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    event_image = models.ImageField(upload_to='events/', blank=True, null=True)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class LiveStream(models.Model):
    title = models.CharField(max_length=200, default="Sunday Service Live")
    youtube_url = models.URLField(help_text="YouTube URL (e.g. https://www.youtube.com/watch?v=...)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        """Extracts the YouTube Video ID from standard and short YouTube URLs."""
        url = self.youtube_url
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0]
        elif 'youtube.com/watch' in url:
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed.query).get('v', [None])[0]
        elif 'youtube.com/embed/' in url:
            return url.split('youtube.com/embed/')[-1].split('?')[0]
        elif 'youtube.com/live/' in url:
            return url.split('youtube.com/live/')[-1].split('?')[0]
        return None

class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Image {self.id}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"





class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username}: {self.action} at {self.created_at}"


class UserNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

