# Thông tin sinh viên

**Tên** : Mạc Văn Hải An

**MSSV** : 24127316

**Ngành** : Công Nghệ Thông Tin

**Trường** : Trường Đại Học Khoa Học Tự Nhiên - ĐHQG TPHCM

# Ứng dụng Lập kế hoạch Du lịch bằng LLM (Ollama + Streamlit)

Dự án này xây dựng ứng dụng lập kế hoạch hành trình du lịch, cho phép người dùng nhập thành phố xuất phát, thành phố đến, ngày đi, sở thích (food/museums/nature/nightlife), và nhịp độ du lịch (relaxed/normal/tight).  
Ứng dụng sẽ tạo ra lịch trình từng ngày (sáng/chiều/tối) bằng mô hình LLM (Mistral) thông qua Ollama.

---

## Cấu trúc thư mục

<img width="368" height="477" alt="image" src="https://github.com/user-attachments/assets/383f0041-8e63-453d-97e4-ddfb7959d636" />


## Tính năng
- Hệ thống đăng ký và đăng nhập người dùng cơ bản
- Tạo lịch trình du lịch bằng mô hình LLM (Mistral qua Ollama)
- Lưu lịch sử chat và kế hoạch vào file JSON (`history.json`)
- Giao diện đơn giản sử dụng Streamlit
- Backend sử dụng Flask xử lý yêu cầu với LLM
- Dữ liệu người dùng và lịch sử lưu trong file JSON (`users.json`, `history.json`)

---

## Hướng dẫn cài đặt

### 1. Clone repo về máy

git clone https://github.com/mvhan/Travel-Itinerary-Planner.git

cd Travel-Itinerary-Planner

### 2. (Tùy chọn) Tạo và kích hoạt môi trường ảo Python

python -m venv venv

// Trên macOS/Linux:

source venv/bin/activate

// Trên Windows:

venv\Scripts\activate

### 3. Cài đặt các thư viện Python cần thiết

pip install -r requirements.txt

### 4. Cài đặt Ollama và tải mô hình

Tải và cài đặt Ollama tại https://ollama.com/download

Sau khi cài đặt, chạy lệnh:

ollama pull mistral

## Cách chạy ứng dụng
### Khởi động backend server

cd backend

python server.py

### Khởi động frontend (Streamlit)

cd frontend

streamlit run app.py

Mở trình duyệt và truy cập địa chỉ được hiển thị (thường là http://localhost:8501

## Lưu ý

Lần đầu chạy, Ollama có thể mất thời gian tải mô hình.

Tài khoản người dùng và lịch sử được lưu trong các file JSON trong thư mục backend.

Nếu muốn reset người dùng hoặc lịch sử, bạn có thể xóa hoặc chỉnh sửa users.json và history.json.

## Liên hệ
Nếu gặp vấn đề, vui lòng liên hệ: hanparker0915@gmail.com

