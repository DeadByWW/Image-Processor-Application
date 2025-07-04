import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk


class ImageProcessorApp:
    """
    Приложение для обработки изображений с графическим интерфейсом.

    Функционал:
    - Загрузка изображений с диска
    - Захват изображений с веб-камеры
    - Просмотр цветовых каналов (R, G, B)
    - Изменение размеров изображения
    - Регулировка яркости
    - Рисование прямоугольников по координатам
    - Сброс всех изменений
    """

    def __init__(self, root):
        """
        Инициализация приложения.

        Args:
            root (tk.Tk): Корневое окно приложения
        """
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("800x600")

        # Основные переменные для работы с изображениями
        self.original_image = None  # Всегда храним оригинал
        self.processed_image = None  # Текущее обработанное изображение
        self.display_image = None  # Изображение для отображения (масштабированное)

        self.setup_ui()

    def setup_ui(self):
        """Настройка графического интерфейса пользователя."""
        # Основной фрейм для кнопок
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки загрузки
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Загрузить изображение", command=self.load_image).pack(pady=2, fill=tk.X)
        tk.Button(btn_frame, text="Сделать снимок", command=self.capture_image).pack(pady=2, fill=tk.X)

        # Выбор канала
        channel_frame = tk.Frame(control_frame)
        channel_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(channel_frame, text="Цветовые каналы:").pack(anchor=tk.W)
        self.channel_var = tk.StringVar(value="None")

        tk.Radiobutton(channel_frame, text="Исходное", variable=self.channel_var,
                       value="None", command=self.process_channel).pack(anchor=tk.W)
        tk.Radiobutton(channel_frame, text="Красный", variable=self.channel_var,
                       value="R", command=self.process_channel).pack(anchor=tk.W)
        tk.Radiobutton(channel_frame, text="Зеленый", variable=self.channel_var,
                       value="G", command=self.process_channel).pack(anchor=tk.W)
        tk.Radiobutton(channel_frame, text="Синий", variable=self.channel_var,
                       value="B", command=self.process_channel).pack(anchor=tk.W)

        # Дополнительные функции
        func_frame = tk.Frame(control_frame)
        func_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(func_frame, text="Операции:").pack(anchor=tk.W)
        tk.Button(func_frame, text="Изменить размер", command=self.resize_image).pack(fill=tk.X, pady=2)
        tk.Button(func_frame, text="Понизить яркость", command=self.adjust_brightness).pack(fill=tk.X, pady=2)
        tk.Button(func_frame, text="Нарисовать прямоугольник", command=self.draw_rectangle).pack(fill=tk.X, pady=2)
        tk.Button(func_frame, text="Сбросить все изменения", command=self.reset_image).pack(fill=tk.X, pady=2)

        # Область изображения с прокруткой
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_frame)
        self.scroll_y = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_on_canvas = None

    def load_image(self):
        """Загрузка изображения с диска."""
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            self.original_image = cv2.imread(path)
            if self.original_image is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
                return

            self.processed_image = self.original_image.copy()
            self.channel_var.set("None")
            self.show_image(self.processed_image)

    def capture_image(self):
        """Захват изображения с веб-камеры."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Веб-камера не доступна!")
            return

        ret, frame = cap.read()
        if ret:
            self.original_image = frame
            self.processed_image = self.original_image.copy()
            self.channel_var.set("None")
            self.show_image(self.processed_image)
        cap.release()

    def show_image(self, img):
        """
        Отображение изображения на холсте.

        Args:
            img (numpy.ndarray): Изображение в формате BGR
        """
        # Конвертируем в RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.display_image = Image.fromarray(img_rgb)

        # Обновляем размеры canvas
        self.canvas.config(scrollregion=(0, 0, self.display_image.width, self.display_image.height))

        # Отображаем изображение
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        if self.image_on_canvas:
            self.canvas.delete(self.image_on_canvas)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def process_channel(self):
        """Обработка и отображение выбранного цветового канала."""
        if self.original_image is None:
            return

        channel = self.channel_var.get()
        if channel == "None":
            self.processed_image = self.original_image.copy()
        else:
            b, g, r = cv2.split(self.original_image)
            zeros = np.zeros_like(b)

            if channel == "R":
                self.processed_image = cv2.merge([zeros, zeros, r])
            elif channel == "G":
                self.processed_image = cv2.merge([zeros, g, zeros])
            elif channel == "B":
                self.processed_image = cv2.merge([b, zeros, zeros])

        self.show_image(self.processed_image)

    def resize_image(self):
        """Изменение размера изображения."""
        if self.original_image is None:
            return

        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение размера")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("300x150")

        # Элементы управления
        tk.Label(dialog, text="Ширина:").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.IntVar(value=self.original_image.shape[1])
        width_entry = tk.Entry(dialog, textvariable=width_var)
        width_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Высота:").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.IntVar(value=self.original_image.shape[0])
        height_entry = tk.Entry(dialog, textvariable=height_var)
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        status_label = tk.Label(dialog, text="", fg="red")
        status_label.grid(row=2, column=0, columnspan=2)

        def apply_resize():
            try:
                width = int(width_var.get())
                height = int(height_var.get())

                if width < 10 or height < 10:
                    status_label.config(text="Размеры должны быть больше 10 пикселей")
                    return

                resized = cv2.resize(self.processed_image, (width, height))
                self.processed_image = resized
                self.show_image(self.processed_image)
                dialog.destroy()
            except ValueError:
                status_label.config(text="Введите числовые значения")

        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Применить", command=apply_resize).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

        # Фокус на первом поле ввода
        width_entry.focus_set()

    def adjust_brightness(self):
        """Регулировка яркости изображения."""
        if self.original_image is None:
            return

        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Настройка яркости")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("300x150")

        # Элементы управления
        tk.Label(dialog, text="Уровень яркости (0-100%):").pack(padx=20, pady=5)
        brightness_var = tk.IntVar(value=20)
        tk.Scale(dialog, from_=0, to=100, orient=tk.HORIZONTAL,
                 variable=brightness_var).pack(padx=20, pady=5)

        def apply_brightness():
            value = brightness_var.get()

            # Конвертируем в HSV и уменьшаем Value канал
            hsv = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype("float32")
            hsv[:, :, 2] *= (1 - value / 100)
            hsv = np.clip(hsv, 0, 255).astype("uint8")
            adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            self.processed_image = adjusted
            self.show_image(self.processed_image)
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Применить", command=apply_brightness).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def draw_rectangle(self):
        """Рисование прямоугольника по заданным координатам."""
        if self.original_image is None:
            return

        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Рисование прямоугольника")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("300x250")

        # Получаем размеры изображения для ограничений
        height, width = self.processed_image.shape[:2]

        # Элементы управления
        tk.Label(dialog, text="Введите координаты:").pack(pady=5)

        coord_frame = tk.Frame(dialog)
        coord_frame.pack(pady=10)

        # Верхний левый угол
        tk.Label(coord_frame, text="Верхний левый:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(coord_frame, text="X1:").grid(row=0, column=1, padx=5, pady=5)
        x1_var = tk.IntVar(value=0)
        x1_entry = tk.Entry(coord_frame, textvariable=x1_var, width=5)
        x1_entry.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(coord_frame, text="Y1:").grid(row=0, column=3, padx=5, pady=5)
        y1_var = tk.IntVar(value=0)
        y1_entry = tk.Entry(coord_frame, textvariable=y1_var, width=5)
        y1_entry.grid(row=0, column=4, padx=5, pady=5)

        # Нижний правый угол
        tk.Label(coord_frame, text="Нижний правый:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(coord_frame, text="X2:").grid(row=1, column=1, padx=5, pady=5)
        x2_var = tk.IntVar(value=width)
        x2_entry = tk.Entry(coord_frame, textvariable=x2_var, width=5)
        x2_entry.grid(row=1, column=2, padx=5, pady=5)

        tk.Label(coord_frame, text="Y2:").grid(row=1, column=3, padx=5, pady=5)
        y2_var = tk.IntVar(value=height)
        y2_entry = tk.Entry(coord_frame, textvariable=y2_var, width=5)
        y2_entry.grid(row=1, column=4, padx=5, pady=5)

        status_label = tk.Label(dialog, text="", fg="red")
        status_label.pack()

        def apply_rectangle():
            try:
                x1 = x1_var.get()
                y1 = y1_var.get()
                x2 = x2_var.get()
                y2 = y2_var.get()

                # Проверка валидности координат
                if (x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or
                        x1 > width or x2 > width or y1 > height or y2 > height):
                    status_label.config(text=f"Координаты вне диапазона (0-{width}, 0-{height})")
                    return

                if x1 >= x2 or y1 >= y2:
                    status_label.config(text="X2 должно быть больше X1, Y2 должно быть больше Y1")
                    return

                # Рисуем прямоугольник
                img_copy = self.processed_image.copy()
                cv2.rectangle(img_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
                self.processed_image = img_copy
                self.show_image(self.processed_image)
                dialog.destroy()
            except ValueError:
                status_label.config(text="Введите числовые значения")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Применить", command=apply_rectangle).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

        # Фокус на первом поле ввода
        x1_entry.focus_set()

    def reset_image(self):
        """Сброс всех изменений к оригинальному изображению."""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.channel_var.set("None")
            self.show_image(self.processed_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()