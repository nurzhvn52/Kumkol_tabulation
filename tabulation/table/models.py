from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,AbstractUser
from django.urls import reverse
from .managers import *
TIMETRACKING_CHOICES = (
    ("plan","Plan"),
    ("fact","Fact")
)

ATTENDACE_CHOICES = (
    ('дни неявок',"Дни Неявок"),
    ("дни явок","Дни Явок")
)
MONTH_CHOICES_RU = (
    ("1", "Январь"),
    ("2", "Февраль"),
    ("3", "Март"),
    ("4", "Апрель"),
    ("5", "Май"),
    ("6", "Июнь"),
    ("7", "Июль"),
    ("8", "Август"),
    ("9", "Сентябрь"),
    ("10", "Октябрь"),
    ("11", "Ноябрь"),
    ("12", "Декабрь"),
)
YEARS_CHOICES = (
    ('2023','2023'),
    ('2024','2024'),
    ('2025','2025')
)

class Job(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Name")
    description = models.CharField(max_length=200, verbose_name = "Description")

    def __str__(self) -> str:
        return self.name
    
class OilPlace(models.Model):
    name = models.CharField(max_length=50, verbose_name = "Name Oil Place")
    description = models.CharField(max_length=200, verbose_name = "Description")

    def __str__(self) -> str:
        return self.name
    

    
class Subdivision(models.Model):
    name = models.CharField(max_length=50,verbose_name = "Name Subdivision")
    description = models.CharField(max_length=200, verbose_name = "Description")

    def __str__(self) -> str:
        return self.name
    

class Tabel(models.Model):
    reservoir= models.ForeignKey(OilPlace, verbose_name="Oil Place",related_name='reservoir', on_delete=models.CASCADE)
    subdivision = models.ForeignKey(Subdivision, verbose_name="Subdivision", on_delete=models.CASCADE,related_name = 'subdivision')
    month = models.CharField(max_length = 100,verbose_name='Month',choices=MONTH_CHOICES_RU,default=None)
    year = models.CharField(verbose_name = 'Year',choices=YEARS_CHOICES,max_length=4,default=None)
    
    def __str__(self) -> str:
        return f"{self.id} {self.subdivision} {self.reservoir} {self.year} "

    def get_absolute_url(self):
        return reverse("tabel", kwargs={"pk": self.pk})


class Employees(models.Model):
    tabel_number = models.BigIntegerField(primary_key = True, verbose_name = "Tabel Number")
    name = models.CharField(max_length=50, verbose_name = "Name")
    middlename = models.CharField(max_length=50, verbose_name = "Middle Name")
    surname = models.CharField(max_length=50, verbose_name = "Surname")
    tariff_category = models.IntegerField(verbose_name = "Tariff Category")
    job = models.ForeignKey(Job, related_name='job', on_delete=models.CASCADE)
    # subdivision = models.ForeignKey(Subdivision, related_name='subdivision', on_delete=models.CASCADE) 
    oil_place = models.ForeignKey(OilPlace, related_name='oil_place', on_delete=models.CASCADE)
    tabel_id = models.ForeignKey(Tabel, verbose_name=("Tabel ID"), on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"{self.tabel_number} {self.name} {self.surname}"


class Attendance(models.Model):
    name = models.CharField(max_length=50, verbose_name = "Name")
    description = models.CharField(max_length=200, verbose_name = "Description")
    type = models.CharField(verbose_name="Type", max_length=100,choices=ATTENDACE_CHOICES)

    def __str__(self) -> str:
        return self.name
    
class TimeTracking(models.Model):
    employee_id = models.ForeignKey(Employees, verbose_name="EmployeeID", on_delete=models.CASCADE)
    type = models.CharField(choices = TIMETRACKING_CHOICES, verbose_name = "Type",max_length=100)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name = "Date")
    worked_hours = models.CharField(max_length = 5, verbose_name = "Worked Hours")

    @classmethod
    def update_missing_fact_entries(cls, month, year):
        # Get distinct dates for the given month and year in type='plan'
        plan_entries = cls.objects.filter(type='plan', date__month=month, date__year=year)

        # Get distinct dates for the given month and year in type='fact'
        fact_entries = cls.objects.filter(type='fact', date__month=month, date__year=year)

        # Identify dates and employees present in plan but not in fact
        missing_entries = plan_entries.exclude(pk__in=fact_entries.values_list('pk', flat=True))

        # Create new TimeTracking objects for missing entries in type='fact'
        for entry in missing_entries:
            # Check if the entry already exists in type='fact'
            if not cls.objects.filter(type='fact', employee_id=entry.employee_id, date=entry.date).exists():
                # If the entry doesn't exist in type='fact', create a new one
                cls.objects.create(
                    employee_id=entry.employee_id,
                    date=entry.date,
                    worked_hours=entry.worked_hours,
                    # Add other fields as needed
                    type='fact'
                )

    def __str__(self) -> str:
        return f"{self.id} {self.employee_id.name} {self.worked_hours} {self.type}"


    
class WorkedTime(models.Model):
    # employee_id = models.ForeignKey(Employees, verbose_name="EmployeeID", on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, verbose_name = "Name")
    description = models.CharField(max_length=200, verbose_name = "Description")

    def __str__(self) -> str:
        return self.name

class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email",max_length=100,null=True,unique=True)
    first_name = models.CharField(max_length=100,verbose_name="First Name")
    last_name = models.CharField(max_length=100,verbose_name="Last Name")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name="Date Joined",auto_now_add=True)
    username = models.CharField(verbose_name = 'username',max_length=100,unique=True)
    USERNAME_FIELD = ('username')
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    objects = CustomUserManager()


    def __str__(self):
        return self.email
    

