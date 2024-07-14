import cv2
import pyautogui
import matplotlib.pyplot as plt
import seaborn as sns
from pynput import mouse
import tkinter as tk
from PIL import Image, ImageTk

class HeatmapGenerator:
    def __init__(self, input_image_path, duration=10):
        self.input_image_path = input_image_path
        self.duration = duration
        self.heatmap_data = []
        self.input_image = None
        self.root = None
        self.canvas = None
        self.scale_factor = 1.0

    def on_move(self, x, y):
        # Adjust coordinates based on scaling
        x = int(x / self.scale_factor)
        y = int(y / self.scale_factor)
        self.heatmap_data.append((x, y))

    def fit_image_to_screen(self, image):
        screen_width, screen_height = pyautogui.size()
        image_width, image_height = image.size

        # Calculate the scaling factor
        width_scale = screen_width / image_width
        height_scale = screen_height / image_height
        self.scale_factor = min(width_scale, height_scale, 1)  # Don't scale up, only down

        # Resize image if necessary
        if self.scale_factor < 1:
            new_width = int(image_width * self.scale_factor)
            new_height = int(image_height * self.scale_factor)
            image = image.resize((new_width, new_height), Image.LANCZOS)

        return image

    def display_image(self):
        self.root = tk.Tk()
        self.root.title("Move your mouse over this image")
        
        image = Image.open(self.input_image_path)
        image = self.fit_image_to_screen(image)
        photo = ImageTk.PhotoImage(image)
        
        self.canvas = tk.Canvas(self.root, width=image.width, height=image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        
        self.root.after(self.duration * 1000, self.root.quit)
        self.root.mainloop()

    def record_mouse_movement(self):
        listener = mouse.Listener(on_move=self.on_move)
        listener.start()
        
        self.display_image()
        
        listener.stop()

    def generate_heatmap(self):
        # Read the input image
        self.input_image = cv2.imread(self.input_image_path)
        if self.input_image is None:
            raise ValueError(f"Failed to load image from {self.input_image_path}")
        
        # Record mouse movement
        print(f"Recording mouse movement for {self.duration} seconds...")
        print("Please move your mouse over the displayed image.")
        self.record_mouse_movement()
        
        # Create a figure with three subplots
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # Display input image
        ax1.imshow(cv2.cvtColor(self.input_image, cv2.COLOR_BGR2RGB))
        ax1.set_title('Input Image')
        ax1.axis('off')
        
        # Generate and display heatmap
        x, y = zip(*self.heatmap_data)
        ax2.set_xlim(0, self.input_image.shape[1])
        ax2.set_ylim(self.input_image.shape[0], 0)  # Invert y-axis
        sns.kdeplot(x=x, y=y, cmap="YlOrRd", shade=True, cbar=True, ax=ax2)
        ax2.set_title('Heatmap')
        ax2.axis('off')
        
        # Overlay heatmap on input image
        ax3.imshow(cv2.cvtColor(self.input_image, cv2.COLOR_BGR2RGB))
        sns.kdeplot(x=x, y=y, cmap="YlOrRd", shade=True, alpha=0.7, ax=ax3)
        ax3.set_title('Overlay')
        ax3.axis('off')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    input_image_path = "map.png"  #image path
    generator = HeatmapGenerator(input_image_path)
    generator.generate_heatmap()