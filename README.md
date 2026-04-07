# AuctionHub — Online Auction System
## Django + PostgreSQL + WebSockets (Channels) + Razorpay

---

## Project Structure

```
auctionhub/
├── auctionhub/               ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py               ← Channels ASGI entry point
│   └── wsgi.py
├── core/                     ← Auth, users, home
│   ├── models.py             (UserProfile)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── signals.py
│   └── apps.py
├── auction/                  ← Auction logic
│   ├── models.py             (Auction, Bid, Payment, Watchlist)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── consumers.py          ← WebSocket consumer
│   ├── routing.py
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── core/
│   │   ├── home.html
│   │   ├── login.html
│   │   └── signup.html
│   ├── auction/
│   │   ├── auction_list.html
│   │   ├── auction_detail.html   ← Live WebSocket bidding
│   │   ├── create_auction.html
│   │   └── payment.html          ← Razorpay checkout
│   └── profile/
│       ├── profile.html
│       ├── seller/dashboard.html
│       ├── buyer/dashboard.html
│       └── admin/dashboard.html
├── static/
├── media/
├── manage.py
└── requirements.txt
```

---

## Quick Setup

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
```sql
-- In psql:
CREATE DATABASE auctionhub;
CREATE USER auctionhub_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE auctionhub TO auctionhub_user;
```

### 4. Configure environment variables
Create a `.env` file or export these variables:
```bash
export DB_NAME=auctionhub
export DB_USER=auctionhub_user
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=5432

# Get these from https://dashboard.razorpay.com → Settings → API Keys
export RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
export RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Run migrations
```bash
cd auctionhub
python manage.py makemigrations core
python manage.py makemigrations auction
python manage.py migrate
```

### 6. Create superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
# Daphne serves both HTTP and WebSocket:
daphne -p 8000 auctionhub.asgi:application

# Or standard Django (no WebSocket):
python manage.py runserver
```

Open → http://127.0.0.1:8000

---

## URL Map

| URL                        | Description                        |
|----------------------------|------------------------------------|
| `/`                        | Home page with featured auctions   |
| `/login/`                  | Sign in                            |
| `/signup/`                 | Create account (buyer or seller)   |
| `/logout/`                 | Sign out                           |
| `/dashboard/`              | Role-specific dashboard            |
| `/profile/`                | Edit profile                       |
| `/auction/`                | Browse all auctions                |
| `/auction/<id>/`           | Auction detail + live bidding      |
| `/auction/create/`         | Create new auction (sellers only)  |
| `/auction/<id>/edit/`      | Edit auction (seller only)         |
| `/auction/<id>/pay/`       | Razorpay payment (winners only)    |
| `/auction/<id>/watch/`     | Toggle watchlist (AJAX)            |
| `/auction/<id>/updates/`   | JSON polling fallback              |
| `ws://…/ws/auction/<id>/`  | WebSocket live bid stream          |
| `/admin/`                  | Django admin panel                 |

---

## WebSocket Architecture

```
Browser ──── ws://host/ws/auction/<id>/ ────► AuctionConsumer
                                                    │
                                    channels.layers.group_send()
                                                    │
                                    All connected browsers ◄───
```

- Uses **InMemoryChannelLayer** for development (zero config).
- Switch to **RedisChannelLayer** for production multi-process deployments.

---

## Razorpay Integration

1. Sign up at https://dashboard.razorpay.com
2. Go to Settings → API Keys → Generate Test Key
3. Copy **Key ID** and **Key Secret** into env variables
4. For real payments, switch to Live keys and enable your bank account

---

## Production Checklist

- [ ] Set `DEBUG=False` in settings
- [ ] Change `SECRET_KEY` to a random 50-char string
- [ ] Use **Redis** channel layer (`channels-redis`)
- [ ] Set up **Nginx** as reverse proxy + **Daphne** for ASGI
- [ ] Enable **SSL/TLS** (Razorpay requires HTTPS for live)
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Configure `STATIC_ROOT` and run `collectstatic`
- [ ] Use environment variables for all secrets
