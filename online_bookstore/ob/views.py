from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import ObUser, ObBook, ObRecord
from ob import models
import decimal
import datetime
# Create your views here.


def ob_login(request,book_id=-1,book_amount=-1):
    if request.method == 'POST' and request.POST['login'] == '登录':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['tip'] = 0
            try:
                is_settle_accounts=request.session['is_settle_accounts']
            except KeyError:
                request.session['is_settle_accounts']=False
            if request.session['is_settle_accounts']:
                return HttpResponseRedirect(reverse('ob:show_shopping_cart'))
            else:
                return HttpResponseRedirect(reverse('ob:index'))
        else:
            return HttpResponseRedirect(reverse('ob:login'))
    else:
        return render(request, 'ob/login.html')


def ob_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('ob:login'))


def ob_register(request):
    if request.method == 'POST':
        password1=request.POST['password1']
        password2=request.POST['password2']
        if password1 != password2:
            return render(request, 'ob/register.html')
        else:
            username=request.POST['username']
            try:
                user=User.objects.get(username=username)
                return render(request, 'ob/register.html')
            except User.DoesNotExist:
                newuser = User.objects.create_user(username=username, password=password1)
                newuser.save()
                copynewuser = ObUser(user=newuser, balance=100)
                copynewuser.save()
                return render(request, 'ob/login.html')

    else:
        return render(request, 'ob/register.html')

def purchasing_record(request):
    if request.user.is_authenticated:
        records=ObRecord.objects.filter(user=request.user)
        return render(request, 'ob/purchasing_record1.html', {'records':records})
    else:
        return HttpResponseRedirect(reverse('ob:index'))


def add_shopping_cart(request):#需要书的id
    book_id = request.POST['book_id']
    book_id=int(book_id)
    book_amount = request.POST['book_amount']
    book_amount=int(book_amount)
    request.session['book_id']=book_id
    request.session['book_amount']=book_amount
    try:
        cart=request.session['cart']
    except KeyError:
        request.session['cart']=list()
        cart=request.session['cart']
    book=ObBook.objects.get(pk=book_id)
    try:
        request.session['sum']
    except KeyError:
        request.session['sum']=float(0)
    sign=False#是否记录过该种书
    flag=True#该种书的库存是否充裕
    for abook in cart:
        if abook['book_id'] == book.id:
            abook['amount']+=book_amount
            if abook['amount'] > book.amount:
                flag=False
                money = (abook['amount'] - book.amount)*book.price
                abook['amount']=book.amount
            else:
                money=book_amount*book.price
            request.session['sum']+=float(money)
            sign=True
            break
    if not sign :
        if book_amount > book.amount:
            money=(book_amount-book.amount)*book.price
            book_amount=book.amount
            flag=False
        money=book_amount*book.price
        temp=request.session['sum']+float(money)
        request.session['sum'] = temp
        cart.append({'book_id':book.id,'amount':book_amount})
    if not flag:
        request.session['tip']=3 #库存不足
        return HttpResponseRedirect('/ob/get_book?book_id='+str(book_id))
    else:
        if request.POST['submit']=='添加购物车':
            return HttpResponseRedirect(reverse('ob:show_shopping_cart'))
        else:
            return HttpResponseRedirect(reverse('ob:settle_accounts'))


def settle_accounts(request):
    request.session['is_settle_accounts']=True
    if not request.user.is_authenticated:
         return render(request,'ob/login.html')
    else:
        try:
            cart=request.session['cart']
        except KeyError:
            request.session['cart']=list()
            cart = request.session['cart']
        if len(cart) <= 0:
            return HttpResponseRedirect(reverse('ob:index'))
        try:
            sum=request.session['sum']
        except KeyError:
            request.session['sum']=float(0)
            sum = request.session['sum']
        obuser=ObUser.objects.get(user=request.user)
        if(obuser.balance<sum):
            request.session['tip']=2 #余额不足
            return HttpResponseRedirect(reverse('ob:show_shopping_cart'))
        else:
            obuser.balance-=decimal.Decimal(sum)
            obuser.save()
            for abook in cart:
                dbbook=ObBook.objects.get(pk=abook['book_id'])
                dbbook.amount-=abook['amount']
                dbbook.save()
                record=ObRecord(user=obuser.user,book=dbbook,amount=abook['amount'])
                record.save()
            cart.clear()
            request.session['sum']=float(0)
            request.session['tip']=1 #购买成功
            return HttpResponseRedirect(reverse('ob:index'))
    #是否登录
    #是清空购物车，还是单个商品
        #清空购物车 数据库库存更新，添加购买记录，余额更新，购物车清空
    #余额是否充足

def show_shopping_cart(request):
    try:
        request.session['sum']
    except KeyError:
        request.session['sum']=float(0)
    try:
        cart=request.session['cart']
    except KeyError:
        request.session['cart']=list()
        cart = request.session['cart']
    count=len(cart)
    books=list()
    for book in cart:
        obbook=ObBook.objects.get(pk=book['book_id'])
        info=dict()
        info['bookname']=obbook.bookname
        info['book_id']=obbook.id
        info['amount']=book['amount']
        info['price']=obbook.price
        info['imagename']=obbook.imagename
        info['introduction']=obbook.introduction
        books.append(info)
    try:
        request.session['tip']
    except KeyError:
        request.session['tip']=0
    if request.session['tip']==2:
        tip="余额不足"
        request.session['tip'] = 0
    else:
        tip=''
    return render(request,"ob/shopping_cart.html",{"count":count,"shopping_cart":books,'tip':tip})
#传给模板：书的种类，购物车，提示信息


def update_cart(request):
    if request.method == 'POST':
        book_id=request.POST['book_id']
        book_id=int(book_id)
        cart=request.session['cart']
        i=0
        money=0
        for book in cart:
            if int(book['book_id'])==book_id:
                dbbook=ObBook.objects.get(pk=book_id)
                money=dbbook.price*book['amount']
                break
            i=i+1
        cart.pop(i)
    # request.session['cart']=cart
        request.session['sum']-=float(money)
        return HttpResponseRedirect(reverse('ob:show_shopping_cart'))
    else:
        return HttpResponseRedirect(reverse('ob:index'))


def show_shopping_records(request):
    if request.user.is_authenticated:
        records=ObRecord.objects.filter(user=request.user)
    # items=list()
    # for record in records:
    #     dbbook=ObBook.objects.get(pk=record.book.id)
    #     items.append(dbbook.price*record.amount)
        return render(request,'ob/purchasing_record.html',{"records":records})
    else:
        return HttpResponseRedirect(reverse('ob:index'))


def ob_index(request):
    # request.session['sum']=0
    keyword = request.GET.get("shangpin", None)
    if request.method == "GET" and str(keyword) != 'None' and str(keyword) != "":
       data = models.ObBook.objects.filter(bookname__icontains=str(keyword))
    else:
       data = models.ObBook.objects.all()
    try:
        if request.session['tip'] == 1:
            tip="您已成功购买，请点击<购买记录>查看。"
            request.session['tip'] = 0
        else:
            tip=''
    except KeyError:
        tip=''
        request.session['tip']=0
    return render(request, "ob/index.html", {"date": data,'tip':tip})


def search_books(request):
    if request.method == "POST" :
        keyword = request.POST.get("shangpin", None)
        data = ObBook.objects.filter(bookname__icontains=keyword)
        return render(request,"ob/index.html",{"date" : data })


def get_book(request):#点击输出的书名应该进入购买页，需要前端实现一下
    if request.method == "GET":
        try:
            book_id = request.GET["book_id"]#需要页面中给出书名连接
            book_id=int(book_id)
            data = ObBook.objects.get(pk = book_id)
            if request.session['tip']==3:
                tip='库存不足'
                request.session['tip'] = 0
            else:
                tip=''
            return render(request, "ob/purchase.html", {"book" : data,'tip':tip})
        except KeyError:
            return HttpResponseRedirect(reverse('ob:index'))


def buy_book(request):#需要书名
    if request.method =="POST" and  request.POST["purchase"] == "直接购买"  :
        if request.user.is_authenticated:
            book1 = models.ObBook.objects.filter(bookname = name)
            book_price = book1.price
            obuser = ObUser.objects.get(user=request.user)
            if (obuser.balance < book_price):
                return HttpResponseRedirect(reverse('ob：buy_book', kwargs={'tip': "余额不足"}))
            else:
                obuser.balance -= book_price
                obuser.save()
                record = ObRecord(user=request.user, book = book1, amount =book_price )
                record.save()
                return HttpResponseRedirect(reverse('ob:index'))