from django.shortcuts import render
from django.utils.http import urlencode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User
import json
import requests
import os

import logging
logger = logging.getLogger(__name__)

class allow(APIView):
    def post(self, request):
        if ('OAUTH_ID' in os.environ and 'OAUTH_SECRET' in os.environ):
            oauthLogin.hostName = request.META["HTTP_ORIGIN"]
            data = {
                "client_id": os.environ.get('OAUTH_ID'),
                "redirect_uri": f"{oauthLogin.hostName}/api/auth/redir",
                "response_type": "code",
                "scope": "public"
            }

            baseurl = "https://api.intra.42.fr/oauth/authorize"
            query_string = urlencode(data)
            baseurl = baseurl + '?' + query_string
            return Response({"data": baseurl, "success": True})
        return Response({"success": False, "error": "no client id or client secret"})

def get_access_token(request) -> Response:
    data = {
        "grant_type": "authorization_code",
        "client_id": os.environ.get('OAUTH_ID'),
        "client_secret": os.environ.get('OAUTH_SECRET'),
        "code": request.GET.get("code"),
        "redirect_uri": f"{oauthLogin.hostName}/api/auth/redir",
    }

    baseurl = "https://api.intra.42.fr/oauth/token"
    return requests.post(baseurl, data=data)

def get_login_details(token):
    response = requests.get("https://api.intra.42.fr/v2/me", headers={'Authorization': token})
    return response

class oauthLogin(APIView):
    hostName = None

    def get(self, request):
        if request.GET.get("code"):
            try:
                token = get_access_token(request)
            except:
                return Response({'success': False, "error": "42 denied the request"})
        if token.status_code == 200:
            req = get_login_details(token.json()['token_type'] + ' ' + token.json()['access_token'])
            details = req.json()
            if req.status_code != 200:
                return Response({'success': False, "error": "failed getting 42 user data"})
            try:
                user = User.objects.get(email__iexact=details['email'])
            except User.DoesNotExist:
                user = User.objects.create(username=details['login'], email=details['email'], nickname=details['login'])
                user.save()
            if user is None:
                return Response({'success': False, "error": "Invalid credentials!"})
            token = RefreshToken.for_user(user)
            access = token.access_token
            data =  {'access': str(access), 'refresh': str(token), 'expiry': access.payload['exp']}
            con = {"json": json.dumps(data)}
            response = render(request, 'api/oauth.html', context=con)
            return response
        return Response({'success': False, "error": "42 auth did not succeed"})
