    from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from accounts.views import role_required
from .models import Medicine, MedicineBatch, StockTransaction, AuditLog
from .forms import MedicineForm, MedicineBatchForm, StockTransactionForm


@login_required
def medicine_list(request):
    query = request.GET.get('q', '').strip()
    medicines = Medicine.objects.prefetch_related('batches').all().order_by('brand_name')
    if query:
        medicines = medicines.filter(brand_name__icontains=query) | medicines.filter(generic_name__icontains=query)
    batches = MedicineBatch.objects.select_related('medicine').all()
    return render(request, 'inventory/medicine_list.html', {
        'medicines': medicines,
        'batches': batches,
        'query': query,
    })


@role_required(['Admin', 'Staff'])
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.created_by = request.user
            med.save()
            AuditLog.objects.create(user=request.user, action_performed=f"Added medicine: {med}")
            messages.success(request, f"Medicine '{med.brand_name}' added successfully.")
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': 'Add New Medicine'})


@role_required(['Admin', 'Staff'])
def medicine_update(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(user=request.user, action_performed=f"Updated medicine: {med}")
            messages.success(request, f"Medicine '{med.brand_name}' updated.")
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=med)
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': f'Edit {med.brand_name}'})


@role_required(['Admin'])
def medicine_delete(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = str(med)
        med.delete()
        AuditLog.objects.create(user=request.user, action_performed=f"Deleted medicine: {name}")
        messages.success(request, f"Medicine '{name}' deleted.")
        return redirect('medicine_list')
    return render(request, 'inventory/medicine_confirm_delete.html', {'medicine': med})


@role_required(['Admin', 'Staff'])
def batch_create(request):
    if request.method == 'POST':
        form = MedicineBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.created_by = request.user
            batch.save()
            if batch.current_quantity > 0:
                StockTransaction.objects.create(
                    user=request.user,
                    batch=batch,
                    transaction_type='STOCK_IN',
                    quantity_changed=batch.current_quantity,
                    remarks='Initial batch stock-in',
                )
            AuditLog.objects.create(
                user=request.user,
                action_performed=f"Created batch {batch.batch_number} for {batch.medicine.brand_name} (Qty: {batch.current_quantity})"
            )
            messages.success(request, f"Batch '{batch.batch_number}' added successfully.")
            return redirect('medicine_list')
    else:
        form = MedicineBatchForm()
    return render(request, 'inventory/batch_form.html', {'form': form})


@role_required(['Admin', 'Staff'])
def record_transaction(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                tx = form.save(commit=False)
                tx.user = request.user
                batch = tx.batch

                if tx.transaction_type == 'STOCK_IN':
                    batch.current_quantity += tx.quantity_changed
                else:
                    batch.current_quantity -= tx.quantity_changed

                batch.save()
                tx.save()

                AuditLog.objects.create(
                    user=request.user,
                    action_performed=(
                        f"{tx.get_transaction_type_display()} | {batch.medicine.brand_name} "
                        f"(Batch {batch.batch_number}) | Qty: {tx.quantity_changed} | Remaining: {batch.current_quantity}"
                    )
                )

            messages.success(request, f"{tx.get_transaction_type_display()} recorded successfully.")
            return redirect('transaction_history')
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/transaction_form.html', {'form': form})


@login_required
def transaction_history(request):
    transactions = StockTransaction.objects.select_related('user', 'batch__medicine').all()
    return render(request, 'inventory/transaction_history.html', {'transactions': transactions})


@role_required(['Admin'])
def audit_log_list(request):
    logs = AuditLog.objects.select_related('user').all()
    return render(request, 'inventory/audit_logs.html', {'logs': logs})