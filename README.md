# Đồ án Nhập Môn Dữ Liệu Lớn - Admin Dashboard

Dự án này là trang Quản trị Hệ thống (Admin Dashboard) đóng vai trò là giao diện tương tác (GUI) cho hệ sinh thái Big Data (Hadoop, MapReduce, Sqoop) và Cơ sở dữ liệu MySQL.

Hệ thống được thiết kế theo mô hình client-server bao gồm:
- **Frontend:** ReactJS (Vite), TailwindCSS, Recharts.
- **Backend:** Python Django, Django REST Framework, Paramiko (điều khiển SSH).
- **Crawler:** Chứa mã nguồn Scrapy (đã có sẵn của bạn).

## 1. Yêu cầu hệ thống (Prerequisites)

- Node.js (phiên bản 16 trở lên) - Dùng để chạy Frontend
- Python (phiên bản 3.9 trở lên) - Dùng để chạy Backend
- Máy ảo VMware Ubuntu chạy cụm Hadoop (Single Node hoặc Cluster đa Node).
- Cơ sở dữ liệu MySQL Server (cài trên máy Host Windows).

---

## 2. Hướng dẫn khởi chạy Backend (Django)

Backend xử lý các logic kết nối đến MySQL và gọi lệnh SSH tới máy ảo Ubuntu.

**Bước 1:** Mở terminal (PowerShell hoặc CMD) và trỏ vào thư mục `backend`:
```bash
cd backend
```

**Bước 2:** Kích hoạt môi trường ảo (Virtual Environment):
- Trên Windows PowerShell:
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- Trên Windows CMD:
  ```cmd
  .\venv\Scripts\activate.bat
  ```

**Bước 3:** Khởi chạy server Django:
```bash
python manage.py runserver
```
*Server Backend sẽ chạy ở địa chỉ: http://localhost:8000*

**Lưu ý cấu hình SSH:**
Để API MapReduce / Sqoop hoạt động, bạn cần cấu hình lại IP máy ảo và username trong file `backend/core_api/utils/hadoop_ssh.py` và đảm bảo đã thiết lập đăng nhập SSH không cần mật khẩu (Pubkey Authentication).

---

## 3. Hướng dẫn khởi chạy Frontend (React)

Frontend là giao diện người dùng trực quan hiển thị Dashboard và các biểu đồ phân tích.

**Bước 1:** Mở một terminal mới (để không đụng với terminal của Backend) và trỏ vào thư mục `frontend`:
```bash
cd frontend
```

**Bước 2:** Cài đặt các gói thư viện (nếu chưa cài):
```bash
npm install
```

**Bước 3:** Khởi chạy server React ở chế độ phát triển (Dev Mode):
```bash
npm run dev
```
*Server Frontend sẽ chạy ở địa chỉ: http://localhost:5173 (bạn có thể click vào link trong terminal hoặc mở trình duyệt web lên và dán vào)*

---

## 4. Cấu trúc thư mục hiện tại

```text
bigdata_project/
├── backend/                       # Source code Django Backend API
│   ├── backend/                   # Settings, URLs cấu hình chính
│   ├── core_api/                  # App chứa logic gọi Hadoop SSH, Views
│   ├── venv/                      # Môi trường ảo chứa thư viện Python
│   └── manage.py                  # File khởi chạy server Django
│
├── frontend/                      # Source code ReactJS Frontend
│   ├── src/                       
│   │   ├── pages/                 # Chứa các giao diện chính (Dashboard.jsx)
│   │   ├── App.jsx                # Component gốc
│   │   └── index.css              # File style chứa Tailwind
│   ├── package.json               # Quản lý thư viện Node.js
│   ├── tailwind.config.js         # Cấu hình TailwindCSS
│   └── vite.config.js             # Cấu hình Vite
│
├── crawler/                       # (Của bạn) Thư mục chứa code Scrapy
├── data/                          # (Của bạn) Lưu trữ data thô
├── database/                      # (Của bạn) Lưu trữ script SQL
└── README.md                      # File hướng dẫn sử dụng này
```

---

*Được xây dựng phục vụ cho đồ án môn học.*
