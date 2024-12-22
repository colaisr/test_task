# main_app/views.py
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth import login,logout


from django.contrib.auth.models import User

def home(request):

    # Check if the session indicates successful Telegram authentication
    if not request.user.is_authenticated and request.session.get('telegram_authenticated'):
        user_id = request.session.get('_auth_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(f"Logging in user: {user.username}")
                login(request, user)
                # Clear the session flag safely
                if 'telegram_authenticated' in request.session:
                    del request.session['telegram_authenticated']
            except User.DoesNotExist:
                print("User ID in session does not exist.")

    return render(request, 'main_app/home.html', {
        'is_authenticated': request.user.is_authenticated,
        'user': request.user if request.user.is_authenticated else None
    })

def logout_view(request):
    logout(request)
    return redirect('home')

def login_with_telegram(request):
    # Generate a unique token
    token = get_random_string(20)
    bot_username = "engry2_bot"  # Replace with your bot's username
    telegram_url = f"https://t.me/{bot_username}?start={token}"

    # Save the token in the session
    request.session['telegram_auth_token'] = token

    # Directly redirect to the Telegram bot
    return HttpResponseRedirect(telegram_url)

