from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	address=models.TextField()
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")
	image=models.ImageField(upload_to="image/", default="", null=True, blank=True)


	def __str__(self):
		return self.fname+" - "+self.usertype

class Watch(models.Model):
	CHOICES=(
		('apple','apple'),
		('mi','mi'),
		('fitbit','fitbit'),
		('samsung','samsung')
		)
	watch_seller=models.ForeignKey(User,on_delete=models.CASCADE,default="2")
	watch_brand=models.CharField(max_length=100,choices=CHOICES)
	watch_model=models.CharField(max_length=100)
	watch_desc=models.TextField()
	watch_price=models.IntegerField()
	watch_image=models.ImageField(upload_to='images/',default="", null=True, blank=True)


	def __str__(self):
		return self.watch_brand+" - "+self.watch_model 		

class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	message=models.TextField()


	def __str__(self):
		return self.name+" - "+self.email
		
class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	watch=models.ForeignKey(Watch,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.watch.watch_brand

class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	watch=models.ForeignKey(Watch,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	price=models.IntegerField()
	qty=models.IntegerField(default=1)
	total_price=models.IntegerField()
	payment_status=models.CharField(max_length=100,default="pending")

	def __str__(self):
		return self.user.fname+" - "+self.watch.watch_brand

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)