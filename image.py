try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Image Editor")
        self.root.geometry("1200x800")
        
        # image variables
        self.original_image = None
        self.current_image = None
        self.display_image = None
        self.photo = None
        
        # parameters for image processing
        self.blur_radius = tk.DoubleVar(value=0)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.red_value = tk.IntVar(value=0)
        self.green_value = tk.IntVar(value=0)
        self.blue_value = tk.IntVar(value=0)
        self.temperature = tk.DoubleVar(value=0)
        self.tint = tk.DoubleVar(value=0)
        
        # crop variables
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.crop_rectangle = None
        self.cropping = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # Right panel for image display
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="File Operations")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Open Image", command=self.open_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Save Image", command=self.save_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Reset", command=self.reset_image).pack(fill=tk.X, pady=2)
        
        # Image size controls
        size_frame = ttk.LabelFrame(control_frame, text="Image Size")
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky=tk.W)
        self.width_entry = ttk.Entry(size_frame, width=10)
        self.width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky=tk.W)
        self.height_entry = ttk.Entry(size_frame, width=10)
        self.height_entry.grid(row=1, column=1, padx=5)
        
        ttk.Button(size_frame, text="Resize", command=self.resize_image).grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Blur control
        blur_frame = ttk.LabelFrame(control_frame, text="Gaussian Blur")
        blur_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(blur_frame, from_=0, to=10, variable=self.blur_radius, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        ttk.Label(blur_frame, textvariable=self.blur_radius).pack()
        
        # Brightness and Contrast
        enhance_frame = ttk.LabelFrame(control_frame, text="Enhancement")
        enhance_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(enhance_frame, text="Brightness").pack(anchor=tk.W)
        ttk.Scale(enhance_frame, from_=0.1, to=3.0, variable=self.brightness, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        ttk.Label(enhance_frame, text="Contrast").pack(anchor=tk.W)
        ttk.Scale(enhance_frame, from_=0.1, to=3.0, variable=self.contrast, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        # RGB Controls
        rgb_frame = ttk.LabelFrame(control_frame, text="RGB Adjustment")
        rgb_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rgb_frame, text="Red").pack(anchor=tk.W)
        ttk.Scale(rgb_frame, from_=-255, to=255, variable=self.red_value, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        ttk.Label(rgb_frame, text="Green").pack(anchor=tk.W)
        ttk.Scale(rgb_frame, from_=-255, to=255, variable=self.green_value, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        ttk.Label(rgb_frame, text="Blue").pack(anchor=tk.W)
        ttk.Scale(rgb_frame, from_=-255, to=255, variable=self.blue_value, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        # Color Temperature and Tint
        color_frame = ttk.LabelFrame(control_frame, text="Color Temperature")
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="Temperature").pack(anchor=tk.W)
        ttk.Scale(color_frame, from_=-100, to=100, variable=self.temperature, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        ttk.Label(color_frame, text="Tint").pack(anchor=tk.W)
        ttk.Scale(color_frame, from_=-100, to=100, variable=self.tint, 
                 orient=tk.HORIZONTAL, command=self.update_image).pack(fill=tk.X)
        
        # Crop controls
        crop_frame = ttk.LabelFrame(control_frame, text="Crop")
        crop_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(crop_frame, text="Start Crop", command=self.start_crop).pack(fill=tk.X, pady=2)
        ttk.Button(crop_frame, text="Apply Crop", command=self.apply_crop).pack(fill=tk.X, pady=2)
        ttk.Button(crop_frame, text="Cancel Crop", command=self.cancel_crop).pack(fill=tk.X, pady=2)
        
        # Histogram button
        ttk.Button(control_frame, text="Show Histogram", command=self.show_histogram).pack(fill=tk.X, pady=(0, 10))
        
        # Image display area
        self.canvas = tk.Canvas(display_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind canvas events for cropping
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                
                # Update size entries
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.original_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.original_image.height))
                
                self.display_image_on_canvas()
                self.reset_parameters()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")
                
    def save_image(self):
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.current_image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No image to save!")
            
    def reset_image(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.reset_parameters()
            self.display_image_on_canvas()
            
    def reset_parameters(self):
        self.blur_radius.set(0)
        self.brightness.set(1.0)
        self.contrast.set(1.0)
        self.red_value.set(0)
        self.green_value.set(0)
        self.blue_value.set(0)
        self.temperature.set(0)
        self.tint.set(0)
        
    def resize_image(self):
        if self.current_image:
            try:
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
                self.original_image = self.current_image.copy()
                self.display_image_on_canvas()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid width and height values!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resize image: {str(e)}")
                
    def apply_rgb_adjustment(self, image):
        # Convert to numpy array for RGB manipulation
        img_array = np.array(image)
        
        # Apply RGB adjustments
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] + self.red_value.get(), 0, 255)
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] + self.green_value.get(), 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] + self.blue_value.get(), 0, 255)
        
        return Image.fromarray(img_array.astype('uint8'))
        
    def apply_temperature_tint(self, image):
        # Convert to numpy array
        img_array = np.array(image).astype(float)
        
        # Apply temperature (affects red-blue balance)
        temp_factor = self.temperature.get() / 100.0
        img_array[:, :, 0] += temp_factor * 20  # Red
        img_array[:, :, 2] -= temp_factor * 20  # Blue
        
        # Apply tint (affects green-magenta balance)
        tint_factor = self.tint.get() / 100.0
        img_array[:, :, 1] += tint_factor * 20  # Green
        
        # Clip values
        img_array = np.clip(img_array, 0, 255)
        
        return Image.fromarray(img_array.astype('uint8'))
        
    def update_image(self, *args):
        if self.original_image:
            # Start with original image
            img = self.original_image.copy()
            
            # Apply blur
            if self.blur_radius.get() > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=self.blur_radius.get()))
            
            # Apply brightness
            if self.brightness.get() != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(self.brightness.get())
            
            # Apply contrast
            if self.contrast.get() != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(self.contrast.get())
            
            # Apply RGB adjustments
            if any([self.red_value.get(), self.green_value.get(), self.blue_value.get()]):
                img = self.apply_rgb_adjustment(img)
            
            # Apply temperature and tint
            if self.temperature.get() != 0 or self.tint.get() != 0:
                img = self.apply_temperature_tint(img)
            
            self.current_image = img
            self.display_image_on_canvas()
            
    def display_image_on_canvas(self):
        if self.current_image:
            # Calculate display size maintaining aspect ratio
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, self.display_image_on_canvas)
                return
                
            img_width, img_height = self.current_image.size
            
            # Calculate scale factor
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize for display
            self.display_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.display_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            
    def start_crop(self):
        if self.current_image:
            self.cropping = True
            messagebox.showinfo("Crop Mode", "Click and drag to select crop area")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
            
    def on_canvas_click(self, event):
        if self.cropping:
            self.crop_start_x = event.x
            self.crop_start_y = event.y
            
    def on_canvas_drag(self, event):
        if self.cropping and self.crop_start_x and self.crop_start_y:
            # Remove previous rectangle
            if self.crop_rectangle:
                self.canvas.delete(self.crop_rectangle)
            
            # Draw new rectangle
            self.crop_rectangle = self.canvas.create_rectangle(
                self.crop_start_x, self.crop_start_y, event.x, event.y,
                outline="red", width=2, dash=(5, 5)
            )
            
    def on_canvas_release(self, event):
        if self.cropping:
            self.crop_end_x = event.x
            self.crop_end_y = event.y
            
    def apply_crop(self):
        if not self.cropping or not all([self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y]):
            messagebox.showwarning("Warning", "No crop area selected!")
            return
            
        try:
            # Get canvas dimensions and image position
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            img_width, img_height = self.current_image.size
            display_width, display_height = self.display_image.size
            
            # Calculate image position on canvas
            x_offset = (canvas_width - display_width) // 2
            y_offset = (canvas_height - display_height) // 2
            
            # Convert canvas coordinates to image coordinates
            scale_x = img_width / display_width
            scale_y = img_height / display_height
            
            crop_x1 = max(0, int((min(self.crop_start_x, self.crop_end_x) - x_offset) * scale_x))
            crop_y1 = max(0, int((min(self.crop_start_y, self.crop_end_y) - y_offset) * scale_y))
            crop_x2 = min(img_width, int((max(self.crop_start_x, self.crop_end_x) - x_offset) * scale_x))
            crop_y2 = min(img_height, int((max(self.crop_start_y, self.crop_end_y) - y_offset) * scale_y))
            
            if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                self.current_image = self.current_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                self.original_image = self.current_image.copy()
                
                # Update size entries
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.current_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.current_image.height))
                
                self.display_image_on_canvas()
                self.cancel_crop()
                messagebox.showinfo("Success", "Image cropped successfully!")
            else:
                messagebox.showerror("Error", "Invalid crop area!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop image: {str(e)}")
            
    def cancel_crop(self):
        self.cropping = False
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        if self.crop_rectangle:
            self.canvas.delete(self.crop_rectangle)
            self.crop_rectangle = None
            
    def show_histogram(self):
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        # Create histogram window
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Histogram")
        hist_window.geometry("600x400")
        
        # Convert image to numpy array
        img_array = np.array(self.current_image)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if len(img_array.shape) == 3:  # Color image
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                hist, bins = np.histogram(img_array[:, :, i], bins=256, range=(0, 256))
                ax.plot(bins[:-1], hist, color=color, alpha=0.7, label=color.capitalize())
        else:  # Grayscale image
            hist, bins = np.histogram(img_array, bins=256, range=(0, 256))
            ax.plot(bins[:-1], hist, color='black', alpha=0.7)
            
        ax.set_xlabel('Pixel Value')
        ax.set_ylabel('Frequency')
        ax.set_title('Image Histogram')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Embed plot in tkinter window
        canvas_hist = FigureCanvasTkAgg(fig, hist_window)
        canvas_hist.draw()
        canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def main():
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()