"""
Seed script: creates sample users with auth credentials + sample data.
Run from project root:
    venv\Scripts\python.exe seed.py
"""
import os
import uuid

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'createch.settings')
django.setup()

from django.contrib.auth.hashers import make_password

from marketplace.models import (
    AuthCredential, Category, Creator, Order, Service, User,
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

# ── Creator profile ───────────────────────────────────────────────────────
print('\n[Creator Profile]')
if not Creator.objects.filter(user_id=creator_user.firebase_uid).exists():
    Creator.objects.create(
        user_id=creator_user.firebase_uid,
        bio='Professional graphic designer with 5 years of experience.',
        skills='{logo design,branding,web design}',
        experience_years='5',
        starting_price='1500',
        turnaround_time='3-5 days',
        verification_status='verified',
    )
    print('  Created creator profile.')
else:
    print('  Creator profile already exists.')

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

# ── Summary ───────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('Seeding complete!')
print('=' * 60)
print('\n--- Test accounts ---')
print('Admin:   admin@createch.com   / Admin@1234')
print('Creator: creator@createch.com / Creator@1234')
print('Client:  client@createch.com  / Client@1234')
