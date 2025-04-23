import sys
import cv2
import numpy as np
import mediapipe as mp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QSlider, QGroupBox, QMenuBar, QMenu, QAction,
                             QInputDialog, QDialog, QFormLayout, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QImage, QPixmap
from effects import fireworks, sparkles, fire, rainbow


class KeyBindingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Key Binding")
        self.setFixedSize(300, 150)

        layout = QFormLayout()

        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Fireworks", "Sparkles", "Fire", "Rainbow Trail"])
        layout.addRow("Select Effect:", self.effect_combo)

        self.key_input = QLineEdit()
        self.key_input.setMaxLength(1)
        self.key_input.setPlaceholderText("Enter key (1–9)")
        layout.addRow("Choose Bind Key:", self.key_input)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_binding(self):
        return self.effect_combo.currentText(), self.key_input.text()


class HandMagicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HandMagic - Gesture Effects App")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize effects
        self.fire_effect = fire.FireEffect()
        self.sparkles_effect = sparkles.SparklesEffect()
        self.fireworks_effect = fireworks.FireworksEffect()
        self.rainbow_effect = rainbow.RainbowEffect()
        self.current_effect = None
        self.effect_intensity = 50

        # Image adjustment settings
        self.brightness_adjust = 0
        self.contrast_adjust = 1.0

        # Hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

        # Camera
        self.cap = None
        self.cam_width = 640
        self.cam_height = 480

        # Settings
        self.settings = QSettings("HandMagic", "GestureEffects")

        # Key bindings
        self.key_bindings = {}

        self.init_ui()
        self.init_camera()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)

        control_panel = QGroupBox("Effect Controls")
        control_layout = QVBoxLayout()

        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["No Effect", "Fireworks", "Sparkles", "Fire", "Rainbow Trail"])
        self.effect_combo.currentTextChanged.connect(self.change_effect)

        intensity_label = QLabel("Effect Intensity:")
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(10, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.update_intensity)

        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(self.settings.value("brightness", 0, type=int))
        self.brightness_slider.valueChanged.connect(self.update_camera_settings)

        contrast_label = QLabel("Contrast:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(self.settings.value("contrast", 100, type=int))
        self.contrast_slider.valueChanged.connect(self.update_camera_settings)
        self.contrast_adjust = self.contrast_slider.value() / 100

        reset_btn = QPushButton("Reset Adjustments")
        reset_btn.clicked.connect(lambda: [
            self.brightness_slider.setValue(0),
            self.contrast_slider.setValue(100),
            self.update_camera_settings()
        ])

        self.info_label = QLabel("Make gestures in front of the camera")
        self.info_label.setAlignment(Qt.AlignCenter)

        control_layout.addWidget(QLabel("Select Effect:"))
        control_layout.addWidget(self.effect_combo)
        control_layout.addWidget(intensity_label)
        control_layout.addWidget(self.intensity_slider)
        control_layout.addWidget(brightness_label)
        control_layout.addWidget(self.brightness_slider)
        control_layout.addWidget(contrast_label)
        control_layout.addWidget(self.contrast_slider)
        control_layout.addWidget(reset_btn)
        control_layout.addWidget(self.info_label)
        control_layout.addStretch()

        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        control_layout.addLayout(button_layout)

        control_panel.setLayout(control_layout)
        main_layout.addWidget(self.video_label, 70)
        main_layout.addWidget(control_panel, 30)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.statusBar().showMessage("Ready")

        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu("Settings")

        keybind_action = QAction("Configure Key Bindings", self)
        keybind_action.triggered.connect(self.configure_key_bindings)
        settings_menu.addAction(keybind_action)

        self.setMenuBar(menu_bar)

    def init_camera(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def start_camera(self):
        try:
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise RuntimeError("Could not open camera")

                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
                self.update_camera_settings(hardware_only=True)

            self.timer.start(20)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.statusBar().showMessage("Camera running")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)

    def stop_camera(self):
        self.timer.stop()
        self.video_label.clear()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("Camera stopped")

    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.statusBar().showMessage("Failed to capture frame")
                return

            frame = self.adjust_image(frame, self.contrast_adjust, self.brightness_adjust)
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    palm_landmarks = [0, 1, 2, 5, 9, 13, 17]
                    palm_x = int(sum(hand_landmarks.landmark[i].x for i in palm_landmarks) / len(palm_landmarks) * self.cam_width)
                    palm_y = int(sum(hand_landmarks.landmark[i].y for i in palm_landmarks) / len(palm_landmarks) * self.cam_height)

                    index_tip_x = int(hand_landmarks.landmark[8].x * self.cam_width)
                    index_tip_y = int(hand_landmarks.landmark[8].y * self.cam_height)
                    self.rainbow_effect.update_trail(index_tip_x, index_tip_y)

                    if self.is_hand_open(hand_landmarks):
                        self.info_label.setText("Hand open - effect active!")

                        if self.current_effect == "Fireworks":
                            frame_bgr = self.fireworks_effect.draw_firework(frame_bgr, palm_x, palm_y, size=self.effect_intensity)
                        elif self.current_effect == "Sparkles":
                            frame_bgr = self.sparkles_effect.draw_sparkles(frame_bgr, palm_x, palm_y, intensity=self.effect_intensity / 100)
                        elif self.current_effect == "Fire":
                            frame_bgr = self.fire_effect.draw_fire(frame_bgr, palm_x, palm_y, size=self.effect_intensity * 2)
                    else:
                        self.info_label.setText("Close your hand to activate effects")

            if self.current_effect == "Rainbow Trail":
                frame_bgr = self.rainbow_effect.draw_rainbow_trail(frame_bgr)

            h, w, ch = frame_bgr.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_bgr.data, w, h, bytes_per_line, QImage.Format_BGR888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            self.stop_camera()

    def adjust_image(self, img, contrast=1.0, brightness=0):
        return cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

    def update_camera_settings(self, hardware_only=False):
        self.brightness_adjust = self.brightness_slider.value()
        self.contrast_adjust = self.contrast_slider.value() / 100

        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness_adjust / 100)
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast_adjust)

        if not hardware_only:
            self.statusBar().showMessage(
                f"Brightness: {self.brightness_adjust}%, Contrast: {int(self.contrast_adjust * 100)}%"
            )

    def is_hand_open(self, hand_landmarks):
        finger_tips = [8, 12, 16, 20]
        finger_bases = [6, 10, 14, 18]
        open_fingers = sum(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y
                           for tip, base in zip(finger_tips, finger_bases))
        return open_fingers >= 3

    def change_effect(self, effect_name):
        self.current_effect = effect_name if effect_name != "No Effect" else None
        if effect_name != "Rainbow Trail":
            self.rainbow_effect.clear_trail()
        self.statusBar().showMessage(f"Effect changed to: {effect_name}")

    def update_intensity(self, value):
        self.effect_intensity = value
        self.statusBar().showMessage(f"Effect intensity: {value}%")

    def configure_key_bindings(self):
        dialog = KeyBindingDialog(self)
        if dialog.exec_():
            effect, key = dialog.get_binding()
            if key.isdigit() and 1 <= int(key) <= 9:
                self.key_bindings[key] = effect
                self.statusBar().showMessage(f"Key {key} bound to {effect}")
            else:
                self.statusBar().showMessage("Invalid key. Must be a digit 1–9.")

    def keyPressEvent(self, event):
        key = event.key()
        if Qt.Key_1 <= key <= Qt.Key_9:
            key_str = str(key - Qt.Key_0)
            if key_str in self.key_bindings:
                effect_name = self.key_bindings[key_str]
                self.effect_combo.setCurrentText(effect_name)
                self.change_effect(effect_name)

    def closeEvent(self, event):
        self.stop_camera()
        if self.cap:
            self.cap.release()
        self.settings.setValue("brightness", self.brightness_slider.value())
        self.settings.setValue("contrast", self.contrast_slider.value())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandMagicApp()
    window.show()
    sys.exit(app.exec_())
