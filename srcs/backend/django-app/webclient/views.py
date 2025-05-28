from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from django.template import TemplateDoesNotExist
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def single_page_app(request):
	return render(request, "webclient/app-base.html", {})

class SubViewManger(APIView):
	def post(self, request, view):
		response = render(request, f"webclient/views/{view}.html", {})
		#try:
		#except TemplateDoesNotExist:
		#	return Response({"success": False, "msg": "Invalid view!"})
		return response