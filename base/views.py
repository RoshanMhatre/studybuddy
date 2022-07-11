from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import RoomForm, MyUserCreationForm, UserForm
from .models import Room, Topic, Message, User


def home(request):
    """
    Renders home page

    Receives:
      request: request from the user

    Returns:
      render: renders home.html with following data
        rooms: rooms containing the query parameter in the topic, name or description
        topics: first 5 topics
        room_count: count of total rooms available
        room_messages: room messages containing query parameter in the topic
    """
    q = request.GET.get('q', '')
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count, 
        'room_messages': room_messages
        }
    return render(request, 'base/home.html', context)


def loginPage(request):
    """
    Renders login page

    Receives:
      request: request from the user

    Returns:
      render: renders login_register.html with following data
        page: sends dict with page as key with 'login' as value
    """
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Email or Password does not match")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutPage(request):
    """
    Logs out the user

    Receives:
      request: request from the user

    Returns:
      redirect: redirect to the home page
    """
    logout(request)
    return redirect('home')


def registerPage(request):
    """
    Renders sign up page

    Receives:
      request: request from the user

    Returns:
      render: renders login_register.html with following data
        form: Custom user creation form
    """
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Error occured during registration")
    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def room(request, pk: str):
    """
    Renders room component

    Receives:
      request: request from the user
      pk: unique id of the room

    Returns:
      render: renders room.html with following data
        room: requested room object
        room_messages: messages from the room
        participants: participants of the room
    """
    our_room = Room.objects.get(id=pk)
    room_messages = our_room.message_set.all()
    participants = our_room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=our_room,
            body=request.POST.get('body')
        )
        our_room.participants.add(request.user)
        return redirect('room', pk=our_room.id)

    context = {'room': our_room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk: str):
    """
    Renders profile page

    Receives:
      request: request from the user
      pk: unique id of the user

    Returns:
      render: renders profile.html with following data
        user: requested user object
        rooms: rooms created by the user
        room_messages: messages from the room
        topics: topics of the room
    """
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    """
    Renders room creation page

    Receives:
      request: request from the user

    Requires:
      login

    Returns:
      render: renders room_form.html with following data
        form: room creation form
        topics: list of available topics
    """
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    """
    Renders room updation page

    Receives:
      request: request from the user
      pk: unique id of the room

    Requires:
      login

    Returns:
      render: renders room_form.html with following data
        form: room creation form
        topics: list of available topics
        room: requested room details
    """
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to do that!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    """
    Renders room deletion page

    Receives:
      request: request from the user
      pk: unique id of the room

    Requires:
      login

    Returns:
      render: renders delete.html with following data
        room: requested room object
    """
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to do that!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    """
    Renders message deletion page

    Receives:
      request: request from the user
      pk: unique id of the message

    Requires:
      login

    Returns:
      render: renders delete.html with following data
        message: requested message object
    """
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to do that!")

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    """
    Renders user updation page

    Receives:
      request: request from the user

    Requires:
      login

    Returns:
      render: renders update_user.html with following data
        form: user form with prefilled data
    """
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    """
    Renders topics page

    Receives:
      request: request from the user

    Returns:
      render: renders topics.html with following data
        topics: list of available topics containing the query parameter
    """
    q = request.GET.get('q', '')
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    """
    Renders activities page

    Receives:
      request: request from the user

    Returns:
      render: renders activity.html with following data
        room_messages: all the messages
    """
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)