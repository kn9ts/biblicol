from django.shortcuts import render


def index(request):
    """Process index/root requests"""
    return render(request, 'index.html', {})
