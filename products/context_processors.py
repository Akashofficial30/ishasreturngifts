from django.db.models import Sum

from .models import CartItem


def cart_count(request):
    """Cart badge count, rendered in the header on every page.

    Aggregates in SQL rather than loading every CartItem, and reads through
    CartItem directly so a session with duplicate Cart rows can't raise
    MultipleObjectsReturned on an unrelated page.
    """
    session_key = request.session.session_key
    if not session_key:
        return {'cart_count': 0}
    total = CartItem.objects.filter(
        cart__session_key=session_key
    ).aggregate(total=Sum('quantity'))['total']
    return {'cart_count': total or 0}
