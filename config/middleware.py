from django.contrib import messages


class LoginRequiredMessageMiddleware:
    """Informa al usuario cuando intenta abrir una vista protegida."""

    message = "Debe iniciar sesión primero para acceder a esta página."

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated and hasattr(view_func, "login_url"):
            messages.warning(request, self.message)

        return None
