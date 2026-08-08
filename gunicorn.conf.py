"""Gunicorn config tuned for a small always-on instance (512MB-1GB).

Sized for this store's traffic — a few hundred requests a day — where the goal
is a low, predictable memory footprint rather than throughput headroom.
Start with: gunicorn isha_return_gifts.wsgi -c gunicorn.conf.py
"""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Threads, not processes. Each worker process carries its own copy of Django
# (~60-80MB here); threads share it. This workload is I/O-bound — waiting on
# Postgres and on the Razorpay API — so threads cover concurrency fine and the
# GIL is not the constraint.
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = 'gthread'
threads = 4

# Recycle workers periodically so any slow leak can't accumulate on a small box.
# The jitter stops all workers restarting on the same request.
max_requests = 1000
max_requests_jitter = 100

# Long enough for a Razorpay API call plus the SMTP sends that still happen in
# the request path. Drop this to 30 once email moves to a background path.
timeout = 60
graceful_timeout = 30

# Keep connections open a little longer than the default 2s; most visitors load
# several pages and a proxy sits in front.
keepalive = 15

accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()

# Load the app before forking so workers share memory pages copy-on-write.
preload_app = True
