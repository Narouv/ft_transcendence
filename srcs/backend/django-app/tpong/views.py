from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from api.models import User

def register():
	user = User(username="testUser42", password="mostSecure")
	user.save()
  
def game_site(request):
	user_list = User.objects.all()
	context = {"user_list": user_list}
	return render(request, "tpong/player-stats.html", context)
	#return render(request, "tpong/pong-game-base.html", {})

def game_window(request):
	return render(request, "tpong/pong-game-base-embed.html", {})
