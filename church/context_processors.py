from .models import ChurchSetting

def church_settings(request):
    """
    Exposes the global church settings and information to all templates.
    """
    return {
        'church_settings': ChurchSetting.get_settings()
    }
