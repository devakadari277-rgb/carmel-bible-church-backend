import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmel_project.settings')
django.setup()

from church.models import ChurchSetting, User, Event, Announcement, LiveStream, PrayerRequest

def seed_database():
    print("Starting database seeding...")
    
    # 1. Initialize or get ChurchSetting
    setting = ChurchSetting.get_settings()
    setting.church_name = "Carmel Bible Church"
    setting.church_logo = "church/church_logo.png"
    setting.hero_title = "Welcome to Carmel Bible Church"
    setting.hero_subtitle = ""
    setting.hero_subtitle_telugu = "దేవుని వాక్యము మా పాదములకు దీపమును, మా త్రోవకు వెలుగునై యున్నది."
    setting.welcome_message = (
        "We are glad you are here! Carmel Bible Church is a fellowship dedicated to the "
        "glory of God through the preaching of His Word, authentic community life, and "
        "service to others. We believe in creating a space where people can have authentic "
        "encounters with Christ, discover their spiritual gifts, and grow in sound doctrine."
    )
    setting.vision = "To know Christ and to make Him known through sound biblical teaching, discipleship, and evangelism."
    setting.vision_telugu = "క్రీస్తును తెలిసికొని, ఆయనను అందరికీ తెలియజేస్తూ, దేవుని వాక్యములో స్థిరపడిన విశ్వాసుల సమాజాన్ని నిర్మించుట."
    setting.mission = "To preach the Gospel, make disciples of all nations, and serve our local community with the love of Christ."
    setting.mission_telugu = "దేవుని వాక్యాన్ని విశ్వసనీయంగా బోధించుట, సువార్తను ప్రకటించుట, శిష్యులను చేయుట, ప్రార్థనలో ఎదుగుట, ప్రేమతో సంఘానికీ సమాజానికీ సేవ చేయుట."
    
    # Pastor Profile
    setting.pastor_name = "Shyam Chevuri"
    setting.pastor_designation = "Pastor - Bible Teacher"
    setting.pastor_photo = "church/pastor_photo.png"
    setting.pastor_welcome_message = (
        "We invite you to join us as we worship our Savior, study His word, and fellowship together. "
        "Whether you are looking for answers or searching for a spiritual home, you are welcome here."
    )
    setting.pastor_bio = (
        "Pastor Shyam Chevuri has been serving the congregation at Carmel Bible Church with faithfulness and dedication. "
        "He holds a degree in theology and has spent over 14 years preaching expository sermons, mentoring young leaders, "
        "and spearheading local community aid initiatives."
    )
    setting.pastor_ministry_info = (
        "Committed to teaching reformed theology, pastoral counseling, expository preaching, "
        "and equipping saints for global missions."
    )
    
    # Contact coordinates
    setting.contact_phone = "87908 73190"
    setting.contact_email = "pastor@carmelbiblechurch.org"
    setting.contact_address = "Carmel Bible Church, side of the water tank, Dolapeta, Rajam Pin: 532127"
    setting.map_embed_url = "https://www.google.com/maps?q=Carmel+Bible+Church,+Dolapeta,+Rajam,+Andhra+Pradesh+532127&output=embed"
    
    # Social links
    setting.facebook_url = "https://facebook.com/carmelbiblechurch"
    setting.youtube_url = "https://youtube.com/carmelbiblechurch"
    setting.instagram_url = "https://instagram.com/carmelbible"
    
    setting.save()
    print("Church Settings seeded.")

    # 2. Seed default users
    # Clean up old default placeholder accounts if they exist
    User.objects.filter(username__in=['pastor', 'deva', 'brother']).delete()

    # Superuser admin users (emails are in default ADMIN_EMAILS in settings.py)
    admins = [
        {
            'username': 'Shyam',
            'email': 'pastor@carmelbiblechurch.org',
            'password': 'CBC Church',
            'first_name': 'Shyam Chevuri',
            'phone': '8790873190',
        },
        {
            'username': 'DEVA',
            'email': 'devakadari277@gmail.com',
            'password': 'DEVA',
            'first_name': 'DEVA',
            'phone': '938496327',
        },
        {
            'username': 'Uday',
            'email': 'brother@carmelbiblechurch.org',
            'password': 'CBC Church',
            'first_name': 'Uday',
            'phone': '8897086472',
        },
    ]

    for admin_data in admins:
        user = User.objects.filter(username=admin_data['username']).first()
        if not user:
            user = User.objects.filter(email=admin_data['email']).first()

        if not user:
            user = User.objects.create_user(
                username=admin_data['username'],
                email=admin_data['email'],
                password=admin_data['password'],
                first_name=admin_data['first_name']
            )
            # Update phone number in profile
            profile = user.profile
            profile.phone_number = admin_data['phone']
            profile.save()
            print(f"Admin User '{admin_data['username']}' ({admin_data['email']}) created successfully.")
        else:
            # Update details if user exists (to apply new password or details)
            user.email = admin_data['email']
            user.set_password(admin_data['password'])
            user.first_name = admin_data['first_name']
            user.save()
            profile = user.profile
            profile.phone_number = admin_data['phone']
            profile.save()
            print(f"Admin User '{admin_data['username']}' updated successfully.")

    # Sample standard member user
    if not User.objects.filter(username="john_member").exists():
        User.objects.create_user(
            username="john_member",
            email="john@example.com",
            password="MemberPassword123"
        )
        print("Sample Member User 'john_member' created with password: MemberPassword123")

    # 3. Seed active Live Stream
    if not LiveStream.objects.exists():
        LiveStream.objects.create(
            title="Sunday Morning Worship Service - Live",
            youtube_url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",  # Sample live video ID
            is_active=True
        )
        print("Sample active Live Stream added.")

    # 4. Seed sample events
    if not Event.objects.exists():
        Event.objects.create(
            title="Annual Bible Conference 2026",
            description="Join us for our annual Bible conference focusing on 'Walking in Grace'. Guest speakers will share insights from the epistles.",
            event_date=timezone.now() + timedelta(days=5, hours=10),
            location="Main Church Sanctuary"
        )
        Event.objects.create(
            title="Youth Fellowship Gathering",
            description="An evening of praise, prayer, and study for youth and young adults. Refreshments will be served after fellowship.",
            event_date=timezone.now() + timedelta(days=12, hours=18),
            location="Church Fellowship Hall"
        )
        print("Sample events added.")

    # 5. Seed sample announcements
    if not Announcement.objects.exists():
        Announcement.objects.create(
            title="Sunday School Resumes",
            content="We are pleased to announce that Sunday School classes for all ages will resume starting next Sunday at 11:00 AM right after the morning worship service. We look forward to seeing the children and teenagers back!"
        )
        Announcement.objects.create(
            title="Midweek Prayer Meeting Schedule",
            content="Please note that our Wednesday Bible Study and Prayer Meeting will start at 07:00 PM in the Fellowship Hall. Expository teaching on the Book of Romans continues."
        )
        print("Sample announcements added.")

    # 6. Seed approved prayer requests
    if not PrayerRequest.objects.exists():
        member_user = User.objects.get(username="john_member")
        pr1 = PrayerRequest.objects.create(
            user=member_user,
            title="Healing for Sister Sarah",
            description="Please join us in praying for Sister Sarah who is recovering from major surgery. Pray for strength, pain relief, and rapid healing.",
            status="approved",
            is_pinned=True
        )
        pr2 = PrayerRequest.objects.create(
            user=member_user,
            title="Grace for Outreach Ministries",
            description="We request prayers for the upcoming weekend tract distribution and local slum outreach. Pray for hearts to be receptive to the Gospel.",
            status="approved",
            is_pinned=False
        )
        print("Sample approved prayer requests added.")

    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
