import calendar
from django.contrib.auth import logout
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import *
import json
from django.contrib.auth import authenticate,login

import datetime
from .forms import *

month_names_ru = {
    "January": "Январь",
    "February": "Февраль",
    "March": "Март",
    "April": "Апрель",
    "May": "Май",
    "June": "Июнь",
    "July": "Июль",
    "August": "Август",
    "September": "Сентябрь",
    "October": "Октябрь",
    "November": "Ноябрь",
    "December": "Декабрь"
}

def base(request):
    if 'tabel_pk' in request.GET:
        tabel_pk=request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk

    tabel = Tabel.objects.get(pk=tabel_pk)
    request.session['tabel_year'] = tabel.year

    context={
        "tabel_pk":tabel_pk,
        "tabel":tabel,
    }

    return render(request, 'table/base.html',context)

def graph(request):
    if 'tabel_pk' in request.GET:
        tabel_pk=request.GET['tabel_pk']
        request.session['chosen_pk'] = tabel_pk

    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    request.session['tabel_year'] = tabel.year
    
    employees = Employees.objects.filter(tabel_id=tabel_pk)
    job = Job.objects.all()
    subdivision = Subdivision.objects.all()
    oil_place = OilPlace.objects.all()
    worked_time = WorkedTime.objects.all()
    time_trackings = TimeTracking.objects.filter(type="plan")

    month = request.GET.get('months')
    request.session['selected_month'] = month
    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTracking.objects.filter(employee_id__in = employees.values_list('tabel_number',flat=True)).filter(type='plan')
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id',flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    else:
        month = 1

    year = int(request.session['tabel_year'])
    filter_month = int(month)
    filter_years = int(request.session['tabel_year'])
    
    name_month_en = calendar.month_name[filter_month]
    name_month_ru = month_names_ru[name_month_en]
    tracking = TimeTracking.objects.filter(date__month=filter_month).filter(type="plan")

    dates = tracking.values_list('date',flat=True).distinct()
    for date in dates:
        filter_month = date.month
        filter_years = year

    num_days = calendar.monthrange(filter_years, filter_month)[1]
    days = range(1, num_days + 1)

    directory = {}

    for employee in employees:
        pairs = [('worked_days', 0), ('weekends', 0), ('days_in_month', len(days)), ('total_work_hours', 0)]
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1 
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                else:
                    directory[f'{employee.name}']['weekends'] += 1

    context = {
        "year": year,
        "tabel_pk": tabel_pk,
        "selected_option_month": request.session['selected_month'],
        "tabel": tabel,
        "selected_month": name_month_ru,
        "month": filter_month,
        "days": days,
        'employees': employees, 
        'job': job, 
        'subdivision': subdivision, 
        'oil_place': oil_place, 
        'worked_time': worked_time, 
        'time_tracking': time_trackings,
        'calculations': directory
        }
    
    return render(request, 'table/graph.html', context)

def tabelPlan(request):
    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = Employees.objects.filter(tabel_id=tabel_pk)
    job = Job.objects.all()
    subdivision = Subdivision.objects.all()
    oil_place = OilPlace.objects.all()
    worked_time = WorkedTime.objects.all()
    attendance_full = Attendance.objects.all()
    attendance = Attendance.objects.filter(type="дни явок")
    no_attendance = Attendance.objects.filter(type="дни неявок")
    time_tracking = TimeTracking.objects.filter(type="plan")
    tracking = TimeTracking.objects.filter(employee_id__in=employees.values_list('tabel_number', flat=True))

    month = request.GET.get('months')
    request.session['selected_month'] = month
    
    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTracking.objects.filter(employee_id__in=employees.values_list('tabel_number', flat=True)).filter(type='plan')
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id', flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    else:
        month = 1

    year = int(request.session['tabel_year'])
    filter_month = int(month)
    name_month_en = calendar.month_name[filter_month]
    name_month_ru = month_names_ru[name_month_en]
    tracking = TimeTracking.objects.filter(date__month=filter_month).filter(type="plan")
    dates = tracking.values_list('date',flat=True).distinct()
    filter_years = int(request.session['tabel_year'])
    for date in dates:
        filter_month = date.month
        filter_years = year

    num_days = calendar.monthrange(filter_years, filter_month)[1]
    days = range(1, num_days + 1)

    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance_full:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1 
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                for dir in directory[f'{employee.name}'].keys():
                    if dir == work.worked_hours:
                        directory[f'{employee.name}'][f'{dir}'] += 1

    context = {
        "year":year,
        "selected_option_month": request.session['selected_month'],
        "tabel": tabel,
        "selected_month": name_month_ru,
        "month": filter_month,
        "days": days,
        'employees': employees, 
        'job': job, 
        'subdivision': subdivision, 
        'oil_place': oil_place, 
        'worked_time': worked_time, 
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': time_tracking,
        'calculations': directory
        }

    return render(request, 'table/tabelPlan.html', context)


def tabelFactRead(request):
    time_tracking = TimeTracking.objects.filter(type='fact')
    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    worked_time = WorkedTime.objects.all()
    jobs = Job.objects.all()
    subdivision = SubdivisionForm()
    no_attendance = Attendance.objects.filter(type="дни неявок")
    attendance = Attendance.objects.filter(type="дни явок") 
    reservoir = ReservoirForm()
    attendance_full = Attendance.objects.all()

    employees = Employees.objects.filter(tabel_id=tabel_pk)
    month = request.GET.get('months')
    request.session['selected_month'] = month

    if month and month is not None:
        filter_month = int(month)
        tracking = TimeTracking.objects.filter(employee_id__in=employees.values_list('tabel_number', flat=True)).filter(type='fact')
        tracking = tracking.filter(date__month=filter_month)
        tabel_numbers = tracking.values_list('employee_id', flat=True)
        employees = employees.filter(tabel_number__in=tabel_numbers)
    else:
        month = 1

    year = int(request.session['tabel_year'])

    filter_month = int(month)
    name_month_en = calendar.month_name[filter_month]
    name_month_ru = month_names_ru[name_month_en]
    tracking = TimeTracking.objects.filter(date__month=filter_month).filter(type="fact")
    dates = tracking.values_list('date',flat=True).distinct()

    filter_years = int(request.session['tabel_year'])
    for date in dates:
            filter_month = date.month
            filter_years = year

    num_days = calendar.monthrange(filter_years, filter_month)[1]
    days = range(1, num_days + 1)

    TimeTracking.update_missing_fact_entries(filter_month, year)

    time_tracking = TimeTracking.objects.filter(
        type='fact', date__year=year, date__month=filter_month
    )

    #nurzh algorithm
    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance_full:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                for dir in directory[f'{employee.name}'].keys():
                    if dir == work.worked_hours:
                        directory[f'{employee.name}'][f'{dir}'] += 1

    context = { 
        "year":filter_years,
        "tabel":tabel,
        "selected_option_month":request.session['selected_month'],
        "selected_month": name_month_ru,
        "month":filter_month,
        "days":days,
        "time_tracking":time_tracking,
        "reservoir":reservoir,
        "subdivision":subdivision,
        "employees":employees,
        "jobs":jobs,
        "attendance":attendance,
        "no_attendance":no_attendance,
        'calculations': directory,
        "worked_time":worked_time}
    return render(request,'table/tabelFactRead.html',context)



def is_valid_queryparam(param):
    return param != '---' and param is not None

def home(request):
    filter_year = request.GET.get('years')
    request.session['selected_year'] = filter_year
    # filter_month = request.GET.get('months')
    tabel = Tabel.objects.all()
    filter_reservoir = request.GET.get('podrazd')
    request.session['selected_reservoir'] = filter_reservoir


    filter_subdiv = request.GET.get('mesto')
    request.session['selected_subdivision'] = filter_subdiv

    if is_valid_queryparam(filter_year):
        tabel = tabel.filter(year=filter_year)
    
    # if is_valid_queryparam(filter_month):
    #     tabel = tabel.filter(month=filter_month)

    if is_valid_queryparam(filter_reservoir):
        tabel = tabel.filter(reservoir__name__icontains=filter_reservoir)

    if is_valid_queryparam(filter_subdiv):
        tabel = tabel.filter(subdivision__name__icontains=filter_subdiv)
    
    
    reservoir_form = TabelReservoirForm()
    subdivision_form = TabelSubdivisionForm()
    year_form = TabelYearForm()
    context = {
        "selected_year":request.session['selected_year'],
        "selected_reservoir": request.session['selected_reservoir'],
        "selected_subdivision": request.session['selected_subdivision'],
        "tabel":tabel,
        "year_form":year_form,
        "reservoir":reservoir_form,
        "subdivision":subdivision_form
        }

    return render(request,'table/home.html',context)

#login

def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username_part_email = form.cleaned_data.get("email")
            username_part=username_part_email.split('@')
            username = username_part[0]
            user = authenticate(request, email=email, password=password,username=username)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    print('User is inactive.')
            else:
                print('Authentication failed.')
        else:
            print(form.errors)
    else:
        form = UserLoginForm(request)

    return render(request, 'table/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


#tabel fact update
def tabelFactUpdate(request):
    tabel_pk = request.session['chosen_pk']
    tabel = Tabel.objects.get(pk=tabel_pk)
    employees = Employees.objects.filter(tabel_id=tabel_pk)
    job = Job.objects.all()
    subdivision = Subdivision.objects.all()
    oil_place = OilPlace.objects.all()
    worked_time = WorkedTime.objects.all()
    attendance_full = Attendance.objects.all()
    attendance = Attendance.objects.filter(type="дни явок")
    no_attendance = Attendance.objects.filter(type="дни неявок")
    selected_month = request.session.get('selected_month')

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('worked_hours_'):
                time_tracking_id = key.split('_')[2]
                time_tracking_instance = TimeTracking.objects.get(pk=time_tracking_id)
                time_tracking_instance.worked_hours = value
                time_tracking_instance.save()
        return redirect(reverse('tabelFactRead') +f'?months={selected_month}')

    today_year =  int(request.session['tabel_year'])
    month = int(selected_month)
    name_month_en = calendar.month_name[month]
    name_month_ru = month_names_ru[name_month_en]
    num_days = calendar.monthrange(today_year, month)[1]
    days = range(1, num_days + 1)
    tracking = TimeTracking.objects.filter(employee_id__in=employees.values_list('tabel_number', flat=True)).filter(type='fact')
    tracking = tracking.filter(date__month=month)
    tabel_numbers = tracking.values_list('employee_id', flat=True)
    employees = employees.filter(tabel_number__in=tabel_numbers)

    directory = {}
    for employee in employees:
        pairs = []
        pairs.append(('worked_days', 0))
        for att in attendance_full:
            pairs.append((f'{att}', 0))
        pairs.append(('days_in_month', len(days)))
        pairs.append(('total_work_hours', 0))
        directory[f'{employee.name}'] = dict(pairs)

    for employee in employees:
        for work in tracking:
            if work.employee_id == employee:
                if str(work.worked_hours).isdigit():
                    directory[f'{employee.name}']['worked_days'] += 1
                    directory[f'{employee.name}']['total_work_hours'] += int(work.worked_hours)
                for dir in directory[f'{employee.name}'].keys():
                    if dir == work.worked_hours:
                        directory[f'{employee.name}'][f'{dir}'] += 1

    context = {
        "month":month,
        "year":today_year,
        "tabel":tabel,
        "selected_month":name_month_ru,
        "days":days,
        'employees': employees, 
        'job': job, 
        'subdivision': subdivision, 
        'oil_place': oil_place, 
        'worked_time': worked_time, 
        'attendance': attendance, 
        'no_attendance': no_attendance,
        'time_tracking': tracking,
        'calculations': directory
        }
    
    return render(request, 'table/tabelFactUpdate.html', context)



