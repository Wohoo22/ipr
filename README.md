---

# HandMagic - Gesture Effects App

A desktop application that lets you trigger real-time visual effects using hand gestures.  
It uses a webcam and MediaPipe for hand detection, and displays effects like fireworks, flames, rainbow trails, and sparkles using OpenCV and PyQt5.

## 🎯 Features

- ✋ Detects hand gestures to trigger visual effects.
- 🔥 Cool effects: Fireworks, Sparkles, Fire, Rainbow Trail.
- 🎛 Adjustable brightness, contrast, and effect intensity.
- 🧠 Hotkey support (1–9) to quickly switch between favorite effects.
- 📷 Intuitive interface with real-time camera feed display.

## 🧱 Technologies Used

- Python 3.x  
- OpenCV  
- MediaPipe  
- PyQt5  
- NumPy  

## 🚀 How to Run the App

1. Install required libraries:

```bash
pip install opencv-python mediapipe PyQt5 numpy
```

2. Run the main file:

```bash
python main.py
```

## 🎮 Controls

- Start camera: Click the **Start Camera** button  
- Select effects: Choose from dropdown or use hotkeys (1–9)  
- Show your hand to the camera and open your palm to trigger an effect  
- Close your hand to turn off the effect  

## 🧠 Custom Hotkeys

You can assign effects to number keys (1–9) via the **Settings → Configure Key Bindings** menu for quick access.

## 📁 Folder Structure

```
IPR/  
├── main.py              # Main entry point  
├── effects/             # Contains individual effects (fireworks.py, snow.py, hearts.py, etc.)  
├── images/              # Icons or image assets  
├── requirements.txt     # List of required libraries  
└── README.md  
```

## 📌 Notes

- Make sure to grant camera access.  
- The app works best when the hand is clearly visible and well-lit in the camera frame.

---
