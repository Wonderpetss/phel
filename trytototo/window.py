from tkinter import *


def btn_clicked():
    print("Button Clicked")


window = Tk()

window.geometry("640x480")
window.configure(bg = "#ffffff")
canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 480,
    width = 640,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

background_img = PhotoImage(file = f"background.png")
background = canvas.create_image(
    0.0, -26.0,
    image=background_img)

img0 = PhotoImage(file = f"img0.png")
b0 = Button(
    image = img0,
    borderwidth = 0,
    highlightthickness = 0,
    command = btn_clicked,
    relief = "flat")

b0.place(
    x = -246, y = -104,
    width = 40,
    height = 39)

img1 = PhotoImage(file = f"img1.png")
b1 = Button(
    image = img1,
    borderwidth = 0,
    highlightthickness = 0,
    command = btn_clicked,
    relief = "flat")

b1.place(
    x = -61, y = 1,
    width = 123,
    height = 105)

canvas.create_text(
    -49.0, -39.0,
    text = "SELECT A SHELF",
    fill = "#000000",
    font = ("MontserratRoman-Regular", int(18.0)))

window.resizable(False, False)
window.mainloop()
