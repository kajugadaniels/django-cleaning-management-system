from urllib.request import Request
from home.forms import *
from home.models import *
from account.models import *
from django.contrib import messages
from django.db.models import Count, Q, F  # Import necessary models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')