import os
import uuid
import re
import requests as http_requests
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import markdown
from dotenv import load_dotenv
from openai import OpenAI
from pytrends.request import TrendReq

import smtplib
from email.mime.text import MIMEText

# ── Load environment ────────────────────────────────────
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
CONTACT_RECEIVER_EMAIL = os.getenv("CONTACT_RECEIVER_EMAIL")
MAIL_FROM = os.getenv("MAIL_FROM", SMTP_USERNAME)

# ── Login rate limiting ──────────────────────────────────
# Simple in-memory tracker: blocks an IP after too many failed admin
# login attempts within a time window. Note: this state lives in a
# single process's memory — if gunicorn runs with more than one worker,
# each worker tracks attempts separately, so this is a first line of
# defense, not a hard guarantee. Fine for a low-traffic single-admin site.
from collections import defaultdict
import time as _time

LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 15 * 60  # 15 minutes
_login_attempts = defaultdict(list)  # ip -> [timestamps of recent failures]

def _get_client_ip():
    # Railway sits behind a proxy; prefer X-Forwarded-For's first entry when present.
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"

def _is_login_locked(ip):
    now = _time.time()
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < LOGIN_WINDOW_SECONDS]
    return len(_login_attempts[ip]) >= LOGIN_MAX_ATTEMPTS

def _record_failed_login(ip):
    _login_attempts[ip].append(_time.time())

def _clear_login_attempts(ip):
    _login_attempts.pop(ip, None)

# ── Flask app ───────────────────────────────────────────
app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Generate one with "
        "`python -c \"import secrets; print(secrets.token_hex(32))\"` "
        "and add it to your .env file before starting the server."
    )
app.secret_key = SECRET_KEY

# ── Custom slug filter (for TOC links) ────────────────
def custom_slugify(value, separator='-'):
    """Convert a string to a URL-friendly slug."""
    value = value.lower().strip()
    value = re.sub(r'[^\w\s-]', '', value)   # remove non-word chars except spaces/dashes
    value = re.sub(r'[\s_]+', separator, value)     # replace spaces/underscores with the given separator
    value = re.sub(r'{}+'.format(re.escape(separator)), separator, value)  # collapse multiple separators
    return value

app.jinja_env.filters['slugify'] = custom_slugify

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year, "now": datetime.now()}

# ── Content folders ─────────────────────────────────────
BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / "content" / "articles"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Admin credentials ────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_USERNAME and ADMIN_PASSWORD must be set in your .env file. "
        "Do not use the old admin/admin123 defaults — anyone could log in "
        "and edit or delete your content."
    )

# ── GitHub Models client ────────────────────────────────
def get_models_client():
    if not GITHUB_TOKEN:
        return None
    return OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=GITHUB_TOKEN,
    )

# ── Markdown to HTML ────────────────────────────────────
def md_to_html(text):
    return markdown.markdown(
        text,
        extensions=['extra', 'codehilite'],
        slugify=custom_slugify
    )

def extract_headings(markdown_text):
    """Return a clean list of H2 headings for the TOC, without Markdown formatting or leading numbers."""
    headings = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        # Only capture "## " lines, not "### "
        if stripped.startswith("## ") and not stripped.startswith("### "):
            heading = stripped[3:].strip()
            # Remove Markdown bold/italic markers
            heading = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading)
            heading = re.sub(r'\*([^*]+)\*', r'\1', heading)
            heading = re.sub(r'__([^_]+)__', r'\1', heading)
            heading = re.sub(r'_([^_]+)_', r'\1', heading)
            # Remove leading numbers like "1. ", "2. " etc.
            heading = re.sub(r'^\d+\.\s+', '', heading)
            heading = heading.strip()
            if heading:
                headings.append(heading)
    return headings

def clean_excerpt(text):
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = text.replace('**', '').replace('__', '')
    text = text.replace('*', '').replace('_', '')
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    text = text.replace('`', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def list_articles():
    articles = []
    for f in sorted(ARTICLES_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        articles.append({
            "slug": f.stem,
            "path": f,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "size": f.stat().st_size,
        })
    return articles

def parse_front_matter(raw):
    meta = {}
    content = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key, val = key.strip().lower(), val.strip()
                    meta[key] = val
            content = parts[2].strip()
    return meta, content

def format_front_matter(meta):
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"

def load_article(slug):
    file = ARTICLES_DIR / f"{slug}.md"
    if not file.exists():
        return None
    raw = file.read_text(encoding="utf-8")
    meta, content = parse_front_matter(raw)
    meta["slug"] = slug
    meta["raw"] = raw
    meta["content"] = content
    return meta

def save_article(slug, meta, content):
    file = ARTICLES_DIR / f"{slug}.md"
    full = format_front_matter(meta) + content
    file.write_text(full, encoding="utf-8")

def get_all_articles_sorted():
    articles = []
    for f in sorted(ARTICLES_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta, content = parse_front_matter(raw)
        excerpt = clean_excerpt(content)[:200]
        if len(content) > 200:
            excerpt += "…"
        author = meta.get("author", "").strip()
        if not author:
            author = "Blogsphere"
        # Safe int parsing — falls back to 0 if missing/invalid (older articles)
        try:
            img_w = int(meta.get("featured_image_width", 0) or 0)
        except (ValueError, TypeError):
            img_w = 0
        try:
            img_h = int(meta.get("featured_image_height", 0) or 0)
        except (ValueError, TypeError):
            img_h = 0
        articles.append({
            "slug": f.stem,
            "title": meta.get("title", f.stem.replace("-", " ").title()),
            "category": meta.get("category", "General"),
            "author": author,
            "author_initial": author[0].upper(),
            "date": meta.get("date", datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")),
            "read_time": meta.get("read_time", "5"),
            "excerpt": excerpt,
            "featured_image": meta.get("featured_image", ""),
            "featured_image_width": img_w,
            "featured_image_height": img_h,
            "featured": meta.get("featured", "").lower() == "true",
        })
    return articles

def get_featured_article(articles):
    for article in articles:
        if article.get("featured"):
            return article
    return articles[0] if articles else None

def get_trending_articles(articles, featured_slug, count=5):
    trending = [a for a in articles if a["slug"] != featured_slug]
    return trending[:count]

def get_featured_categories(categories=None, count=4):
    """Return a list of dicts with category name, latest article image and slug."""
    if categories is None:
        categories = ["Technology", "Design", "Finance", "Health"]
    all_articles = get_all_articles_sorted()
    result = []
    for cat in categories:
        article = next((a for a in all_articles if a["category"].lower() == cat.lower()), None)
        result.append({
            "category": cat,
            "image": article["featured_image"] if article and article.get("featured_image") else None,
            "slug": article["slug"] if article else None,
        })
        if len(result) >= count:
            break
    return result

def get_related_articles(current_slug, current_category, limit=4):
    """Return up to `limit` articles in the same category, falling back to recent articles."""
    all_articles = get_all_articles_sorted()
    same_cat = [a for a in all_articles
                if a["slug"] != current_slug and a["category"].lower() == current_category.lower()]
    if len(same_cat) >= limit:
        return same_cat[:limit]
    seen = {a["slug"] for a in same_cat}
    others = [a for a in all_articles if a["slug"] != current_slug and a["slug"] not in seen]
    return (same_cat + others)[:limit]

# ── Admin decorator ─────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ── Trending topics (Google Trends) ─────────────────────
def get_trending_topics(niche="technology", count=8):
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(kw_list=[niche], timeframe='today 3-m')
        related = pytrends.related_queries()
        rising = related.get(niche, {}).get('rising', None)
        if rising is not None and not rising.empty:
            return rising.head(count)['query'].tolist()
        top = related.get(niche, {}).get('top', None)
        if top is not None and not top.empty:
            return top.head(count)['query'].tolist()
    except Exception as e:
        print(f"Trends error: {e}")
    return [
        "AI in everyday life",
        "Minimalist design trends",
        "Productivity hacks",
        "Future of remote work",
        "Climate tech innovations",
        "Personal finance basics",
        "Deep focus techniques",
        "Second brain methodology"
    ]

# ══════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/")
def home():
    all_articles = get_all_articles_sorted()
    carousel_articles = all_articles[:5]
    featured = carousel_articles[0] if carousel_articles else None
    trending = get_trending_articles(all_articles, featured["slug"] if featured else None, count=5) if all_articles else []
    remaining = [a for a in all_articles if a != featured] if featured else []
    initial_articles = remaining[:8]
    total_remaining = len(remaining)
    featured_cats = get_featured_categories()

    return render_template("home.html",
                           carousel_articles=carousel_articles,
                           featured=featured,
                           trending=trending,
                           articles=initial_articles,
                           total_articles=total_remaining,
                           featured_cats=featured_cats)

@app.route("/articles")
def articles_listing():
    return render_template("articles.html", articles=get_all_articles_sorted())

@app.route("/article/<slug>")
def article(slug):
    data = load_article(slug)
    if not data:
        abort(404)
    title = data.get("title", slug.replace("-", " ").title())
    category = data.get("category", "General")
    author_name = data.get("author", "BlogSphere")
    author_bio = data.get("author_bio", "A curious mind writing about the things that matter.")
    read_time = int(data.get("read_time", 5))
    publish_date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    tags = [t.strip() for t in data.get("tags", "").split(",") if t.strip()]
    content_html = md_to_html(data["content"])
    headings = extract_headings(data["content"])
    featured_image = data.get("featured_image", "")
    try:
        featured_image_width = int(data.get("featured_image_width", 0) or 0)
    except (ValueError, TypeError):
        featured_image_width = 0
    try:
        featured_image_height = int(data.get("featured_image_height", 0) or 0)
    except (ValueError, TypeError):
        featured_image_height = 0
    # Build excerpt for meta tags — first 160 chars of body text
    import re as _re
    raw_text = _re.sub(r'<[^>]+>', '', md_to_html(data["content"][:600]))
    article_excerpt = raw_text.strip()[:160].rsplit(' ', 1)[0] + '…' if len(raw_text) > 160 else raw_text.strip()
    related = get_related_articles(slug, category)
    return render_template("article.html", article_title=title, article_category=category,
                           author_name=author_name, author_initial=author_name[0].upper() if author_name else "B",
                           author_bio=author_bio, publish_date=publish_date, read_time=read_time,
                           tags=tags, content=content_html, headings=headings, featured_image=featured_image,
                           featured_image_width=featured_image_width, featured_image_height=featured_image_height,
                           article_excerpt=article_excerpt,
                           related_articles=related)

@app.route("/about")
def about():
    return render_template("about.html")

def send_contact_email(name, email, subject, message):
    body = f"From: {name} <{email}>\n\n{message}"
    msg = MIMEText(body)
    msg["Subject"] = f"[Contact Form] {subject}"
    msg["From"] = MAIL_FROM
    msg["To"] = CONTACT_RECEIVER_EMAIL
    msg["Reply-To"] = email  # so hitting "reply" goes to the visitor, not yourself

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(MAIL_FROM, [CONTACT_RECEIVER_EMAIL], msg.as_string())

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and subject and message:
            try:
                send_contact_email(name, email, subject, message)
                flash("Message sent! We will get back to you within two business days.", "contact_success")
            except Exception as e:
                app.logger.error(f"Contact form email failed: {e}")
                flash("Sorry, something went wrong sending your message. Please try again later.", "contact_danger")
        else:
            flash("Please fill in all required fields.", "contact_danger")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    from datetime import datetime
    return render_template("privacy.html", now=datetime.utcnow())

@app.route("/terms")
def terms():
    from datetime import datetime
    return render_template("terms.html", now=datetime.utcnow())

@app.route("/disclaimer")
def disclaimer():
    from datetime import datetime
    return render_template("disclaimer.html", now=datetime.utcnow())

@app.route("/cookies")
def cookies():
    from datetime import datetime
    return render_template("cookies.html", now=datetime.utcnow())

@app.route("/category/<category_name>")
def category_page(category_name):
    all_articles = get_all_articles_sorted()
    # Case-insensitive match, preserve original casing from first match
    matched = [a for a in all_articles if a["category"].lower() == category_name.lower()]
    if not matched:
        abort(404)
    # Use the category name as stored in articles (preserves capitalisation)
    canonical_name = matched[0]["category"]
    # Related categories (other categories that have articles)
    all_cats = list(dict.fromkeys(
        a["category"] for a in all_articles
        if a["category"].lower() != category_name.lower()
    ))
    return render_template("category.html",
        category=canonical_name,
        articles=matched,
        total=len(matched),
        other_categories=all_cats[:8],
    )

# ── AJAX Endpoints ────

@app.route("/api/articles")
def api_articles():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 8, type=int)
    category = request.args.get("category", "").strip()

    all_articles = get_all_articles_sorted()

    # When no category filter, exclude the first article (used as hero/featured)
    # so the grid matches what the server initially rendered
    if not category and all_articles:
        all_articles = all_articles[1:]

    if category:
        filtered = [a for a in all_articles if a["category"].lower() == category.lower()]
    else:
        filtered = all_articles

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    page_articles = filtered[start:end]

    return jsonify({
        "articles": page_articles,
        "has_next": end < total,
        "page": page,
        "total": total,
    })

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])

    results = []
    for f in sorted(ARTICLES_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta, content = parse_front_matter(raw)

        title = meta.get("title", f.stem.replace("-", " ").title()).lower()
        slug = f.stem.lower()
        body = content.lower()

        score = 0
        if q in title: score += 3
        if q in slug: score += 2
        if q in body: score += 1

        if score > 0:
            excerpt = clean_excerpt(content)[:100]
            results.append({
                "slug": f.stem,
                "title": meta.get("title", f.stem.replace("-", " ").title()),
                "excerpt": excerpt,
                "category": meta.get("category", "General"),
                "date": meta.get("date", ""),
                "featured_image": meta.get("featured_image", ""),
                "score": score,
            })

    results.sort(key=lambda x: (-x["score"], x["date"]), reverse=True)
    results = results[:5]
    for r in results: del r["score"]
    return jsonify(results)

# ══════════════════════════════════════════════════════════
# ADMIN ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/admin")
@admin_required
def admin_dashboard():
    articles = list_articles()
    all_summaries = get_all_articles_sorted()
    image_count = len(list(UPLOAD_FOLDER.glob("*.*"))) if UPLOAD_FOLDER.exists() else 0
    stats = {
        "total_articles": len(articles),
        "total_images": image_count,
        "recent_articles": all_summaries,  # full list so table & category bars have real data
    }
    return render_template("admin/dashboard.html", articles=articles, stats=stats)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        client_ip = _get_client_ip()

        if _is_login_locked(client_ip):
            flash("Too many failed login attempts. Please try again in 15 minutes.", "danger")
            return render_template("admin/login.html")

        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            _clear_login_attempts(client_ip)
            session["admin_logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            _record_failed_login(client_ip)
            remaining = LOGIN_MAX_ATTEMPTS - len(_login_attempts[client_ip])
            if remaining > 0:
                flash(f"Invalid credentials. {remaining} attempt(s) remaining before temporary lockout.", "danger")
            else:
                flash("Too many failed login attempts. Please try again in 15 minutes.", "danger")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin/new")
@admin_required
def admin_new_article():
    return render_template("admin/editor.html", article=None, mode="new")

@app.route("/admin/edit/<slug>")
@admin_required
def admin_edit(slug):
    article = load_article(slug)
    if not article:
        flash("Article not found.", "danger")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/editor.html", article=article, mode="edit")

@app.route("/admin/save", methods=["POST"])
@admin_required
def admin_save():
    slug = request.form.get("slug", "").strip()
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "General").strip()
    author = request.form.get("author", "Admin").strip()
    author_bio = request.form.get("author_bio", "").strip()
    date = request.form.get("date", datetime.now().strftime("%Y-%m-%d")).strip()
    read_time = request.form.get("read_time", "5").strip()
    tags = request.form.get("tags", "").strip()
    content = request.form.get("content", "")
    featured_image = request.form.get("featured_image", "").strip()
    featured_image_width = request.form.get("featured_image_width", "").strip()
    featured_image_height = request.form.get("featured_image_height", "").strip()

    if not slug:
        if title:
            slug = title.lower().replace(" ", "-").replace("'", "")
        else:
            slug = f"article-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    if not slug:
        slug = "untitled"

    meta = {
        "title": title or "Untitled",
        "category": category,
        "author": author,
        "author_bio": author_bio,
        "date": date,
        "read_time": read_time,
        "tags": tags,
        "featured_image": featured_image,
        "featured_image_width": featured_image_width,
        "featured_image_height": featured_image_height,
    }
    save_article(slug, meta, content)
    flash("Article saved successfully.", "success")
    return redirect(url_for("admin_edit", slug=slug))

@app.route("/admin/delete/<slug>")
@admin_required
def admin_delete(slug):
    file = ARTICLES_DIR / f"{slug}.md"
    if file.exists():
        file.unlink()
        flash("Article deleted.", "info")
    return redirect(url_for("admin_dashboard"))

# ── Image Management ────────────────────────────────────
def process_and_save_image(file_obj, original_name):
    """
    Save an uploaded image as WebP (quality 85) for best compression.
    Falls back to original format if Pillow unavailable or conversion fails.
    Returns (unique_name, width, height, url).
    """
    try:
        from PIL import Image as PilImage
        img = PilImage.open(file_obj)

        # Convert RGBA/P to RGB for JPEG-family formats
        if img.mode in ('RGBA', 'P', 'LA'):
            bg = PilImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size

        # Cap maximum dimension at 1800px to save storage
        max_dim = 1800
        if width > max_dim or height > max_dim:
            img.thumbnail((max_dim, max_dim), PilImage.LANCZOS)
            width, height = img.size

        unique_name = f"{uuid.uuid4().hex}.webp"
        save_path = UPLOAD_FOLDER / unique_name
        img.save(save_path, 'WEBP', quality=85, method=6)

    except Exception:
        # Pillow unavailable or conversion failed — save original
        file_obj.seek(0)
        ext = secure_filename(original_name).rsplit('.', 1)[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = UPLOAD_FOLDER / unique_name
        file_obj.save(save_path)
        try:
            from PIL import Image as PilImage
            with PilImage.open(save_path) as im:
                width, height = im.size
        except Exception:
            width, height = 0, 0

    image_url = url_for('static', filename=f'uploads/{unique_name}')
    return unique_name, width, height, image_url


@app.route("/admin/list-images")
@admin_required
def list_images():
    images = []
    for f in sorted(UPLOAD_FOLDER.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.suffix.lower().lstrip('.') in ALLOWED_EXTENSIONS | {'webp'}:
            try:
                from PIL import Image as PilImage
                with PilImage.open(f) as im:
                    w, h = im.size
            except Exception:
                w, h = 0, 0
            images.append({
                "filename": f.name,
                "url": url_for('static', filename=f'uploads/{f.name}'),
                "size": f.stat().st_size,
                "width": w,
                "height": h,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
    return jsonify(images)

@app.route("/admin/delete-image", methods=["POST"])
@admin_required
def delete_image():
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    file_path = UPLOAD_FOLDER / secure_filename(filename)
    if file_path.exists():
        file_path.unlink()
        return jsonify({"success": True})
    return jsonify({"error": "File not found"}), 404

@app.route("/admin/upload-image", methods=["POST"])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    _, width, height, image_url = process_and_save_image(file, file.filename)
    return jsonify({"url": image_url, "width": width, "height": height})

@app.route("/admin/upload-featured", methods=["POST"])
@admin_required
def upload_featured():
    return upload_image()

@app.route("/admin/upload-via-url", methods=["POST"])
@admin_required
def upload_via_url():
    image_url = request.json.get("url")
    if not image_url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        resp = http_requests.get(image_url, stream=True, timeout=10)
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', '')
        ext = 'jpg'
        if 'png' in content_type: ext = 'png'
        elif 'gif' in content_type: ext = 'gif'
        elif 'webp' in content_type: ext = 'webp'
        # Save to a temp buffer then process
        import io
        buf = io.BytesIO()
        for chunk in resp.iter_content(8192):
            buf.write(chunk)
        buf.seek(0)
        buf.name = f"remote.{ext}"
        _, width, height, image_url_local = process_and_save_image(buf, buf.name)
        return jsonify({"url": image_url_local, "width": width, "height": height})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── Assistant API endpoints ─────────────────────────────
@app.route("/admin/generate-outline", methods=["POST"])
@admin_required
def ajax_generate_outline():
    topic = request.json.get("topic")
    if not topic:
        return {"error": "Missing topic"}, 400
    client = get_models_client()
    if not client:
        return {"error": "GitHub token not configured."}, 500
    prompt = f"""You are an expert editor. Create a detailed outline for an article titled "{topic}".

RULES:
- Use exactly 5-7 sections.
- Each section title MUST start with "## " (two hashes and a space).
- Example:
  ## The rise of remote work
  ## Tools that actually work
  ## Common mistakes to avoid

Return ONLY the section titles, one per line, with no extra commentary."""
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return {"outline": resp.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/admin/generate-draft", methods=["POST"])
@admin_required
def ajax_generate_draft():
    data = request.json
    topic = data.get("topic")
    outline = data.get("outline", "")
    if not topic:
        return {"error": "Missing topic"}, 400
    client = get_models_client()
    if not client:
        return {"error": "GitHub token not configured."}, 500
    prompt = f"""You are an expert writer. Write a first draft for an article titled "{topic}".

INSTRUCTIONS:
- Use the following outline exactly as given – each section should start with "## Section Title" (two hashes).
- Write 2-3 paragraphs per section.
- Tone: neutral, informative, professional.
- Do NOT invent statistics or fake data.
- This is raw material for a human writer – it does not need to be perfect.

Outline:
{outline}

Draft (at least 800 words):"""
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000,
        )
        return {"draft": resp.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/admin/trends")
@admin_required
def ajax_trending():
    niche = request.args.get("niche", "technology")
    topics = get_trending_topics(niche)
    return {"trending": topics}

# ── Sitemap ──────────────────────────────────────────────
@app.route("/sitemap.xml")
def sitemap():
    articles = get_all_articles_sorted()
    base = request.host_url.rstrip('/')
    now = datetime.utcnow().strftime('%Y-%m-%d')

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Static pages
    for path, priority, freq in [
        ('/',           '1.0', 'daily'),
        ('/articles',   '0.8', 'daily'),
        ('/about',      '0.5', 'monthly'),
        ('/contact',    '0.5', 'monthly'),
        ('/privacy',    '0.3', 'yearly'),
        ('/terms',      '0.3', 'yearly'),
        ('/disclaimer', '0.3', 'yearly'),
        ('/cookies',    '0.3', 'yearly'),
    ]:
        lines.append(f'''  <url>
    <loc>{base}{path}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>''')

    # Category pages
    all_arts = get_all_articles_sorted()
    seen_cats = set()
    for a in all_arts:
        cat = a.get('category', '')
        if cat and cat not in seen_cats:
            seen_cats.add(cat)
            lines.append(f'''  <url>
    <loc>{base}/category/{cat}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>''')

    # Article pages
    for a in articles:
        date = a.get('date', now)
        slug = a.get('slug', '')
        image = a.get('featured_image', '')
        img_block = f'''
    <image:image xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
      <image:loc>{base}{image}</image:loc>
    </image:image>''' if image else ''
        lines.append(f'''  <url>
    <loc>{base}/article/{slug}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>{img_block}
  </url>''')

    lines.append('</urlset>')
    xml = '\n'.join(lines)
    return app.response_class(xml, mimetype='application/xml')

# ── RSS feed ─────────────────────────────────────────────
@app.route("/rss.xml")
def rss_feed():
    articles = get_all_articles_sorted()[:20]
    base = request.host_url.rstrip('/')
    now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

    items = []
    for a in articles:
        items.append(f'''  <item>
    <title>{a['title']}</title>
    <link>{base}/article/{a['slug']}</link>
    <guid>{base}/article/{a['slug']}</guid>
    <description>{a['excerpt']}</description>
    <category>{a['category']}</category>
    <pubDate>{a['date']}</pubDate>
  </item>''')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>BlogSphere</title>
  <link>{base}/</link>
  <description>Independent journalism and thoughtful perspectives on technology, design, finance, health, and culture.</description>
  <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>'''
    return app.response_class(xml, mimetype='application/rss+xml')

# ── robots.txt ───────────────────────────────────────────
@app.route("/robots.txt")
def robots():
    base = request.host_url.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {base}/sitemap.xml
"""
    return app.response_class(content, mimetype='text/plain')

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/x-icon')

@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return send_from_directory(app.static_folder, 'apple-touch-icon.png', mimetype='image/png')

# ── 404 handler ──────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    recent = get_all_articles_sorted()[:4]
    return render_template("404.html", recent_articles=recent), 404

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)), debug=debug_mode)