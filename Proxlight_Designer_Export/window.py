from tkinter import Tk, Canvas, PhotoImage, Button
from PIL import Image, ImageTk
import os

class ImageWindow:
    def __init__(self, root):
        self.root = root

        self.root.geometry("640x480")
        self.root.configure(bg="#0000FF")
        self.canvas = Canvas(
            self.root,
            bg="#ffffff",
            height=480,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Get the absolute path to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Load background image
        background_img = PhotoImage(file=os.path.join(script_dir, "background.png"))
        background = self.canvas.create_image(320, 200, anchor='center', image=background_img)

        # Load button images
        img0 = PhotoImage(file=os.path.join(script_dir, "img0.png"))
        b0 = Button(
            self.canvas,
            image=img0,
            borderwidth=0,
            highlightthickness=0,
            command=self.btn_clicked,
            relief="flat"
        )
        b0.place(x=115, y=220, width=123, height=105)

        img1 = PhotoImage(file=os.path.join(script_dir, "img1.png"))
        b1 = Button(
            self.canvas,
            image=img1,
            borderwidth=0,
            highlightthickness=0,
            command=self.btn_clicked,
            relief="flat"
        )
        b1.place(x=258, y=220, width=123, height=105)

        img2 = PhotoImage(file=os.path.join(script_dir, "img2.png"))
        b2 = Button(
            self.canvas,
            image=img2,
            borderwidth=0,
            highlightthickness=0,
            command=self.btn_clicked,
            relief="flat"
        )
        b2.place(x=400, y=220, width=123, height=105)

        self.root.resizable(False, False)
        self.root.mainloop()

    def btn_clicked(self):
        print("Button Clicked")

if __name__ == "__main__":
    root = Tk()
    app = ImageWindow(root)
