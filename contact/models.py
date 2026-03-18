from django.db import models


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('order', 'Order Issue'),
        ('payment', 'Payment Problem'),
        ('shipping', 'Shipping Query'),
        ('return', 'Return / Refund'),
        ('bulk', 'Bulk Order Enquiry'),
        ('custom', 'Customization Request'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='other')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} – {self.get_subject_display()} ({self.status})"
