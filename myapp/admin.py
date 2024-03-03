from django.contrib import admin
from .models import User,Watch,Contact,Wishlist,Cart,Transaction
# Register your models here.
admin.site.register(User)
admin.site.register(Watch)
admin.site.register(Contact)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Transaction)