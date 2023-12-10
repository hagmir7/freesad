from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.contrib import messages
import requests
import json
from django.utils.translation import gettext as _


class LinkCreateView(View):
    template_name = (
        "link/list.html"  # Replace 'your_template_name' with the actual template name
    )

    def get(self, request):
        form = LinkForm()
        query = request.GET.get("query")
        if query:
            name = Link.objects.filter(name__icontains=query)
            custom = Link.objects.filter(custom__icontains=query)
            link = Link.objects.filter(link__icontains=query)
            results = link | name | custom
        else:
            results = Link.objects.all().order_by("-date")
        paginator = Paginator(results, 30)
        page_number = request.GET.get("page")
        links = paginator.get_page(page_number)
        context = {"form": form, "links": links}
        return render(request, self.template_name, context)

    def post(self, request):
        form = LinkForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            long_url = form.cleaned_data.get("link")
            name = form.cleaned_data.get("name")
            custom = form.cleaned_data.get("custom")
            start = form.cleaned_data.get("start")
            end = form.cleaned_data.get("end")

            url = "https://enshom.link/api/url/add"
            headers = {
                "Authorization": "Bearer 217c8b20829a5bcdf77c28d46f8dd328",
                "Content-Type": "application/json",
            }

            for i in range(start, end + 1, 1):
                data = {
                    "url": long_url,
                    "custom": f"{custom}-{i}",
                    "type": "Direct",
                    "metatitle": name,
                    "metadescription": name,
                    # Exclude the file from the JSON data
                }
                response = requests.post(url, headers=headers, data=json.dumps(data))

                if response.status_code == 200:
                    print(f"{custom}-{i}")
                    print(response.json())
                else:
                    print(f"Request failed with status code: {response.status_code}")

            messages.success(request, _("Link created successfully"))
            return redirect(request.META.get("HTTP_REFERER", "/"))

        return render(request, self.template_name, {"form": form})


def delete_link(request):
    if request.method == "POST":
        selected_links = request.POST.getlist("link[]")
        print(selected_links)
        if selected_links:
            Link.objects.filter(pk__in=selected_links).delete()
            messages.success(request, _("Links deleted successfully"))
        else:
            messages.warning(request, _("No links selected"))

        # Redirect to a specific URL or use a default if HTTP_REFERER is not available
        return redirect(request.META.get("HTTP_REFERER", "/"))

    messages.warning(request, _("Failed to delete links"))
    return redirect(request.META.get("HTTP_REFERER"))


def update_link(request, id):
    link = Link.objects.get(id=id)
    form = LinkForm(instance=link)
    if request.method == "POST":
        form = LinkForm(request.POST, request.FILES, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, _("Link updated successfully"))
            return redirect("/tools/links")

    context = {"form": form}
    return render(request, "link/form.html", context)


def create_facebook_group(request):
    

    if request.method == "POST":
        form = FacebookGroupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        form = FacebookGroupForm()
        query = request.GET.get("query")
        if query:
            name = FacebookGroup.objects.filter(name__icontains=query)
            description = FacebookGroup.objects.filter(description__icontains=query)
            results = name | description
        else:
            results = FacebookGroup.objects.all().order_by("-date")
        paginator = Paginator(results, 30)
        page_number = request.GET.get("page")
        groups = paginator.get_page(page_number)

    return render(request, "group/list.html", {"form": form, "groups": groups})


def create_account(request):
    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        form = AccountForm()

    return render(request, "create_account.html", {"form": form})


def update_facebook_group(request, pk):
    facebook_group = get_object_or_404(FacebookGroup, pk=pk)

    if request.method == "POST":
        form = FacebookGroupForm(request.POST, request.FILES, instance=facebook_group)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        form = FacebookGroupForm(instance=facebook_group)

    return render(
        request,
        "update_facebook_group.html",
        {"form": form, "facebook_group": facebook_group},
    )


def update_account(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        form = AccountForm(instance=account)

    return render(request, "update_account.html", {"form": form, "account": account})


def delete_facebook_group(request, pk):
    facebook_group = get_object_or_404(FacebookGroup, pk=pk)

    if request.method == "POST":
        facebook_group.delete()
        return redirect(request.META.get("HTTP_REFERER"))

    return render(
        request, "delete_facebook_group.html", {"facebook_group": facebook_group}
    )


def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        account.delete()
        return redirect(request.META.get("HTTP_REFERER"))

    return render(request, "delete_account.html", {"account": account})
