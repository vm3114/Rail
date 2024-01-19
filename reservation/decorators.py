from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import *



def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, 'Access Denied.')
            return redirect('login') 

        return view_func(request, *args, **kwargs)

    return _wrapped_view

def superuser_or_staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            elif request.user.account.is_staff:
                return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Access Denied.')
        return redirect('home')
            
    return _wrapped_view