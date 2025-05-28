from django.contrib import admin
from .models import PongMatch, PongStats

# Register your models here.
admin.site.register(PongMatch)
admin.site.register(PongStats)
	