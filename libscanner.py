import cv2
import os
from pyzbar.pyzbar import decode
import requests
import tkinter as tk
from tkinter import Label, Button, ttk, messagebox, Canvas, PhotoImage, font 
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import MySQLdb
import sshtunnel

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

current_date = datetime.now()
formatted_current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')



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
        self.b1.place(x=258, y=195, width=103, height=95)
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

        # self.scan_button = Button(self.window, text="Scan ID", command=self.scan_id)
        # self.scan_button.pack()

        # self.done_button = Button(self.window, text="Done", command=self.done, state="disabled")
        # self.done_button.pack()

        self.scanned_id_label = Label(self.window,text=self.scanned_id)
        self.scanned_id_label.pack_forget()
 
        self.capture_running = True
        self.update()
    
    # def open(self):
    #     qrcodescanner = QRCodeScanner(self.done)

    # def get_scanuser(self):
    #     return self.scanuser

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
                        messagebox.showwarning("Warning", "Username not found.")
                        self.qr_scanid_label.config(text="Username: ")
                    
                    else:
                        messagebox.showinfo("Username", "Successfully logged in")
                        print('Username exists')
                        self.scanIDpic.config(state="disabled")
                        self.Done.config(state="active")

                        
                    cursor.close()
                    connection.close()

            except Exception as e:
                messagebox.showwarning("Warning", "Connection timed out. Try again.")
                self.qr_scanid_label.config(text="Username:")
                print("Error fetching data from database:", str(e))


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
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the methods window?")
        
        if asktoproceed:
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
                self.scanIDpic.config(state="active")
                self.Done.config(state="disabled")
                self.scan_id()  
            else:
                pass  

class QRCodeScanner:
    def __init__(self, parent_window=None, selected_shelf="", selected_row="", scanuser = None):
        self.parent_window = parent_window
        self.selected_shelf = selected_shelf
        self.selected_row = selected_row
        self.scanuser = scanuser

        # self.user_instance = ScanUser()
        # self.scan_user_instance = ScanUser(parent_window=self.parent_window)
        # # Accessing the scanned_id attribute directly from the instance
        # self.scanned_id = self.scan_user_instance.get_scanned_id()

        # self.scanned_id= ScanUser.scanned_id
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("QR Code Scanner")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  # Set the width to 1920 pixels
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  # Set the height to 1080 pixels

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
                ok = messagebox.showwarning("Warning", "Connection timed out. Try again.")
                if ok:
                    self.open_combobox()
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
        print('wow')
        asktoproceed = messagebox.askyesno("Confirmation", "Done scanning?")
        if asktoproceed:
            self.update_stop_datetime()
            self.insert_misplaced()
            ask = messagebox.askyesno("Confirmation", "Scan Again?")
            if ask: 
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
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
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
            
            self.borrow_button.config(state="normal")
            self.borrower_button.config(state="disabled")
        
    def borrow_qr_code(self):
        return_date = current_date + timedelta(days=3)
        formatted_return_date = return_date.strftime('%Y-%m-%d %H:%M:%S')

        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")
            self.strqr = str(self.qr_data)
            self.borrow_button.config(state="disabled")

            asktoproceed = messagebox.askyesno("Confirmation", "Done scanning?") 
            if asktoproceed:   
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
                        cursor.execute("SELECT quantity FROM gen_books WHERE book_id = %s", (self.strqr,))
                        cur_quan = cursor.fetchone()

                        if cur_quan:
                            cur_quan = cur_quan[0]  
                            new_quan = cur_quan - 1  

                            #update quantity field -subtract 1
                            cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_id = %s", (new_quan, self.strqr))
                            connection.commit()
                            print("Quantity updated successfully!")

                            if new_quan == 0:
                                cursor.execute("UPDATE gen_books SET availability = %s WHERE book_id = %s", ('not available', self.strqr))
                                connection.commit()
                                print("Book not available")


                            #insert to database
                            insert_query = "INSERT INTO borrowed_books (book_id, staff_librarian, borrower, date_borrowed, date_return, status) VALUES (%s,%s,%s, %s, %s, %s)"
                            data_to_insert = (self.strqr, self.scanuser, self.borrowersqr, formatted_current_date, formatted_return_date, 'Borrowed')  # Define the values to be inserted
                            cursor.execute(insert_query, data_to_insert)
                            connection.commit()
                            print('Successfully inserted')
                            messagebox.showinfo("Success", "Borrowed succesfully.")

                        else:
                            messagebox.showwarning("Warning", "Book not found in inventory")


                        cursor.close()
                        connection.close()

                except Exception as e:
                    print("Error fetching data from database:", str(e))
                    messagebox.showinfo("Try Again", "Connection Timed out. Try again")
                
                asktoproceed = messagebox.askyesno("Confirmation", "Scan with the same borrower again?")
                if asktoproceed:
                    self.borrow_button.config(state="active")
                else:
                    self.window.destroy()
                    self.camera_running = False
                    if self.camera.isOpened():
                        self.camera.release()
                    self.parent_window.deiconify()       
            else:
                asktoproceed = messagebox.askyesno("Confirmation", "Scan the book again?")
                if asktoproceed:
                    self.borrow_button.config(state="active")
                

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

        self.borrower_button = Button(self.window, text="Scan Borrower", command=self.borrower_qr_code, state="active")
        self.borrower_button.pack()

        self.return_button = Button(self.window, text="Return", command=self.return_qr_code, state="disabled")
        self.return_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")
            self.borrowerqr = self.qr_databorrowers

            self.return_button.config(state="active")
            self.borrower_button.config(state="disabled")

    def return_qr_code(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")
            self.strqr = self.qr_data     
        
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
                cursor.execute("SELECT quantity FROM gen_books WHERE book_id = %s", (self.strqr,))
                cur_quan = cursor.fetchone()

                if cur_quan:
                    cur_quan = cur_quan[0]  
                    new_quan = cur_quan + 1  

                    #update quantity field -subtract 1
                    cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_id = %s", (new_quan, self.strqr))
                    connection.commit()
                    print("Quantity updated successfully!")

                    if new_quan > 0:
                        cursor.execute("UPDATE gen_books SET availability = %s WHERE book_id = %s", ('available', self.strqr))
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
                            messagebox.showwarning("Warning", "Book is returned late.")

                        else:
                            cursor.execute("UPDATE borrowed_books SET status = %s WHERE book_id = %s and borrower = %s", ('Returned', self.strqr, self.borrowerqr))
                            connection.commit()
                            print("returned")
                            messagebox.showinfo("Information", "Successfully returned.")

                cursor.close()
                connection.close()

        except Exception as e:
            messagebox.showinfo("Try Again", "Connection Timed out. Try again")
            print("Error fetching data from database:", str(e))


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
    def __init__(self, parent_window=None, scanuser=None):
        self.parent_window = parent_window
        self.window = tk.Toplevel(parent_window) 
        self.window.title("First Window")
        self.window.geometry("640x480")
        self.window.configure(bg="#ffffff")

        self.scanuser = scanuser
        # self.scanuser_string = str(self.scanuser)  # Convert scanuser to string
        # print(self.scanuser_string)

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

        self.scanuser_label = Label(self.window, text="")
        self.scanuser_label.pack()
    
    def show_scanuser_label(self, scanuser):
        self.scanuser_label.config(text=f"Welcome, {scanuser}")
        self.scanuser_string = str(scanuser)
        print(self.scanuser_string)

    def open_second_window(self):
        self.window.withdraw()
        # scanuser_text = self.show_scanuser_label(self.scanuser_string)
        # print("Scan User in First Window:", scanuser_text)
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
        asktoproceed = messagebox.askyesno("Confirmation", "Are you sure you want to log out?")
        
        if asktoproceed:
            self.window.withdraw()
            user_window = tk.Toplevel(self.parent_window)
            user_window.title("User Window")
            User(user_window)

class MainApplication(tk.Toplevel):
    def __init__(self, parent_window, scanuser_str=None):
        self.parent_window = parent_window
        super().__init__(parent_window)
        self.title("Main Application")
        self.geometry("640x480")
        self.configure(bg="#ffffff")

        self.scanuser_str = scanuser_str
        # #  self.scanuser = scanuser
        # print("Scan User in Main Application:", self.scanuser)

        # Call show_scanuser_label after initializing scanuser
        # self.show_scanuser_label()

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
        self.combo_box_value = tk.StringVar()  
        self.row_value = tk.StringVar() 

        self.row = ttk.Combobox(
            self, 
            values=["R-1", "R-2", "R-3", "R-4", "R-5"],
            textvariable=self.row_value,
            font=("Arial", 14),
            state="readonly",
)
        self.row.place(x=170, y=160, width=297, height=39)

        self.combo_box = ttk.Combobox(
            self, 
            values=["shelf01", "shelf02", "shelf03"],
            textvariable=self.combo_box_value,
            font=("Arial", 14),
            state="readonly",
)
        self.combo_box.place(x=170, y=210, width=297, height=39)
        
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

        self.row.bind("<<ComboboxSelected>>", self.update_selected_shelf_label)

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
        selected_shelf = self.combo_box_value.get()
        selected_row = self.row_value.get()
        if selected_shelf and selected_row:
            self.withdraw()
            qr_scanner = QRCodeScanner(self.parent_window, selected_shelf, selected_row)
            qr_scanner.show_scanuser_label(self.scanuser)
            self.return2.config(command=qr_scanner.close_window) 
        else:
            messagebox.showwarning("Warning", "Please select both shelf and row first.")

    def back_to_first_window(self):
        ask_to_proceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        if ask_to_proceed:
            self.destroy()
            self.parent_window.deiconify()


if __name__ == '__main__':
    root = tk.Tk()
    app = User(root)  
    root.mainloop()



# scan_user_instance = ScanUser()
# scanned_id = scan_user_instance.get_scanned_id()
# print(scanned_id)