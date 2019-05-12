from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ObUser(models.Model):
    user = models.ForeignKey(User,unique=True,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=8, decimal_places=2)  #余额最大9999 9999.99元

    def __str__(self):
        return str(self.user.username)+"---"+str(self.balance)


class ObBook(models.Model):
    bookname = models.CharField(max_length=30)#书名
    price = models.DecimalField(max_digits=6, decimal_places=2)  #书的单价最大9999.99元
    amount=models.IntegerField()#库存
    introduction=models.CharField(max_length=300)#简介
    imagename=models.CharField(max_length=30)#封面地址

    def __str__(self):
        return "bookname:"+self.bookname+"--price:"+str(self.price)+"--amount:"+str(self.amount)+"--imagename:"+self.imagename


class ObRecord(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)#用户
    book=models.ForeignKey(ObBook,on_delete=models.CASCADE)#书
    amount = models.IntegerField()#数量
    purchasing_date=models.DateTimeField("purchaing date",auto_now_add=True)#购买日期,auto_now_add=True

    def __str__(self):
        return "username:"+self.user.username+"--book:"+self.book.bookname+"--amount:"+str(self.amount)+"--date:"+str(self.purchasing_date)
