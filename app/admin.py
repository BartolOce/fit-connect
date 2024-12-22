from django.contrib import admin

from app.models import UserProfile, TrainerProfile, Job, Bid, TopUp, Dispute

admin.site.register(UserProfile)
admin.site.register(TrainerProfile)
admin.site.register(Job)
admin.site.register(Bid)
admin.site.register(TopUp)
admin.site.register(Dispute)
