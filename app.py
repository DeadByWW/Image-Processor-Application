import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


def load_image(self):
    path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
    if path:
        self.image = cv2.imread(path)
        self.show_image(self.image)


def capture_image(self):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Ошибка", "Веб-камера не доступна!")
        return

    ret, frame = cap.read()
    if ret:
        self.image = frame
        self.show_image(self.image)
    cap.release()


def show_image(self, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(img_pil)
    self.panel.config(image=img_tk)
    self.panel.image = img_tk


def process_channel(self):
    if self.image is None:
        return

    channel = self.channel_var.get()
    if channel == "None":
        return

    b, g, r = cv2.split(self.image)
    zeros = np.zeros_like(b)

    if channel == "R":
        processed = cv2.merge([zeros, zeros, r])
    elif channel == "G":
        processed = cv2.merge([zeros, g, zeros])
    elif channel == "B":
        processed = cv2.merge([b, zeros, zeros])

    self.show_image(processed)