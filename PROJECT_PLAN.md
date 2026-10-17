# Mess Management System — Project Plan & Specification

---

## 1. Project Overview

**Project Name:** Mess Management System
**Type:** Single-mess (single-tenant) web application, mobile-friendly (PWA-ready)
**Purpose:** একটা মেসের সদস্যদের meal tracking, deposit/bill management, ও expense management স্বয়ংক্রিয়ভাবে পরিচালনা করা।

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 5.x |
| API | Django REST Framework (DRF) |
| Frontend | Django Templates + Bootstrap 5 / Tailwind CSS (mobile-first, PWA-ready with `manifest.json` + service worker) |
| Database | PostgreSQL |
| Auth | Custom Django User Model (mobile number as username field), Session/Token-based auth |
| Hosting (suggested) | Render / Railway (backend + DB), same as prior DoctorDesk project pattern |
| Others | Django Signals (for balance/bill auto-calculation), Django Admin (for Super Manager quick access) |

---

## 3. Django Apps Structure

```
mess_management/
├── config/                 # project settings
├── accounts/                # Custom User, roles, registration, approval
├── mess_core/                # Mess settings (rent, current bill, seat bill, meal rate config)
├── meals/                    # Daily meal on/off, meal count
├── deposits/                  # Deposit claim + approval flow
├── expenses/                  # Bazar (market) expense entries — boro/choto bazar
├── bills/                     # Seat bill, current bill, house rent, electricity bill tracking
├── complaints/                 # Complaint system
├── dashboard/                  # Role-based dashboard views/APIs
└── api/                        # DRF routers/serializers aggregation (optional, or per-app)
```

---

## 4. User Roles & Permissions

একটাই `User` model, তার সাথে একটা `role` বা `is_monthly_manager` / `is_super_manager` flag থাকবে যাতে একজন User একসাথে একাধিক role (General User + Monthly Manager) রাখতে পারে।

```python
class User(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=15, unique=True)  # login field
    full_name = models.CharField(max_length=100)
    is_super_manager = models.BooleanField(default=False)
    is_active_member = models.BooleanField(default=False)  # False until Super Manager approves
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    USERNAME_FIELD = 'mobile_number'
```

**Monthly Manager** আলাদা model দিয়ে track হবে (এক সময়ে একজনই active থাকবে — validation logic লাগবে):

```python
class MonthlyManagerAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # store as YYYY-MM-01
    assigned_by = models.ForeignKey(User, related_name='assignments_made', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
```

> **Rule:** একই সময়ে একাধিক `is_active=True` MonthlyManagerAssignment থাকতে পারবে না — `save()` override বা signal দিয়ে validate করতে হবে।

### Role Permission Matrix

| Feature | General User | Monthly Manager | Super Manager |
|---|---|---|---|
| Own deposit/meal/bill দেখা | ✅ | ✅ | ✅ |
| Meal On/Off | ✅ (নিজের) | ✅ (নিজের) | ✅ (নিজের) |
| Deposit claim করা | ✅ | ✅ | ✅ |
| Deposit approve করা | ❌ | ✅ | ✅ |
| সবার meal count দেখা | ❌ | ✅ | ✅ |
| বাজার খরচ যোগ করা | ❌ | ✅ | ✅ |
| Fixed monthly meal assign | ❌ | ✅ | ✅ |
| বাসা ভাড়া/বিদ্যুৎ বিল নির্ধারণ | ❌ | ❌ | ✅ |
| Monthly Manager assign করা | ❌ | ❌ | ✅ |
| Default meal/seat/current bill value পরিবর্তন | ❌ | ❌ | ✅ |
| User registration approve | ❌ | ❌ | ✅ |
| Complaint দেখা (নিজের mess-এর) | নিজেরটা | সব | সব |

---

## 5. Core Models (Detailed)

### 5.1 `mess_core` app — Global Settings

```python
class MessSettings(models.Model):
    """Singleton-style model — শুধু ১টা row থাকবে"""
    seat_bill_default = models.DecimalField(max_digits=8, decimal_places=2, default=1150.00)
    current_bill_default = models.DecimalField(max_digits=8, decimal_places=2, default=300.00)
    breakfast_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=0.5)
    lunch_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    dinner_meal_value = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    meal_off_cutoff_time = models.TimeField(default="22:00")  # রাত ১০টা ডিফল্ট
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 5.2 `meals` app

```python
class DailyMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    breakfast = models.BooleanField(default=True)
    lunch = models.BooleanField(default=True)
    dinner = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'date')

    def total_meal_value(self):
        settings = MessSettings.objects.first()
        total = 0
        if self.breakfast: total += settings.breakfast_meal_value
        if self.lunch: total += settings.lunch_meal_value
        if self.dinner: total += settings.dinner_meal_value
        return total
```

> **Note:** ভবিষ্যতের প্রতিটা দিনের জন্য default row (all True) auto-create করা যেতে পারে (management command / signal দিয়ে, প্রতি মাসের শুরুতে বা daily cron দিয়ে)। Meal Off করলে সেই date-এর row update হবে — কিন্তু `meal_off_cutoff_time`-এর পরে আজকের/আগামীকালের meal off করা আটকাতে হবে (view-level validation)।

### 5.3 `deposits` app

```python
class Deposit(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    user = models.ForeignKey(User, related_name='deposits', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_claimed = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, related_name='approved_deposits', null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 5.4 `expenses` app — বাজার খরচ

```python
class BazarExpense(models.Model):
    BAZAR_TYPE = [('boro', 'বড় বাজার'), ('choto', 'ছোট বাজার')]
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Monthly Manager
    bazar_type = models.CharField(max_length=10, choices=BAZAR_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='bazar_receipts/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    month = models.DateField()  # YYYY-MM-01, for monthly aggregation
```

### 5.5 `bills` app

```python
class MonthlyBillCycle(models.Model):
    month = models.DateField(unique=True)  # YYYY-MM-01
    house_rent_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    house_rent_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_bill_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_bill_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_meal_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # calculated field
    meal_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # calculated field
    set_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class UserBillRecord(models.Model):
    """প্রতি মাসে প্রতি User-এর জন্য bill snapshot"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    seat_bill = models.DecimalField(max_digits=8, decimal_places=2)
    current_bill_share = models.DecimalField(max_digits=8, decimal_places=2)
    house_rent_share = models.DecimalField(max_digits=8, decimal_places=2)
    electricity_share = models.DecimalField(max_digits=8, decimal_places=2)
    meal_cost = models.DecimalField(max_digits=10, decimal_places=2)  # meal_count * meal_rate
    total_due = models.DecimalField(max_digits=10, decimal_places=2)  # calculated
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2)  # sum of approved deposits
    balance = models.DecimalField(max_digits=10, decimal_places=2)  # deposit - due

    class Meta:
        unique_together = ('user', 'month')
```

> **Bill Calculation Logic (Business Rule):**
> `Total Due = Meal Cost + Seat Bill + Current Bill Share + House Rent Share + Electricity Share`
> সব share সমান ভাগে ভাগ হবে active member সংখ্যা দিয়ে (assumption হিসেবে confirm করা হয়েছে)।
> `Balance = Total Approved Deposit − Total Due` (negative হলে বাকি আছে হিসেবে দেখাবে)

### 5.6 `complaints` app

```python
class Complaint(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')]
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    handled_by = models.ForeignKey(User, related_name='handled_complaints', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
```

---

## 6. Key Business Logic Rules (Recap)

1. **Meal Value (default):** সকাল = 0.5, দুপুর = 1.0, রাত = 1.0 (Super Manager পরিবর্তনযোগ্য via `MessSettings`)
2. **Meal Off Cutoff:** ডিফল্ট রাত ১০টা — এর পরে পরদিনের meal off করা যাবে না (adjustable)
3. **Meal Rate Formula:** `Meal Rate = Total Bazar Expense (মাসিক) ÷ Total Meal Count (মাসিক)`
4. **Deposit Flow:** User claim → status = pending → Manager/Super Manager approve → balance-এ যোগ হবে
5. **Registration Flow:** Sign up → `is_active_member = False` → Super Manager approve → Active
6. **Monthly Manager:** এক সময়ে একজনই active, বারবার একই User হতে পারবে, Super Manager মাঝপথেও পরিবর্তন করতে পারবে
7. **Default Values:** Seat Bill = ৳1150, Current Bill = ৳300 (Super Manager পরিবর্তনযোগ্য)
8. **Bazar Entry:** শুধু Monthly Manager (এবং Super Manager) করতে পারবে, Receipt Image optional
9. **Complaint:** General User → Monthly Manager-কে যায়, Super Manager সব দেখতে পারে, status track হয়

---

## 7. Authentication Details

- Login: **Mobile Number + Password** (OTP পরে যোগ করার সুযোগ রেখে architecture করা — `accounts/services/otp.py` আলাদা রাখলে ভবিষ্যতে সহজে যোগ করা যাবে)
- Custom User Model থেকে `AbstractBaseUser` + `PermissionsMixin` inherit
- Django Admin দিয়ে প্রথম Super Manager manually তৈরি করতে হবে (`createsuperuser` + role flag)
- Password reset: mobile number verification দিয়ে (future scope)

---

## 8. Suggested API Endpoints (DRF)

```
POST   /api/auth/register/
POST   /api/auth/login/
GET    /api/users/me/
GET    /api/users/pending-approval/        [Super Manager only]
POST   /api/users/<id>/approve/            [Super Manager only]

GET    /api/meals/my-meals/?month=2026-08
POST   /api/meals/toggle/                  {date, breakfast, lunch, dinner}
GET    /api/meals/summary/                 [Manager+ — সবার meal count]

POST   /api/deposits/claim/
GET    /api/deposits/my-deposits/
GET    /api/deposits/pending/              [Manager+]
POST   /api/deposits/<id>/approve/         [Manager+]

POST   /api/expenses/bazar/                [Manager+]
GET    /api/expenses/bazar/?month=2026-08

GET    /api/bills/my-bill/?month=2026-08
POST   /api/bills/set-house-rent/          [Super Manager]
POST   /api/bills/set-electricity/         [Super Manager]
POST   /api/bills/generate/                [Manager+ — মাস শেষে bill calculate করার trigger]

POST   /api/complaints/
GET    /api/complaints/my-complaints/
GET    /api/complaints/all/                [Manager+]
PATCH  /api/complaints/<id>/status/        [Manager+]

GET    /api/settings/                      [সবাই দেখতে পারবে]
PATCH  /api/settings/                      [Super Manager only]

POST   /api/manager/assign/                [Super Manager — Monthly Manager assign]
```

---

## 9. Security Checklist

- [ ] Password hashing (Django default PBKDF2/Argon2)
- [ ] Role-based permission classes (DRF custom `IsSuperManager`, `IsMonthlyManagerOrAbove`)
- [ ] `is_active_member=False` User-দের login/API access block করা
- [ ] Rate limiting on login endpoint (django-ratelimit বা DRF throttling)
- [ ] CSRF protection (template-based views-এর জন্য)
- [ ] Environment variables দিয়ে SECRET_KEY, DB credentials রাখা (`.env` + `python-decouple`)
- [ ] File upload validation (receipt/profile images — size/type check)
- [ ] HTTPS enforced in production

---

## 10. Development Phases (Suggested Timeline)

| Phase | কাজ | সময় |
|---|---|---|
| 1 | Project setup, Custom User Model, Auth (register/login/approve) | সপ্তাহ ১ |
| 2 | Mess Settings, Meal On/Off system | সপ্তাহ ২ |
| 3 | Deposit claim + approval flow | সপ্তাহ ৩ |
| 4 | Bazar expense + Meal rate calculation | সপ্তাহ ৪ |
| 5 | Bill generation (rent, electricity, seat, current bill) | সপ্তাহ ৫ |
| 6 | Complaint system + Dashboard (role-based) | সপ্তাহ ৬ |
| 7 | Frontend polish (mobile-friendly UI, PWA manifest) | সপ্তাহ ৭ |
| 8 | Testing, bug fixing, deployment (Render) | সপ্তাহ ৮ |

---

## 11. Open Items for Future Iteration (V2 Scope)

- bKash/Nagad payment gateway integration
- SMS/OTP-based login
- Push notification (bill due reminder, meal reminder)
- Monthly PDF statement/report generation
- Multi-mess support (multi-tenant) if needed later
