from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

class UserLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that sets the language for the current session based on the user's preference.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get the user's language preference
            user_language = request.user.language_preference
            # Activate the user's preferred language
            translation.activate(user_language)
            request.LANGUAGE_CODE = user_language