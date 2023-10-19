# shift_scheduler
A dynamic and automated scheduling Flask based webapp tailored designed to seamlessly integrate with "API Healthcare"

```
shift_scheduler
├─ .gitignore
├─ LICENSE
├─ README.md
├─ app
│  ├─ __init__.py
│  ├─ blueprints
│  │  ├─ auth
│  │  │  ├─ __init__.py
│  │  │  ├─ forms.py
│  │  │  ├─ routes.py
│  │  │  └─ templates
│  │  │     ├─ login.html
│  │  │     └─ register.html
│  │  └─ main
│  │     ├─ __init__.py
│  │     ├─ routes.py
│  │     └─ templates
│  │        └─ index.html
│  ├─ commands
│  ├─ database
│  │  ├─ __init__.py
│  │  ├─ db_operations.py
│  │  └─ queries
│  │     └─ get_shift_codes.sql
│  ├─ forms
│  │  └─ __init__.py
│  ├─ media
│  │  ├─ ...
│  │  └─ jinja-swipe-bootstrap-5-screen.png
│  ├─ models
│  │  ├─ __init__.py
│  │  └─ user.py
│  ├─ static
│  │  ├─ __init__.py
│  │  ├─ assets
│  │  │  ├─ css
│  │  │  │  ├─ swipe.css
│  │  │  │  └─ swipe.min.css
│  │  │  ├─ img
│  │  │  │  ├─ clients
│  │  │  │  │  ├─ airbnb.svg
│  │  │  │  │  ├─ business-school.svg
│  │  │  │  │  ├─ corsair.svg
│  │  │  │  │  ├─ docker.svg
│  │  │  │  │  ├─ ebay.svg
│  │  │  │  │  ├─ elastic.svg
│  │  │  │  │  ├─ forbes.svg
│  │  │  │  │  ├─ google.svg
│  │  │  │  │  ├─ northwestern.svg
│  │  │  │  │  ├─ paypal.svg
│  │  │  │  │  ├─ pinterest.svg
│  │  │  │  │  └─ university-of-chicago.svg
│  │  │  │  ├─ dark.svg
│  │  │  │  ├─ favicon
│  │  │  │  │  ├─ android-chrome-192x192.png
│  │  │  │  │  ├─ android-chrome-512x512.png
│  │  │  │  │  ├─ apple-touch-icon.png
│  │  │  │  │  ├─ browserconfig.xml
│  │  │  │  │  ├─ favicon-16x16.png
│  │  │  │  │  ├─ favicon-32x32.png
│  │  │  │  │  ├─ favicon.ico
│  │  │  │  │  ├─ manifest.json
│  │  │  │  │  ├─ mstile-150x150.png
│  │  │  │  │  ├─ safari-pinned-tab.svg
│  │  │  │  │  └─ site.webmanifest
│  │  │  │  ├─ illustrations
│  │  │  │  │  ├─ 404.svg
│  │  │  │  │  ├─ 500.svg
│  │  │  │  │  ├─ login.svg
│  │  │  │  │  ├─ scene-2.svg
│  │  │  │  │  ├─ scene-3.svg
│  │  │  │  │  └─ scene.svg
│  │  │  │  ├─ light.svg
│  │  │  │  └─ themesberg.svg
│  │  │  ├─ js
│  │  │  │  └─ swipe.js
│  │  │  ├─ scss
│  │  │  │  └─ ...
│  │  │  └─ vendor
│  │  │     └─ ...
│  │  └─ styles.css
│  ├─ templates
│  │  ├─ __init__.py
│  │  ├─ auth
│  │  ├─ includes
│  │  │  ├─ footer.html
│  │  │  ├─ navigation.html
│  │  │  ├─ scripts.html
│  │  │  └─ sidebar.html
│  │  ├─ layouts
│  │  │  ├─ base-fullscreen.html
│  │  │  └─ base.html
│  │  ├─ page-403.html
│  │  ├─ page-404.html
│  │  ├─ page-500.html
│  │  ├─ schedule.html
│  │  ├─ upload.html
│  │  └─ views.py
│  ├─ utils
│  │  └─ __init__.py
│  └─ views
│     └─ __init__.py
├─ migrations
│  ├─ README
│  ├─ alembic.ini
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions
│     ├─ 2f1e0b35fd7c_updated_user_model_for_password_hashing.py
│     └─ 79d15448e3eb_init_db.py
├─ requirements.txt
└─ run.py

```