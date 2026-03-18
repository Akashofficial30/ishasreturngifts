from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

FAQS = [
    ("How long does delivery take?", "We deliver Pan India within 3–7 business days. Express delivery (1–3 days) is available for major cities at an additional charge."),
    ("What is your minimum order quantity for bulk orders?", "For bulk/wedding orders, the minimum quantity is 25 pieces. Special discounts apply for orders of 50+ pieces. Contact us for a custom quote."),
    ("Can I customize the products with our names or wedding date?", "Yes! We offer full customization including name engraving, date printing, and custom packaging. Additional charges apply. Minimum 30 pieces for customization."),
    ("What is your return and refund policy?", "We accept returns within 7 days of delivery for damaged or defective items. Customized products cannot be returned unless they are defective. Refunds are processed within 5–7 business days."),
    ("Do you offer gift packaging?", "Yes! All orders come with complimentary basic gift packaging. Premium gift boxes with personalized ribbons and tags are available at ₹25–₹50 per piece."),
    ("How do I track my order?", "Once your order is shipped, you'll receive a tracking number via SMS and email. You can also contact us on WhatsApp with your Order ID for updates."),
    ("Do you accept online payments?", "Yes! We accept UPI (PhonePe, GPay, Paytm), Credit/Debit Cards, Net Banking, and Cash on Delivery (COD) for orders under ₹5,000."),
    ("How can I place a bulk wedding order?", "You can either use our website to place the order directly, or contact us via WhatsApp/email with your requirements and we'll create a custom order for you with special pricing."),
]

def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject', 'other'),
            message=request.POST.get('message', ''),
        )
        messages.success(request, "✅ Thank you! Your message has been sent. We'll get back to you within 24 hours.")
        return redirect('contact')
    return render(request, 'contact/contact.html', {'faqs': FAQS})

def faq(request):
    return render(request, 'contact/faq.html', {'faqs': FAQS})
