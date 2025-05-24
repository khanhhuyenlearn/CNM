from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile, Job

class Command(BaseCommand):
    help = 'Thêm các công việc mẫu vào database'

    def handle(self, *args, **kwargs):
        # Tạo tài khoản nhà tuyển dụng mẫu nếu chưa tồn tại
        employer, created = User.objects.get_or_create(
            username='employer1',
            defaults={
                'email': 'employer1@example.com',
                'first_name': 'Công ty',
                'last_name': 'ABC'
            }
        )
        if created:
            employer.set_password('password123')
            employer.save()
            Profile.objects.create(
                user=employer,
                user_type='employer',
                company_name='Công ty TNHH ABC',
                bio='Công ty công nghệ hàng đầu Việt Nam'
            )

        # Danh sách công việc mẫu
        sample_jobs = [
            {
                'title': 'Lập Trình Viên Python Backend',
                'description': 'Tìm kiếm lập trình viên Python Backend có kinh nghiệm để tham gia phát triển các ứng dụng web. Công việc bao gồm:\n- Phát triển và duy trì các API RESTful\n- Tối ưu hóa hiệu suất cơ sở dữ liệu\n- Làm việc với Django/Flask\n- Tích hợp với các dịch vụ bên thứ ba',
                'requirements': '- Kinh nghiệm 2+ năm với Python\n- Thành thạo Django/Flask\n- Hiểu biết về RESTful APIs\n- Kinh nghiệm với PostgreSQL/MySQL\n- Tiếng Anh giao tiếp tốt',
                'location': 'Hà Nội',
                'salary_range': '15-25 triệu/tháng'
            },
            {
                'title': 'Frontend Developer (React)',
                'description': 'Tuyển dụng Frontend Developer có kinh nghiệm với React để phát triển giao diện người dùng. Công việc bao gồm:\n- Phát triển UI/UX responsive\n- Tối ưu hóa hiệu suất frontend\n- Làm việc với REST APIs\n- Tích hợp với các thư viện UI',
                'requirements': '- Kinh nghiệm 2+ năm với React\n- Thành thạo JavaScript/TypeScript\n- Hiểu biết về HTML5, CSS3\n- Kinh nghiệm với Redux/Context API\n- Tiếng Anh giao tiếp tốt',
                'location': 'TP. Hồ Chí Minh',
                'salary_range': '18-28 triệu/tháng'
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Tuyển dụng DevOps Engineer để quản lý và tự động hóa quy trình phát triển phần mềm. Công việc bao gồm:\n- Quản lý và tối ưu hóa hệ thống cloud\n- Tự động hóa CI/CD\n- Giám sát và bảo mật hệ thống\n- Tối ưu hóa hiệu suất',
                'requirements': '- Kinh nghiệm với AWS/Azure/GCP\n- Thành thạo Docker, Kubernetes\n- Kinh nghiệm với CI/CD tools\n- Hiểu biết về Linux\n- Tiếng Anh giao tiếp tốt',
                'location': 'Hà Nội',
                'salary_range': '25-35 triệu/tháng'
            },
            {
                'title': 'Data Scientist',
                'description': 'Tuyển dụng Data Scientist để phân tích dữ liệu và xây dựng các mô hình machine learning. Công việc bao gồm:\n- Phân tích dữ liệu lớn\n- Xây dựng và triển khai mô hình ML\n- Tối ưu hóa thuật toán\n- Báo cáo và trình bày kết quả',
                'requirements': '- Kinh nghiệm với Python/R\n- Thành thạo các thư viện ML (TensorFlow, PyTorch)\n- Hiểu biết về thống kê\n- Kinh nghiệm với SQL\n- Tiếng Anh giao tiếp tốt',
                'location': 'TP. Hồ Chí Minh',
                'salary_range': '20-30 triệu/tháng'
            },
            {
                'title': 'Mobile Developer (Flutter)',
                'description': 'Tuyển dụng Mobile Developer có kinh nghiệm với Flutter để phát triển ứng dụng di động. Công việc bao gồm:\n- Phát triển ứng dụng cross-platform\n- Tối ưu hóa hiệu suất\n- Tích hợp với backend\n- Đảm bảo chất lượng code',
                'requirements': '- Kinh nghiệm 2+ năm với Flutter\n- Thành thạo Dart\n- Hiểu biết về iOS/Android\n- Kinh nghiệm với state management\n- Tiếng Anh giao tiếp tốt',
                'location': 'Đà Nẵng',
                'salary_range': '15-25 triệu/tháng'
            }
        ]

        # Thêm các công việc vào database
        for job_data in sample_jobs:
            Job.objects.create(
                recruiter=employer,
                **job_data
            )

        self.stdout.write(self.style.SUCCESS('Đã thêm thành công các công việc mẫu!')) 