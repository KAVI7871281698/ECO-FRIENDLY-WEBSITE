from django.db import models
from django.core.validators import RegexValidator

# Phone number validator
phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits."
)

class Register(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(
        max_length=10,
        validators=[phone_validator],
        unique=True
    )
    city = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    profile_img = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    
    ROLE_CHOICES = (
        ('User', 'User'),
        ('Admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class product(models.Model):
    product_img = models.ImageField(upload_to='uploads', null=True, blank=True)
    product_Categorie = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=100)
    product_des = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name

class Cart(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.product.product_price

    def __str__(self):
        return f"{self.user.first_name}'s cart - {self.product.product_name}"

class Order(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

class CarbonFootprint(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    transport_type = models.CharField(max_length=20)
    distance = models.FloatField()
    electricity = models.FloatField()
    plastic = models.FloatField()
    total_carbon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}'s calculation - {self.total_carbon} kg"

class PickupRequest(models.Model):
    WASTE_TYPES = (
        ('Plastic', 'Plastic'),
        ('Paper', 'Paper'),
        ('Metal', 'Metal'),
        ('Glass', 'Glass'),
        ('Electronic', 'Electronic/E-Waste'),
        ('Other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=50, choices=WASTE_TYPES)
    pickup_date = models.DateField()
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pickup #{self.id} for {self.user.first_name} ({self.waste_type})"


