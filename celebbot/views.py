from django.shortcuts import render, redirect
import json
# Create your views here.
def index(request):

  if request.method == "GET":
    return render(request, 'celebbot/index.html')
  if request.method == "POST":
    return render(request, 'celebbot/index.html')
