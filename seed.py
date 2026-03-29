"""
Seed script: creates admin superuser + sample creator user + sample data.
Run from project root:
    venv\Scripts\python.exe seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'createch.settings')
django.setup()

from marketplace.models import User, Service, Order, Project, WalletTransaction

# --- Superuser (admin)
if not User.objects.filter(email='admin@createch.com').exists():
    admin = User.objects.create_superuser(
        email='admin@createch.com',
        password='Admin@1234',
        first_name='Admin',
        last_name='Createch',
    )
    print(f'Created superuser: {admin.email}')
else:
    admin = User.objects.get(email='admin@createch.com')
    print(f'Superuser already exists: {admin.email}')

# --- Creator user
if not User.objects.filter(email='creator@createch.com').exists():
    creator = User.objects.create_user(
        email='creator@createch.com',
        password='Creator@1234',
        first_name='Juan',
        last_name='Dela Cruz',
        phone='09123456789',
        role='creator',
        is_verified=True,
        wallet_balance=1500.00,
    )
    print(f'Created creator: {creator.email}')
else:
    creator = User.objects.get(email='creator@createch.com')
    print(f'Creator already exists: {creator.email}')

# --- Client user
if not User.objects.filter(email='client@createch.com').exists():
    client = User.objects.create_user(
        email='client@createch.com',
        password='Client@1234',
        first_name='Maria',
        last_name='Santos',
        phone='09987654321',
        role='client',
        is_verified=True,
        wallet_balance=5000.00,
    )
    print(f'Created client: {client.email}')
else:
    client = User.objects.get(email='client@createch.com')
    print(f'Client already exists: {client.email}')

# --- Services
if not Service.objects.exists():
    s1 = Service.objects.create(
        creator=creator,
        title='Professional Logo Design',
        description='I will design a modern, professional logo for your business.',
        price=2500.00,
        category='design',
        delivery_days=5,
    )
    s2 = Service.objects.create(
        creator=creator,
        title='Social Media Assets Pack',
        description='Complete set of social media banners, posts, and story templates.',
        price=1500.00,
        category='design',
        delivery_days=3,
    )
    s3 = Service.objects.create(
        creator=creator,
        title='Website Mockup (Figma)',
        description='High-fidelity Figma mockup for your website — desktop and mobile.',
        price=7500.00,
        category='design',
        delivery_days=7,
    )
    print('Created 3 sample services.')

# --- Orders
if not Order.objects.exists():
    Order.objects.create(
        client=client,
        creator=creator,
        service_title='Professional Logo Design',
        price=2500.00,
        status='completed',
        requirements='We need a blue/gold color scheme, modern style.',
    )
    Order.objects.create(
        client=client,
        creator=creator,
        service_title='Website Mockup (Figma)',
        price=7500.00,
        status='pending',
        requirements='E-commerce site for clothing brand.',
    )
    Order.objects.create(
        client=client,
        creator=creator,
        service_title='Social Media Assets Pack',
        price=1500.00,
        status='in_progress',
        requirements='For Instagram and Facebook.',
    )
    print('Created 3 sample orders.')

# --- Projects
if not Project.objects.exists():
    Project.objects.create(
        creator=creator,
        title='Acme Corp Rebrand',
        client_name='Acme Corporation',
        status='In Progress',
        budget=15000.00,
        description='Full brand identity redesign including logo, colors, and typography.',
    )
    Project.objects.create(
        creator=creator,
        title='Santos E-Commerce Site',
        client_name='Maria Santos',
        status='Pending',
        budget=25000.00,
        description='Online store for handmade crafts.',
    )
    Project.objects.create(
        creator=creator,
        title='Dela Cruz Photography Portfolio',
        client_name='Lito Dela Cruz',
        status='Completed',
        budget=8000.00,
        description='Portfolio website for a professional photographer.',
    )
    print('Created 3 sample projects.')

# --- Wallet transactions
if not WalletTransaction.objects.exists():
    WalletTransaction.objects.create(
        user=creator,
        transaction_type='earning',
        amount=2500.00,
        description='Payment for Professional Logo Design',
    )
    WalletTransaction.objects.create(
        user=client,
        transaction_type='deposit',
        amount=5000.00,
        description='Initial wallet top-up',
    )
    WalletTransaction.objects.create(
        user=client,
        transaction_type='payment',
        amount=2500.00,
        description='Payment for Professional Logo Design',
    )
    print('Created 3 sample wallet transactions.')

print('\nSeeding complete!')
print('--- Test accounts ---')
print('Admin:   admin@createch.com   / Admin@1234')
print('Creator: creator@createch.com / Creator@1234')
print('Client:  client@createch.com  / Client@1234')
