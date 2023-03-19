from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import File


# Files

def files(request):
    if request.user.is_authenticated :
        
        files = File.objects.filter(user=request.user).order_by('-created')
        context = {
            'files': files,
            'title': "Files"
        }
        return render(request, 'files.html', context)
    else:
        return render(request, '404.html')

def deleteFiles(request, id):
    file = get_object_or_404(File, id=id)
    if file.user == request.user:
        file.delete()
        messages.success(request, "File deleted successfully...")
        return redirect('/files')
    else:
        return render(request, '404.html')

