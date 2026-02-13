# IMPORTS: 

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.forms import UserChangeForm # DEUD! | future changes


# VIEWS:

# registration::

# In case the request is a user POSTING information to the server, we put the information in the slots automatically
# and save the form in a variable 'register_formulary'. In case it's valid, we push it to the database. If the formulary
# is incorrect, we reset it. Finally we serve the html and the form variable

def register_user(request):
    if request.method == 'POST':
        register_formulary = UserCreationForm(request.POST)
        
        if register_formulary.is_valid():
            register_formulary.save()

            # login user
            return redirect('')
    
    else:
        register_formulary = UserCreationForm
