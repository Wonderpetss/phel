import cv2
import os
from pyzbar.pyzbar import decode
import requests
import tkinter as tk
from tkinter import Label, Button, ttk, messagebox, Canvas, PhotoImage, font 
from tkinter.font import Font
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import MySQLdb
import sshtunnel

os.environ['DISPLAY'] = ':0'

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

current_date = datetime.now()
formatted_current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

import tkinter as tk

class CustomMessageBoxYN:
    def __init__(self, parent, title, message):
        self.result = False
        
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("365x100") 
        
        label = tk.Label(self.popup, text=message)
        label.pack(padx=15, pady=10)

        button_frame = tk.Frame(self.popup)
        button_frame.pack(padx=25, pady=13)

        yes_button = tk.Button(button_frame, text="Yes", command=self.set_result_true, width=15, height=3)
        yes_button.pack(side=tk.LEFT, padx=10, pady=1, expand=True)

        no_button = tk.Button(button_frame, text="No", command=self.close, width=15, height=3)
        no_button.pack(side=tk.LEFT, padx=10, pady=1, expand=True)

        x = (800 - 365) // 2
        y = (480 - 100) // 2

        self.popup.geometry(f"+{x}+{y}")

    def set_result_true(self):
        self.result = True  
        self.close()

    def close(self):
        self.popup.destroy()

class CustomMessageBox:
    def __init__(self, parent, title, message):
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("280x100")
        
        label = tk.Label(self.popup, text=message, font=("Arial", 11))
        label.pack(padx=20, pady=10)

        button = tk.Button(self.popup, text="OK", command=self.close, width=10, font=("Arial", 11))
        button.pack(pady=10)

        x = (800 - 280) // 2
        y = (480 - 100) // 2

        self.popup.geometry(f"+{x}+{y}")

    def close(self):
        self.popup.destroy()

class User:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Library Locator")
        self.root.geometry("640x410")
        self.root.configure(bg="#ffffff")
        self.canvas = Canvas(
            self.root,
            bg="#ffffff",
            height=440,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "scaniduser.png")

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
        self.b1.place(x=258, y=195, width=117, height=95)
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

        self.canvas = tk.Canvas(self.window, height=440, width=640,)
        self.canvas.pack()
 
        self.qr_detected = False
        self.scanned_id = ''
        label_font = font.Font(size=12, family="Arial", weight="bold")

        self.qr_scanid_label = Label(self.window, text="Username: ", font=label_font)
        self.qr_scanid_label.place(x=190, y=360)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        #scan id button
        img6 = PhotoImage(file=os.path.join(script_dir, "scanIDpic.png"))
        self.scanIDpic = Button(
            self.canvas,
            image = img6,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.scan_id,
            relief = "flat")
        self.scanIDpic.place(x = 144, y = 395, width = 173, height = 44)
        self.scanIDpic.image=img6
        
        #done button
        img7 = PhotoImage(file=os.path.join(script_dir, "Done.png"))
        self.Done = Button(
            self.canvas,
            image = img7,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.done, 
            state="disabled",
            relief = "flat")
        self.Done.place(x = 330, y = 395, width = 173, height = 44)
        self.Done.image=img7

        self.scanned_id_label = Label(self.window,text=self.scanned_id)
        self.scanned_id_label.pack_forget()
 
        self.capture_running = True
        self.update()

    def scan_id(self):
        if self.qr_detected:
            self.qr_scanid_label.config(text=f"Username: {self.scanned_id}")
            self.scanuser = self.scanned_id
            print(self.scanuser)

            try:
                with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username='wonderpets', ssh_password='Bo0kLocator!',
                remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
            ) as tunnel:
                    connection = MySQLdb.connect(
                        user='wonderpets',
                        passwd='chocolate290',
                        host='127.0.0.1', port=tunnel.local_bind_port,
                        db='wonderpets$db_library',
                    )

                    cursor = connection.cursor()

                    cursor.execute("SELECT username FROM userss WHERE username = %s", (self.scanned_id,))
                    user = cursor.fetchone()

                    if not user:
                        CustomMessageBox(self.window, "Warning", "Username not found.")
                        self.qr_scanid_label.config(text="Username: ")
                    
                    else:
                       
                        print('Username exists')
                        self.scanIDpic.config(state="disabled")
                        self.Done.config(state="active")

                    cursor.close()
                    connection.close()


            except Exception as e:
                self.qr_scanid_label.config(text="Username:")
                print("Error fetching data from database:", str(e))
                CustomMessageBox(self.window,"Warning", "Connection timed out. Try again.")


    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.scanned_id = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.scanned_id = ""

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
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Do you want to proceed to the methods window?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()
    
    def open_first_window(self):
        self.window.withdraw()  
        first_window = FirstWindow(self.window)
        first_window.show_scanuser_label(self.scanuser)
    

    def done(self):
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Do you want to proceed to the methods window?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.open_first_window()
        else:
            message_box = CustomMessageBoxYN(self.window, "Scan Again", "Do you want to scan again?")
            self.window.wait_window(message_box.popup)
            if message_box.result:
                self.qr_scanid_label.config(text=f"Username: ")
                self.scanIDpic.config(state="active")
                self.Done.config(state="disabled")
                self.scan_id()            

class QRCodeScanner:
    def __init__(self, parent_window=None, selected_shelf="", selected_row="", scanuser = None):
        self.parent_window = parent_window
        self.selected_shelf = selected_shelf
        self.selected_row = selected_row
        self.scanuser = scanuser
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("QR Code Scanner")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(
            self.window,
            bg="#ffffff",
            height=440,
            width=640, 
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        self.canvas.pack()

        self.results_label = Label(self.window, text="Scanning QR codes...")
        self.results_label.pack_forget
        self.combo_box_value = tk.StringVar() 
        self.row_value = tk.StringVar()
     
        self.combo_box_label = Label(self.window, textvariable=self.combo_box_value)
        self.combo_box_label.pack_forget()
        
        self.selected_shelf_label = Label(self.window, text=f"Selected Shelf: {self.selected_shelf}")  
        self.selected_shelf_label.pack_forget()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        img5 = PhotoImage(file=os.path.join(script_dir, "StopCam.png"))
        self.stopCam = Button(
            self.canvas,
            image=img5,
            borderwidth=0,
            highlightthickness=0,
            command=self.close_window,
            relief="flat",
            bg="#FFFFFF"
        )
        self.stopCam.place(x =200 , y = 380, width = 250, height = 60)
        self.stopCam.image=img5   

        #home button
        imgH = PhotoImage(file=os.path.join(script_dir, "Homie.png"))
        self.Homie = Button(
            self.canvas,
            image=imgH,
            borderwidth=0,
            highlightthickness=0,
            command=self.back_to_first_window,
            relief="flat"
        )
        self.Homie.place(x =10 , y = 390, width = 30, height = 23)
        self.Homie.image=imgH  

        self.qr_values = self.retrieve_data(self.selected_shelf, self.selected_row)  
        self.camera_running = True

        self.red_qr_codes = set()

        self.update()

        self.start_datetime = datetime.now()
        self.stop_datetime = None

        self.scanuser_label = Label (self.window, text ="")
        self.scanuser_label.pack_forget()

    def show_scanuser_label (self, scanuser):
        self.scanuser_label.config(text=scanuser)
        self.scanuser_str= str(scanuser)
        print(self.scanuser_str)

    def update_stop_datetime(self):
        self.stop_datetime = datetime.now()

    def red_codes (self):
        self.length = len(self.red_qr_codes)
        a = self.length
        return a

    def retrieve_data(self, selected_shelf, selected_row):
        try:
            base_url = "https://wonderpets.pythonanywhere.com/"
            shelf_url = base_url + selected_shelf + "/" + selected_row
            response = requests.get(shelf_url)
            print("API RESPONSE:", response.json())
            if response.status_code == 200:
                qr_values = response.json()
                return set(qr_values)
            else:
                print("Error fetching data from API:", response.text)
                # return set()
        except Exception as e:
            print("Error fetching data from API:", str(e))
            # maireturn set()
    

    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            self.show_frame(frame, decoded_objects)
        self.window.after(30, self.update)

    def close_window(self):
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Done scanning?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.update_stop_datetime()
            self.insert_misplaced()
            
            message_box = CustomMessageBoxYN(self.window, "Confirmation", "Scan Again?")
            self.window.wait_window(message_box.popup)
            if message_box.result:
                self.camera_running = False
                if self.camera.isOpened():
                    self.camera.release()
                self.open_combobox()
            else:
                self.window.destroy()
                self.camera_running = False
                if self.camera.isOpened():
                    self.camera.release()
                self.parent_window.deiconify()

    def open_combobox(self):
        self.window.destroy()
        parent = self.parent_window if self.parent_window else None
        print(self.scanuser_str)
        MainApplication(parent)
        
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
                self.red_qr_codes.add(qr_data)
                print(self.red_qr_codes)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.photo = photo

    def insert_misplaced(self):
        try:
            with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='wonderpets', ssh_password='Bo0kLocator!',
            remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
                connection = MySQLdb.connect(
                    user='wonderpets',
                    passwd='chocolate290',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    db='wonderpets$db_library',
                )

                cursor = connection.cursor()

                red_code_length = self.red_codes()

                #insert to database
                insert_query = "INSERT INTO log_read (username, misplaced_books, date_startscan, date_stopscan) VALUES (%s,%s, %s, %s)"
                data_to_insert = (
                    self.scanuser_str, 
                    red_code_length , 
                    self.start_datetime.strftime('%Y-%m-%d %H:%M:%S'), 
                    self.stop_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    ) 
                cursor.execute(insert_query, data_to_insert)
                connection.commit()
                print('Successfully inserted')

                cursor.close()
                connection.close()

        except Exception as e:
            print("Error fetching data from database:", str(e))

    def back_to_first_window(self):
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Do you want to proceed to methods window?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()
            self.update_date_time() 

class Borrow:
    def __init__(self, parent_window=None, scanuser_str = None):
        self.parent_window = parent_window
        self.scanuser_str = scanuser_str

        self.window = tk.Toplevel(parent_window)
        self.window.title("Borrow")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(self.window, width=640, height=440)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""

        self.wow_label = Label(self.window, text="")
        self.wow_label.pack_forget()
        custom_font = Font(size=13)

        self.qr_borrower_label = Label(self.window, text="Borrower:", font=custom_font)
        self.qr_borrower_label.place(x=90, y=370)

        self.qr_data_label = Label(self.window, text="Borrow Book: ", font=custom_font)
        self.qr_data_label.place(x=90, y=400)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        imgbook = PhotoImage(file=os.path.join(script_dir, "BorrowerLogo.png"))
        self.ScanBorrower = Button(
            self.canvas,
            image = imgbook,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.borrower_qr_code,
            relief = "flat")
        self.ScanBorrower.place(x = 310, y = 360, width = 158, height = 75)
        self.ScanBorrower.image=imgbook

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        imgbook2 = PhotoImage(file=os.path.join(script_dir, "BorrowLogo.png"))
        self.BookBorrow = Button(
            self.canvas,
            image = imgbook2,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.borrow_qr_code,
            relief = "flat")
        self.BookBorrow.place(x = 481, y = 360, width = 158, height = 75)
        self.BookBorrow.image=imgbook2      

        imgH = PhotoImage(file=os.path.join(script_dir, "Homie.png"))
        self.Homie = Button(
            self.canvas,
            image=imgH,
            borderwidth=0,
            highlightthickness=0,
            command=self.back_to_first_window,
            relief="flat"
        )
        self.Homie.place(x =10 , y = 390, width = 30, height = 23)
        self.Homie.image=imgH       

        self.capture_running = True
        self.update()

        self.scanuser_label = Label(self.window, text="")
        self.scanuser_label.pack_forget()
    
    def show_scanuser_label(self, scanuser_str):
        self.scanuser_label.config(text=scanuser_str)
        self.scanuser = str(scanuser_str)
        print(self.scanuser)

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")
            self.borrowersqr = str(self.qr_databorrowers)
            
            self.BookBorrow.config(state="normal")
            self.ScanBorrower.config(state="disabled")
        
    def borrow_qr_code(self):
        return_date = current_date + timedelta(days=3)
        formatted_return_date = return_date.strftime('%Y-%m-%d %H:%M:%S')

        if self.qr_detected:
            self.qr_data_label.config(text=f"Borrow Book: {self.qr_data}")
            self.strqr = str(self.qr_data)
            self.BookBorrow.config(state="disabled")

            message_box = CustomMessageBoxYN(self.window, "Confirmation", "Done scanning?")
            self.window.wait_window(message_box.popup)
            if message_box.result:
                try:
                    with sshtunnel.SSHTunnelForwarder(
                    ('ssh.pythonanywhere.com'),
                    ssh_username='wonderpets', ssh_password='Bo0kLocator!',
                    remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
                ) as tunnel:
                        connection = MySQLdb.connect(
                            user='wonderpets',
                            passwd='chocolate290',
                            host='127.0.0.1', port=tunnel.local_bind_port,
                            db='wonderpets$db_library',
                        )

                        cursor = connection.cursor()

                        print(self.strqr)
                        #get quantity of the book_id detected
                        cursor.execute("SELECT quantity FROM gen_books WHERE book_loc = %s", (self.strqr,))
                        cur_quan = cursor.fetchone()

                        if cur_quan:
                            cur_quan = cur_quan[0]  
                            new_quan = cur_quan - 1  

                            #update quantity field -subtract 1
                            cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_loc = %s", (new_quan, self.strqr))
                            connection.commit()
                            print("Quantity updated successfully!")

                            if new_quan == 0:
                                cursor.execute("UPDATE gen_books SET availability = %s WHERE book_loc = %s", ('not available', self.strqr))
                                connection.commit()
                                print("Book not available")


                            #insert to database
                            insert_query = "INSERT INTO borrowed_books (book_id, staff_librarian, borrower, date_borrowed, date_return, status) VALUES (%s,%s,%s, %s, %s, %s)"
                            data_to_insert = (self.strqr, self.scanuser, self.borrowersqr, formatted_current_date, formatted_return_date, 'Borrowed')  # Define the values to be inserted
                            cursor.execute(insert_query, data_to_insert)
                            connection.commit()
                            print('Successfully inserted')
                            CustomMessageBox(self.window,"Success", "Borrowed succesfully.")

                        else:
                            CustomMessageBox(self.window,"Warning", "Book not found in inventory")


                        cursor.close()
                        connection.close()

                except Exception as e:
                    print("Error fetching data from database:", str(e))
                    CustomMessageBox(self.window,"Try Again", "Connection Timed out. Try again")
                
                message_box = CustomMessageBoxYN(self.window, "Scan Again", "Scan with the same borrower again?")
                self.window.wait_window(message_box.popup)
                if message_box.result:
                    self.BookBorrow.config(state="active")
                else:
                    self.qr_borrower_label.config(text=f"Borrower: ")
                    self.qr_data_label.config(text=f"Borrow Book: ")
                    self.BookBorrow.config(state="disabled")
                    self.ScanBorrower.config(state="active")
            else:
                message_box = CustomMessageBoxYN(self.window, "Scan Again", "Scan the book again?")
                self.window.wait_window(message_box.popup)
                if message_box.result:
                    self.BookBorrow.config(state="active")
                

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
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Do you want to proceed to methods window?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
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

        self.canvas = tk.Canvas(self.window, width=640, height=440)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""
        custom_font = Font(size=13)

        self.qr_borrower_label = Label(self.window, text="Borrower:", font=custom_font)
        self.qr_borrower_label.place(x=90, y=370)

        self.qr_data_label = Label(self.window, text="Return Book: ", font=custom_font)
        self.qr_data_label.place(x=90, y=400)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        imgbook = PhotoImage(file=os.path.join(script_dir, "BorrowerLogo.png"))
        self.ScanBorrower = Button(
            self.canvas,
            image = imgbook,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.borrower_qr_code,
            relief = "flat")
        self.ScanBorrower.place(x = 310, y = 360, width = 158, height = 75)
        self.ScanBorrower.image=imgbook

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        imgbook2 = PhotoImage(file=os.path.join(script_dir, "ReturnLogo.png"))
        self.BookReturnw = Button(
            self.canvas,
            image = imgbook2,
            borderwidth = 0,
            highlightthickness = 0,
            command = self.return_qr_code,
            relief = "flat")
        self.BookReturn.place(x = 481, y = 360, width = 158, height = 75)
        self.BookReturn.image=imgbook2  

        imgH = PhotoImage(file=os.path.join(script_dir, "Homie.png"))
        self.Homie = Button(
            self.canvas,
            image=imgH,
            borderwidth=0,
            highlightthickness=0,
            command=self.back_to_first_window,
            relief="flat"
        )
        self.Homie.place(x =10 , y = 390, width = 30, height = 23)
        self.Homie.image=imgH      

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")
            self.borrowerqr = self.qr_databorrowers

            self.Book.config(state="active")
            self.ScanBorrower.config(state="disabled")

    def return_qr_code(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"Return Book: {self.qr_data}")
            self.strqr = self.qr_data

            message_box = CustomMessageBoxYN(self.window, "Confirmation", "Done scanning?")
            self.window.wait_window(message_box.popup)
            if message_box.result:  
                try:
                    with sshtunnel.SSHTunnelForwarder(
                    ('ssh.pythonanywhere.com'),
                    ssh_username='wonderpets', ssh_password='Bo0kLocator!',
                    remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
                ) as tunnel:
                        connection = MySQLdb.connect(
                            user='wonderpets',
                            passwd='chocolate290',
                            host='127.0.0.1', port=tunnel.local_bind_port,
                            db='wonderpets$db_library',
                        )

                        cursor = connection.cursor()

                        #get quantity of the book_id detected
                        cursor.execute("SELECT quantity FROM gen_books WHERE book_loc = %s", (self.strqr,))
                        cur_quan = cursor.fetchone()

                        if cur_quan:
                            cur_quan = cur_quan[0]  
                            new_quan = cur_quan + 1  

                            #update quantity field -subtract 1
                            cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_loc = %s", (new_quan, self.strqr))
                            connection.commit()
                            print("Quantity updated successfully!")

                            if new_quan > 0:
                                cursor.execute("UPDATE gen_books SET availability = %s WHERE book_loc = %s", ('available', self.strqr))
                                connection.commit()
                                print("Book available")

                            #get date_return based from the macthed book_id and borrower detected
                            cursor.execute("SELECT date_return FROM borrowed_books WHERE book_id = %s and borrower = %s", (self.strqr,self.borrowerqr))
                            cur_datereturn = cursor.fetchone()

                            if cur_datereturn:
                                cur_datereturn = cur_datereturn[0]

                                if current_date > cur_datereturn:
                                    #update borrowed_books
                                    cursor.execute("UPDATE borrowed_books SET status = %s WHERE book_id = %s and borrower = %s", ('Returned Late', self.strqr, self.borrowerqr))
                                    connection.commit()
                                    print("returned late")
                                    CustomMessageBox(self.window,"Warning", "Book is returned late.")

                                else:
                                    cursor.execute("UPDATE borrowed_books SET status = %s WHERE book_id = %s and borrower = %s", ('Returned', self.strqr, self.borrowerqr))
                                    connection.commit()
                                    print("returned")
                                    CustomMessageBox(self.window,"Information", "Successfully returned.")
                                   

                        cursor.close()
                        connection.close()

                except Exception as e:
                    CustomMessageBox(self.window,"Try Again", "Connection Timed out. Try again")
                    print("Error fetching data from database:", str(e))
                
                message_box = CustomMessageBoxYN(self.window, "Scan Again", "Scan with the same borrower again?")
                self.window.wait_window(message_box.popup)
                if message_box.result:
                    self.BookBorrow.config(state="active")
                else:
                    self.qr_borrower_label.config(text=f"Borrower: ")
                    self.qr_data_label.config(text=f"Return Book: ")
                    self.BookBorrow.config(state="disabled")
                    self.ScanBorrower.config(state="active")
            else:
                message_box = CustomMessageBoxYN(self.window, "Scan Again", "Scan the book again?")
                self.window.wait_window(message_box.popup)
                if message_box.result:
                    self.BookBorrow.config(state="active")
                

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
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Do you want to proceed to methods window?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class FirstWindow:
    def __init__(self, parent_window=None, scanuser=None):
        self.parent_window = parent_window
        self.window = tk.Toplevel(parent_window) 
        self.window.title("First Window")
        self.window.geometry("640x410")
        self.window.configure(bg="#ffffff")

        self.scanuser = scanuser

        self.canvas = Canvas(
            self.window,
            bg="#ffffff",
            height=440,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "selectmethod.png")

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
        self.b0.place(x=115, y=185, width=123, height=105)
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
        self.b1.place(x=258, y=185, width=123, height=105)
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
        self.b2.place(x=400, y=185, width=123, height=105)
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
        self.b3.place(x=270, y=310, width=98, height=25)
        self.b3.image= img3

        self.scanuser_label = Label(self.window, text="")
        self.scanuser_label.pack_forget()
    
    def show_scanuser_label(self, scanuser):
        self.scanuser_label.config(
            text=f"Welcome, {scanuser}",
            font=("Arial", 13, "bold"),
            highlightthickness=0, 
            highlightbackground=self.window.cget("bg")
        )
        self.scanuser_label.place(x=78, y=74)
        self.scanuser_string = str(scanuser)
        print(self.scanuser_string)

    def open_second_window(self):
        self.window.withdraw()
        main_app = MainApplication(self.window)
        main_app.show_scanuser_label(self.scanuser_string)

    def open_pers_window(self):
        self.window.withdraw()
        borrow_app = Borrow(self.window)
        borrow_app.show_scanuser_label(self.scanuser_string)

    def open_third_window(self):
        self.window.withdraw()
        Return(self.window)

    def scan_user_window(self):
        message_box = CustomMessageBoxYN(self.window, "Confirmation", "Are you sure you want to log-out?")
        self.window.wait_window(message_box.popup)
        if message_box.result:
            self.window.withdraw()
            user_window = tk.Toplevel(self.parent_window)
            user_window.title("User Window")
            User(user_window)

class CustomCombobox:
    def __init__(self, master, values):
        self.master = master
        self.values = values

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(master, textvariable=self.entry_var, font=("Helvetica", 16))
        self.entry.pack(pady=10)
        self.entry.bind("<Button-1>", self.show_dropdown)

        self.listbox = tk.Listbox(master, font=("Helvetica", 16), selectmode=tk.SINGLE)
        for item in values:
            self.listbox.insert(tk.END, item)

        self.listbox.bind("<Button-1>", self.on_listbox_select)
        self.listbox.place_forget()

    def on_listbox_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_value = self.listbox.get(selected_index)
            self.entry_var.set(selected_value)
            self.listbox.place_forget()

    def on_touch_release(self, event):
        x = event.x_root - self.master.winfo_rootx()
        y = event.y_root - self.master.winfo_rooty()
        if self.entry.winfo_rootx() <= x <= self.entry.winfo_rootx() + self.entry.winfo_width() and \
                self.entry.winfo_rooty() <= y <= self.entry.winfo_rooty() + self.entry.winfo_height():
            self.show_dropdown()

        if self.listbox.winfo_ismapped() and not (self.listbox.winfo_rootx() <= x <= self.listbox.winfo_rootx() + self.listbox.winfo_width() and \
                self.listbox.winfo_rooty() <= y <= self.listbox.winfo_rooty() + self.listbox.winfo_height()):
            self.listbox.place_forget()

    def bind_touch_events(self):
        self.entry.bind("<ButtonRelease-1>", self.on_touch_release)
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)

    def show_dropdown(self, event):
        x_entry, y_entry, width, height = self.entry.winfo_rootx(), self.entry.winfo_rooty(), self.entry.winfo_width(), self.entry.winfo_height()
        x_master = self.master.winfo_rootx() 
        y_master = self.master.winfo_rooty()  

        
        rel_x = x_entry - x_master
        rel_y = y_entry - y_master + height  

       
        self.listbox.place(x=rel_x, y=rel_y)
        self.listbox.lift()

class MainApplication(tk.Toplevel):
    def __init__(self, parent_window, scanuser_str=None):
        self.parent_window = parent_window
        super().__init__(parent_window)
        self.title("Main Application")
        self.geometry("640x410")
        self.configure(bg="#ffffff")

        self.scanuser_str = scanuser_str

        self.canvas = Canvas(
            self,
            bg="#ffffff",
            height=440,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "mainapp.png")

        if os.path.exists(image_path):
            background_img = PhotoImage(file=image_path)
            
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

        self.Home.place(x = 80, y = 108, width = 40, height = 39)
        self.Home.image=imgHome
        self.combo_box_value = tk.StringVar() 
        self.row_value = tk.StringVar() 

         # Create an instance of CustomCombobox for shelf selection
        self.combo_box_values = ["shelf01", "shelf02", "shelf03", "shelf04", "shelf05", "shelf06",
                            "shelf07", "shelf08", "shelf09", "shelf10", "shelf11", "shelf12",
                            "shelf13", "shelf14", "shelf15"]
        self.custom_combobox_shelf = CustomCombobox(self, self.combo_box_values)
        self.custom_combobox_shelf.entry.place(x=140, y=150, width=150, height=39)

        # Create an instance of CustomCombobox for row selection
        self.row_values = ["R1", "R2", "R3", "R4", "R5"]
        self.custom_combobox_row = CustomCombobox(self, self.row_values)
        self.custom_combobox_row.entry.place(x=347, y=150, width=150, height=39)

        self.custom_combobox_shelf.entry.bind("<<ComboboxSelected>>", self.update_selected_shelf_label)
        self.custom_combobox_row.entry.bind("<<ComboboxSelected>>", self.update_selected_row_label)


        img4 = PhotoImage(file=os.path.join(script_dir, "BroBro.png"))
        self.return2 = Button(
            self.canvas,
            image=img4,
            borderwidth=0,
            highlightthickness=0,
            command=self.open_scanner,
            relief="flat"
        )
        self.return2.place(x=270, y=220, width=120, height=90)
        self.return2.image=img4
        
        # self.combo_box.bind("<<ComboboxSelected>>", self.update_selected_shelf_label)

        # self.row.bind("<<ComboboxSelected>>", self.update_selected_shelf_label)

        self.selected_shelf_label = Label(self, text="Selected Shelf: None")
        self.selected_shelf_label.pack_forget()

        self.selected_row_label = Label(self, text="Selected Row: None")
        self.selected_row_label.pack_forget()

        self.scanuser_label = Label(self, text="")
        self.scanuser_label.pack_forget()

    def show_scanuser_label(self, scanuser_str):
        self.scanuser_label.config(text=scanuser_str)
        self.scanuser= str(scanuser_str)
        print(self.scanuser)


    def update_selected_shelf_label(self, event):
        self.selected_shelf = self.combo_box_value.get()
        self.selected_shelf_label.config(text=f"Selected Shelf: {self.selected_shelf}")
        

    def update_selected_row_label(self, event):
        selected_row = self.row_value.get()
        self.selected_row_label.config(text=f"Selected Shelf: {selected_row}")


    def open_scanner(self):
        selected_shelf = self.custom_combobox_shelf.entry_var.get()
        print(selected_shelf)
        selected_row = self.custom_combobox_row.entry_var.get()
        print(selected_row)
        if selected_shelf and selected_row:
            self.withdraw()
            qr_scanner = QRCodeScanner(self.parent_window, selected_shelf, selected_row)
            qr_scanner.show_scanuser_label(self.scanuser)
            self.return2.config(command=qr_scanner.close_window) 
        else:
            CustomMessageBox(self,"Warning", "Please select both shelf and row first.")

    def back_to_first_window(self):
        message_box = CustomMessageBoxYN(self, "Confirmation", "Do you want to proceed to methods window?")
        self.wait_window(message_box.popup)
        if message_box.result:
            self.destroy()
            self.parent_window.deiconify()


if __name__ == '__main__':
    root = tk.Tk()
    app = User(root)  
    root.mainloop()

