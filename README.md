# WASA Malawi Django Dashboard

Run locally:

```bash
python manage.py runserver 127.0.0.1:8051
```

The dashboard is a Django app that renders Plotly.js charts from the curated
baseline tables in `data.py`. Filters are handled with query parameters so
links remain shareable.
