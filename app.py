import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.image = None
        self.setup_ui()


    def setup_ui(self):
        # Кнопки загрузки
        btn_load = tk.Button(self.root, text="Загрузить изображение", command=self.load_image)
        btn_load.pack(pady=5)

        btn_camera = tk.Button(self.root, text="Сделать снимок", command=self.capture_image)
        btn_camera.pack(pady=5)

        # Выбор канала
        self.channel_var = tk.StringVar(value="None")
        tk.Radiobutton(self.root, text="Красный", variable=self.channel_var, value="R").pack()
        tk.Radiobutton(self.root, text="Зеленый", variable=self.channel_var, value="G").pack()
        tk.Radiobutton(self.root, text="Синий", variable=self.channel_var, value="B").pack()

        # Дополнительные функции
        tk.Button(self.root, text="Изменить размер", command=self.resize_image).pack(pady=5)
        tk.Button(self.root, text="Понизить яркость", command=self.adjust_brightness).pack(pady=5)
        tk.Button(self.root, text="Нарисовать прямоугольник", command=self.draw_rectangle).pack(pady=5)

        # Область изображения
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()