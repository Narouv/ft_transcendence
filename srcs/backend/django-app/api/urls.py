from django.urls import path

from . import views
from .endpoints.auth.JWT import login, logout, refresh
from .endpoints.auth.oauth.oauth import oauthLogin, allow
from .endpoints.user.friends import FriendAPI, FriendRequestAPI
from .endpoints.pong.matchmaking import Matchmaking
from .endpoints.pong.match import PongMatchApi
from .endpoints.user.user import UserManager, PasswordReset
from .endpoints.user.avatar import AvatarAPI
from .endpoints import devtest
from .endpoints.auth.TwoFactor.TwoFactor import TwoFactorAPI


urlpatterns = [
    path("auth/logout/", logout.Logout.as_view(), name="logout"),
    path("auth/token/", login.Login.as_view(), name="create_token"),
    path("auth/token/refresh/", refresh.TokenRefresh.as_view(), name="refresh_token"),
    path("pong/matchmaking/register/", Matchmaking.as_view(), name="matchmaking"),
    path("pong/match/", PongMatchApi.as_view(), name="match"),
    path("user/avatar/", AvatarAPI.as_view(), name="avatar"),
    path("user/friends/", FriendAPI.as_view(), name="friends"),
    path("user/friends/request/", FriendRequestAPI.as_view(), name="friend_requests"),
    path("user/password", PasswordReset.as_view(), name="pass_reset"),
    path("user/", UserManager.as_view(), name="user"),

    path("lobby/test/<str:type>/", devtest.LobbyEdit.as_view(), name="index"),
    path("test/", devtest.testView, name="test"),
    path("auth/2FA/", TwoFactorAPI.as_view(), name="2FA"),
    #path("test/", views.testView, name="test"),
    #path("login/<str:username>/<str:password>/", views.loginPage, name="login"),
    #path("register/<str:username>/<str:email>/<str:password>/", views.register, name="register"),
	path("auth/oauth", allow.as_view(), name="oauth"),
	path("auth/redir", oauthLogin.as_view(), name="redir"),
]