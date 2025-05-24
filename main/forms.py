from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Job, Application
from allauth.account.forms import SignupForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    USER_TYPE_CHOICES = [
        ("applicant", "Ứng viên"),
        ("employer", "Nhà tuyển dụng"),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Bạn là"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='Tên')
    last_name = forms.CharField(max_length=30, required=False, label='Họ')
    company_name = forms.CharField(max_length=100, required=False, label='Tên công ty')
    
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'company_name', 'phone_number', 'address', 'bio', 'profile_picture', 'cv']
        labels = {
            'phone_number': 'Số điện thoại',
            'address': 'Địa chỉ',
            'bio': 'Giới thiệu',
            'profile_picture': 'Ảnh đại diện',
            'cv': 'CV'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            
        # Ẩn các trường không cần thiết dựa vào loại tài khoản
        if self.instance.user_type == 'employer':
            self.fields['first_name'].widget = forms.HiddenInput()
            self.fields['last_name'].widget = forms.HiddenInput()
            self.fields['cv'].widget = forms.HiddenInput()
        else:
            self.fields['company_name'].widget = forms.HiddenInput()
            
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        # Chỉ cập nhật first_name và last_name cho ứng viên
        if profile.user_type == 'applicant':
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
            
        if commit:
            profile.save()
        return profile

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'salary_range', 'is_active']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = []  # Không cần thêm trường, chỉ cần job_id và user_id

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class CustomSignupForm(SignupForm):
    user_type = forms.ChoiceField(choices=Profile.USER_TYPE_CHOICES, widget=forms.RadioSelect)
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=200, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        
        user_type = self.cleaned_data.get('user_type')
        company_name = self.cleaned_data.get('company_name')
        phone = self.cleaned_data.get('phone')
        address = self.cleaned_data.get('address')
        bio = self.cleaned_data.get('bio')

        Profile.objects.create(
            user=user,
            user_type=user_type,
            company_name=company_name if user_type == 'employer' else None,
            phone=phone,
            address=address,
            bio=bio
        )
        return user 