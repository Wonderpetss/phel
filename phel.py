import cv2
import os
from pyzbar.pyzbar import decode
import requests
import tkinter as tk
from tkinter import Label, Button, ttk, messagebox, Canvas, PhotoImage
from PIL import Image, ImageTk
# import pymysql
import datetime


# csrf_token = requests.headers.get('X-CSRFToken')

class User:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Library Locator")
        self.root.geometry("640x480")
        self.root.configure(bg="#ffffff")
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
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "user.png")

        if os.path.exists(image_path):
            background_img = PhotoImage(file=image_path)
            
            # Try displaying the image on a label for testing
            label = Label(self.canvas, image=background_img, bd=0, highlightthickness=0)
            label.place(x=0, y=-25, relwidth=1, relheight=1)
            label.image = background_img  

        img1 = PhotoImage(file=os.path.join(script_dir, "scanuserimg.png"))
        self.b1 = Button(
            self.canvas,
            image=img1,
            borderwidth=0,
            highlightthickness=0,
            command=self.scanuser_window,
            relief="flat"
        )
        self.b1.place(x=258, y=225, width=123, height=105)
        self.b1.image = img1  
     
    def scanuser_window(self):
        self.root.withdraw()
        ScanUser(self.root)

class ScanUser:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Scan User ID")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_data = ""

        # self.wow_label = Label(self.window, text="")
        # self.wow_label.pack_forget()

        self.qr_data_label = Label(self.window, text="Username: ")
        self.qr_data_label.pack()

        self.scan_button = Button(self.window, text="Scan ID", command=self.scan_id)
        self.scan_button.pack()

        self.done_button = Button(self.window, text="Done", command=self.done, state="disabled")
        self.done_button.pack()
 
        self.capture_running = True
        self.update()
        
    def scan_id(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"Username: {self.qr_data}")
            self.scan_button.config(state="disabled")
            self.done_button.config(state="active")

    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.qr_databorrowers = decoded_objects[0].data.decode('utf-8')
                self.qr_data = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.qr_data = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the methods window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()
    
    def open_first_window(self):
        self.window.withdraw()  
        FirstWindow(self.window)  

    def done(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the methods windows?")
        
        if asktoproceed:
            #self.window.destroy()
            self.open_first_window()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            #self.parent_window.deiconify()
        else:
            ask_to_scan_again = messagebox.askyesno("Scan Again", "Do you want to scan again?")
            if ask_to_scan_again:
                self.scan_button.config(state="active")
                self.done_button.config(state="disabled")
                self.scan_id()  
            else:
                pass  

class QRCodeScanner:
    def __init__(self, parent_window=None, selected_shelf=""):
        self.parent_window = parent_window
        self.selected_shelf = selected_shelf  # Store selected shelf

        self.window = tk.Toplevel(parent_window)
        self.window.title("QR Code Scanner")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  # Set the width to 1920 pixels
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  # Set the height to 1080 pixels

        self.canvas = tk.Canvas(
            self.window,
            bg="#ffffff",
            height=480,
            width=640, 
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        self.canvas.pack()


        self.results_label = Label(self.window, text="Scanning QR codes...")
        self.results_label.place(x =260 , y = 400)
        self.combo_box_value = tk.StringVar()  # Variable to store the selected combo box value

        # Create a label to display the combo box value
        self.combo_box_label = Label(self.window, textvariable=self.combo_box_value)
        self.combo_box_label.pack()
        
        self.selected_shelf_label = Label(self.window, text=f"Selected Shelf: {self.selected_shelf}")  # Display selected shelf
        self.selected_shelf_label.pack_forget()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        img5 = PhotoImage(file=os.path.join(script_dir, "stopCam.png"))
        self.stopCam = Button(
            self.canvas,
            image=img5,
            borderwidth=0,
            highlightthickness=0,
            command=self.close_window,
            relief="flat"
        )
        self.stopCam.place(x =200 , y = 450, width = 232, height = 30)
        self.stopCam.image=img5    
       
        self.stop_button = Button(self.window, text="Stop Camera", command=self.close_window)
        self.stop_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.qr_values = self.retrieve_data(self.selected_shelf)  # Fetch the QR code data from the API
        self.camera_running = True

        self.update()

    def retrieve_data(self, selected_shelf):
        try:
            base_url = "https://wonderpets.pythonanywhere.com/"
            shelf_url = base_url + selected_shelf
            response = requests.get(shelf_url)
            print("API RESPONSE:", response.json())
            if response.status_code == 200:
                qr_values = response.json()
                return set(qr_values)
            else:
                print("Error fetching data from API:", response.text)
                return set()
        except Exception as e:
            print("Error fetching data from API:", str(e))
            return set()

    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            self.show_frame(frame, decoded_objects)
        self.window.after(30, self.update)

    def close_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Done scanning?")
        if asktoproceed:
            ask = messagebox.askyesno("Confirmation", "Scan Again?")
            if ask: 
                self.camera_running = False
                if self.camera.isOpened():
                    self.camera.release()
                self.open_combobox()
            else:
                pass

    def open_combobox(self):
        self.window.withdraw()
        MainApplication(self.window)
       
    def show_frame(self, frame, decoded_objects):
        for obj in decoded_objects:
            x, y, w, h = obj.rect
            qr_data = obj.data.decode('utf-8')

            if qr_data in self.qr_values:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.photo = photo

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class Borrow:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Borrow")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""

        self.wow_label = Label(self.window, text="")
        self.wow_label.pack_forget()

        self.qr_borrower_label = Label(self.window, text="Borrower:")
        self.qr_borrower_label.pack()

        self.qr_data_label = Label(self.window, text="QR Code Data: ")
        self.qr_data_label.pack()

        self.borrower_button = Button(self.window, text="Scan Borrower", command=self.borrower_qr_code)
        self.borrower_button.pack()

        self.borrow_button = Button(self.window, text="Scan Borrowed Book", command=self.borrow_qr_code, state="disabled")
        self.borrow_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")
            
            # Enable the borrow_button and disable the borrower_button
            self.borrow_button.config(state="normal")
            self.borrower_button.config(state="disabled")

        
    def borrow_qr_code(self):
        inventory_url = "http://172.20.10.3:5000/genbooks"
        logbook_url = "http://172.20.10.3:5000/borrowed_books"

        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")

            try:
                
                response = requests.get(inventory_url)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    token = response.json().get('csrf_token')

                    headers = {
                    'X-CSRF-Token': token 
                }
                    print(headers)

                    if isinstance(data, list) and len(data) > 0:
                        book_ids = [item.get("book_id") for item in data if "book_id" in item]
                        print(book_ids)

                        for a in book_ids:
                            if a == self.qr_data:
                                print("Match found!")

                                #update quantity
                                upd_inventory_url = f"http://172.20.10.3:5000/genbooks/{self.qr_data}"

                                print(upd_inventory_url)

                                data_to_update = {
                                    # "book_id": self.qr_data,
                                    "quantity": 2
                                    }  
                                
                                update_response = requests.put(upd_inventory_url, json=data_to_update)                         
                                
                                #print(update_response)
                                
                                # #insert to logbook
                                # data_to_insert = {
                                #     'book_id' : self.qr_data,
                                #     'borrower': self.qr_databorrowers,
                                #     'status': 'Borrowed'
                                # }

                                # insert_response = requests.post(logbook_url, json=data_to_insert, headers=headers)

                                # print(insert_response)

                                if update_response.status_code == 200 :
                                    print("Data updated in table 1 and inserted into table 2 successfully.")
                                else:
                                    print("Error updating/inserting data:", update_response)
                    else:
                        print("No books found in inventory.")

            except Exception as e:
                print("Error fetching data from API:", str(e))

    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.qr_databorrowers = decoded_objects[0].data.decode('utf-8')
                self.qr_data = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.qr_databorrowers = ""
                self.qr_data = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class Return:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Return")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""

        self.qr_borrower_label = Label(self.window, text="Borrower:")
        self.qr_borrower_label.pack()

        self.qr_data_label = Label(self.window, text="QR Code Data: ")
        self.qr_data_label.pack()

        self.borrower_button = Button(self.window, text="Scan Borrower", command=self.borrower_qr_code)
        self.borrower_button.pack()

        self.return_button = Button(self.window, text="Return", command=self.return_qr_code)
        self.return_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")

            self.borrow_button.config(state="normal")
            self.borrower_button.config(state="disabled")

    def return_qr_code(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")

            try:
                inventory_url = "http://192.168.2.4:5000/gen_books"
                logbook_url = "http://192.168.2.4:5000/borrowed_books"
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                response = requests.get(logbook_url)
                
                if response.status_code == 200:
                    data = response.json() 

                    if isinstance(data, list) and len(data) > 0:
                        book_ids = [item.get("book_id") for item in data if "book_id" in item]
                        # dateborrowed = [item.get("date_borrowed") for item in data if "data_borrowed" in item] 
                        mustreturndate = [item.get("date_return") for item in data if "date_return" in item] 
                        borrower = [item.get("borrower") for item in data if "borrower" in item] 
                        print(book_ids)

                        for a, b in zip(borrower, book_ids):
                            if a == self.qr_databorrowers and b == self.qr_data:
                                data_to_update = {
                                    'quantity': 'quantity + 1'
                                }
                                update_response = requests.put(inventory_url, json=data_to_update)

                        for a in mustreturndate:
                            if a <= current_datetime:
                                data_to_update1 = {
                                    'status': 'Returned'
                                }
                            else:
                                data_to_update1 = {
                                    'status': 'Returned Late'
                                }

                                update1_response = requests.put(logbook_url, json=data_to_update1)

                    if update_response.status_code == 200 and update1_response.status_code == 200:
                        print("Data updated in table 1 and inserted into table 2 successfully.")
                    else:
                        print("Error updating data:", update_response.text, update1_response.text)

            except Exception as e:
                print("Error fetching data from API:", str(e))


    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.qr_data = decoded_objects[0].data.decode('utf-8')
                self.qr_databorrowers = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.qr_data = ""
                self.qr_databorrowers = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()
    
    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class FirstWindow:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self.window = tk.Toplevel(parent_window) 
        self.window.title("First Window")
        self.window.geometry("640x480")
        self.window.configure(bg="#ffffff")
        
        self.canvas = Canvas(
            self.window,
            bg="#ffffff",
            height=480,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "method.png")

        if os.path.exists(image_path):
            background_img = PhotoImage(file=image_path)
            label = Label(self.canvas, image=background_img, bd=0, highlightthickness=0)
            label.place(x=0, y=-25, relwidth=1, relheight=1)
            label.image = background_img  

        img0 = PhotoImage(file=os.path.join(script_dir, "img0.png"))
        self.b0 = Button(
            self.canvas,
            image=img0,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_second_window,
            relief="flat"
        )
        self.b0.place(x=115, y=220, width=123, height=105)
        self.b0.image = img0  

        img1 = PhotoImage(file=os.path.join(script_dir, "img1.png"))
        self.b1 = Button(
            self.canvas,
            image=img1,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_pers_window,
            relief="flat"
        )
        self.b1.place(x=258, y=220, width=123, height=105)
        self.b1.image = img1  

        img2 = PhotoImage(file=os.path.join(script_dir, "img2.png"))
        self.b2 = Button(
            self.canvas,
            image=img2,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_third_window,
            relief="flat"
        )
        self.b2.place(x=400, y=220, width=123, height=105)
        self.b2.image= img2

        img3 = PhotoImage(file=os.path.join(script_dir, "img3.png"))
        self.b3 = Button(
            self.canvas,
            image=img3,
            borderwidth=0,
            highlightthickness=0,
            command=self.scan_user_window,
            relief="flat"
        )
        self.b3.place(x=258, y=350, width=123, height=25)
        self.b3.image= img3

    def open_second_window(self):
        self.window.withdraw()
        MainApplication(self.window)

    def open_pers_window(self):
        self.window.withdraw()
        Borrow(self.window)

    def open_third_window(self):
        self.window.withdraw()
        Return(self.window)

    def scan_user_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to scan user again?")
        
        if asktoproceed:
            self.window.withdraw()
            user_window = tk.Toplevel(self.parent_window)
            user_window.title("User Window")
            User(user_window)

class MainApplication(tk.Toplevel):
    def __init__(self, parent_window):
        self.parent_window = parent_window
        super().__init__(parent_window)
        self.title("Main Application")
        self.geometry("640x480")
        self.configure(bg="#ffffff")
        self.canvas = Canvas(
            self,
            bg="#ffffff",
            height=480,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "combobox.png")

        if os.path.exists(image_path):
            background_img = PhotoImage(file=image_path)
            
            # Try displaying the image on a label for testing
            label = Label(self.canvas, image=background_img, bd=0, highlightthickness=0)
            label.place(x=0, y=-25, relwidth=1, relheight=1)
            label.image = background_img
        
        imgHome = PhotoImage(file =os.path.join(script_dir, "home.png"))
        self.Home = Button(
            self.canvas,
            image = imgHome,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.back_to_first_window,
            relief = "flat")

        self.Home.place(x = 80, y = 145, width = 40, height = 39)
        self.Home.image=imgHome
        self.combo_box_value = tk.StringVar()  # Variable to store the combo box value

        self.combo_box = ttk.Combobox(
            self, 
            values=["shelf1", "shelf2", "shelf3"],
            textvariable=self.combo_box_value,
            font=("Arial", 14), # Adjust the font family and size as needed
            state="readonly",
)
        self.combo_box.place(x=170, y=180, width=297, height=39)
        
        img4 = PhotoImage(file=os.path.join(script_dir, "return.png"))
        self.return2 = Button(
            self.canvas,
            image=img4,
            borderwidth=0,
            highlightthickness=0,
            command=self.open_scanner,
            relief="flat"
        )
        self.return2.place(x=270, y=250, width=100, height=90)
        self.return2.image=img4
        

        self.combo_box.bind("<<ComboboxSelected>>", self.update_selected_shelf_label)

        self.selected_shelf_label = Label(self, text="Selected Shelf: None")
        self.selected_shelf_label.pack_forget()

    def update_selected_shelf_label(self, event):
        selected_shelf = self.combo_box_value.get()
        self.selected_shelf_label.config(text=f"Selected Shelf: {selected_shelf}")
        
        # Enable the "Open Scanner" button if a shelf is selected
        if selected_shelf:
            self.return2.config(state="normal")
        else:
            self.return2.config(state="disabled")

    def open_scanner(self):
        selected_shelf = self.combo_box_value.get()
        if selected_shelf:  # Only proceed if a shelf is selected
            self.withdraw()
            QRCodeScanner(self.parent_window, selected_shelf)  # Pass selected_shelf to QRCodeScanner
        else:
            messagebox.showwarning("Warning", "Please select a shelf first.")

    def back_to_first_window(self):
        ask_to_proceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        if ask_to_proceed:
            self.destroy()
            self.parent_window.deiconify()

if __name__ == '__main__':
    root = tk.Tk()
    app = User(root)  
    root.mainloop()