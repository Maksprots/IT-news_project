from django.core.paginator import Paginator
from django.conf import settings


def make_paginator(objects, request):
    paginator = Paginator(objects, settings.NUMBER_OBJ_TO_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
