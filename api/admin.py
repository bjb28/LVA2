"""LVA2 API Admin.py."""
# Third-Party Libraries
from django.apps import apps
from django.contrib import admin

models = apps.get_models()

for model in models:
    if model._meta.app_label == "api":
        admin.site.register(model)
