from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User

from django.core import serializers

from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Manga, Profile

import random
import requests

from .tags import mangaTag

def home(request):
    if request.user.is_authenticated:
        profileObj = Profile.objects.get(user_id=request.user)
        libraryList = list(profileObj.library.all())
        libraryList.sort(key=lambda p: p.title)
        return render(request, 'mangalib/library.html', {'library': libraryList})
    else:
        return render(request, 'mangalib/index.html')


def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'mangalib/register.html', {"message": "Password confirmation not the same"})

        if User.objects.filter(username=username).exists():
            return render(request, 'mangalib/register.html', {"message": "Username has been taken"})

        newUser = User.objects.create_user(username, email, password)
        newUser.save()

        newProfile = Profile.objects.create(user_id=newUser, name=username)
        newProfile.save()

        return HttpResponseRedirect(reverse('mangalib:home'))
    else:
        return render(request, 'mangalib/register.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('mangalib:home'))
        else:
            messages.error(request, 'Wrong username or password')
            return render(request, 'mangalib/login.html', {"message": "Wrong username or password."})
    else:
        return render(request, 'mangalib/login.html', {})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('mangalib:home'))

def save_database(mangaId):
    if Manga.objects.filter(id=mangaId).exists() == False:
        requestLink = "https://api.mangadex.org/manga?ids[]=" + \
            str(mangaId) + "&limit=1&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic"
        mangaVar = requests.get(requestLink).json()
        mangaAttributes = mangaVar['data'][0]['attributes']
        if 'en' in mangaAttributes['title']:
            mangaTitle = mangaAttributes['title']['en']
        else:
            mangaTitle = mangaAttributes['title']['jp']
        mangaUrl = "https://mangadex.org/title/" + mangaId
        if 'en' in mangaAttributes['description']:
            mangaSynopsis = mangaAttributes['description']['en']
        else:
            mangaSynopsis = "No Synopsis Available"
        requestImageLink = "https://api.mangadex.org/cover?manga[]=" + mangaId
        returnImageVar = requests.get(requestImageLink).json()
        coverImageFile = returnImageVar['data'][0]['attributes']['fileName']
        coverImageLink = "https://uploads.mangadex.org/covers/" + \
            mangaId + "/" + coverImageFile

        mangaObj = Manga(id=mangaId, title=mangaTitle, url=mangaUrl,
                         cover=coverImageLink, synopsis=mangaSynopsis)
        mangaObj.save()
    return

def manga(request, mangaId):
    manga = Manga.objects.get(id = mangaId)
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id = request.user)
        saved = True if manga in profile.library.all() else False
        return render(request, 'mangalib/manga.html', {'manga' : manga, 'saved' : saved})
    else :
        return render(request, 'mangalib/manga.html', {'manga' : manga})

@login_required(login_url='/login', redirect_field_name=None)
def save_manga(request, mangaId):
    user = request.user
    manga = Manga.objects.get(id=mangaId)
    profile = Profile.objects.get(user_id=user)
    profile.library.add(manga)
    return HttpResponseRedirect(reverse('mangalib:home'))

def validate_manga(mangaId):
    if Manga.objects.filter(id=mangaId).exists():
        return True
    requestLink = "https://api.mangadex.org/manga?ids[]=" + \
        str(mangaId) + "&limit=1&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic"
    print(requestLink)
    mangaVar = requests.get(requestLink).json()
    if mangaVar['result'] != 'ok' or len(mangaVar['data']) == 0:
        return False
    if ('en' not in mangaVar['data'][0]['attributes']['title']) and ('jp' not in mangaVar['data'][0]['attributes']['title']):
        return False
    return True

@login_required(login_url='/login', redirect_field_name=None)
def add_manga(request):
    user = request.user
    if request.method == "POST":
        mangaId = request.POST['id']
        user = request.user
        if validate_manga(mangaId) == False:
            return render(request, 'mangalib/addmanga.html', {'message': 'Invalid ID'})
        else:
            save_database(mangaId)
            return HttpResponseRedirect(reverse('mangalib:save', args = [mangaId]))
    else:
        return render(request, 'mangalib/addmanga.html', {})

@login_required(login_url='/login', redirect_field_name=None)
def delete_manga(request, mangaId):
    user = request.user
    profile = Profile.objects.get(user_id=user)
    manga = Manga.objects.get(id=mangaId)

    profile.library.remove(manga)
    return HttpResponseRedirect(reverse('mangalib:home'))

def gimme(request):
    if request.method == "POST":
        checked_tags = request.POST.getlist('tags[]')
        tag_append = ''
        for i in checked_tags:
            tag_append += mangaTag[i]
        t, l, r, maxOffset = 0, 0, 8000, -1
        while l <= r:
            offset = int((l + r) / 2)
            requestLink = "https://api.mangadex.org/manga?limit=100&offset=" + str(offset) + tag_append
            returnVar = requests.get(requestLink).json()
            if len(returnVar['data']) == 0:
                r = offset - 1
            else:
                l = offset + 1
                maxOffset = offset
        if(maxOffset < 0):
            return render(request, 'mangalib/gimme.html', {'tags' : mangaTag, 'message' : 'No manga under given constraints.'})
        for i in range(100):
            requestLink = "https://api.mangadex.org/manga?limit=100&originalLanguage[]=ja&offset=" + str(random.randint(0, maxOffset)) + tag_append
            returnVar = requests.get(requestLink).json()
            if len(returnVar['data']) > 0:
                break
        if returnVar['result'] != "ok":
            return render(request, 'mangalib/gimme.html', {'tags' : dict(sorted(mangaTag.items())), 'message' : 'Error!'})
        if len(returnVar['data']) == 0:
            return render(request, 'mangalib/gimme.html', {'tags' : dict(sorted(mangaTag.items())), 'message' : 'No manga under given constraints.'})
        mangaId = returnVar['data'][random.randint(0, len(returnVar['data']) - 1)]['id']
        save_database(mangaId)
        return HttpResponseRedirect(reverse('mangalib:manga', args = [mangaId]))
    return render(request, 'mangalib/gimme.html', {'tags' : dict(sorted(mangaTag.items()))})