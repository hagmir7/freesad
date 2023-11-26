from django.shortcuts import render, redirect
from django.views import View
from .models import Link
from .forms import LinkForm
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
        contact_list = Link.objects.all().order_by("-date")
        paginator = Paginator(contact_list, 30)
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
    return redirect(request.META.get("HTTP_REFERER", "/"))


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
