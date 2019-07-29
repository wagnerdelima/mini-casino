from django.contrib import admin

from casino.models import CustomerUser, Wallet, Bonus

admin.site.register(CustomerUser)
admin.site.register(Wallet)
admin.site.register(Bonus)
