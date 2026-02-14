from django.shortcuts import render
from .models import blog
from django.core.paginator import Paginator
def blog1(request,page):
    blogs=blog.objects.all()
    page_product1=Paginator(blogs,2)
    page_product=page_product1.get_page(page)
    total_page=page_product1.page_range
    ifprev=page_product.has_previous()
    ifnext=page_product.has_next()
    prevpage=page_product.previous_page_number
    nextpage=page_product.next_page_number
    c={
        'page_range':total_page,
        'ifprev':ifprev,
        "ifnext":ifnext,
        "nextpage":nextpage,
        "prevpage":prevpage,
        'results': page_product,
    }
    return render(request,"bloggrid.html",c)