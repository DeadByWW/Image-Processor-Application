import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog  # Добавлен simpledialog
from PIL import Image, ImageTk


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("800x600")  # Установка начального размера окна
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
        frame_channels = tk.Frame(self.root)
        frame_channels.pack(pady=5)

        # Добавлен command для обработки выбора канала
        tk.Radiobutton(frame_channels, text="Красный", variable=self.channel_var,
                       value="R", command=self.process_channel).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_channels, text="Зеленый", variable=self.channel_var,
                       value="G", command=self.process_channel).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_channels, text="Синий", variable=self.channel_var,
                       value="B", command=self.process_channel).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_channels, text="Исходное", variable=self.channel_var,
                       value="None", command=self.show_original).pack(side=tk.LEFT, padx=5)

        # Дополнительные функции
        frame_actions = tk.Frame(self.root)
        frame_actions.pack(pady=5)

        tk.Button(frame_actions, text="Изменить размер", command=self.resize_image).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_actions, text="Понизить яркость", command=self.adjust_brightness).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_actions, text="Нарисовать прямоугольник", command=self.draw_rectangle).pack(side=tk.LEFT,
                                                                                                    padx=5)

        # Область изображения
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            self.image = cv2.imread(path)
            if self.image is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
                return
            self.show_image(self.image)
            self.channel_var.set("None")  # Сброс выбора канала

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Веб-камера не доступна!")
            return

        ret, frame = cap.read()
        if ret:
            self.image = frame
            self.show_image(self.image)
            self.channel_var.set("None")  # Сброс выбора канала
        cap.release()

    def show_image(self, img):
        # Сохраняем оригинал для восстановления
        self.original_image = img.copy()

        # Конвертируем для отображения
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)

        # Масштабируем изображение под размер окна
        width, height = self.get_scaled_size(img_pil.size)
        img_pil = img_pil.resize((width, height), Image.LANCZOS)

        img_tk = ImageTk.PhotoImage(img_pil)
        self.panel.config(image=img_tk)
        self.panel.image = img_tk  # Сохраняем ссылку

    def get_scaled_size(self, size):
        max_width = self.root.winfo_width() - 20
        max_height = self.root.winfo_height() - 150

        width, height = size
        ratio = min(max_width / width, max_height / height, 1.0)
        return int(width * ratio), int(height * ratio)

    def show_original(self):
        if self.image is not None:
            self.show_image(self.original_image)

    def process_channel(self):
        if self.image is None:
            return

        channel = self.channel_var.get()
        if channel == "None":
            self.show_original()
            return

        b, g, r = cv2.split(self.original_image)
        zeros = np.zeros_like(b)

        if channel == "R":
            processed = cv2.merge([zeros, zeros, r])
        elif channel == "G":
            processed = cv2.merge([zeros, g, zeros])
        elif channel == "B":
            processed = cv2.merge([b, zeros, zeros])
        else:
            processed = self.original_image.copy()

        self.show_image(processed)

    def resize_image(self):
        if self.image is None:
            return

        width = simpledialog.askinteger("Размер", "Ширина:", minvalue=10, maxvalue=4000)
        height = simpledialog.askinteger("Размер", "Высота:", minvalue=10, maxvalue=4000)

        if width and height:
            resized = cv2.resize(self.original_image, (width, height))
            self.show_image(resized)

    def adjust_brightness(self):
        if self.image is None:
            return

        value = simpledialog.askinteger("Яркость", "Значение (0-100):",
                                        minvalue=0, maxvalue=100, initialvalue=20)
        if value is not None:
            # Конвертируем в HSV и уменьшаем Value канал
            hsv = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype("float32")
            hsv[:, :, 2] *= (1 - value / 100)
            hsv = np.clip(hsv, 0, 255).astype("uint8")
            adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            self.show_image(adjusted)

    def draw_rectangle(self):
        if self.image is None:
            return

        # Используем оригинальное изображение для рисования
        img_copy = self.original_image.copy()
        height, width = img_copy.shape[:2]

        # Запрашиваем координаты с валидацией
        x1 = simpledialog.askinteger("Координаты", "X1 (левый верх):",
                                     minvalue=0, maxvalue=width - 1)
        y1 = simpledialog.askinteger("Координаты", "Y1 (левый верх):",
                                     minvalue=0, maxvalue=height - 1)
        x2 = simpledialog.askinteger("Координаты", "X2 (правый низ):",
                                     minvalue=x1 + 1 if x1 else 0, maxvalue=width - 1)
        y2 = simpledialog.askinteger("Координаты", "Y2 (правый низ):",
                                     minvalue=y1 + 1 if y1 else 0, maxvalue=height - 1)

        if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Синий в BGR
            self.show_image(img_copy)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()