from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not in_groups(request.user):
                return redirect('no_autorizado')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator