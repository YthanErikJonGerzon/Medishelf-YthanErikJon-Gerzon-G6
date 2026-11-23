from django import forms
from .models import Medicine, MedicineBatch, StockTransaction


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['brand_name', 'generic_name', 'category', 'dosage_form', 'strength', 'reorder_level']


class MedicineBatchForm(forms.ModelForm):
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = MedicineBatch
        fields = ['medicine', 'batch_number', 'current_quantity', 'expiration_date']


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['batch', 'transaction_type', 'quantity_changed', 'remarks']

    def clean_quantity_changed(self):
        qty = self.cleaned_data.get('quantity_changed')
        if qty is None or qty <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return qty

    def clean(self):
        cleaned_data = super().clean()
        batch = cleaned_data.get('batch')
        tx_type = cleaned_data.get('transaction_type')
        qty = cleaned_data.get('quantity_changed')

        if batch and tx_type == 'STOCK_OUT' and qty:
            if qty > batch.current_quantity:
                raise forms.ValidationError(
                    f"Insufficient stock in Batch {batch.batch_number}. Available: {batch.current_quantity}."
                )
            if batch.expiration_status == 'Expired':
                raise forms.ValidationError(
                    f"Cannot dispense Batch {batch.batch_number} because it is already EXPIRED."
                )
        return cleaned_data