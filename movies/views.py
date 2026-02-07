from django.shortcuts import render

# HOMEPAGE FUNCTION:
def index_devolution(request):
    return render(request, 'movies/index.html') # return the homepage (index by default standar)