from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Profile, Job, Application, Notification
from .forms import UserRegistrationForm, ProfileForm, JobForm, ApplicationForm, ApplicationStatusForm
from django.http import HttpResponseRedirect, FileResponse
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.views.generic import View
from django.conf import settings
import os
import logging
logger = logging.getLogger(__name__)

def home(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'main/home.html', {'jobs': jobs})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user_type = form.cleaned_data['user_type']
            logger.debug(f"Registering user {user.username} with user_type: {user_type}")
            # Kiểm tra user_type hợp lệ
            if user_type not in dict(Profile.USER_TYPE_CHOICES).keys():
                logger.error(f"Invalid user_type: {user_type}")
                messages.error(request, 'Loại tài khoản không hợp lệ!')
                return redirect('register')
            Profile.objects.create(user=user, user_type=user_type)
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')
        else:
            logger.debug(f"Form errors: {form.errors}")
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Bỏ qua xác thực CV nếu người dùng là admin
            if request.user.is_staff or request.user.is_superuser:
                # Lưu form mà không yêu cầu CV
                profile_instance = form.save(commit=False)
                profile_instance.save()
            else:
                form.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật thành công!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'profile_user': request.user,
        'is_own_profile': True
    }
    
    return render(request, 'main/profile.html', context)

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    return render(request, 'main/job_list.html', {'jobs': jobs})

@login_required
def create_job(request):
    if request.user.profile.user_type != 'employer':
        messages.error(request, "Chỉ nhà tuyển dụng mới có thể đăng tin tuyển dụng!")
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, 'Đăng tin tuyển dụng thành công!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'main/create_job.html', {'form': form})

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    has_applied = Application.objects.filter(job=job, applicant=request.user).exists() if request.user.is_authenticated else False
    
    is_recruiter = request.user.is_authenticated and request.user == job.recruiter
    applications = None
    
    if is_recruiter:
        applications = Application.objects.filter(job=job)
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_recruiter': is_recruiter,
        'applications': applications,
    }
    
    return render(request, 'main/job_detail.html', context)

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Kiểm tra nếu người dùng là admin (is_staff hoặc is_superuser)
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Tài khoản admin không được phép nộp đơn ứng tuyển!")
        return redirect('job_detail', job_id=job.id)
    
    # Kiểm tra nếu người dùng không phải là applicant
    if request.user.profile.user_type != 'applicant':
        messages.error(request, "Chỉ ứng viên mới có thể nộp đơn ứng tuyển!")
        return redirect('job_detail', job_id=job.id)
    
    # Kiểm tra xem user đã apply job này chưa
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'Bạn đã nộp đơn cho công việc này rồi.')
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Tạo thông báo cho người đăng tin
            Notification.objects.create(
                user=job.recruiter,
                message=f"Ứng viên {request.user.username} đã ứng tuyển vào vị trí {job.title}."
            )
            
            messages.success(request, 'Nộp đơn ứng tuyển thành công!')
            return redirect('my_applications')
    else:
        form = ApplicationForm()
    
    return render(request, 'main/apply_job.html', {'form': form, 'job': job})

@login_required
def post_job(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền đăng tuyển dụng!')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, 'Đăng tuyển dụng thành công!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'main/post_job.html', {'form': form})

@login_required
def my_applications(request):
    if request.user.profile.user_type == 'employer':
        applications = Application.objects.filter(job__recruiter=request.user)
        template = 'main/employer_applications.html'
    else:
        # Chỉ hiển thị cho applicant, loại trừ admin
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, "Tài khoản admin không được phép xem danh sách ứng tuyển!")
            return redirect('home')
        applications = Application.objects.filter(applicant=request.user)
        template = 'main/my_applications.html'
    
    return render(request, template, {'applications': applications})

@login_required
def manage_applications(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền quản lý hồ sơ!')
        return redirect('home')
    
    jobs = Job.objects.filter(recruiter=request.user)
    applications = Application.objects.filter(job__in=jobs)
    return render(request, 'main/manage_applications.html', {'applications': applications})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    job = application.job
    
    # Chỉ cho phép nhà tuyển dụng (recruiter) cập nhật trạng thái
    if request.user != job.recruiter:
        messages.error(request, 'Bạn không có quyền cập nhật trạng thái ứng tuyển này!')
        return redirect('employer_applications')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = application.status
            application.status = new_status
            application.save()
            
            # Tạo thông báo cho ứng viên
            Notification.objects.create(
                user=application.applicant,
                message=f'Trạng thái ứng tuyển của bạn cho vị trí {job.title} đã được cập nhật thành {application.get_status_display()}.'
            )
            
            messages.success(request, f'Đã cập nhật trạng thái ứng tuyển thành {application.get_status_display()}')
        else:
            messages.error(request, f'Trạng thái "{new_status}" không hợp lệ!')
    
    return redirect('employer_applications')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/notifications.html', {'notifications': notifications})

@receiver(user_signed_up)
def user_signed_up_signal(request, user, **kwargs):
    """
    Xử lý sau khi người dùng đăng ký qua allauth
    """
    if request and 'user_type' in request.POST:
        user_type = request.POST.get('user_type')
        logger.debug(f"Signal user_signed_up for {user.username} with user_type: {user_type}")
        if user_type not in dict(Profile.USER_TYPE_CHOICES).keys():
            logger.error(f"Invalid user_type in signal: {user_type}")
            user_type = 'applicant'  # Mặc định là applicant nếu giá trị không hợp lệ
        try:
            profile = user.profile
            profile.user_type = user_type
            profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=user, user_type=user_type)

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Kiểm tra xem người dùng có phải là người đăng tin
    if request.user != job.recruiter:
        messages.error(request, "Bạn không có quyền chỉnh sửa tin tuyển dụng này!")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật tin tuyển dụng thành công!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'main/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Kiểm tra xem người dùng có phải là người đăng tin
    if request.user != job.recruiter:
        messages.error(request, "Bạn không có quyền xóa tin tuyển dụng này!")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Xóa tin tuyển dụng thành công!')
        return redirect('profile')
    
    return render(request, 'main/delete_job.html', {'job': job})

@login_required
def view_applicant_profile(request, user_id):
    # Kiểm tra xem người dùng có phải là nhà tuyển dụng
    if request.user.profile.user_type != 'employer':
        messages.error(request, "Chỉ nhà tuyển dụng mới có thể xem thông tin ứng viên!")
        return redirect('home')
        
    applicant = get_object_or_404(User, id=user_id)
    
    # Kiểm tra xem ứng viên có đã ứng tuyển vào công việc của nhà tuyển dụng không
    applications = Application.objects.filter(
        applicant=applicant,
        job__recruiter=request.user
    )
    
    if not applications.exists():
        messages.error(request, "Bạn không có quyền xem thông tin của ứng viên này!")
        return redirect('profile')
    
    return render(request, 'main/applicant_profile.html', {
        'applicant': applicant,
        'applications': applications
    })

@login_required
def view_employer_profile(request, user_id):
    employer = get_object_or_404(User, id=user_id)
    
    # Kiểm tra xem user có phải là nhà tuyển dụng không
    if employer.profile.user_type != 'employer':
        messages.error(request, "Người dùng này không phải là nhà tuyển dụng!")
        return redirect('home')
    
    jobs = Job.objects.filter(recruiter=employer, is_active=True)
    
    return render(request, 'main/employer_public_profile.html', {
        'employer': employer,
        'jobs': jobs
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.status = 'read'
    notification.save()
    
    # Nếu có tham số next trong URL, chuyển hướng đến URL đó
    next_url = request.GET.get('next', 'notifications')
    if next_url.startswith('http'):
        next_url = 'notifications'  # Tránh open redirect vulnerability
    
    return redirect(next_url)

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, status='unread').update(status='read')
    return redirect('notifications')

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=profile_user)
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_own_profile': False
    }
    response = render(request, 'main/profile.html', context)
    response['X-Frame-Options'] = 'ALLOWALL'
    return response

@login_required
def profile(request):
    context = {
        'profile_user': request.user,
        'profile': request.user.profile,
        'is_own_profile': True
    }
    return render(request, 'main/profile.html', context)

class PDFView(View):
    def get(self, request, path):
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['X-Frame-Options'] = 'ALLOWALL'
        return response

@login_required
def employer_applications(request):
    if request.user.profile.user_type != 'employer' and not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập trang này!')
        return redirect('home')

    if request.user.is_staff:
        jobs = Job.objects.all()
        applications = Application.objects.all()
    else:
        jobs = Job.objects.filter(recruiter=request.user)
        applications = Application.objects.filter(job__in=jobs)

    # Lọc theo trạng thái, công việc, ngày ứng tuyển nếu có
    status = request.GET.get('status')
    job_id = request.GET.get('job')
    date = request.GET.get('date')
    if status:
        applications = applications.filter(status=status)
    if job_id:
        applications = applications.filter(job_id=job_id)
    if date:
        applications = applications.filter(created_at__date=date)

    return render(request, 'main/employer_applications.html', {
        'jobs': jobs,
        'applications': applications,
    })
