# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Report
from .forms import ReportFilterForm
from .utils import generate_monthly_report


@login_required
def report_list(request):
    form = ReportFilterForm(request.GET or None)
    reports = Report.objects.all()

    if form.is_valid():
        church = form.cleaned_data.get('church')
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')

        if church:
            reports = reports.filter(church_name=church)
        if month:
            reports = reports.filter(month=month)
        if year:
            reports = reports.filter(year=year)

    context = {
        'reports': reports,
        'form': form,
    }
    return render(request, 'reports/list.html', context)


@login_required
def report_detail(request, pk):
    report = Report.objects.get(pk=pk)
    return render(request, 'reports/detail.html', {'report': report})


@login_required
def generate_report(request):
    if request.method == 'POST':
        church = request.POST.get('church')
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))

        report = generate_monthly_report(church, month, year)
        return redirect('report_detail', pk=report.pk)

    return render(request, 'reports/generate.html')