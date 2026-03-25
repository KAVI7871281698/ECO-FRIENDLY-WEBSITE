from .models import Cart, Register

def cart_count(request):
    count = 0
    user_role = request.session.get('user_role', 'User')
    
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        
        # Verify and sync role from database to session
        try:
            user = Register.objects.get(id=user_id)
            if user.role != user_role:
                request.session['user_role'] = user.role
                user_role = user.role
        except Register.DoesNotExist:
            # If user deleted but session exists, clear session
            request.session.flush()
            return {'cart_count': 0, 'user_role': 'User'}

        cart_items = Cart.objects.filter(user_id=user_id)
        count = sum(item.quantity for item in cart_items)
        
    return {
        'cart_count': count,
        'user_role': user_role
    }
