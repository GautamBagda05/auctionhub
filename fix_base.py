"""
Run this script from your project root to automatically replace base.html.
Usage: python fix_base.py
"""

content = r"""{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}AuctionHub{% endblock %}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />

  <style>
    :root {
      --bg:        #080b10;
      --bg2:       #0e1318;
      --bg3:       #141b23;
      --border:    rgba(255,255,255,0.07);
      --gold:      #c8992a;
      --gold2:     #e8b84b;
      --gold-dim:  rgba(200,153,42,0.15);
      --text:      #e8e2d5;
      --text-muted:#8a8070;
      --red:       #e05252;
      --green:     #4caf7d;
      --blue:      #4a90e2;
      --radius:    10px;
      --shadow:    0 8px 32px rgba(0,0,0,0.6);
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }

    /* ── Navbar ── */
    .navbar {
      position: sticky; top: 0; z-index: 100;
      background: rgba(8,11,16,0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      padding: 0 2rem;
      display: flex; align-items: center; justify-content: space-between;
      height: 64px;
    }
    .nav-brand {
      font-family: 'Cinzel', serif;
      font-size: 1.4rem; font-weight: 700;
      color: var(--gold2); text-decoration: none;
      letter-spacing: 0.04em;
      display: flex; align-items: center; gap: 10px;
    }
    .nav-brand .gavel { font-size: 1.2rem; }

    .nav-links { display: flex; align-items: center; gap: 0.25rem; }

    .nav-links a {
      color: var(--text-muted); text-decoration: none;
      padding: 6px 14px; border-radius: 6px;
      font-size: 0.875rem; font-weight: 500;
      transition: color 0.2s, background 0.2s;
      position: relative;
    }
    .nav-links a:hover { color: var(--text); background: var(--bg3); }

    /* Active highlight — gold glow + underline */
    .nav-links a.active {
      color: var(--gold2);
      background: var(--gold-dim);
    }
    .nav-links a.active::after {
      content: '';
      position: absolute;
      bottom: -1px; left: 50%; transform: translateX(-50%);
      width: 55%; height: 2px;
      background: var(--gold);
      border-radius: 2px;
    }

    .nav-links .btn-primary {
      background: var(--gold); color: #080b10;
      font-weight: 600; padding: 7px 18px; border-radius: 6px;
    }
    .nav-links .btn-primary:hover { background: var(--gold2); color: #080b10; }
    /* No underline on Join Free button */
    .nav-links .btn-primary::after { display: none !important; }

    /* ── Nav User Dropdown ── */
    .nav-user {
      position: relative; display: flex; align-items: center;
      padding-bottom: 10px; margin-bottom: -10px;
    }
    .nav-user-trigger {
      display: flex; align-items: center; gap: 8px;
      cursor: pointer; padding: 5px 10px; border-radius: 8px;
      transition: background 0.2s;
    }
    .nav-user:hover .nav-user-trigger { background: var(--bg3); }
    .nav-avatar {
      width: 34px; height: 34px; border-radius: 50%;
      background: var(--gold-dim); border: 1.5px solid var(--gold);
      display: flex; align-items: center; justify-content: center;
      font-size: 0.85rem; font-weight: 600; color: var(--gold);
      font-family: 'Cinzel', serif; flex-shrink: 0;
    }
    .nav-user-name { font-size: 0.875rem; color: var(--text-muted); }
    .nav-caret { font-size: 0.6rem; color: var(--text-muted); transition: transform 0.2s; }
    .nav-user:hover .nav-caret { transform: rotate(180deg); }

    .nav-dropdown-menu {
      display: none; position: absolute; top: 100%; right: 0;
      background: var(--bg2); border: 1px solid var(--border);
      border-radius: var(--radius); min-width: 190px;
      box-shadow: var(--shadow); overflow: hidden; z-index: 200;
    }
    .nav-user:hover .nav-dropdown-menu { display: block; }
    .nav-dropdown-menu a {
      display: flex; align-items: center; gap: 10px;
      padding: 11px 16px; color: var(--text-muted);
      text-decoration: none; font-size: 0.875rem;
      transition: background 0.2s, color 0.2s;
      position: static;
    }
    .nav-dropdown-menu a:hover { background: var(--bg3); color: var(--text); }
    .nav-dropdown-menu a::after { display: none !important; }
    .nav-dropdown-menu .dd-divider { height: 1px; background: var(--border); margin: 4px 0; }
    .nav-dropdown-menu .danger { color: var(--red) !important; }
    .nav-dropdown-menu .danger:hover { background: rgba(224,82,82,0.08) !important; color: var(--red) !important; }

    /* ── Toast ── */
    .messages-container {
      position: fixed; top: 76px; right: 1.5rem; z-index: 999;
      display: flex; flex-direction: column; gap: 8px; width: 340px;
    }
    .toast {
      background: var(--bg2); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 14px 18px;
      display: flex; align-items: center; gap: 12px;
      box-shadow: var(--shadow); animation: slideIn 0.3s ease; transition: opacity 0.4s;
    }
    .toast.success { border-left: 3px solid var(--green); }
    .toast.error   { border-left: 3px solid var(--red); }
    .toast.info    { border-left: 3px solid var(--blue); }
    .toast .icon   { font-size: 1.1rem; }
    .toast .msg    { font-size: 0.875rem; flex: 1; }
    .toast .close-toast { cursor: pointer; color: var(--text-muted); font-size: 1rem; padding: 2px; }
    @keyframes slideIn { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

    /* ── Layout ── */
    .container { max-width: 1240px; margin: 0 auto; padding: 0 1.5rem; }
    .page-pad  { padding-top: 2.5rem; padding-bottom: 4rem; }

    .card {
      background: var(--bg2); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      transition: border-color 0.2s, transform 0.2s;
    }
    .card:hover { border-color: rgba(200,153,42,0.3); transform: translateY(-2px); }

    /* ── Auction Card ── */
    .auction-card { display: flex; flex-direction: column; }
    .auction-card .img-wrap { height: 200px; overflow: hidden; background: var(--bg3); position: relative; }
    .auction-card .img-wrap img { width: 100%; height: 100%; object-fit: cover; }
    .auction-card .img-placeholder {
      width: 100%; height: 100%; display: flex;
      align-items: center; justify-content: center;
      font-size: 3rem; color: var(--text-muted);
    }
    .auction-card .badge {
      position: absolute; top: 10px; left: 10px;
      background: var(--gold); color: #080b10;
      font-size: 0.7rem; font-weight: 700; padding: 3px 8px;
      border-radius: 4px; font-family: 'DM Mono', monospace;
      text-transform: uppercase; letter-spacing: 0.05em;
    }
    .auction-card .badge.ended { background: var(--text-muted); }
    .auction-card .body { padding: 1rem 1.25rem; flex: 1; display: flex; flex-direction: column; gap: 8px; }
    .auction-card .cat { font-size: 0.7rem; color: var(--gold); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .auction-card .title {
      font-family: 'Cinzel', serif; font-size: 1rem; font-weight: 600;
      color: var(--text); line-height: 1.3;
      display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2;
      -webkit-box-orient: vertical; overflow: hidden;
    }
    .auction-card .bid-row {
      display: flex; justify-content: space-between; align-items: flex-end;
      margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border);
    }
    .auction-card .bid-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .auction-card .bid-amount { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--gold2); font-weight: 600; }
    .auction-card .time-left { font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
    .auction-card .time-left.urgent { color: var(--red); }

    .grid-3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.25rem; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; }

    .btn {
      display: inline-flex; align-items: center; gap: 7px;
      padding: 9px 20px; border-radius: 7px; font-size: 0.875rem;
      font-weight: 600; cursor: pointer; border: none;
      text-decoration: none; transition: all 0.2s; font-family: 'DM Sans', sans-serif;
    }
    .btn-gold    { background: var(--gold); color: #080b10; }
    .btn-gold:hover { background: var(--gold2); }
    .btn-outline { background: transparent; color: var(--text); border: 1px solid var(--border); }
    .btn-outline:hover { border-color: var(--gold); color: var(--gold); }
    .btn-ghost   { background: var(--bg3); color: var(--text-muted); }
    .btn-ghost:hover { color: var(--text); }
    .btn-danger  { background: var(--red); color: #fff; }
    .btn-sm      { padding: 6px 14px; font-size: 0.8rem; }
    .btn-lg      { padding: 13px 32px; font-size: 1rem; }
    .btn-block   { width: 100%; justify-content: center; }

    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .form-control {
      background: var(--bg3); border: 1px solid var(--border);
      color: var(--text); border-radius: 7px; padding: 10px 14px;
      font-size: 0.9rem; font-family: 'DM Sans', sans-serif;
      width: 100%; transition: border-color 0.2s; outline: none;
    }
    .form-control:focus { border-color: var(--gold); }
    .form-control::placeholder { color: var(--text-muted); }
    textarea.form-control { resize: vertical; min-height: 100px; }
    select.form-control { appearance: none; cursor: pointer; }
    .form-error { font-size: 0.78rem; color: var(--red); margin-top: 2px; }

    .section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 1.5rem; }
    .section-head h2 { font-family: 'Cinzel', serif; font-size: 1.5rem; font-weight: 700; color: var(--text); }
    .section-head .see-all { font-size: 0.85rem; color: var(--gold); text-decoration: none; }
    .section-head .see-all:hover { text-decoration: underline; }

    .divider { height: 1px; background: var(--border); margin: 1.5rem 0; }

    table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    th { text-align: left; padding: 10px 14px; color: var(--text-muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border); }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border); color: var(--text); }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255,255,255,0.02); }

    .pill { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
    .pill-active  { background: rgba(76,175,125,0.15); color: var(--green); }
    .pill-ended   { background: rgba(138,128,112,0.15); color: var(--text-muted); }
    .pill-pending { background: rgba(74,144,226,0.15); color: var(--blue); }
    .pill-done    { background: rgba(76,175,125,0.15); color: var(--green); }

    footer {
      border-top: 1px solid var(--border); padding: 2rem 1.5rem;
      text-align: center; color: var(--text-muted); font-size: 0.82rem; margin-top: auto;
    }
    footer a { color: var(--gold); text-decoration: none; }

    @media (max-width: 768px) {
      .navbar { padding: 0 1rem; }
      .nav-links { gap: 0; }
      .nav-links a { padding: 6px 10px; font-size: 0.82rem; }
      .nav-user-name { display: none; }
      .grid-3, .grid-4, .grid-2 { grid-template-columns: 1fr; }
    }
  </style>

  {% block extra_head %}{% endblock %}
</head>
<body>

<nav class="navbar">
  <a class="nav-brand" href="{% url 'home' %}">
    <span class="gavel">&#128296;</span> AuctionHub
  </a>

  <div class="nav-links">

    <a href="{% url 'home' %}"
       class="{% if request.resolver_match.url_name == 'home' %}active{% endif %}">
      &#127968; Home
    </a>

    <a href="{% url 'auction_list' %}"
       class="{% if request.resolver_match.url_name == 'auction_list' %}active{% endif %}">
      Browse
    </a>

    {% if user.is_authenticated %}

      {% if user.profile.role == 'seller' or user.is_staff %}
        <a href="{% url 'create_auction' %}"
           class="{% if request.resolver_match.url_name == 'create_auction' %}active{% endif %}">
          + List Item
        </a>
      {% endif %}

      <a href="{% url 'dashboard' %}"
         class="{% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}">
        Dashboard
      </a>

      <div class="nav-user">
        <div class="nav-user-trigger">
          <div class="nav-avatar">{{ user.username|first|upper }}</div>
          <span class="nav-user-name">{{ user.first_name|default:user.username }}</span>
          <span class="nav-caret">&#9660;</span>
        </div>
        <div class="nav-dropdown-menu">
          <a href="{% url 'profile' %}">&#9881; Profile</a>
          <a href="{% url 'dashboard' %}">&#128202; Dashboard</a>
          <div class="dd-divider"></div>
          <a href="{% url 'logout' %}" class="danger">&#8617; Sign Out</a>
        </div>
      </div>

    {% else %}

      <a href="{% url 'login' %}"
         class="{% if request.resolver_match.url_name == 'login' %}active{% endif %}">
        Sign In
      </a>
      <a href="{% url 'signup' %}" class="btn-primary">Join Free</a>

    {% endif %}

  </div>
</nav>

{% if messages %}
<div class="messages-container" id="toastContainer">
  {% for msg in messages %}
  <div class="toast {% if msg.tags == 'error' %}error{% elif msg.tags == 'success' %}success{% else %}info{% endif %}">
    <span class="icon">{% if msg.tags == 'error' %}&#10005;{% elif msg.tags == 'success' %}&#10003;{% else %}&#8505;{% endif %}</span>
    <span class="msg">{{ msg }}</span>
    <span class="close-toast" onclick="this.parentElement.remove()">&#10005;</span>
  </div>
  {% endfor %}
</div>
<script>
  setTimeout(function() {
    document.querySelectorAll('.toast').forEach(function(t) { t.style.opacity = '0'; });
    setTimeout(function() { var c = document.getElementById('toastContainer'); if (c) c.remove(); }, 400);
  }, 4000);
</script>
{% endif %}

<main>
  {% block content %}{% endblock %}
</main>

<footer>
  <p>&copy; 2025 <a href="/">AuctionHub</a> &middot; Built with Django &amp; Channels &middot; All Rights Reserved</p>
</footer>

{% block extra_js %}{% endblock %}
</body>
</html>"""

import os

target = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates', 'base.html'
)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"SUCCESS: base.html written to {target}")
print("Restart your Django server now.")