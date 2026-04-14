r"""
Seed script: creates sample users with auth credentials + sample data.
Run from project root:
    venv\Scripts\python.exe seed.py
"""
import os
import uuid
from datetime import datetime, time, timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'createch.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from marketplace.models import (
    AuthCredential,
    Category,
    Creator,
    DailyAnalytics,
    Follow,
    Match,
    Message,
    Order,
    PaymentMethod,
    Review,
    Service,
    SupportTicket,
    User,
    UserWallet,
    Withdrawal,
)


def seed_user(email, password, first_name, last_name, role, phone=''):
    """Create a User + AuthCredential pair (idempotent)."""
    if AuthCredential.objects.filter(email=email).exists():
        cred = AuthCredential.objects.get(email=email)
        user = User.objects.get(firebase_uid=cred.firebase_uid)
        print(f'  Already exists: {email}')
        return user

    firebase_uid = f'django_{uuid.uuid4().hex[:16]}'
    full_name = f'{first_name} {last_name}'.strip()

    user = User.objects.create(
        firebase_uid=firebase_uid,
        email=email,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        phone=phone,
        role=role,
    )
    AuthCredential.objects.create(
        firebase_uid=firebase_uid,
        email=email,
        password_hash=make_password(password),
    )
    print(f'  Created: {email} (role={role})')
    return user


def ensure_creator_profile(user, **defaults):
    creator, created = Creator.objects.get_or_create(
        user_id=user.firebase_uid,
        defaults=defaults,
    )
    print('  Created creator profile.' if created else '  Creator profile already exists.')
    return creator


def ensure_record(model, lookup, defaults, created_message, existing_message):
    _, created = model.objects.get_or_create(**lookup, defaults=defaults)
    print(created_message if created else existing_message)


# ── Users ─────────────────────────────────────────────────────────────────
print('=' * 60)
print('CREATECH — SEEDING DATABASE')
print('=' * 60)

print('\n[Users]')
admin_user = seed_user(
    'admin@createch.com', 'Admin@1234',
    'Admin', 'Createch', 'admin',
)
creator_user = seed_user(
    'creator@createch.com', 'Creator@1234',
    'Juan', 'Dela Cruz', 'creator', '09123456789',
)
client_user = seed_user(
    'client@createch.com', 'Client@1234',
    'Maria', 'Santos', 'client', '09987654321',
)
mobile_client_user = seed_user(
    'alex@createch.app', 'password',
    'Alex', 'Rivera', 'client', '09171234567',
)
mobile_creator_user = seed_user(
    'maya@createch.app', 'password',
    'Maya', 'Santos', 'creator', '09181234567',
)
mobile_admin_user = seed_user(
    'admin@createch.app', 'password',
    'System', 'Admin', 'admin', '09190000000',
)

# ── Creator profile ───────────────────────────────────────────────────────
print('\n[Creator Profile]')
ensure_creator_profile(
    creator_user,
    bio='Professional graphic designer with 5 years of experience.',
    skills='{logo design,branding,web design}',
    experience_years='5',
    starting_price='1500',
    turnaround_time='3-5 days',
    verification_status='verified',
)
ensure_creator_profile(
    mobile_creator_user,
    bio='Brand strategist and UI designer focused on startup launches.',
    skills='{branding,ui/ux design,social media kit}',
    experience_years='4',
    starting_price='1800',
    turnaround_time='2-4 days',
    verification_status='verified',
)

# ── Categories ────────────────────────────────────────────────────────────
print('\n[Categories]')
if not Category.objects.exists():
    categories = [
        ('Design', '🎨', '#6366F1'),
        ('Development', '💻', '#10B981'),
        ('Writing', '✍️', '#F59E0B'),
        ('Marketing', '📢', '#EF4444'),
        ('Video', '🎬', '#8B5CF6'),
    ]
    for label, icon, color in categories:
        Category.objects.create(label=label, icon=icon, color=color)
    print(f'  Created {len(categories)} categories.')
else:
    print('  Categories already exist.')

# ── Services ──────────────────────────────────────────────────────────────
print('\n[Services]')
if not Service.objects.filter(creator_id=creator_user.firebase_uid).exists():
    services = [
        ('Professional Logo Design', 'Logo Design', '2500', 'Design'),
        ('Social Media Assets Pack', 'Social Media', '1500', 'Design'),
        ('Website Mockup (Figma)', 'Web Mockup', '7500', 'Design'),
    ]
    for title, label, price, category in services:
        Service.objects.create(
            creator_id=creator_user.firebase_uid,
            title=title,
            label=label,
            price=price,
            category=category,
        )
    print(f'  Created {len(services)} services.')
else:
    print('  Services already exist.')

if not Service.objects.filter(creator_id=mobile_creator_user.firebase_uid).exists():
    services = [
        ('Startup Brand Kit', 'Brand Style Guides', '3200', 'Design'),
        ('Instagram Launch Pack', 'Social Media Marketing', '2100', 'Marketing'),
    ]
    for title, label, price, category in services:
        Service.objects.create(
            creator_id=mobile_creator_user.firebase_uid,
            title=title,
            label=label,
            description=f'{title} service package for fast delivery.',
            price=price,
            category=category,
        )
    print(f'  Created {len(services)} mobile demo services.')
else:
    print('  Mobile demo services already exist.')

# ── Orders ────────────────────────────────────────────────────────────────
print('\n[Orders]')
if not Order.objects.filter(client_id=client_user.firebase_uid).exists():
    orders = [
        ('Professional Logo Design', '2500', 'completed'),
        ('Website Mockup (Figma)', '7500', 'pending'),
        ('Social Media Assets Pack', '1500', 'in_progress'),
    ]
    for title, price, order_status in orders:
        Order.objects.create(
            client_id=client_user.firebase_uid,
            creator_id=creator_user.firebase_uid,
            service_title=title,
            price=price,
            status=order_status,
            client_name=client_user.full_name,
            creator_name=creator_user.full_name,
        )
    print(f'  Created {len(orders)} orders.')
else:
    print('  Orders already exist.')

if not Order.objects.filter(client_id=mobile_client_user.firebase_uid).exists():
    orders = [
        ('Startup Brand Kit', '3200', 'accepted', 'held'),
        ('Instagram Launch Pack', '2100', 'delivered', 'held'),
    ]
    for title, price, order_status, escrow_status in orders:
        Order.objects.create(
            client_id=mobile_client_user.firebase_uid,
            creator_id=mobile_creator_user.firebase_uid,
            service_title=title,
            price=price,
            status=order_status,
            escrow_status=escrow_status,
            client_name=mobile_client_user.full_name,
            creator_name=mobile_creator_user.full_name,
            due_date=timezone.make_aware(datetime.combine(datetime.today().date() + timedelta(days=5), time(hour=17))),
        )
    print(f'  Created {len(orders)} mobile demo orders.')
else:
    print('  Mobile demo orders already exist.')

print('\n[Integration Data]')
ensure_record(
    PaymentMethod,
    {'user_id': client_user.firebase_uid, 'masked_number': '0912 345 6789'},
    {'method_type': 'GCash'},
    '  Created client payment method.',
    '  Client payment method already exists.',
)
ensure_record(
    PaymentMethod,
    {'user_id': mobile_client_user.firebase_uid, 'masked_number': '0917 123 4567'},
    {'method_type': 'GCash'},
    '  Created mobile client payment method.',
    '  Mobile client payment method already exists.',
)
ensure_record(
    UserWallet,
    {'user_id': creator_user.firebase_uid, 'wallet_type': 'PayPal'},
    {'account_name': creator_user.full_name, 'account_number': 'creator@createch.com', 'is_active': True},
    '  Created creator wallet.',
    '  Creator wallet already exists.',
)
ensure_record(
    UserWallet,
    {'user_id': mobile_creator_user.firebase_uid, 'wallet_type': 'GCash'},
    {'account_name': mobile_creator_user.full_name, 'account_number': '09181234567', 'is_active': True},
    '  Created mobile creator wallet.',
    '  Mobile creator wallet already exists.',
)
ensure_record(
    Follow,
    {'follower_id': client_user.firebase_uid, 'following_id': creator_user.firebase_uid},
    {},
    '  Created follow relationship.',
    '  Follow relationship already exists.',
)
ensure_record(
    Follow,
    {'follower_id': mobile_client_user.firebase_uid, 'following_id': mobile_creator_user.firebase_uid},
    {},
    '  Created mobile follow relationship.',
    '  Mobile follow relationship already exists.',
)
ensure_record(
    Message,
    {'sender_id': client_user.firebase_uid, 'receiver_id': creator_user.firebase_uid, 'content': 'Hi, I would like to discuss a logo project.'},
    {'is_read': False},
    '  Created starter message.',
    '  Starter message already exists.',
)
ensure_record(
    Review,
    {'reviewer_id': client_user.firebase_uid, 'reviewee_id': creator_user.firebase_uid, 'comment': 'Fast turnaround and great communication.'},
    {'rating': 5},
    '  Created creator review.',
    '  Creator review already exists.',
)
ensure_record(
    Match,
    {'client_id': mobile_client_user.firebase_uid, 'creator_id': mobile_creator_user.firebase_uid},
    {
        'match_score': 94,
        'project_description': 'Branding support for a social launch campaign.',
        'reasons': ['branding', 'social media kit'],
        'status': 'new',
    },
    '  Created mobile match.',
    '  Mobile match already exists.',
)
ensure_record(
    DailyAnalytics,
    {'creator_id': creator_user.firebase_uid, 'date': date.today()},
    {'profile_views': 18, 'service_clicks': 7},
    '  Created creator analytics.',
    '  Creator analytics already exists.',
)
ensure_record(
    DailyAnalytics,
    {'creator_id': mobile_creator_user.firebase_uid, 'date': date.today()},
    {'profile_views': 24, 'service_clicks': 11},
    '  Created mobile creator analytics.',
    '  Mobile creator analytics already exists.',
)
ensure_record(
    SupportTicket,
    {'ticket_number': 'SUP-DEMO-001'},
    {
        'user_id': client_user.firebase_uid,
        'email': client_user.email,
        'category': 'general',
        'message': 'Need help with a completed order.',
        'status': 'open',
        'priority': 'normal',
        'user_role': client_user.role,
    },
    '  Created support ticket.',
    '  Support ticket already exists.',
)
ensure_record(
    Withdrawal,
    {'user_id': creator_user.firebase_uid, 'amount': '1500.00', 'method_type': 'PayPal'},
    {'status': 'completed', 'account_details': 'creator@createch.com'},
    '  Created withdrawal history.',
    '  Withdrawal history already exists.',
)

# ── Summary ───────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('Seeding complete!')
print('=' * 60)
print('\n--- Test accounts ---')
print('Admin:   admin@createch.com   / Admin@1234')
print('Creator: creator@createch.com / Creator@1234')
print('Client:  client@createch.com  / Client@1234')
print('Mobile client:  alex@createch.app  / password')
print('Mobile creator: maya@createch.app  / password')
print('Mobile admin:   admin@createch.app / password')
