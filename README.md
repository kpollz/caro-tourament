# Caro Tournament - Hướng dẫn cài đặt và chạy

## 1. Yêu cầu hệ thống
- Docker & Docker Compose (khuyến nghị)
- Hoặc: Python 3.10+, pip, PostgreSQL, Redis (nếu chạy local)

## 2. Chạy bằng Docker Compose (Khuyến nghị)

### Bước 1: Clone source code
```bash
git clone <repo-url>
cd caro-tourament
```

### Bước 2: Build và khởi động các service
```bash
docker-compose up --build
```
- Lệnh này sẽ tự động build image, cài đặt các dependencies, khởi tạo database, Redis và chạy server Django.

### Bước 2.1: Chạy migrate database (bắt buộc lần đầu hoặc khi thay đổi models)
Mở một terminal mới và chạy:
```bash
docker-compose exec web python manage.py migrate
```

### Bước 3: Truy cập ứng dụng
- Mở trình duyệt và truy cập: [http://localhost:8000](http://localhost:8000)

### Bước 4: Tạo tài khoản admin (lần đầu)
Mở một terminal mới và chạy:
```bash
docker-compose exec web python manage.py createsuperuser
```

## 3. Chạy local (không dùng Docker)

### Bước 1: Cài đặt Python, PostgreSQL, Redis
- Cài Python 3.10+, pip
- Cài PostgreSQL, tạo database `caro_db`, user `caro_user` (hoặc sửa lại trong `settings.py`)
- Cài Redis server

### Bước 2: Cài dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình database và Redis
- Sửa file `backend/caro_project/settings.py` cho đúng thông tin DB, Redis

### Bước 4: Chạy migrate và collectstatic
```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
```

### Bước 5: Chạy server
```bash
python manage.py runserver
```
Hoặc dùng Daphne/Uvicorn để chạy ASGI:
```bash
daphne caro_project.asgi:application
```

### Bước 6: Truy cập ứng dụng
- Mở trình duyệt và truy cập: [http://localhost:8000](http://localhost:8000)

## 4. Một số lệnh quản trị
- Tạo tài khoản admin:
  ```bash
  python manage.py createsuperuser
  ```
- Xem log container:
  ```bash
  docker-compose logs -f
  ```

## 5. Thông tin thêm
- Trang admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Sảnh chờ: [http://localhost:8000/lobby/](http://localhost:8000/lobby/)

## 6. Lưu ý
- Nếu gặp lỗi kết nối WebSocket, kiểm tra lại Redis, cấu hình Channels, hoặc port mapping Docker.
- Nếu migrate lỗi do model, hãy kiểm tra lại các trường mới thêm và migration.

---
Chúc bạn cài đặt và trải nghiệm game Caro thành công! 