from rest_framework import serializers
from .models import User, Profile, ChurchSetting, PrayerRequest, Event, Announcement, LiveStream, Gallery, ContactMessage, ActivityLog, UserNotification

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_photo', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'role', 'is_staff', 'is_superuser', 'profile', 'date_joined']
        read_only_fields = ['id', 'role', 'is_staff', 'is_superuser', 'date_joined']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update user fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.save()

        # Update profile fields
        if profile_data:
            profile = instance.profile
            profile.phone_number = profile_data.get('phone_number', profile.phone_number)
            profile.address = profile_data.get('address', profile.address)
            profile.bio = profile_data.get('bio', profile.bio)
            if 'profile_photo' in profile_data:
                profile.profile_photo = profile_data.get('profile_photo', profile.profile_photo)
            profile.save()

        return instance

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(required=False, allow_blank=True, default='')
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        
        # This will call our custom User.save() which handles admin email role setting
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Update profile
        if profile_data:
            profile = user.profile
            profile.phone_number = profile_data.get('phone_number', '')
            profile.address = profile_data.get('address', '')
            profile.bio = profile_data.get('bio', '')
            profile.save()

        return user

class ChurchSettingSerializer(serializers.ModelSerializer):
    church_logo = serializers.SerializerMethodField()
    pastor_photo = serializers.SerializerMethodField()

    class Meta:
        model = ChurchSetting
        fields = '__all__'
        extra_kwargs = {
            'hero_subtitle': {'allow_blank': True, 'required': False},
            'hero_subtitle_telugu': {'allow_blank': True, 'required': False},
            'welcome_message': {'allow_blank': True, 'required': False},
            'vision': {'allow_blank': True, 'required': False},
            'vision_telugu': {'allow_blank': True, 'required': False},
            'mission': {'allow_blank': True, 'required': False},
            'mission_telugu': {'allow_blank': True, 'required': False},
            'pastor_name': {'allow_blank': True, 'required': False},
            'pastor_designation': {'allow_blank': True, 'required': False},
            'pastor_bio': {'allow_blank': True, 'required': False},
            'pastor_ministry_info': {'allow_blank': True, 'required': False},
            'pastor_welcome_message': {'allow_blank': True, 'required': False},
            'contact_phone': {'allow_blank': True, 'required': False},
            'contact_email': {'allow_blank': True, 'required': False},
            'contact_address': {'allow_blank': True, 'required': False},
            'map_embed_url': {'allow_blank': True, 'required': False},
            'facebook_url': {'allow_blank': True, 'required': False},
            'youtube_url': {'allow_blank': True, 'required': False},
            'instagram_url': {'allow_blank': True, 'required': False},
        }

    def get_church_logo(self, obj):
        if obj.church_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.church_logo.url)
            return obj.church_logo.url
        return None

    def get_pastor_photo(self, obj):
        if obj.pastor_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pastor_photo.url)
            return obj.pastor_photo.url
        return None

class PrayerRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = PrayerRequest
        fields = ['id', 'user_id', 'username', 'title', 'description', 'is_anonymous', 'status', 'is_pinned', 'visibility', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'username', 'created_at', 'updated_at']

class EventSerializer(serializers.ModelSerializer):
    event_image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_event_image(self, obj):
        if obj.event_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.event_image.url)
            return obj.event_image.url
        return None

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class LiveStreamSerializer(serializers.ModelSerializer):
    youtube_id = serializers.CharField(read_only=True)

    class Meta:
        model = LiveStream
        fields = ['id', 'title', 'youtube_url', 'youtube_id', 'is_active', 'created_at']

class GallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'username', 'action', 'created_at']


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = '__all__'
