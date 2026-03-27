from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .models import Register, Category, product as ProductModel, Cart, Order, OrderItem, CarbonFootprint, PickupRequest


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import razorpay
import json
import google.generativeai as genai

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def index(request):
    return render(request, 'Pages/index.html')

def product(request):
    selected_category = request.GET.get('category')
    categories = Category.objects.all()
    
    if selected_category and selected_category != 'all':
        view_product = ProductModel.objects.filter(product_Categorie__name=selected_category)
    else:
        view_product = ProductModel.objects.all()
        
    context = {
        'view_product': view_product,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'Pages/product.html', context)

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = Register.objects.get(email=email)
            if user.password == password:
                request.session['user_id'] = user.id
                request.session['user_name'] = user.first_name
                request.session['user_role'] = user.role
                request.session['user_image'] = user.profile_img.url if user.profile_img else None
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid password.')
        except Register.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
            
    return render(request, 'Pages/signin.html')

def signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        city = request.POST.get('city')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_pass')
        profile_img = request.FILES.get('profile_img')

        if not email or not phone:
            messages.error(request, 'Email and Phone are required')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return redirect('signup')

        if Register.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signin')
        
        if Register.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists')
            return redirect('signup')

        Register.objects.create(
            first_name=fname,
            last_name=lname,
            email=email,
            phone=phone,
            city=city,
            password=password,
            confirm_password=confirm_password,
            profile_img=profile_img
        )

        messages.success(request, 'Registered Successfully')
        return redirect('signin')

    return render(request, 'Pages/signup.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_name' in request.session:
        del request.session['user_name']
    if 'user_role' in request.session:
        del request.session['user_role']
    if 'user_image' in request.session:
        del request.session['user_image']
    messages.success(request, 'Logged out successfully.')
    return redirect('index')

# Cart Views
def add_to_cart(request, product_id):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to add products to cart.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    prod = get_object_or_404(ProductModel, id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(user=user, product=prod)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'"{prod.product_name}" added to cart.')
    return redirect('product')

def view_cart(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view your cart.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    cart_items = Cart.objects.filter(user=user)
    
    total = sum(item.total_price() for item in cart_items)
    
    return render(request, 'Pages/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def remove_from_cart(request, cart_id):
    if 'user_id' not in request.session:
        return redirect('signin')
    
    cart_item = get_object_or_404(Cart, id=cart_id, user_id=request.session['user_id'])
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')

# Checkout Views
def checkout(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to checkout.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('product')
    
    total = sum(item.total_price() for item in cart_items)
    
    # Razorpay Order Creation
    razorpay_order = razorpay_client.order.create({
        "amount": int(total * 100), # amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'user': user,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'Pages/checkout.html', context)

def place_order(request):
    if request.method == 'POST':
        user = Register.objects.get(id=request.session['user_id'])
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        
        # Payment details from Razorpay
        payment_id = request.POST.get('razorpay_payment_id')
        razor_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Verify Razorpay Signature
        try:
            params_dict = {
                'razorpay_order_id': razor_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
        except Exception:
            messages.error(request, 'Payment verification failed.')
            return redirect('checkout')
        
        cart_items = Cart.objects.filter(user=user)
        total = sum(item.total_price() for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            zip_code=zip_code,
            total_price=total,
            status='Paid' # Since signature verified
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.product_price,
                quantity=item.quantity
            )
        
        # Clear cart
        cart_items.delete()
        
        return render(request, 'Pages/order_success.html', {'order': order})
    
    return redirect('checkout')

def my_orders(request):
    if 'user_id' not in request.session:
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'Pages/orders.html', {'orders': orders})

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            u_msg = data.get('message', '').lower().strip()
            
            products = ProductModel.objects.all()
            eco_analysis = {
                "oil": "Oils at Verdana are cold-pressed and organic. They are essential for deep hydration without clogging pores. 🥥🌿",
                "serum": "Our Botanical Serums are packed with active plant extracts. Safe for you and the earth! 🌊🍃",
                "brush": "Bamboo brushes are the #1 way to reduce plastic waste. They are naturally antibacterial! 🎍✨",
                "soap": "Handmade soaps avoid the sulfates and parabens found in factory soaps. 🧼💧",
                "eco": "Choosing eco-friendly products reduces your carbon footprint significantly! 🌎💚",
            }

            resp_data = {"response": "", "options": []}

            # --- GREETINGS ---
            if u_msg in ['hi', 'hello', 'hey', 'start', 'get started']:
                resp_data["response"] = "Hi there! 🌿 I'm your Verdana Smart Assistant. How can I help you live more sustainably today?"
                resp_data["options"] = ["📦 Order Tracking", "🚚 Delivery Info", "🌿 Explore Products", "📉 Carbon Info"]
                return JsonResponse(resp_data)

            # --- PRODUCT LIST ---
            if any(x in u_msg for x in ['explore products', 'product list', 'browse', 'show products']):
                items = "\n".join([f"• **{p.product_name}** - ₹{p.product_price}" for p in products[:5]])
                resp_data["response"] = f"🌿 **Eco-Product Collection:**\n\n{items}\n\nSelect a category to learn more! ✨"
                resp_data["options"] = ["🥥 Oils", "🧼 Soaps", "🎍 Bamboo", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            # --- ORDER TRACKING ---
            if any(x in u_msg for x in ['order tracking', 'my order', 'track']):
                if 'user_id' not in request.session:
                    resp_data["response"] = "Please sign in to view your orders. 👤"
                    resp_data["options"] = ["🔑 Sign In", "🚚 Shipping Policy"]
                    return JsonResponse(resp_data)
                
                user = Register.objects.get(id=request.session['user_id'])
                orders = Order.objects.filter(user=user).order_by('-created_at')[:3]
                
                if not orders:
                    resp_data["response"] = "You haven't placed any orders yet. Ready to start your green journey? 🛒"
                    resp_data["options"] = ["🌿 Explore Products", "🔙 Back to Menu"]
                else:
                    msg = "📦 **Your Recent Orders:**\n\n"
                    for o in orders:
                        msg += f"🏷️ **OrderID:** #{o.id} | **Status:** {o.status} | **Total:** ₹{o.total_price}\n"
                    msg += "\nTrack full details in your Profile! 🌿"
                    resp_data["response"] = msg
                    resp_data["options"] = ["🚚 Delivery Times", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            # --- DELIVERY INFO ---
            if any(x in u_msg for x in ['delivery info', 'shipping', 'delivery details']):
                resp_data["response"] = "🚚 **Shipping & Sustainability**\n\n• **Standard:** 3-5 days (Carbon Neutral)\n• **Express:** 1-2 days\n• **Packaging:** 100% Plastic-free\n\nWe ensure every mile of delivery is tracked for its eco-impact! 🌍"
                resp_data["options"] = ["📦 Order Tracking", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            # --- CARBON INFO ---
            if u_msg in ['carbon info', 'carbon calculator', 'footprint']:
                resp_data["response"] = "🌍 **Reduce your Footprint**\n\nWe offer a built-in **Carbon Calculator** to help you track your impact. Reducing travel and switching to bamboo products can save up to 5kg of CO2 per month! 🌿"
                resp_data["options"] = ["📉 Start Calculator", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            # --- PRODUCT CATEGORIES (Nested) ---
            if "oil" in u_msg:
                resp_data["response"] = f"🥥 **Verdana Cold-Pressed Oils:** {eco_analysis['oil']}\n\nWould you like to see detailed product specs?"
                resp_data["options"] = ["🛒 View Oils in Shop", "🔙 Back to Menu"]
                return JsonResponse(resp_data)
            
            if "soap" in u_msg:
                resp_data["response"] = f"🧼 **Natural Handmade Soaps:** {eco_analysis['soap']}\n\nBetter for your skin and the groundwater!"
                resp_data["options"] = ["🛒 View Soaps in Shop", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            if "bamboo" in u_msg:
                resp_data["response"] = f"🎍 **Bamboo Essentials:** {eco_analysis['brush']}\n\nA simple switch to bamboo saves thousands of plastic items from landfills! ✨"
                resp_data["options"] = ["🛒 View Bamboo in Shop", "🔙 Back to Menu"]
                return JsonResponse(resp_data)

            # --- DEFAULT RESPONSE ---
            resp_data["response"] = "I'm here to help! 🌿 Try selecting an option below or type your query about our eco-products."
            resp_data["options"] = ["📦 Order Tracking", "🚚 Delivery Info", "🌿 Explore Products", "📉 Carbon Info"]
            return JsonResponse(resp_data)

        except Exception as e:
            print(f"Chatbot Error: {e}")
            return JsonResponse({'response': "I had a tiny hiccup! Try saying 'Hi' to restart our chat. 🌿", "options": ["Hi"]}, status=200)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.db.models import Sum

def admin_dashboard(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please login as Admin.")
        return redirect('signin')
    
    # Fetch user from DB to verify current role
    try:
        user = Register.objects.get(id=request.session['user_id'])
        if user.role != 'Admin':
            # Sync session just in case
            request.session['user_role'] = user.role
            messages.error(request, "Access Denied: Admin privileges required.")
            return redirect('product')
    except Register.DoesNotExist:
        request.session.flush()
        return redirect('signin')
    
    # Stats Calculation
    total_users = Register.objects.count()
    total_orders = Order.objects.count()
    
    # Accurate revenue calculation using DB aggregation
    revenue_data = Order.objects.aggregate(total=Sum('total_price'))
    total_revenue = revenue_data['total'] if revenue_data['total'] is not None else 0.00
    
    total_products = ProductModel.objects.count()
    
    # Recent items
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_users = Register.objects.order_by('-id')[:5]

    # All Products for Management
    all_products = ProductModel.objects.all().order_by('-id')
    categories = Category.objects.all()
    
    # Recent Pickup Requests
    recent_pickups = PickupRequest.objects.all().order_by('-created_at')[:5]
    total_pickups = PickupRequest.objects.count()
    
    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
        'products': all_products,
        'categories': categories,
        'recent_pickups': recent_pickups,
        'total_pickups': total_pickups,
    }
    return render(request, 'Pages/admin_dashboard.html', context)


def admin_add_product(request):
    if 'user_id' not in request.session or request.session.get('user_role') != 'Admin':
        messages.error(request, "Authorization required.")
        return redirect('signin')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id)
        
        ProductModel.objects.create(
            product_name=name,
            product_Categorie=category,
            product_price=price,
            product_des=description,
            product_img=image
        )
        messages.success(request, f'Product "{name}" added successfully.')
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')

def admin_update_product(request, id):
    if 'user_id' not in request.session or request.session.get('user_role') != 'Admin':
        messages.error(request, "Authorization required.")
        return redirect('signin')
    
    p = get_object_or_404(ProductModel, id=id)
    
    if request.method == 'POST':
        p.product_name = request.POST.get('name')
        category_id = request.POST.get('category')
        p.product_price = request.POST.get('price')
        p.product_des = request.POST.get('description')
        
        if request.FILES.get('image'):
            p.product_img = request.FILES.get('image')
            
        p.product_Categorie = get_object_or_404(Category, id=category_id)
        p.save()
        
        messages.success(request, f'Product "{p.product_name}" updated successfully.')
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')

def admin_delete_product(request, id):
    if 'user_id' not in request.session or request.session.get('user_role') != 'Admin':
        messages.error(request, "Authorization required.")
        return redirect('signin')
    
    p = get_object_or_404(ProductModel, id=id)
    name = p.product_name
    p.delete()
    messages.success(request, f'Product "{name}" deleted successfully.')
    return redirect('admin_dashboard')

def my_profile(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please sign in to view your profile.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        user.first_name = request.POST.get('fname')
        user.last_name = request.POST.get('lname')
        # Email is not editable as per requirement
        user.phone = request.POST.get('phone')
        user.city = request.POST.get('city')
        
        if request.FILES.get('profile_img'):
            user.profile_img = request.FILES.get('profile_img')
            
        user.save()
        
        # Update session
        request.session['user_name'] = user.first_name
        request.session['user_image'] = user.profile_img.url if user.profile_img else None
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('my_profile')
        
        
    return render(request, 'Pages/profile.html', {'user': user})

def contact_us(request):
    if request.method == 'POST':
        # Here you could handle form submission (e.g., save to DB or send email)
        messages.success(request, 'Thank you! Your message has been sent. We will get back to you soon. 🌿')
        return redirect('contact_us')
    return render(request, 'Pages/contact.html')

def faq(request):
    return render(request, 'Pages/faq.html')

def product_details(request, id):
    product_obj = ProductModel.objects.get(id=id)
    return render(request, 'Pages/product_details.html', {'product': product_obj})

def carbon_calculator(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to use the Carbon Calculator.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        transport_type = request.POST.get('transport_type')
        distance = float(request.POST.get('distance', 0))
        electricity = float(request.POST.get('electricity', 0))
        plastic = float(request.POST.get('plastic', 0))
        
        # Calculation
        transport_carbon = distance * 0.2
        electricity_carbon = electricity * 0.5
        plastic_carbon = plastic * 0.1
        
        total_carbon = transport_carbon + electricity_carbon + plastic_carbon
        
        # Store in DB
        CarbonFootprint.objects.create(
            user=user,
            transport_type=transport_type,
            distance=distance,
            electricity=electricity,
            plastic=plastic,
            total_carbon=total_carbon
        )
        
        # Suggestions
        suggestions = []
        if total_carbon > 10:
            suggestions = [
                "Use public transport to reduce your travel emissions.",
                "Reduce plastic usage and switch to compostable bags.",
                "Buy eco-friendly products from our store to support sustainability."
            ]
        else:
            suggestions = [
                "Great job! Your footprint is relatively low. Continue your eco-friendly habits.",
                "Share your results to inspire others to reduce their carbon footprint."
            ]
            
        context = {
            'total_carbon': round(total_carbon, 2),
            'suggestions': suggestions,
            'distance': distance,
            'electricity': electricity,
            'plastic': plastic,
            'transport_type': transport_type,
            'result': True
        }
        return render(request, 'Pages/carbon_calculator.html', context)
        
    return render(request, 'Pages/carbon_calculator.html')

def request_pickup(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to request a recycling pickup.')
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        waste_type = request.POST.get('waste_type')
        pickup_date = request.POST.get('pickup_date')
        address = request.POST.get('address')
        
        # Verbose Logging
        print(f"SUBMISSION ATTEMPT: User ID: {request.session.get('user_id')}, Waste: {waste_type}, Date: {pickup_date}, Address: {address}")
        
        if waste_type and pickup_date and address:
            try:
                PickupRequest.objects.create(
                    user=user,
                    waste_type=waste_type,
                    pickup_date=pickup_date,
                    address=address
                )
                messages.success(request, 'Successfully Requested Pickup! 🌱')
                return redirect('my_pickups')
            except Exception as e:
                messages.error(request, f"Database Error: {e}")
                print(f"DATABASE ERROR during pickup create: {e}")
        else:
            messages.error(request, 'Please fill all the mandatory fields.')
            
    # Fetch user's pickups to show on the same page
    pickups = PickupRequest.objects.filter(user=user).order_by('-created_at')
    
    from datetime import date
    return render(request, 'Pages/request_pickup.html', {
        'current_date': date.today().strftime('%Y-%m-%d'),
        'pickups': pickups
    })





def my_pickups(request):
    if 'user_id' not in request.session:
        return redirect('signin')
    
    user = Register.objects.get(id=request.session['user_id'])
    pickups = PickupRequest.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'Pages/my_pickups.html', {'pickups': pickups})

def admin_manage_pickups(request):
    if 'user_id' not in request.session or request.session.get('user_role') != 'Admin':
        return redirect('signin')
        
    pickups = PickupRequest.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        pickup_id = request.POST.get('pickup_id')
        new_status = request.POST.get('status')
        
        pickup = get_object_or_404(PickupRequest, id=pickup_id)
        pickup.status = new_status
        pickup.save()
        
        messages.success(request, f'Pickup #{pickup_id} status updated to {new_status}.')
        
        # Redirect back to where the request came from (Dashboard or Pickup page)
        return redirect(request.META.get('HTTP_REFERER', 'admin_manage_pickups'))

        
    return render(request, 'Pages/admin_pickups.html', {'pickups': pickups})


