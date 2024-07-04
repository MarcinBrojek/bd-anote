from django.contrib import admin

from .models import User, Authorized, Subject, Classes, Note, Correction, Observation

admin.site.register(User)
admin.site.register(Authorized)
admin.site.register(Subject)
admin.site.register(Classes)
admin.site.register(Note)
admin.site.register(Correction)
admin.site.register(Observation)
