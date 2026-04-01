from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
from .face_utils import save_face_photo, verify_face
from voting.models import Voter
import json

# Create your views here.

def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            # Face verification for voters only
            if user.user_type == '2':
                try:
                    voter = Voter.objects.get(admin=user)
                    if voter.face_photo:
                        face_data = request.POST.get('face_data')
                        if not face_data:
                            messages.error(request, "Please capture your face photo to login!")
                            return redirect("/")
                        if not verify_face(face_data, str(voter.face_photo)):
                            messages.error(request, "Face verification failed! Please try again.")
                            return redirect("/")
                except Voter.DoesNotExist:
                    pass

            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()

            # Save face photo if provided
            face_data = request.POST.get('face_data')
            if face_data:
                filename = f"face_{user.id}.jpg"
                face_path = save_face_photo(face_data, filename)
                voter.face_photo = face_path
                voter.save()

            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")

    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))