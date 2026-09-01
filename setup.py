#!/usr/bin/env python3
"""
Blogsphere_v2 – One‑step production site builder.
Run this script to create the entire project structure.
"""

import os
import sys
import subprocess
from pathlib import Path

# ── Paths ────────────────────────────────────────────────
BASE = Path(__file__).parent
TEMPLATES = BASE / "templates"
STATIC = BASE / "static"
SCRIPTS = BASE / "scripts"
CONTENT = BASE / "content"
ARTICLES = CONTENT / "articles"

# ── Create folders ──────────────────────────────────────
for d in [TEMPLATES, STATIC, SCRIPTS, ARTICLES, CONTENT / "published"]:
    d.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {d}")

# ── Write style.css (extracted from original design) ─────
# (The entire CSS from your HTML – I've kept it identical.)
style_css = """/* ─── BlogSphere Complete CSS ─── */
:root {
  --ink: #0f0e0c;
  --ink-2: #3a3830;
  --ink-3: #7a7670;
  --paper: #faf8f3;
  --paper-2: #f2efe8;
  --paper-3: #e8e4d8;
  --accent: #c8401a;
  --accent-2: #e8956a;
  --accent-light: #fdf0eb;
  --gold: #b8920a;
  --radius: 3px;
  --serif: 'Playfair Display', Georgia, serif;
  --sans: 'DM Sans', sans-serif;
  --mono: 'DM Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--sans);
  background: var(--paper);
  color: var(--ink);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* ─── NAV ─────────────────────────────────── */
nav {
  position: sticky; top: 0; z-index: 100;
  background: var(--paper);
  border-bottom: 1px solid var(--paper-3);
  padding: 0 clamp(16px, 5vw, 60px);
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
  transition: box-shadow .2s;
}
nav.scrolled { box-shadow: 0 2px 20px rgba(0,0,0,.07); }

.nav-logo {
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -.3px;
  cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  text-decoration: none;
}
.nav-logo span {
  display: inline-block;
  width: 28px; height: 28px;
  background: var(--accent);
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.nav-links {
  display: flex; align-items: center; gap: 6px;
  list-style: none;
}
.nav-links a {
  font-size: 14px; font-weight: 400;
  color: var(--ink-2);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: var(--radius);
  transition: background .15s, color .15s;
}
.nav-links a:hover, .nav-links a.active { background: var(--paper-2); color: var(--ink); }

.nav-search {
  display: flex; align-items: center; gap: 10px;
}
.search-box {
  display: flex; align-items: center; gap: 8px;
  background: var(--paper-2);
  border: 1px solid var(--paper-3);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px; color: var(--ink-3);
  cursor: pointer;
  transition: border-color .15s;
}
.search-box:hover { border-color: var(--ink-3); }
.search-box svg { opacity: .6; }

.btn-subscribe {
  background: var(--accent);
  color: #fff;
  border: none; border-radius: var(--radius);
  padding: 8px 18px;
  font-size: 13px; font-weight: 500;
  font-family: var(--sans);
  cursor: pointer;
  transition: background .15s, transform .1s;
  white-space: nowrap;
}
.btn-subscribe:hover { background: #a83315; transform: translateY(-1px); }

/* ─── HERO ─────────────────────────────────── */
.hero {
  padding: 60px clamp(16px, 5vw, 60px) 0;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
}
@media (max-width: 820px) { .hero { grid-template-columns: 1fr; } .hero-sidebar { display: none; } }

.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 11px; font-weight: 500;
  letter-spacing: .6px; text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 20px;
  margin-bottom: 14px;
  font-family: var(--mono);
}
.hero-badge::before { content: ''; width: 6px; height: 6px; background: var(--accent); border-radius: 50%; }

.hero-title {
  font-family: var(--serif);
  font-size: clamp(32px, 4vw, 52px);
  line-height: 1.12;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 18px;
  max-width: 620px;
}
.hero-title em { font-style: italic; color: var(--accent); }

.hero-meta {
  display: flex; align-items: center; gap: 16px;
  font-size: 13px; color: var(--ink-3);
  margin-bottom: 20px;
}
.hero-meta .author-chip {
  display: flex; align-items: center; gap: 8px;
  color: var(--ink-2);
}
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-2), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #fff;
  flex-shrink: 0;
}
.hero-excerpt {
  font-size: 17px; line-height: 1.7;
  color: var(--ink-2);
  margin-bottom: 24px;
  max-width: 560px;
}
.read-more-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--ink);
  color: var(--paper);
  text-decoration: none;
  padding: 12px 22px;
  border-radius: var(--radius);
  font-size: 14px; font-weight: 500;
  cursor: pointer;
  transition: background .15s, gap .2s;
  border: none; font-family: var(--sans);
}
.read-more-btn:hover { background: var(--accent); gap: 12px; }
.read-more-btn svg { transition: transform .2s; }
.read-more-btn:hover svg { transform: translateX(3px); }

.hero-img {
  width: 100%; aspect-ratio: 16/10;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  margin-top: 36px;
  flex-shrink: 0;
}
.hero-img-placeholder {
  width: 100%; height: 100%;
  background: linear-gradient(135deg, #e8e0d0 0%, #d4c9b4 50%, #c8bca4 100%);
  display: flex; align-items: center; justify-content: center;
  position: relative;
  overflow: hidden;
}
.hero-img-placeholder::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23b0a898' fill-opacity='0.2'%3E%3Cpath d='M0 0h20v20H0V0zm20 20h20v20H20V20z'/%3E%3C/g%3E%3C/svg%3E");
}
.img-label {
  font-size: 13px; color: rgba(0,0,0,.4);
  font-family: var(--mono);
  z-index: 1;
}

/* Sidebar */
.hero-sidebar { padding-top: 36px; }
.sidebar-section { margin-bottom: 32px; }
.sidebar-label {
  font-size: 10px; font-weight: 500; letter-spacing: 1.2px;
  text-transform: uppercase; color: var(--ink-3);
  font-family: var(--mono);
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--paper-3);
}
.trending-list { list-style: none; }
.trending-item {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid var(--paper-2);
  cursor: pointer;
  transition: opacity .15s;
}
.trending-item:hover { opacity: .7; }
.trending-num {
  font-family: var(--serif);
  font-size: 22px; color: var(--paper-3);
  font-weight: 700; line-height: 1;
  flex-shrink: 0; padding-top: 2px;
}
.trending-text { font-size: 14px; line-height: 1.45; font-weight: 400; color: var(--ink-2); }
.trending-cat { font-size: 11px; color: var(--accent); font-family: var(--mono); margin-top: 2px; }

/* ─── TICKER ─────────────────────────────────── */
.ticker-bar {
  border-top: 2px solid var(--ink);
  border-bottom: 1px solid var(--paper-3);
  padding: 10px clamp(16px,5vw,60px);
  display: flex; align-items: center; gap: 20px;
  overflow: hidden;
  margin-top: 40px;
}
.ticker-label {
  font-size: 10px; font-weight: 500; letter-spacing: 1.2px;
  text-transform: uppercase; color: #fff;
  background: var(--accent);
  padding: 3px 8px;
  border-radius: 2px;
  flex-shrink: 0;
  font-family: var(--mono);
}
.ticker-items {
  display: flex; gap: 32px;
  font-size: 13px; color: var(--ink-2);
  overflow: hidden;
  white-space: nowrap;
}
.ticker-dot { color: var(--accent); }

/* ─── SECTION ─────────────────────────────────── */
.section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 52px clamp(16px, 5vw, 60px);
}
.section-header {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 28px;
  border-bottom: 2px solid var(--ink);
  padding-bottom: 12px;
}
.section-title {
  font-family: var(--serif);
  font-size: 26px; font-weight: 700;
  color: var(--ink);
}
.section-link {
  font-size: 13px; color: var(--accent);
  text-decoration: none; cursor: pointer;
  display: flex; align-items: center; gap: 4px;
}
.section-link:hover { text-decoration: underline; }

/* ─── ARTICLE GRID ─────────────────────────────────── */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 32px;
}
.article-card {
  cursor: pointer;
  transition: transform .2s;
}
.article-card:hover { transform: translateY(-3px); }
.article-card:hover .card-title { color: var(--accent); }

.card-img {
  width: 100%; aspect-ratio: 16/9;
  border-radius: 4px; overflow: hidden;
  margin-bottom: 14px;
}
.card-img-ph {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: rgba(0,0,0,.35);
  font-family: var(--mono);
}
.card-category {
  font-size: 11px; font-weight: 500; letter-spacing: .6px;
  text-transform: uppercase;
  color: var(--accent);
  font-family: var(--mono);
  margin-bottom: 6px;
}
.card-title {
  font-family: var(--serif);
  font-size: 20px; line-height: 1.28;
  font-weight: 600; color: var(--ink);
  margin-bottom: 8px;
  transition: color .15s;
}
.card-excerpt {
  font-size: 14px; line-height: 1.65;
  color: var(--ink-3);
  margin-bottom: 12px;
}
.card-meta {
  display: flex; align-items: center; gap: 10px;
  font-size: 12px; color: var(--ink-3);
}
.card-meta .dot { color: var(--paper-3); }
.tag {
  display: inline-block;
  background: var(--paper-2); color: var(--ink-2);
  font-size: 11px; padding: 2px 8px;
  border-radius: 2px;
  font-family: var(--mono);
}

/* ─── FEATURED WIDE ─────────────────────────────────── */
.featured-wide {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border: 1px solid var(--paper-3);
  border-radius: 6px; overflow: hidden;
  cursor: pointer;
  transition: box-shadow .2s;
  margin-bottom: 32px;
}
.featured-wide:hover { box-shadow: 0 8px 40px rgba(0,0,0,.08); }
.featured-wide-img {
  height: 260px;
  background: linear-gradient(135deg, #d4c5b0 0%, #c0af98 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: rgba(0,0,0,.35); font-family: var(--mono);
}
.featured-wide-body {
  padding: 32px;
  display: flex; flex-direction: column; justify-content: center;
  background: var(--paper);
}
.featured-wide-body .card-title { font-size: 24px; }
@media (max-width: 640px) { .featured-wide { grid-template-columns: 1fr; } .featured-wide-img { height: 200px; } }

/* ─── CATEGORIES BAR ─────────────────────────────────── */
.categories-bar {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 36px;
}
.cat-pill {
  padding: 6px 16px; border-radius: 20px;
  border: 1px solid var(--paper-3);
  font-size: 13px; color: var(--ink-2);
  cursor: pointer;
  transition: all .15s;
  background: var(--paper);
}
.cat-pill:hover, .cat-pill.active {
  background: var(--ink); color: var(--paper);
  border-color: var(--ink);
}

/* ─── NEWSLETTER ─────────────────────────────────── */
.newsletter-strip {
  background: var(--ink);
  padding: 52px clamp(16px, 5vw, 60px);
  text-align: center;
}
.newsletter-strip h2 {
  font-family: var(--serif);
  font-size: clamp(24px, 3vw, 38px);
  color: var(--paper);
  margin-bottom: 8px;
}
.newsletter-strip p {
  color: rgba(250,248,243,.6);
  font-size: 15px; margin-bottom: 24px;
}
.newsletter-form {
  display: flex; gap: 8px;
  max-width: 440px; margin: 0 auto;
}
.newsletter-form input {
  flex: 1;
  background: rgba(255,255,255,.1);
  border: 1px solid rgba(255,255,255,.15);
  border-radius: var(--radius);
  padding: 11px 16px;
  color: var(--paper);
  font-size: 14px;
  font-family: var(--sans);
  outline: none;
  transition: border-color .15s;
}
.newsletter-form input::placeholder { color: rgba(255,255,255,.35); }
.newsletter-form input:focus { border-color: var(--accent-2); }
.newsletter-form button {
  background: var(--accent);
  color: #fff; border: none;
  border-radius: var(--radius);
  padding: 11px 20px;
  font-size: 14px; font-weight: 500;
  font-family: var(--sans);
  cursor: pointer;
  white-space: nowrap;
  transition: background .15s;
}
.newsletter-form button:hover { background: #a83315; }

/* ─── FOOTER ─────────────────────────────────── */
footer {
  border-top: 1px solid var(--paper-3);
  padding: 40px clamp(16px, 5vw, 60px) 24px;
  max-width: 1200px; margin: 0 auto;
}
.footer-top {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 32px; margin-bottom: 32px;
}
@media (max-width: 700px) { .footer-top { grid-template-columns: 1fr 1fr; } }
.footer-brand p {
  font-size: 13px; color: var(--ink-3); line-height: 1.7;
  margin-top: 10px;
}
.footer-col h4 {
  font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
  color: var(--ink-3); font-family: var(--mono);
  margin-bottom: 12px;
}
.footer-col ul { list-style: none; }
.footer-col ul li {
  font-size: 13px; color: var(--ink-2);
  margin-bottom: 8px; cursor: pointer;
  transition: color .15s;
}
.footer-col ul li:hover { color: var(--accent); }
.footer-bottom {
  border-top: 1px solid var(--paper-3);
  padding-top: 20px;
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12px; color: var(--ink-3);
  flex-wrap: wrap; gap: 12px;
}
.footer-bottom a { color: var(--ink-3); text-decoration: none; }
.footer-bottom a:hover { color: var(--accent); }

/* ─── ARTICLE PAGE ─────────────────────────────────── */
.article-layout {
  max-width: 1200px; margin: 0 auto;
  padding: 40px clamp(16px, 5vw, 60px);
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 60px;
}
@media (max-width: 860px) { .article-layout { grid-template-columns: 1fr; } .article-aside { display: none; } }

.article-header { margin-bottom: 32px; }
.article-category-pill {
  display: inline-block;
  background: var(--accent-light); color: var(--accent);
  font-size: 11px; font-weight: 500; letter-spacing: .6px;
  text-transform: uppercase; font-family: var(--mono);
  padding: 4px 10px; border-radius: 20px;
  margin-bottom: 16px;
}
.article-title {
  font-family: var(--serif);
  font-size: clamp(28px, 4vw, 46px);
  line-height: 1.12; font-weight: 700;
  margin-bottom: 20px;
}
.article-meta-row {
  display: flex; align-items: center; gap: 16px;
  padding: 16px 0;
  border-top: 1px solid var(--paper-3);
  border-bottom: 1px solid var(--paper-3);
  margin-bottom: 28px;
}
.article-meta-row .author-chip { display: flex; align-items: center; gap: 10px; }
.author-info .name { font-size: 14px; font-weight: 500; }
.author-info .date { font-size: 12px; color: var(--ink-3); }
.meta-stats { margin-left: auto; display: flex; gap: 16px; font-size: 12px; color: var(--ink-3); align-items: center; }
.meta-stat { display: flex; align-items: center; gap: 4px; }

.article-hero-img {
  width: 100%; aspect-ratio: 16/8;
  background: linear-gradient(135deg, #ddd5c3 0%, #c8bba6 100%);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: rgba(0,0,0,.35); font-family: var(--mono);
  margin-bottom: 32px;
}
.article-body { font-size: 18px; line-height: 1.75; color: var(--ink-2); }
.article-body h2 {
  font-family: var(--serif);
  font-size: 26px; font-weight: 700;
  color: var(--ink); margin: 40px 0 16px;
}
.article-body p { margin-bottom: 22px; }
.article-body blockquote {
  border-left: 3px solid var(--accent);
  padding: 12px 20px;
  margin: 28px 0;
  background: var(--accent-light);
  border-radius: 0 4px 4px 0;
}
.article-body blockquote p {
  font-family: var(--serif);
  font-size: 19px; font-style: italic;
  color: var(--ink); margin: 0;
  line-height: 1.55;
}
.article-body .highlight {
  background: linear-gradient(transparent 60%, rgba(200,64,26,.15) 60%);
  display: inline;
}

/* TOC */
.toc-box {
  background: var(--paper-2);
  border: 1px solid var(--paper-3);
  border-radius: 4px;
  padding: 20px;
  margin: 28px 0;
}
.toc-box h3 {
  font-family: var(--serif); font-size: 15px; font-weight: 600;
  margin-bottom: 12px;
}
.toc-box ol {
  padding-left: 20px;
  font-size: 14px; color: var(--ink-2);
  line-height: 2;
}
.toc-box ol li { cursor: pointer; }
.toc-box ol li:hover { color: var(--accent); }

/* Tags + share */
.article-tags { display: flex; gap: 8px; flex-wrap: wrap; margin: 32px 0; }
.share-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 0;
  border-top: 1px solid var(--paper-3);
  border-bottom: 1px solid var(--paper-3);
  margin-bottom: 40px;
}
.share-label { font-size: 13px; color: var(--ink-3); margin-right: 4px; }
.share-btn {
  padding: 6px 14px;
  border: 1px solid var(--paper-3);
  border-radius: 20px;
  font-size: 12px; color: var(--ink-2);
  cursor: pointer;
  transition: all .15s;
  background: var(--paper);
}
.share-btn:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }

/* Author card */
.author-card {
  border: 1px solid var(--paper-3);
  border-radius: 6px;
  padding: 28px;
  margin-bottom: 40px;
  display: flex; gap: 20px;
  align-items: flex-start;
}
.author-card .avatar { width: 54px; height: 54px; font-size: 18px; flex-shrink: 0; }
.author-card h4 { font-family: var(--serif); font-size: 18px; margin-bottom: 4px; }
.author-card p { font-size: 14px; color: var(--ink-3); line-height: 1.6; }

/* Sidebar sticky */
.article-aside { position: sticky; top: 80px; align-self: start; }
.aside-box {
  border: 1px solid var(--paper-3);
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}
.aside-box h4 {
  font-family: var(--serif); font-size: 16px; font-weight: 600;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--paper-3);
}
.related-mini {
  display: flex; gap: 10px;
  margin-bottom: 12px; cursor: pointer;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--paper-2);
  transition: opacity .15s;
}
.related-mini:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.related-mini:hover { opacity: .7; }
.related-mini-img {
  width: 56px; height: 44px; flex-shrink: 0;
  border-radius: 3px;
  background: linear-gradient(135deg, #ddd5c3, #c8bba6);
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; color: rgba(0,0,0,.3); font-family: var(--mono);
}
.related-mini-title { font-size: 13px; line-height: 1.4; color: var(--ink-2); }
.related-mini-cat { font-size: 11px; color: var(--accent); font-family: var(--mono); margin-top: 2px; }

/* Progress bar */
#read-progress {
  position: fixed; top: 64px; left: 0; height: 3px;
  background: var(--accent); z-index: 99;
  width: 0%; transition: width .1s;
  display: none;
}

/* ─── ABOUT PAGE ─────────────────────────────────── */
.about-layout {
  max-width: 820px; margin: 0 auto;
  padding: 52px clamp(16px, 5vw, 60px);
}
.about-hero {
  display: grid; grid-template-columns: 1fr 280px;
  gap: 40px; margin-bottom: 52px; align-items: center;
}
@media (max-width: 640px) { .about-hero { grid-template-columns: 1fr; } }
.about-hero h1 {
  font-family: var(--serif);
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.12; font-weight: 700;
  margin-bottom: 16px;
}
.about-hero p { font-size: 16px; color: var(--ink-2); line-height: 1.7; }
.about-img-ph {
  width: 100%; aspect-ratio: 1;
  background: linear-gradient(135deg, #ddd5c3 0%, #c0af98 100%);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: rgba(0,0,0,.3); font-family: var(--mono);
}
.about-body h2 {
  font-family: var(--serif); font-size: 26px;
  margin: 36px 0 14px;
}
.about-body p { font-size: 16px; color: var(--ink-2); line-height: 1.75; margin-bottom: 18px; }
.values-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 16px; margin: 20px 0 32px;
}
.value-card {
  background: var(--paper-2);
  border-radius: 4px; padding: 20px;
  border-left: 3px solid var(--accent);
}
.value-card h4 { font-size: 15px; font-weight: 500; margin-bottom: 6px; }
.value-card p { font-size: 13px; color: var(--ink-3); margin: 0; line-height: 1.6; }

/* ─── CONTACT PAGE ─────────────────────────────────── */
.contact-layout {
  max-width: 700px; margin: 0 auto;
  padding: 52px clamp(16px, 5vw, 60px);
}
.contact-layout h1 {
  font-family: var(--serif); font-size: clamp(28px, 4vw, 42px);
  margin-bottom: 10px;
}
.contact-layout > p { font-size: 16px; color: var(--ink-2); margin-bottom: 36px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 500px) { .form-grid { grid-template-columns: 1fr; } }
.form-group { margin-bottom: 20px; }
.form-group.span-2 { grid-column: 1 / -1; }
.form-group label {
  display: block; font-size: 13px; font-weight: 500;
  margin-bottom: 6px; color: var(--ink-2);
}
.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  background: var(--paper-2);
  border: 1px solid var(--paper-3);
  border-radius: var(--radius);
  padding: 11px 14px;
  font-size: 14px; font-family: var(--sans); color: var(--ink);
  outline: none; transition: border-color .15s;
  -webkit-appearance: none;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  border-color: var(--accent);
  background: #fff;
}
.form-group textarea { min-height: 130px; resize: vertical; line-height: 1.6; }
.form-submit {
  background: var(--accent); color: #fff;
  border: none; border-radius: var(--radius);
  padding: 12px 28px; font-size: 15px; font-weight: 500;
  font-family: var(--sans); cursor: pointer;
  transition: background .15s;
}
.form-submit:hover { background: #a83315; }

/* ─── PRIVACY PAGE ─────────────────────────────────── */
.policy-layout {
  max-width: 760px; margin: 0 auto;
  padding: 52px clamp(16px, 5vw, 60px);
}
.policy-layout h1 {
  font-family: var(--serif); font-size: 38px;
  margin-bottom: 6px;
}
.policy-date { font-size: 13px; color: var(--ink-3); margin-bottom: 36px; font-family: var(--mono); }
.policy-layout h2 { font-family: var(--serif); font-size: 22px; margin: 32px 0 12px; }
.policy-layout p { font-size: 15px; color: var(--ink-2); line-height: 1.75; margin-bottom: 16px; }
.policy-layout ul { padding-left: 20px; margin-bottom: 16px; }
.policy-layout ul li { font-size: 15px; color: var(--ink-2); line-height: 2; }

/* ─── COOKIE BANNER ─────────────────────────────────── */
.cookie-banner {
  position: fixed; bottom: 20px; left: 20px; right: 20px;
  max-width: 520px;
  background: var(--ink);
  border-radius: 8px;
  padding: 18px 20px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: 0 8px 40px rgba(0,0,0,.2);
  z-index: 300;
  animation: slideUp .4s ease;
}
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.cookie-banner.hidden { display: none; }
.cookie-text { flex: 1; font-size: 13px; color: rgba(250,248,243,.75); line-height: 1.5; }
.cookie-text a { color: var(--accent-2); }
.cookie-accept {
  background: var(--accent); color: #fff;
  border: none; border-radius: 4px;
  padding: 8px 16px; font-size: 13px;
  font-family: var(--sans); font-weight: 500;
  cursor: pointer; white-space: nowrap;
  transition: background .15s;
}
.cookie-accept:hover { background: #a83315; }
.cookie-close {
  background: none; border: none;
  color: rgba(255,255,255,.4); cursor: pointer;
  font-size: 20px; padding: 0; line-height: 1;
}
.cookie-close:hover { color: rgba(255,255,255,.8); }

/* ─── AD PLACEHOLDER ─────────────────────────────────── */
.ad-slot {
  width: 100%;
  background: var(--paper-2);
  border: 1px dashed var(--paper-3);
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: var(--ink-3);
  font-family: var(--mono);
  margin: 20px 0;
}
.ad-slot.leaderboard { height: 90px; }
.ad-slot.rectangle { height: 250px; }
.ad-slot.sidebar { height: 200px; }
"""

with open(STATIC / "style.css", "w", encoding="utf-8") as f:
    f.write(style_css)
print("✓ style.css written")

# ── Write Flask templates ─────────────────────────────

# base.html
base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BlogSphere{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div id="read-progress"></div>
<nav id="main-nav">
  <a class="nav-logo" href="/"><span>B</span> BlogSphere</a>
  <ul class="nav-links">
    <li><a href="/">Home</a></li>
    <li><a href="/articles">Articles</a></li>
    <li><a href="/about">About</a></li>
    <li><a href="/contact">Contact</a></li>
    <li><a href="/privacy">Privacy</a></li>
  </ul>
  <div class="nav-search">
    <div class="search-box">
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      Search
    </div>
    <button class="btn-subscribe">Subscribe</button>
  </div>
</nav>

{% block content %}{% endblock %}

<footer>
  <div class="footer-top">
    <div class="footer-brand">
      <div class="nav-logo" style="cursor:default"><span>B</span> BlogSphere</div>
      <p>Independent journalism and thoughtful perspectives on technology, culture, and the world we're building together.</p>
    </div>
    <div class="footer-col">
      <h4>Topics</h4>
      <ul>
        <li>Technology</li><li>Design</li><li>Finance</li>
        <li>Health</li><li>Science</li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <ul>
        <li><a href="/about">About us</a></li>
        <li><a href="/contact">Contact</a></li>
        <li>Newsletter</li>
        <li>Advertise</li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <ul>
        <li><a href="/privacy">Privacy Policy</a></li>
        <li>Terms of Use</li>
        <li>Disclaimer</li>
        <li>Cookie Policy</li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2025 BlogSphere. All rights reserved.</span>
    <div style="display:flex;gap:16px">
      <a href="/privacy">Privacy</a>
      <a>Terms</a>
      <a href="/contact">Contact</a>
    </div>
  </div>
</footer>

<div class="cookie-banner" id="cookie-banner">
  <div class="cookie-text">We use cookies to improve your experience and serve ads via <a href="#">Google AdSense</a>. By continuing, you accept our <a href="/privacy">Privacy Policy</a>.</div>
  <button class="cookie-accept" onclick="document.getElementById('cookie-banner').classList.add('hidden')">Accept</button>
  <button class="cookie-close" onclick="document.getElementById('cookie-banner').classList.add('hidden')">✕</button>
</div>

<script>
  // Scroll effects
  window.addEventListener('scroll', () => {
    document.getElementById('main-nav').classList.toggle('scrolled', window.scrollY > 10);
    const articleBody = document.querySelector('.article-body');
    if (articleBody) {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      document.getElementById('read-progress').style.width = Math.round((window.scrollY/h)*100) + '%';
      document.getElementById('read-progress').style.display = 'block';
    } else {
      document.getElementById('read-progress').style.display = 'none';
    }
  });
  // Active nav link
  document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
      link.classList.add('active');
    }
  });
</script>
</body>
</html>"""

with open(TEMPLATES / "base.html", "w", encoding="utf-8") as f:
    f.write(base_html)

# home.html (extends base, contains the full homepage content from original design)
home_html = """{% extends "base.html" %}
{% block title %}BlogSphere – Thoughtful stories for curious minds{% endblock %}
{% block content %}
<div class="page active">
  <div class="hero">
    <div>
      <div class="hero-badge">Featured story</div>
      <h1 class="hero-title">The Future of <em>Artificial Intelligence</em> in Everyday Life</h1>
      <div class="hero-meta">
        <div class="author-chip">
          <div class="avatar">JD</div>
          <span>James Douglas</span>
        </div>
        <span>·</span><span>May 14, 2025</span><span>·</span><span>8 min read</span>
      </div>
      <p class="hero-excerpt">From smart assistants to autonomous vehicles, AI is reshaping the world as we know it. We explore what's next — and what it means for you.</p>
      <button class="read-more-btn" onclick="location.href='/article/future-of-ai'">
        Read the full story
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
      </button>
      <div class="hero-img" style="max-width:600px">
        <div class="hero-img-placeholder"><span class="img-label">Featured article image</span></div>
      </div>
    </div>
    <aside class="hero-sidebar">
      <div class="sidebar-section">
        <div class="sidebar-label">Trending now</div>
        <ul class="trending-list">
          <li class="trending-item" onclick="location.href='/article/minimalism'">
            <span class="trending-num">01</span><div><div class="trending-text">Why Minimalism Is More Than a Design Trend</div><div class="trending-cat">Design</div></div>
          </li>
          <li class="trending-item" onclick="location.href='/article/productive-morning'">
            <span class="trending-num">02</span><div><div class="trending-text">The Science Behind a Perfectly Productive Morning</div><div class="trending-cat">Productivity</div></div>
          </li>
          <li class="trending-item" onclick="location.href='/article/blockchain-beyond-hype'">
            <span class="trending-num">03</span><div><div class="trending-text">Understanding Blockchain Beyond the Hype</div><div class="trending-cat">Technology</div></div>
          </li>
        </ul>
      </div>
      <div class="ad-slot rectangle">Google AdSense 300×250</div>
    </aside>
  </div>

  <div class="ticker-bar">
    <span class="ticker-label">Latest</span>
    <div class="ticker-items">
      <span>Tech & Society</span><span class="ticker-dot">●</span>
      <span>Design Thinking</span><span class="ticker-dot">●</span>
      <span>Productivity</span><span class="ticker-dot">●</span>
      <span>Science</span>
    </div>
  </div>

  <div style="max-width:1200px;margin:0 auto;padding:20px clamp(16px,5vw,60px) 0">
    <div class="ad-slot leaderboard">Google AdSense Leaderboard 728×90</div>
  </div>

  <section class="section">
    <div class="section-header">
      <h2 class="section-title">Latest Articles</h2>
      <a class="section-link" href="/articles">View all →</a>
    </div>
    <div class="featured-wide" onclick="location.href='/article/quantum-crypto'">
      <div class="featured-wide-img">Article image</div>
      <div class="featured-wide-body">
        <div class="card-category">Technology</div>
        <h3 class="card-title">How Quantum Computing Will Change Cryptography Forever</h3>
        <p class="card-excerpt">The cryptographic systems protecting your data today may be obsolete within a decade.</p>
        <div class="card-meta">
          <div class="avatar" style="width:24px;height:24px;font-size:10px">AR</div>
          <span>Ariel Rahman</span><span class="dot">·</span><span>May 10, 2025</span><span class="dot">·</span><span>12 min read</span>
        </div>
      </div>
    </div>
    <div class="articles-grid">
      <div class="article-card" onclick="location.href='/article/color-psychology'">
        <div class="card-img" style="background:linear-gradient(135deg,#e4d5c2,#c8b89a)"><div class="card-img-ph">Article image</div></div>
        <div class="card-category">Design</div>
        <h3 class="card-title">The Psychology of Color in UI Design</h3>
        <p class="card-excerpt">Color isn't just aesthetic — it shapes how users feel, act, and remember your product.</p>
        <div class="card-meta"><span>Sofia Chen</span><span class="dot">·</span><span>7 min read</span></div>
      </div>
      <div class="article-card" onclick="location.href='/article/slow-wealth'">
        <div class="card-img" style="background:linear-gradient(135deg,#d5e4d5,#a8c8a8)"><div class="card-img-ph">Article image</div></div>
        <div class="card-category">Finance</div>
        <h3 class="card-title">Building Wealth Slowly: The Boring Strategy That Works</h3>
        <p class="card-excerpt">Compound interest and index funds aren't glamorous. They're consistently effective.</p>
        <div class="card-meta"><span>Tom Walker</span><span class="dot">·</span><span>9 min read</span></div>
      </div>
      <div class="article-card" onclick="location.href='/article/deep-focus'">
        <div class="card-img" style="background:linear-gradient(135deg,#d5dde4,#a8b8c8)"><div class="card-img-ph">Article image</div></div>
        <div class="card-category">Health</div>
        <h3 class="card-title">What Neuroscience Tells Us About Deep Focus</h3>
        <p class="card-excerpt">Your brain isn't built for modern distraction. Here's what the science says about reclaiming it.</p>
        <div class="card-meta"><span>Lena Park</span><span class="dot">·</span><span>6 min read</span></div>
      </div>
    </div>
  </section>

  <div class="newsletter-strip">
    <h2>Thoughtful reads, every week.</h2>
    <p>Join 12,000+ readers getting curated articles delivered to their inbox.</p>
    <div class="newsletter-form">
      <input type="email" placeholder="Enter your email address">
      <button>Subscribe</button>
    </div>
  </div>
</div>
{% endblock %}"""

with open(TEMPLATES / "home.html", "w", encoding="utf-8") as f:
    f.write(home_html)

# article.html (dynamic, uses {{ content }} and {{ article_title }} from route)
article_html = """{% extends "base.html" %}
{% block title %}{{ article_title }} – BlogSphere{% endblock %}
{% block content %}
<div class="article-layout">
  <article>
    <div class="article-header">
      <div class="article-category-pill">{{ article_category }}</div>
      <h1 class="article-title">{{ article_title }}</h1>
      <div class="article-meta-row">
        <div class="author-chip">
          <div class="avatar">{{ author_initial }}</div>
          <div class="author-info">
            <div class="name">{{ author_name }}</div>
            <div class="date">{{ publish_date }}</div>
          </div>
        </div>
        <div class="meta-stats">
          <span class="meta-stat">⏱ {{ read_time }} min read</span>
          <span class="meta-stat">👁 1,234 views</span>
        </div>
      </div>
    </div>
    <div class="ad-slot leaderboard">Google AdSense 728×90</div>
    <div class="article-hero-img">Featured article image (1200×630)</div>
    <div class="article-body">
      {{ content|safe }}
    </div>
    <div class="ad-slot rectangle">Google AdSense In-Article 300×250</div>
    <div class="article-tags">
      {% for tag in tags %}<span class="tag">{{ tag }}</span>{% endfor %}
    </div>
    <div class="share-bar">
      <span class="share-label">Share this article:</span>
      <button class="share-btn">Twitter / X</button>
      <button class="share-btn">LinkedIn</button>
      <button class="share-btn">Facebook</button>
      <button class="share-btn">Copy link</button>
    </div>
    <div class="author-card">
      <div class="avatar" style="width:54px;height:54px;font-size:18px">{{ author_initial }}</div>
      <div>
        <h4>{{ author_name }}</h4>
        <p>{{ author_bio }}</p>
      </div>
    </div>
  </article>
  <aside class="article-aside">
    <div class="ad-slot sidebar">Google AdSense 300×250</div>
    <div class="aside-box">
      <h4>Related Articles</h4>
      <div class="related-mini" onclick="location.href='/article/quantum-crypto'">
        <div class="related-mini-img">img</div>
        <div><div class="related-mini-title">How Quantum Computing Will Change Cryptography</div><div class="related-mini-cat">Technology</div></div>
      </div>
    </div>
    <div class="aside-box">
      <h4>Newsletter</h4>
      <p style="font-size:13px;color:var(--ink-3);line-height:1.6;margin-bottom:14px">Thoughtful reads, every week.</p>
      <input type="email" placeholder="Your email" style="width:100%;background:var(--paper-2);border:1px solid var(--paper-3);border-radius:3px;padding:9px 12px;font-size:13px;font-family:var(--sans);outline:none;margin-bottom:8px">
      <button class="btn-subscribe" style="width:100%;padding:9px">Subscribe</button>
    </div>
  </aside>
</div>
{% endblock %}"""

with open(TEMPLATES / "article.html", "w", encoding="utf-8") as f:
    f.write(article_html)

# about.html (identical to original)
about_html = """{% extends "base.html" %}
{% block title %}About – BlogSphere{% endblock %}
{% block content %}
<div class="about-layout">
  <div class="about-hero">
    <div>
      <h1>We write about the world <em style="font-style:italic;color:var(--accent)">worth reading about.</em></h1>
      <p>BlogSphere is an independent publication dedicated to thoughtful, well-researched articles on technology, design, finance, health, and the ideas shaping our world. No clickbait. No filler. Just genuine writing that respects your time.</p>
    </div>
    <div class="about-img-ph">Team photo</div>
  </div>
  <div class="about-body">
    <h2>Our mission</h2>
    <p>We started BlogSphere because we were tired of content designed to rank rather than content designed to inform. The internet is full of articles written for algorithms. We write for people — curious, busy, thoughtful people who want to understand the world a little better.</p>
    <p>Every article published on BlogSphere goes through a rigorous editorial process. We fact-check, we cite sources, and we're honest about what we don't know. We believe good journalism — even in blog form — has standards worth upholding.</p>
    <h2>What we cover</h2>
    <div class="values-grid">
      <div class="value-card"><h4>Technology</h4><p>AI, software, digital culture and the tools reshaping work and life.</p></div>
      <div class="value-card"><h4>Finance</h4><p>Personal finance, investing, and economic ideas that actually matter.</p></div>
      <div class="value-card"><h4>Health & Science</h4><p>Evidence-based writing on the body, mind, and cutting-edge research.</p></div>
      <div class="value-card"><h4>Design & Culture</h4><p>How things are made, why aesthetics matter, and creative thinking.</p></div>
    </div>
    <h2>Advertising & independence</h2>
    <p>BlogSphere is supported by Google AdSense advertising and optional reader subscriptions. Our editorial decisions are entirely independent of our advertising relationships. We do not accept sponsored articles, and no advertiser has ever influenced a single word of our editorial content.</p>
    <p>If you'd like to work with us, please reach out via the contact page.</p>
  </div>
</div>
{% endblock %}"""

with open(TEMPLATES / "about.html", "w", encoding="utf-8") as f:
    f.write(about_html)

# contact.html (identical)
contact_html = """{% extends "base.html" %}
{% block title %}Contact – BlogSphere{% endblock %}
{% block content %}
<div class="contact-layout">
  <h1>Get in touch</h1>
  <p>Whether you have a story tip, a correction, a collaboration idea, or just want to say hello — we'd love to hear from you. We read every message and reply within 2 business days.</p>
  <div class="form-grid">
    <div class="form-group"><label>First name</label><input type="text" placeholder="Jane"></div>
    <div class="form-group"><label>Last name</label><input type="text" placeholder="Smith"></div>
    <div class="form-group span-2"><label>Email address</label><input type="email" placeholder="jane@example.com"></div>
    <div class="form-group span-2"><label>Subject</label><select><option>General enquiry</option><option>Story tip</option><option>Correction or feedback</option><option>Collaboration</option><option>Advertising</option><option>Other</option></select></div>
    <div class="form-group span-2"><label>Message</label><textarea placeholder="Write your message here..."></textarea></div>
  </div>
  <button class="form-submit">Send message</button>
</div>
{% endblock %}"""

with open(TEMPLATES / "contact.html", "w", encoding="utf-8") as f:
    f.write(contact_html)

# privacy.html (identical)
privacy_html = """{% extends "base.html" %}
{% block title %}Privacy Policy – BlogSphere{% endblock %}
{% block content %}
<div class="policy-layout">
  <h1>Privacy Policy</h1>
  <div class="policy-date">Last updated: 14 May 2025</div>
  <p>BlogSphere ("we", "our", or "us") is committed to protecting your personal information. This Privacy Policy explains how we collect, use, and protect data when you visit blogsphere.com.</p>
  <h2>Information we collect</h2>
  <p>We may collect the following types of information:</p>
  <ul>
    <li>Information you provide voluntarily (name, email address when subscribing or contacting us)</li>
    <li>Usage data collected automatically (pages visited, time on site, referring URLs)</li>
    <li>Device information (browser type, operating system, screen resolution)</li>
    <li>Cookies and similar tracking technologies (see Cookie Policy below)</li>
  </ul>
  <h2>How we use your information</h2>
  <p>We use the information we collect to deliver and improve the website, send the newsletter (only to subscribers who have opted in), respond to contact form enquiries, and analyse site performance.</p>
  <h2>Google AdSense and advertising</h2>
  <p>This website uses Google AdSense to display advertisements. Google and its partners use cookies to serve ads based on your prior visits to this and other websites. You may opt out of personalised advertising by visiting <a href="#" style="color:var(--accent)">Google Ads Settings</a>.</p>
  <h2>Cookies</h2>
  <p>We use cookies to improve your browsing experience and to enable advertising. You can control cookie preferences through your browser settings or via our cookie consent banner.</p>
  <h2>Your rights (GDPR)</h2>
  <p>If you are in the European Economic Area, you have the right to access, rectify, or erase personal data we hold about you. You also have the right to restrict or object to processing, and the right to data portability. To exercise these rights, contact us at privacy@blogsphere.com.</p>
  <h2>Contact</h2>
  <p>If you have questions about this Privacy Policy, please contact us at <a href="/contact" style="color:var(--accent)">our contact page</a> or by email at privacy@blogsphere.com.</p>
</div>
{% endblock %}"""

with open(TEMPLATES / "privacy.html", "w", encoding="utf-8") as f:
    f.write(privacy_html)

print("✓ All templates written")

# ── Write server.py ───────────────────────────────────
server_code = """from flask import Flask, render_template, abort, url_for
from pathlib import Path
import markdown
import re

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/articles")
def articles():
    # For now redirect to home; you can build a dedicated listing page later.
    return render_template("home.html")

@app.route("/article/<slug>")
def article(slug):
    md_file = Path(f"content/articles/{slug}.md")
    if not md_file.exists():
        abort(404)
    raw = md_file.read_text(encoding="utf-8")
    # Parse simple front-matter (optional)
    title = slug.replace("-", " ").title()
    category = "General"
    author_name = "BlogSphere"
    author_initial = "B"
    author_bio = "A curious mind writing about the things that matter."
    read_time = 5
    publish_date = "2025-01-01"
    tags = []
    content_text = raw

    # Very basic front-matter detection
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            front = parts[1]
            content_text = parts[2]
            for line in front.strip().split("\\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key, val = key.strip().lower(), val.strip()
                    if key == "title": title = val
                    elif key == "category": category = val
                    elif key == "author": author_name = val
                    elif key == "author_bio": author_bio = val
                    elif key == "date": publish_date = val
                    elif key == "tags": tags = [t.strip() for t in val.split(",")]
                    elif key == "read_time": read_time = int(val) if val.isdigit() else 5
        else:
            content_text = raw
    content_html = markdown.markdown(content_text, extensions=['extra', 'codehilite'])
    return render_template(
        "article.html",
        article_title=title,
        article_category=category,
        author_name=author_name,
        author_initial=author_name[0].upper() if author_name else "B",
        author_bio=author_bio,
        publish_date=publish_date,
        read_time=read_time,
        tags=tags,
        content=content_html
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
"""

with open(BASE / "server.py", "w", encoding="utf-8") as f:
    f.write(server_code)
print("✓ server.py written")

# ── Install dependencies ──────────────────────────────
requirements = [
    "flask>=2.3",
    "markdown>=3.4",
    "python-dotenv>=1.0",
]
with open(SCRIPTS / "requirements.txt", "w") as f:
    f.write("\n".join(requirements))

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(SCRIPTS / "requirements.txt")])
    print("✓ Dependencies installed")
except subprocess.CalledProcessError:
    print("⚠️  Could not auto-install. Please run: pip install -r scripts/requirements.txt")

print("\n✅ Blogsphere_v2 is ready!")
print("Run: python server.py")
print("Then open http://localhost:8080")