# HandMagic - Gesture Effects App

Ứng dụng desktop cho phép bạn tạo hiệu ứng hình ảnh theo cử chỉ tay thời gian thực.  
Sử dụng camera, MediaPipe để phát hiện tay và OpenCV + PyQt5 để hiển thị hiệu ứng như: pháo hoa, lửa, cầu vồng, tia lửa...

## 🎯 Tính năng

- ✋ Nhận diện cử chỉ tay để kích hoạt hiệu ứng.
- 🔥 Các hiệu ứng thú vị: Fireworks, Sparkles, Fire, Rainbow Trail.
- 🎛 Tùy chỉnh độ sáng, tương phản và cường độ hiệu ứng.
- 🧠 Gán phím (1-9) để nhanh chóng chọn hiệu ứng yêu thích.
- 📷 Giao diện trực quan hiển thị video trực tiếp từ camera.

## 🧱 Công nghệ sử dụng

- Python 3.x
- OpenCV
- MediaPipe
- PyQt5
- NumPy

## 🚀 Cách chạy ứng dụng

1. Cài đặt thư viện cần thiết:

```pip install opencv-python mediapipe PyQt5 numpy```

2. Chạy file chính:

```python main.py```

## 🎮 Điều khiển

- Mở camera: Nhấn nút **Start Camera**
- Chọn hiệu ứng: Chọn từ dropdown hoặc gán phím (1–9)
- Đưa tay trước camera, xòe tay ra để kích hoạt hiệu ứng.
- Đóng tay lại để tắt hiệu ứng.

## 🧠 Phím tắt tùy chỉnh

Bạn có thể vào menu **Settings → Configure Key Bindings** để gán nhanh hiệu ứng cho các phím số từ 1–9.

## 📁 Cấu trúc thư mục

IPR/  
├── main.py — File chạy chính   
├── effects/ — Các hiệu ứng riêng biệt (fireworks.py, snow.py, hearts.py,...)   
├── images/ — Thư mục chứa icon hoặc hình ảnh  
├── requirements.txt — Danh sách thư viện cần cài  
└── README.md  


## 📌 Lưu ý

- Cần bật quyền truy cập camera.
- Ứng dụng chạy tốt nhất khi bàn tay nằm trong khung hình rõ ràng và đủ sáng.

---
