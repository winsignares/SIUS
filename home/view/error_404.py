from django.shortcuts import render


def error_404_view(request, exception):
    """
    Vista para manejar errores 404.
    """

    return render(request, '404.html', status=404)