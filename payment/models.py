from django.db import models

# Create your models here.
class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True,default='NO_DISCOUNT')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.code
    
class Tax(models.Model):
    type = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.type

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=4,default='usd')

    def __str__(self):
        return self.name
    
class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_ordered= models.BooleanField(default=False)

class Order(models.Model):
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)

