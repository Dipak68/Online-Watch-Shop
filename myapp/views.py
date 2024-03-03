from django.shortcuts import render, redirect
from .models import User,Watch,Contact,Wishlist,Cart,Transaction
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def validate_email(request):
	print("views called")
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

def search(request):
	if request.method=="POST":
		search_watch=request.POST['search_watch']
		all_watch=Watch.objects.filter(watch_brand=search_watch)
		return render(request,'search.html',{'all_watch':all_watch})
	else:
		return render(request,'search.html')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status="completed")
	return render(request,'myorder.html',{'carts':carts})
def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'index.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(user.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts=Cart.objects.filter(user=user,payment_status="pending")
    for i in carts:
    	i.payment_status="completed"
    	i.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return redirect('mycart')


# Create your views here.
def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="user":
			return render(request,'index.html')
		elif user.usertype=="seller":
			return render(request,'seller_index.html')
	except:
		return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def watches(request):
	all_watch=Watch.objects.all()
	return render(request,'watches.html',{'all_watch':all_watch})


def about(request):
	return render(request,'about.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				message=request.POST['message']
			)
		msg="Contact Save Successfully"
		return render(request,'contact.html',{'msg':msg})
	else:
		return render(request,'contact.html')

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					address=request.POST['address'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword']	
					)
				msg="User Sign Up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
				
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
				email=request.POST['email'],
				password=request.POST['password']
				)
			if user.usertype=="user":
				request.session['fname']=user.fname
				request.session['email']=user.email
				wishlists=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user)
				request.session['cart_count']=len(carts)
				return render(request,'index.html')
			elif user.usertype=="seller":
				request.session['fname']=user.fname
				request.session['email']=user.email
				return render(request,'seller_index.html')
		except:
			msg="Email or Password is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['fname']
		del request.session['email']
		del request.session['wishlist_count']
		del request.session['cart_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')


def add_watches(request):
	if request.method=="POST":
		watch_seller=User.objects.get(email=request.session['email'])
		Watch.objects.create(
			watch_seller=watch_seller,
			watch_brand=request.POST['watch_brand'],
			watch_model=request.POST['watch_model'],
			watch_desc=request.POST['watch_desc'],
			watch_price=request.POST['watch_price'],
			watch_image=request.FILES['watch_image']
		)
		msg="Watch Added Successfully"
		return render(request,'add_watches.html',{'msg':msg})
	else:
		return render(request,'add_watches.html')


def view_watches(request):
	watch_seller=User.objects.get(email=request.session['email'])
	watches=Watch.objects.filter(watch_seller=watch_seller)
	return render(request,'view_watches.html',{'watches':watches})

	
def watch_detail(request,pk):
	watch=Watch.objects.get(pk=pk)
	return render(request,'watch_detail.html',{'watch':watch})

def user_watch_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	user=User.objects.get(email=request.session['email'])
	watch=Watch.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,watch=watch)
		wishlist_flag=True
	except:
		pass

	try:
		Cart.objects.get(user=user,watch=watch)
		cart_flag=True
	except:
		pass
	return render(request,'user_watch_detail.html',{'watch':watch,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def watch_edit(request,pk):
	watch=Watch.objects.get(pk=pk)
	if request.method=="POST":
		watch.watch_model=request.POST['watch_model']
		watch.watch_desc=request.POST['watch_desc']
		watch.watch_price=request.POST['watch_price']
		try:
			watch.watch_image=request.FILES['watch_image']
		except:
			pass
			watch.save()
			return render(request,'watch_detail.html',{'watch':watch})

	return render(request,'watch_edit.html',{'watch':watch})

def watch_delete(request,pk):
	watch=Watch.objects.get(pk=pk)
	watch.delete()
	return redirect('view_watches')

def add_to_wishlist(request,pk):
	watch=Watch.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(
				user=user,
				watch=watch
		)

	return redirect('mywishlist')


def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	watch=Watch.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,watch=watch)
	wishlist.delete()
	return redirect('mywishlist')

def mycart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status="pending")
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request, 'mycart.html',{'carts':carts,'net_price':net_price})


def add_to_cart(request,pk):
	watch=Watch.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
			user=user,
			watch=watch,
			price=watch.watch_price,
			total_price=watch.watch_price
		)
	return redirect('mycart')

def remove_from_cart(request,pk):
	watch=Watch.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,watch=watch)
	cart.delete()
	return redirect('mycart')

def change_qty(request):
	cart=Cart.objects.get(pk=request.POST['cart_id'])
	qty=int(request.POST['qty'])
	cart.qty=qty
	cart.total_price=qty*cart.price
	cart.save()
	return redirect('mycart')


