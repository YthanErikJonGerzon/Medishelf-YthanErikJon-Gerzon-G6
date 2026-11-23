from datetime import date
from django.conf import settings
from django.db import models


class Medicine(models.Model):
    CATEGORY_CHOICES = (
        ('Analgesic', 'Analgesic / Antipyretic'),
        ('Antibiotic', 'Antibiotic'),
        ('Antihistamine', 'Antihistamine'),
        ('Antiseptic', 'Antiseptic / First Aid'),
        ('Vitamins', 'Vitamins & Supplements'),
        ('Other', 'Other'),
    )
    DOSAGE_CHOICES = (
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup / Suspension'),
        ('Ointment', 'Ointment / Cream'),
        ('Drops', 'Drops'),
        ('Injection', 'Injection'),
    )

    brand_name = models.CharField(max_length=150)
    generic_name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    dosage_form = models.CharField(max_length=50, choices=DOSAGE_CHOICES, default='Tablet')
    strength = models.CharField(max_length=50, help_text="e.g., 500mg, 250mg/5mL")
    reorder_level = models.PositiveIntegerField(default=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='medicines_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} ({self.generic_name} {self.strength})"

    @property
    def total_stock(self):
        today = date.today()
        return sum(
            b.current_quantity for b in self.batches.all()
            if b.expiration_date > today
        )

    @property
    def is_low_stock(self):
        return self.total_stock <= self.reorder_level


class MedicineBatch(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=80)
    current_quantity = models.PositiveIntegerField(default=0)
    expiration_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('medicine', 'batch_number')
        ordering = ['expiration_date']

    def __str__(self):
        return f"{self.medicine.brand_name} - Batch {self.batch_number}"

    @property
    def expiration_status(self):
        days_left = (self.expiration_date - date.today()).days
        if days_left <= 0:
            return 'Expired'
        elif days_left <= 30:
            return 'Expiring Soon'
        return 'Valid'


class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('STOCK_IN', 'Stock-In (Receive)'),
        ('STOCK_OUT', 'Stock-Out (Dispense)'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='stock_transactions')
    batch = models.ForeignKey(MedicineBatch, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity_changed = models.PositiveIntegerField()
    remarks = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity_changed} of {self.batch}"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action_performed = models.CharField(max_length=255)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"[{self.logged_at:%Y-%m-%d %H:%M}] {self.user.username}: {self.action_performed}"