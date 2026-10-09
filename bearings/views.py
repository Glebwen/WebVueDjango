from django.shortcuts import render
from django.http import HttpResponse
from typing import Any

from django.views.generic import TemplateView
from bearings.models import Client

# Create your views here.
class ShowClientsView(TemplateView):
    template_name = "clients/show_clients.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        
        return context