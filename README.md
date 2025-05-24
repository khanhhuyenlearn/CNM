# Job Portal

Một nền tảng tuyển dụng trực tuyến được xây dựng bằng Django, cho phép nhà tuyển dụng đăng tin tuyển dụng và ứng viên có thể tìm kiếm, ứng tuyển vào các vị trí phù hợp.

## Tính năng

### Dành cho Nhà tuyển dụng
- Đăng tin tuyển dụng với thông tin chi tiết
- Quản lý các tin tuyển dụng (chỉnh sửa, xóa)
- Xem danh sách ứng viên đã ứng tuyển
- Quản lý hồ sơ công ty
- Xem CV của ứng viên trực tiếp trên web

### Dành cho Ứng viên
- Tìm kiếm việc làm
- Ứng tuyển vào các vị trí phù hợp
- Quản lý hồ sơ cá nhân
- Tải lên và quản lý CV
- Theo dõi trạng thái ứng tuyển

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/HTAnh2003/JobPortal_FinalCNM
cd JobPortal_FinalCNM
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

4. Thực hiện migrate database:
```bash
python manage.py migrate
```

5. Tạo tài khoản admin:
```bash
python manage.py createsuperuser
```

6. Chạy server:
```bash
python manage.py runserver
```

Truy cập http://localhost:8000 để sử dụng ứng dụng.

## Công nghệ sử dụng

- **Backend:** Django 5.0.3
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Authentication:** Django Allauth
- **File Storage:** Django File Storage

## Cấu trúc Project

```
job-portal/
├── jobportal/          # Project settings
├── main/              # Main application
│   ├── models.py      # Database models
│   ├── views.py       # View logic
│   ├── urls.py        # URL routing
│   └── forms.py       # Forms
├── templates/         # HTML templates
├── static/           # Static files
├── media/           # User uploaded files
└── requirements.txt  # Project dependencies
```

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.