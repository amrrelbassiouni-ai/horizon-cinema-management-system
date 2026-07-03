import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date, timedelta
import bcrypt
import hashlib

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="YOUR_MYSQL_PASSWORD",
    database="hcinema"
)
cursor = conn.cursor(buffered=True)

# ---------- COLOR SCHEME ------------
DARK_BLUE_BG = "#001F3F"   # Main background (deep navy)
CARD_BLUE_BG = "#003366"   # Card background (slightly lighter navy)
ACCENT_COLOR = "#39CCCC"   # Vibrant teal accent
TEXT_COLOR   = "#FFFFFF"   # White text
BUTTON_FG    = "#001F3F"   # Dark text on buttons
# -------------------------------------

class HorizonCinemasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Horizon Cinemas")
        self.selected_movie_id = None
        self.booking_date = date.today()  # Global booking date used in queries
        self.user_city = "Unknown"  # Will be set on login

        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
      
        self.create_home_page()

    # ---------- Authentication ----------
    

    def authenticate(self, role):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            if role == "Admin":
                cursor.execute("SELECT password, city FROM admin WHERE username = %s", (username,))
            elif role == "Staff":
                cursor.execute("SELECT password, city FROM staff WHERE username = %s", (username,))
            elif role == "Manager":
                cursor.execute("SELECT password FROM manager WHERE username = %s", (username,))
            else:
                messagebox.showerror("Error", "Invalid role selected.")
                return

            result = cursor.fetchone()

            if result:
                stored_password = result[0]
                city = result[1] if role in ["Admin", "Staff"] else "All Cities"

                if stored_password == hashed_password:
                    self.user_city = city
                    self.user_role = role 
                    messagebox.showinfo("Login Success", f"Welcome {role}!")

                    self.login_frame.pack_forget()
                    if role == "Admin":
                        self.admin_view()
                    elif role == "Manager":
                        self.manager_view()
                    elif role == "Staff":
                        self.staff_booking_page()
                else:
                    messagebox.showerror("Login Failed", "Incorrect password.")
            else:
                messagebox.showerror("Login Failed", "Username not found.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")



    def back_to_home(self):
        for frame in ['login_frame', 'staff_booking_frame', 'booking_frame', 'receipt_frame',
                      'admin_frame', 'movie_frame', 'assign_frame', 'showtime_frame',
                      'add_cinema_frame', 'listing_frame', 'manager_frame']:
            if hasattr(self, frame):
                getattr(self, frame).pack_forget()
        self.create_home_page()

    def create_home_page(self):
        self.home_frame = tk.Frame(self.root, bg='#1e1e1e')
        self.home_frame.pack(fill='both', expand=True)

        title_label = tk.Label(self.home_frame, text="Horizon Cinemas", 
                               font=('Arial', 45, 'bold'), fg='white', bg='#1e1e1e')
        title_label.pack(pady=50)

        roles = ['Admin', 'Manager', 'Staff']
        for role in roles:
            button = tk.Button(self.home_frame, text=role, font=('Arial', 22, 'bold'),
                               fg='black', bg='#d9d9d9', width=20, height=2,
                               relief='raised', bd=5,
                               command=lambda r=role: self.open_login(r))
            button.pack(pady=20)

    def open_login(self, role):
        self.home_frame.pack_forget()
        self.login_page(role)

    def login_page(self, role):
        self.login_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.login_frame.pack(fill='both', expand=True)

        title_label = tk.Label(self.login_frame, text=f"{role} Login", 
                               font=('Arial', 35, 'bold'), fg='white', bg='#2b2b2b')
        title_label.pack(pady=40)

        username_label = tk.Label(self.login_frame, text="Username:", 
                                  font=('Arial', 18), fg='white', bg='#2b2b2b')
        username_label.pack()
        self.username_entry = tk.Entry(self.login_frame, font=('Arial', 16),
                                       width=30, bg='#d9d9d9', fg='black')
        self.username_entry.pack(pady=10)

        password_label = tk.Label(self.login_frame, text="Password:", 
                                  font=('Arial', 18), fg='white', bg='#2b2b2b')
        password_label.pack()
        self.password_entry = tk.Entry(self.login_frame, font=('Arial', 16),
                                       width=30, show='*', bg='#d9d9d9', fg='black')
        self.password_entry.pack(pady=10)

        login_button = tk.Button(self.login_frame, text="Login", 
                                 font=('Arial', 18, 'bold'), fg='black', bg='#d9d9d9', 
                                 width=20, command=lambda: self.authenticate(role))
        login_button.pack(pady=20)

        back_button = tk.Button(self.login_frame, text="Back", 
                                font=('Arial', 16, 'bold'), fg='black', bg='#a0a0a0', 
                                width=20, command=self.back_to_home)
        back_button.pack(pady=10)

    # ---------- Staff Booking Page ----------
    def staff_booking_page(self):
        self.staff_booking_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.staff_booking_frame.pack(fill='both', expand=True)

        title_label = tk.Label(self.staff_booking_frame, text=f"{self.user_city} Staff Booking Page", 
                               font=('Arial', 40, 'bold'), fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title_label.pack(pady=20)

        # Date selection
        date_frame = tk.Frame(self.staff_booking_frame, bg=DARK_BLUE_BG)
        date_frame.pack(pady=10)
        prev_date_btn = tk.Button(date_frame, text="Previous Day", font=('Arial', 14, 'bold'),
                                  fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.decrement_date_staff)
        prev_date_btn.pack(side="left", padx=10)
        self.date_label = tk.Label(date_frame, text=self.booking_date.strftime("%Y-%m-%d"),
                                   font=('Arial', 18, 'bold'), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        self.date_label.pack(side="left", padx=10)
        next_date_btn = tk.Button(date_frame, text="Next Day", font=('Arial', 14, 'bold'),
                                  fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.increment_date_staff)
        next_date_btn.pack(side="left", padx=10)

        separator = ttk.Separator(self.staff_booking_frame, orient='horizontal')
        separator.pack(fill='x', padx=40)

        # List movies
        cursor.execute("SELECT * FROM Movies")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        movies = []
        for row in rows:
            movie = {column_names[i]: row[i] for i in range(len(column_names))}
            movies.append(movie)

        canvas_frame = tk.Frame(self.staff_booking_frame, bg=DARK_BLUE_BG)
        canvas_frame.pack(fill='both', expand=True)
        canvas = tk.Canvas(canvas_frame, bg=DARK_BLUE_BG, highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.config(scrollregion=canvas.bbox('all')))
        content_frame = tk.Frame(canvas, bg=DARK_BLUE_BG)
        canvas.create_window((0, 0), window=content_frame, anchor='nw')

        booking_date_str = self.booking_date.strftime("%Y-%m-%d")
        for movie in movies:
            cursor.execute(
                "SELECT show_time FROM movie_showings WHERE movie_id = %s AND city = %s AND screen_id IS NOT NULL AND time_id IS NOT NULL",
                (movie['Movie_ID'], self.user_city)
            )
            time_rows = cursor.fetchall()
            showtimes = [t[0] for t in time_rows]

            card_frame = tk.Frame(content_frame, bg=CARD_BLUE_BG, bd=5, relief='ridge')
            card_frame.pack(fill='x', expand=True, padx=40, pady=20)

            movie_name_label = tk.Label(card_frame, text=movie['Movie_Name'],
                                        font=('Arial', 24, 'bold'), fg=TEXT_COLOR, bg=CARD_BLUE_BG)
            movie_name_label.pack(anchor='w', padx=15, pady=(15, 5))

            movie_description_label = tk.Label(card_frame, text=movie['Movie_Description'],
                                               font=('Arial', 16), fg=TEXT_COLOR, bg=CARD_BLUE_BG,
                                               wraplength=1500, justify='left')
            movie_description_label.pack(anchor='w', padx=15, pady=5)

            details_frame = tk.Frame(card_frame, bg=CARD_BLUE_BG)
            details_frame.pack(anchor='w', padx=15, pady=10)
            genre_label = tk.Label(details_frame, text=f"Genre: {movie['Genre']}",
                                   font=('Arial', 14), fg=TEXT_COLOR, bg=CARD_BLUE_BG)
            genre_label.pack(side='left', padx=(0, 20))
            rating_label = tk.Label(details_frame, text=f"Rating: {movie['Rating']}",
                                    font=('Arial', 14), fg=TEXT_COLOR, bg=CARD_BLUE_BG)
            rating_label.pack(side='left', padx=(0, 20))
            age_label = tk.Label(details_frame, text=f"Age: {movie['Age']}+",
                                 font=('Arial', 14), fg=TEXT_COLOR, bg=CARD_BLUE_BG)
            age_label.pack(side='left', padx=(0, 20))

            if showtimes:
                showtimes_frame = tk.Frame(card_frame, bg=CARD_BLUE_BG)
                showtimes_frame.pack(fill='x', anchor='w', padx=15, pady=(0, 10))
                showtime_title_label = tk.Label(showtimes_frame, text="Showtimes:",
                                                font=('Arial', 16, 'bold'),
                                                fg=ACCENT_COLOR, bg=CARD_BLUE_BG)
                showtime_title_label.pack(anchor='w', pady=5)
                times_container = tk.Frame(showtimes_frame, bg=CARD_BLUE_BG)
                times_container.pack(anchor='w')
                for st in showtimes:
                    st_group = tk.Frame(times_container, bg=CARD_BLUE_BG)
                    st_group.pack(side="left", padx=10, pady=5)
                    showtime_btn = tk.Button(st_group, text=st, font=("Arial", 14, "bold"), 
                                             bg="#FFD700", fg="black", padx=10, pady=5, bd=1)
                    showtime_btn.pack()
                    cursor.execute(
                        "SELECT showing_id FROM movie_showings WHERE movie_id = %s AND show_time = %s AND city = %s AND screen_id IS NOT NULL AND time_id IS NOT NULL",
                        (movie['Movie_ID'], st, self.user_city)
                    )
                    sd = cursor.fetchone()
                    if sd:
                        cursor.execute("SELECT Screen_id FROM movie_showings WHERE showing_id = %s", (sd[0],))
                        se = cursor.fetchone()
                        if se:
                            cursor.execute("SELECT seating_capacity FROM screen WHERE screen_id = %s", (se[0],))
                            sc = cursor.fetchone()[0]
                            cursor.execute("SELECT COUNT(*) FROM booked_seats WHERE showings_id = %s AND `date` = %s",
                                           (sd[0], booking_date_str))
                            count = cursor.fetchone()[0]
                            available_seats = sc - count
                        else:
                            available_seats = "N/A"
                    else:
                        available_seats = "N/A"
                    view_seats_btn = tk.Button(st_group, text=f"{available_seats} Seats", font=("Arial", 12, "bold"),
                           bg="#B32D00", fg="black", padx=8, pady=4, bd=1, relief="solid",
                           highlightbackground="#B32D00", activebackground="#D9534F", activeforeground="white",
                           command=lambda sid=sd[0], scr_id=se[0]: self.show_category_breakdown(sid, scr_id))
                    view_seats_btn.pack(pady=5)
            else:
                no_showtimes_label = tk.Label(card_frame, text="No showtimes available in this city.",
                                              font=('Arial', 14), fg=TEXT_COLOR, bg=CARD_BLUE_BG)
                no_showtimes_label.pack(anchor='w', padx=15, pady=(0, 10))

            book_button = tk.Button(card_frame, text="Book", font=('Arial', 16, 'bold'),
                                    fg=BUTTON_FG, bg=ACCENT_COLOR, cursor="hand2", width=10,
                                    command=lambda movie_id=movie['Movie_ID']: self.book_movie(movie_id))
            book_button.pack(anchor='e', padx=15, pady=(5, 15))
        back_button = tk.Button(self.staff_booking_frame, text="Back to Login", font=('Arial', 20, 'bold'),
                                fg=BUTTON_FG, bg=ACCENT_COLOR, width=20, command=self.back_to_home)
        back_button.pack(pady=30)
        cancel_btn = tk.Button(self.staff_booking_frame, text="Cancel a Booking", font=('Arial', 18, 'bold'),
                       fg=BUTTON_FG, bg=ACCENT_COLOR, width=25, command=self.view_and_cancel_bookings)
        cancel_btn.pack(pady=10)

    def increment_date_staff(self):
        self.booking_date += timedelta(days=1)
        self.refresh_staff_booking_page()

    def decrement_date_staff(self):
        new_date = self.booking_date - timedelta(days=1)
        if new_date >= date.today():
            self.booking_date = new_date
            self.refresh_staff_booking_page()

    def refresh_staff_booking_page(self):
        if hasattr(self, 'staff_booking_frame'):
            self.staff_booking_frame.destroy()
        self.staff_booking_page()

    # ---------- Book Movie Method ----------
    def book_movie(self, movie_id):
        self.selected_movie_id = movie_id
        self.staff_booking_frame.pack_forget()
        self.booking_page()

    # ----------------- Booking Page -----------------
    def booking_page(self):
        self.booking_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.booking_frame.pack(fill='both', expand=True)
        nav_frame = tk.Frame(self.booking_frame, bg=DARK_BLUE_BG)
        nav_frame.pack(pady=10)
        prev_date_btn = tk.Button(nav_frame, text="Previous Day", font=("Arial", 14, "bold"),
                                  fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.decrement_date_booking)
        prev_date_btn.pack(side="left", padx=10)
        self.booking_date_label = tk.Label(nav_frame, text=self.booking_date.strftime("%Y-%m-%d"),
                                           font=("Arial", 16, "bold"), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        self.booking_date_label.pack(side="left", padx=10)
        next_date_btn = tk.Button(nav_frame, text="Next Day", font=("Arial", 14, "bold"),
                                  fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.increment_date_booking)
        next_date_btn.pack(side="left", padx=10)
        title = tk.Label(self.booking_frame, text=f"Booking for Movie ID: {self.selected_movie_id} on {self.booking_date.strftime('%Y-%m-%d')}",
                         font=("Arial", 40, "bold"), fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=20)
        guest_frame = tk.Frame(self.booking_frame, bg=DARK_BLUE_BG)
        guest_frame.pack(pady=20)
        guest_id_label = tk.Label(guest_frame, text="Enter Phone Number:", font=("Arial", 18, "bold"),
                                  fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        guest_id_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.guest_id_entry = tk.Entry(guest_frame, font=("Arial", 16), width=20)
        self.guest_id_entry.grid(row=0, column=1, padx=10, pady=5)
        check_guest_btn = tk.Button(guest_frame, text="Check Guest", font=("Arial", 16, "bold"),
                                    fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.check_guest)
        check_guest_btn.grid(row=0, column=2, padx=10, pady=5)
        signup_label = tk.Label(guest_frame, text="New Guest Signup:", font=("Arial", 18, "bold"),
                                fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        signup_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=10)
        fname_label = tk.Label(guest_frame, text="First Name:", font=("Arial", 16),
                               fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        fname_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.fname_entry = tk.Entry(guest_frame, font=("Arial", 16), width=20)
        self.fname_entry.grid(row=2, column=1, padx=10, pady=5)
        lname_label = tk.Label(guest_frame, text="Last Name:", font=("Arial", 16),
                               fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        lname_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.lname_entry = tk.Entry(guest_frame, font=("Arial", 16), width=20)
        self.lname_entry.grid(row=3, column=1, padx=10, pady=5)
        phone_label = tk.Label(guest_frame, text="Phone Number:", font=("Arial", 16),
                               fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        phone_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.phone_entry = tk.Entry(guest_frame, font=("Arial", 16), width=20)
        self.phone_entry.grid(row=4, column=1, padx=10, pady=5)
        options_frame = tk.Frame(self.booking_frame, bg=DARK_BLUE_BG)
        options_frame.pack(pady=20)
        cursor.execute("SELECT DISTINCT show_Time FROM movie_showings WHERE movie_id = %s AND city = %s", 
                       (self.selected_movie_id, self.user_city))
        showtime_rows = cursor.fetchall()
        available_showtimes = [row[0] for row in showtime_rows]
        showtime_label = tk.Label(options_frame, text="Select Showtime:", font=("Arial", 18, "bold"),
                                  fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        showtime_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.showtime_combo = ttk.Combobox(options_frame, values=available_showtimes,
                                           font=("Arial", 16), width=20)
        self.showtime_combo.grid(row=0, column=1, padx=10, pady=5)
        if available_showtimes:
            self.showtime_combo.current(0)
        tickets_label = tk.Label(options_frame, text="Number of Tickets:", font=("Arial", 18, "bold"),
                                 fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        tickets_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.tickets_spinbox = tk.Spinbox(options_frame, from_=1, to=10, font=("Arial", 16), width=5)
        self.tickets_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        seat_label = tk.Label(options_frame, text="Seat Category:", font=("Arial", 18, "bold"),
                              fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        seat_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        cursor.execute("SELECT Category_Name FROM category")
        seat_rows = cursor.fetchall()
        categories = [row[0] for row in seat_rows]
        self.seat_combo = ttk.Combobox(options_frame, values=categories,
                                       font=("Arial", 16), width=20)
        self.seat_combo.grid(row=2, column=1, padx=10, pady=5)
        if categories:
            self.seat_combo.current(0)
        confirm_btn = tk.Button(self.booking_frame, text="Confirm Booking", font=("Arial", 20, "bold"),
                                fg=BUTTON_FG, bg=ACCENT_COLOR, width=20, command=self.confirm_booking)
        confirm_btn.pack(pady=20)
        back_btn = tk.Button(self.booking_frame, text="Back", font=("Arial", 18, "bold"),
                             fg=BUTTON_FG, bg=ACCENT_COLOR, width=15, command=self.back_to_staff_booking)
        back_btn.pack(pady=10)

    def increment_date_booking(self):
        self.booking_date += timedelta(days=1)
        self.refresh_booking_page()

    def decrement_date_booking(self):
        new_date = self.booking_date - timedelta(days=1)
        if new_date >= date.today():
            self.booking_date = new_date
            self.refresh_booking_page()

    def refresh_booking_page(self):
        if hasattr(self, 'booking_frame'):
            self.booking_frame.destroy()
        self.booking_page()

    def check_guest(self):
        guest_id = self.guest_id_entry.get().strip()
        if not guest_id:
            messagebox.showerror("Input Error", "Please enter a Guest ID to check.")
            return
        try:
            cursor.execute("SELECT phone_number FROM guest WHERE phone_number = %s", (guest_id,))
            result = cursor.fetchone()
            if result:
                messagebox.showinfo("Guest Check", "Guest Exists")
            else:
                messagebox.showinfo("Guest Check", "Guest not found, please sign up.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def confirm_booking(self):
        phone = self.guest_id_entry.get().strip() or self.phone_entry.get().strip()
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        showtime = self.showtime_combo.get()
        tickets = int(self.tickets_spinbox.get())
        seat_category = self.seat_combo.get()

        if not phone:
            messagebox.showerror("Input Error", "Please enter a Phone Number for the guest.")
            return

        cursor.execute("SELECT first_name, last_name FROM guest WHERE phone_number = %s", (phone,))
        guest_result = cursor.fetchone()

        if guest_result:
            fname, lname = guest_result
        else:
            if not (fname and lname):
                messagebox.showerror("Input Error", "New guest requires First Name and Last Name.")
                return

            cursor.execute("""
                INSERT INTO guest (first_name, last_name, phone_number)
                VALUES (%s, %s, %s)
            """, (fname, lname, phone))
            conn.commit()

        cursor.execute("""
            SELECT screen_id FROM movie_showings 
            WHERE movie_id = %s AND show_time = %s AND city = %s
        """, (self.selected_movie_id, showtime, self.user_city))
        screen_row = cursor.fetchone()
        if not screen_row:
            messagebox.showerror("Error", "No screen found for this movie and time.")
            return
        screen_id = screen_row[0]

        cursor.execute("""
            SELECT showing_id FROM movie_showings 
            WHERE movie_id = %s AND show_time = %s AND city = %s
        """, (self.selected_movie_id, showtime, self.user_city))
        showing_row = cursor.fetchone()
        if not showing_row:
            messagebox.showerror("Error", "No showing found for this movie and time.")
            return
        showing_id = showing_row[0]

        cursor.execute("SELECT category_id FROM category WHERE category_name = %s", (seat_category,))
        cat_row = cursor.fetchone()
        if not cat_row:
            messagebox.showerror("Error", "Seat category not found.")
            return
        category_id = cat_row[0]

        booking_date_str = self.booking_date.strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT seat_id FROM seat
            WHERE screen_id = %s
            AND category_id = %s
            AND seat_id NOT IN (
                    SELECT seatID FROM booked_seats 
                    WHERE showings_id = %s AND `date` = %s
            )
            ORDER BY RAND()
            LIMIT %s
        """, (screen_id, category_id, showing_id, booking_date_str, tickets))
        available_seats = cursor.fetchall()

        if len(available_seats) < tickets:
            messagebox.showinfo("Not Enough Seats", "Not enough seats available for this booking.")
            return

        cursor.execute("SELECT movie_name FROM movies WHERE movie_id = %s", (self.selected_movie_id,))
        movie_name_row = cursor.fetchone()
        if not movie_name_row:
            messagebox.showerror("Error", "Movie not found.")
            return
        movie_name = movie_name_row[0]

        cursor.execute("""
            INSERT INTO Booking (showing_id, movie_name, ticket_category, first_name, last_name, show_time, number_of_tickets, booking_date, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (showing_id, movie_name, seat_category, fname, lname, showtime, tickets, booking_date_str, phone))
        booking_id = cursor.lastrowid

        # Step 6: Insert booked seats
        for seat in available_seats:
            seat_id = seat[0]
            cursor.execute("""
                INSERT INTO booked_seats (seatID, showings_id, `date`)
                VALUES (%s, %s, %s)
            """, (seat_id, showing_id, booking_date_str))

        conn.commit()

        messagebox.showinfo("Success", "Booking confirmed successfully!")
        self.booking_frame.pack_forget()
        self.receipt_page(booking_id, category_id)

            #except mysql.connector.Error as err:
            #messagebox.showerror("Database Error", f"Error: {err}")

    def receipt_page(self, booking_id, cat_id):
        self.receipt_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.receipt_frame.pack(fill='both', expand=True)
    
        title = tk.Label(
            self.receipt_frame,
            text="Booking Receipt",
            font=("Arial", 40, "bold"),
            fg=ACCENT_COLOR,
            bg=DARK_BLUE_BG
        )
        title.pack(pady=40)
    
        cursor.execute("""
            SELECT movie_name, ticket_category, first_name, last_name, phone_number, 
                   show_time, number_of_tickets, booking_date
            FROM Booking 
            WHERE booking_id = %s
        """, (booking_id,))
        booking_details = cursor.fetchone()
        if booking_details:
            (movie_name, ticket_category, first_name, last_name, phone_number, show_time, number_of_tickets, booking_date) = booking_details
        else:
            messagebox.showerror("Error", "Booking details not found.")
            return
    
        details_frame = tk.Frame(self.receipt_frame, bg=DARK_BLUE_BG)
        details_frame.pack(pady=20)
    
        details = [
            ("Movie Name:", movie_name),
            ("Ticket Category:", ticket_category),
            ("First Name:", first_name),
            ("Last Name:", last_name),
            ("Phone Number:", phone_number),
            ("Showtime:", show_time),
            ("Number of Tickets:", number_of_tickets),
            ("Booking Date:", booking_date),
        ]
        for label_text, value in details:
            row_frame = tk.Frame(details_frame, bg=DARK_BLUE_BG)
            row_frame.pack(fill='x', padx=40, pady=5)
            lbl = tk.Label(
                row_frame,
                text=label_text,
                font=("Arial", 18, "bold"),
                fg=TEXT_COLOR,
                bg=DARK_BLUE_BG
            )
            lbl.pack(side="left")
            val_lbl = tk.Label(
                row_frame,
                text=str(value),
                font=("Arial", 18),
                fg=TEXT_COLOR,
                bg=DARK_BLUE_BG
            )
            val_lbl.pack(side="left", padx=10)
    
        cursor.execute("SELECT showing_id FROM Booking WHERE booking_id = %s", (booking_id,))
        sh_id_tuple = cursor.fetchone()
        sh_id = sh_id_tuple[0] if sh_id_tuple else None
    
        cursor.execute("SELECT time_id FROM movie_showings WHERE showing_id = %s", (sh_id,))
        time_id_tuple = cursor.fetchone()
        time_id = time_id_tuple[0] if time_id_tuple else None
    
        print("DEBUG: time_id =", time_id, "city =", self.user_city, "cat_id =", cat_id)
    
        cursor.execute(
            "SELECT price FROM price WHERE time_id = %s AND city = %s AND category_id = %s",
            (time_id, self.user_city, cat_id)
        )
        result = cursor.fetchone()
    
        if result is None:
            messagebox.showerror(
                "Price Error",
                "No price set for the selected time, city, and category."
            )
            return
    
        price = result[0]
        total = price * number_of_tickets
    
        price_frame = tk.Frame(self.receipt_frame, bg=DARK_BLUE_BG)
        price_frame.pack(pady=20)
    
        price_label = tk.Label(
            price_frame,
            text="Total Price:",
            font=("Arial", 20, "bold"),
            fg=TEXT_COLOR,
            bg=DARK_BLUE_BG
        )
        price_label.pack(side="left", padx=10)
    
        price_value_label = tk.Label(
            price_frame,
            text=str(total),
            font=("Arial", 20),
            fg=TEXT_COLOR,
            bg=DARK_BLUE_BG
        )
        price_value_label.pack(side="left", padx=10)
    
        buttons_frame = tk.Frame(self.receipt_frame, bg=DARK_BLUE_BG)
        buttons_frame.pack(pady=30)
    
        confirm_payment_btn = tk.Button(
            buttons_frame,
            text="Confirm Payment",
            font=("Arial", 18, "bold"),
            fg=BUTTON_FG,
            bg=ACCENT_COLOR,
            width=15,
            command=self.confirm_payment
        )
        confirm_payment_btn.pack(side="left", padx=20)
    
        cancel_payment_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            font=("Arial", 18, "bold"),
            fg=BUTTON_FG,
            bg=ACCENT_COLOR,
            width=15,
            command=self.cancel_payment
        )
        cancel_payment_btn.pack(side="left", padx=20)
    
        self.bid = booking_id

    def confirm_payment(self):
        messagebox.showinfo("Payment", "Payment confirmed!")
        self.receipt_frame.pack_forget()
        self.booking_page()

    def cancel_payment(self):
        messagebox.showinfo("Payment", "Booking cancelled.")
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        cursor.execute("DELETE FROM Booking WHERE booking_id = %s;", (self.bid,))
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")
        conn.commit()
        self.receipt_frame.pack_forget()
        self.staff_booking_page()

    def back_to_staff_booking(self):
        self.booking_frame.pack_forget()
        self.staff_booking_page()

    # ---------------------- Admin and Manager Views ----------------------
    def admin_view(self):
        if hasattr(self, 'admin_frame'):
            self.admin_frame.destroy()
        self.admin_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.admin_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.admin_frame, text="Admin Dashboard", font=("Arial", 36, "bold"), 
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        buttons = [
            ("Add / Remove / Update Movies", self.manage_movies),
            ("Manage Showtimes", self.manage_showtimes),
            ("Assign Shows to Screens", self.assign_shows),
            ("Generate Reports", self.generate_reports),
            ("Back", self.back_to_home)
        ]
    
        for text, command in buttons:
            btn = tk.Button(self.admin_frame, text=text, font=("Arial", 20), bg=ACCENT_COLOR, fg=BUTTON_FG,
                            width=30, command=command)
            btn.pack(pady=10)
    
    def manager_view(self):
        if hasattr(self, 'manager_frame'):
            self.manager_frame.destroy()
        self.manager_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.manager_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.manager_frame, text="Manager Dashboard", font=("Arial", 36, "bold"), 
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        buttons = [
            ("Add New Cinema", self.add_cinema),
            ("Add Listings to Cities", self.add_listings),
            ("Access Admin View", self.access_admin_view),
            ("Generate Reports", self.generate_reports),
            ("Add New User", self.add_user),
            ("Back", self.back_to_home)
        ]
    
        for text, command in buttons:
            btn = tk.Button(self.manager_frame, text=text, font=("Arial", 20), bg=ACCENT_COLOR, fg=BUTTON_FG,
                            width=30, command=command)
            btn.pack(pady=10)

    # ---------------------- Movies Management ----------------------
    def manage_movies(self):
        self.admin_frame.pack_forget()
        self.movie_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.movie_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.movie_frame, text="Manage Movies", font=("Arial", 36, "bold"), 
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        fields = [("Movie Name", "name"), ("Description", "desc"), ("Genre", "genre"), ("Rating", "rating"), ("Age Limit", "age")]
        self.movie_entries = {}
        for label_text, field_key in fields:
            lbl = tk.Label(self.movie_frame, text=label_text + ":", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
            lbl.pack()
            ent = tk.Entry(self.movie_frame, font=("Arial", 14), width=40)
            ent.pack(pady=5)
            self.movie_entries[field_key] = ent
    
        btn_frame = tk.Frame(self.movie_frame, bg=DARK_BLUE_BG)
        btn_frame.pack(pady=20)
    
        tk.Button(btn_frame, text="Add Movie", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.add_movie_only).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Update Movie", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.update_movie).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Delete Movie", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.delete_movie).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.back_to_admin).pack(side='left', padx=10)
    
        self.movie_list = ttk.Combobox(self.movie_frame, font=("Arial", 14), width=50)
        self.movie_list.pack(pady=10)
        self.load_movies()
        self.movie_list.bind("<<ComboboxSelected>>", self.fill_movie_fields)
    
    def load_movies(self):
        cursor.execute("SELECT Movie_ID, Movie_Name FROM movies")
        movies = cursor.fetchall()
        self.movies_dict = {f"{m[1]} (ID: {m[0]})": m[0] for m in movies}
        self.movie_list['values'] = list(self.movies_dict.keys())
    
    def fill_movie_fields(self, event):
        selected = self.movie_list.get()
        movie_id = self.movies_dict.get(selected)
        cursor.execute("SELECT Movie_Name, Movie_Description, Genre, Rating, Age FROM movies WHERE Movie_ID = %s", (movie_id,))
        row = cursor.fetchone()
        if row:
            fields = ['name', 'desc', 'genre', 'rating', 'age']
            for i, val in enumerate(row):
                self.movie_entries[fields[i]].delete(0, 'end')
                self.movie_entries[fields[i]].insert(0, str(val))
            self.selected_movie_id = movie_id
    
    def add_movie_only(self):
        self.movie_frame.pack_forget()
    
        self.add_movie_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.add_movie_frame.pack(fill='both', expand=True)
    
        tk.Label(self.add_movie_frame, text="Add Movie", font=("Arial", 30, "bold"), 
             fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack(pady=30)
    
        labels = ["Movie Name", "Description", "Genre", "Rating", "Age"]
        self.movie_entries_new = {}
        for label_text in labels:
            tk.Label(self.add_movie_frame, text=label_text + ":", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
            entry = tk.Entry(self.add_movie_frame, font=("Arial", 16), width=40)
            entry.pack(pady=5)
            self.movie_entries_new[label_text] = entry
    
        save_btn = tk.Button(self.add_movie_frame, text="Save Movie", font=("Arial", 18, "bold"),
                         fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.save_movie_only)
        save_btn.pack(pady=20)
    
    def save_movie_only(self):
        try:
            movie_data = (
                self.movie_entries_new["Description"].get(),
                self.movie_entries_new["Movie Name"].get(),
                self.movie_entries_new["Genre"].get(),
                self.movie_entries_new["Rating"].get(),
                int(self.movie_entries_new["Age"].get())
        )
            cursor.execute(
                "INSERT INTO movies (Movie_Description, Movie_Name, Genre, Rating, Age) VALUES (%s, %s, %s, %s, %s)",
                movie_data
        )
            conn.commit()
            messagebox.showinfo("Success", "Movie added successfully.")
            self.add_movie_frame.pack_forget()
            self.admin_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_movie(self):
        if not hasattr(self, 'selected_movie_id'):
            messagebox.showerror("Selection Error", "Select a movie to update.")
            return
        data = [self.movie_entries[key].get().strip() for key in ['name', 'desc', 'genre', 'rating', 'age']]
        cursor.execute("""
            UPDATE movies 
            SET Movie_Name=%s, Movie_Description=%s, Genre=%s, Rating=%s, Age=%s 
            WHERE Movie_ID=%s
        """, (*data, self.selected_movie_id))
        conn.commit()
        messagebox.showinfo("Success", "Movie updated.")
        self.load_movies()
    
    def delete_movie(self):
        if not hasattr(self, 'selected_movie_id'):
            messagebox.showerror("Selection Error", "Select a movie to delete.")
            return
        cursor.execute("DELETE FROM movies WHERE Movie_ID = %s", (self.selected_movie_id,))
        conn.commit()
        messagebox.showinfo("Success", "Movie deleted.")
        self.load_movies()
    
    # ---------------------- Showtimes Management ----------------------
    def manage_showtimes(self):
        self.admin_frame.pack_forget()
        self.showtime_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.showtime_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.showtime_frame, text="Manage Showtimes", font=("Arial", 36, "bold"),
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        tk.Label(self.showtime_frame, text="Select Movie:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.st_movie_combo = ttk.Combobox(self.showtime_frame, font=("Arial", 14), width=50)
        self.st_movie_combo.pack(pady=5)
        cursor.execute("SELECT Movie_ID, Movie_Name FROM movies")
        movies = cursor.fetchall()
        self.movie_id_map = {f"{name} (ID:{mid})": mid for mid, name in movies}
        self.st_movie_combo['values'] = list(self.movie_id_map.keys())
    
        if self.user_role == "Manager":
            tk.Label(self.showtime_frame, text="Select City:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
            cursor.execute("SELECT DISTINCT City FROM cinemas")
            cities = [row[0] for row in cursor.fetchall()]
            self.st_city_combo = ttk.Combobox(self.showtime_frame, values=cities, font=("Arial", 14), width=30)
            self.st_city_combo.pack(pady=5)
        else:
            tk.Label(self.showtime_frame, text=f"City: {self.user_city}", font=("Arial", 16, "bold"), fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack()
            self.st_city = self.user_city
    
        tk.Label(self.showtime_frame, text="New Showtime (e.g. 19:00):", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.st_time_entry = tk.Entry(self.showtime_frame, font=("Arial", 14), width=20)
        self.st_time_entry.pack(pady=5)
    
        btn_frame = tk.Frame(self.showtime_frame, bg=DARK_BLUE_BG)
        btn_frame.pack(pady=15)
    
        tk.Button(btn_frame, text="Add Showtime", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.add_showtime).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Delete Showtime", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.delete_showtime).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.back_to_admin).pack(side='left', padx=10)
    
        tk.Label(self.showtime_frame, text="Existing Showtimes:", font=("Arial", 16, "bold"), fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack(pady=10)
        self.existing_showtimes_listbox = tk.Listbox(self.showtime_frame, font=("Arial", 14), width=40, height=8)
        self.existing_showtimes_listbox.pack()
        self.st_movie_combo.bind("<<ComboboxSelected>>", self.load_showtimes)
    
    def load_showtimes(self, event=None):
        self.existing_showtimes_listbox.delete(0, 'end')
        city = self.st_city
        movie_key = self.st_movie_combo.get()
        movie_id = self.movie_id_map.get(movie_key)
        if not city or not movie_id:
            return
        cursor.execute("SELECT show_time FROM movie_showings WHERE movie_id = %s AND city = %s", (movie_id, city))
        results = cursor.fetchall()
        for row in results:
            self.existing_showtimes_listbox.insert('end', row[0])
    
    def add_showtime(self):
        city = self.st_city
        show_time = self.st_time_entry.get().strip()
        movie_key = self.st_movie_combo.get()
        movie_id = self.movie_id_map.get(movie_key)
    
        if not (movie_id and city and show_time):
            messagebox.showerror("Input Error", "All fields are required.")
            return
    
        cursor.execute("SELECT COUNT(*) FROM movie_showings WHERE movie_id = %s AND show_time = %s AND city = %s",
                       (movie_id, show_time, city))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Duplicate", "Showtime already exists.")
            return
    
        cursor.execute("INSERT INTO movie_showings (movie_id, show_time, city) VALUES (%s, %s, %s)",
                       (movie_id, show_time, city))
        conn.commit()
        messagebox.showinfo("Success", "Showtime added.")
        self.load_showtimes()
    
    def delete_showtime(self):
        selected = self.existing_showtimes_listbox.curselection()
        if not selected:
            messagebox.showerror("Selection Error", "Select a showtime to delete.")
            return
        show_time = self.existing_showtimes_listbox.get(selected[0])
        city = self.st_city
        movie_id = self.movie_id_map.get(self.st_movie_combo.get())
        cursor.execute("DELETE FROM movie_showings WHERE movie_id = %s AND show_time = %s AND city = %s",
                       (movie_id, show_time, city))
        conn.commit()
        messagebox.showinfo("Deleted", f"Deleted showtime: {show_time}")
        self.load_showtimes()
    
    # ---------------------- Assign Shows to Screens ----------------------
    def assign_shows(self):
        self.admin_frame.pack_forget()
        self.assign_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.assign_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.assign_frame, text="Assign Show to Screen", font=("Arial", 36, "bold"),
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        tk.Label(self.assign_frame, text="Select Movie:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.assign_movie_combo = ttk.Combobox(self.assign_frame, font=("Arial", 14), width=50)
        self.assign_movie_combo.pack(pady=5)
        cursor.execute("SELECT Movie_ID, Movie_Name FROM movies")
        movies = cursor.fetchall()
        self.assign_movie_dict = {f"{name} (ID:{mid})": mid for mid, name in movies}
        self.assign_movie_combo['values'] = list(self.assign_movie_dict.keys())
    
        if self.user_role == "Admin":
            tk.Label(self.assign_frame, text=f"City: {self.user_city}", font=("Arial", 16, "bold"), fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack()
            self.assign_city = self.user_city
        else:
            tk.Label(self.assign_frame, text="City:", font=("Arial", 16, "bold"), fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack()
            self.assign_city_entry = tk.Entry(self.assign_frame, font=("Arial", 14), width=30)
            self.assign_city_entry.pack(pady=5)

    
        tk.Label(self.assign_frame, text="Showtime (e.g. 19:00):", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.assign_showtime_entry = tk.Entry(self.assign_frame, font=("Arial", 14), width=30)
        self.assign_showtime_entry.pack(pady=5)
    
        tk.Label(self.assign_frame, text="Select Screen:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.assign_screen_combo = ttk.Combobox(self.assign_frame, font=("Arial", 14), width=40)
        self.assign_screen_combo.pack(pady=5)
    
        tk.Button(self.assign_frame, text="Load Screens for City", font=("Arial", 12), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.load_screens_for_assign).pack(pady=5)
    
        tk.Label(self.assign_frame, text="Select Time Period:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.assign_time_combo = ttk.Combobox(self.assign_frame, font=("Arial", 14), width=30)
        self.assign_time_combo['values'] = ['Morning (2)', 'Afternoon (3)', 'Evening (4)']
        self.assign_time_combo.pack(pady=5)
    
        tk.Button(self.assign_frame, text="Assign Show", font=("Arial", 16), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.save_assigned_show).pack(pady=15)
    
        tk.Button(self.assign_frame, text="Back", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.back_to_admin).pack(pady=5)
    
    def load_screens_for_assign(self):
        if self.user_role == "Admin":
            city = self.assign_city
        else:
            city = self.assign_city_entry.get().strip()

        if not city:
            messagebox.showerror("Input Error", "Enter a city first.")
            return

        cursor.execute("SELECT Screen_ID, Screen_Number FROM screen WHERE city = %s", (city,))
        rows = cursor.fetchall()
        self.assign_screen_map = {f"Screen {sn} (ID:{sid})": sid for sid, sn in rows}
        self.assign_screen_combo['values'] = list(self.assign_screen_map.keys())

    
    def save_assigned_show(self):
        if self.user_role == "Admin":
            city = self.assign_city
        else:
            city = self.assign_city_entry.get().strip()
        showtime = self.assign_showtime_entry.get().strip()
        movie_id = self.assign_movie_dict.get(self.assign_movie_combo.get())
        screen_id = self.assign_screen_map.get(self.assign_screen_combo.get())
        time_label = self.assign_time_combo.get()
    
        if not (city and showtime and movie_id and screen_id and time_label):
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
    
        time_id = int(time_label.split("(")[-1].replace(")", ""))
    
        cursor.execute("""
            UPDATE movie_showings
            SET screen_id = %s, time_id = %s
            WHERE movie_id = %s AND show_time = %s AND city = %s
        """, (screen_id, time_id, movie_id, showtime, city))
    
        cursor.execute("SELECT screen_id FROM movie_showings WHERE movie_id = %s AND show_time = %s AND city = %s",
                       (movie_id, showtime, city))
        screen_result = cursor.fetchone()
    
        if screen_result:
            screen_id_for_seats = screen_result[0]
            cursor.execute("SELECT COUNT(*) FROM seat WHERE screen_id = %s", (screen_id_for_seats,))
            existing_seats = cursor.fetchone()[0]
            if existing_seats == 0:
                cursor.execute("SELECT UH_Capacity, LH_Capacity, VIP_Capacity FROM screen WHERE screen_id = %s", (screen_id_for_seats,))
                row = cursor.fetchone()
                uh_cap = row[0]
                lh_cap = row[1]
                vip_cap = row[2]
                cursor.execute("SELECT Category_ID FROM category WHERE Category_Name = %s", ('Upper Hall',))
                uh_cat = cursor.fetchone()[0]
                for _ in range(uh_cap):
                    cursor.execute("INSERT INTO seat (Screen_ID, Category_ID) VALUES (%s, %s)", (screen_id_for_seats, uh_cat))
                cursor.execute("SELECT Category_ID FROM category WHERE Category_Name = %s", ('Lowe Hall',))
                lh_cat = cursor.fetchone()[0]
                for _ in range(lh_cap):
                    cursor.execute("INSERT INTO seat (Screen_ID, Category_ID) VALUES (%s, %s)", (screen_id_for_seats, lh_cat))
                cursor.execute("SELECT Category_ID FROM category WHERE Category_Name = %s", ('VIP',))
                vip_cat = cursor.fetchone()[0]
                for _ in range(vip_cap):
                    cursor.execute("INSERT INTO seat (Screen_ID, Category_ID) VALUES (%s, %s)", (screen_id_for_seats, vip_cat))
        else:
            messagebox.showerror("Error", "No movie showing found with the given parameters.")
            return
    
        conn.commit()
        messagebox.showinfo("Success", "Show assigned to screen and time slot, and seats initialized.")
    
    # ---------------------- Listings Management ----------------------
    def add_listings(self):
        self.manager_frame.pack_forget()
        self.listing_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.listing_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.listing_frame, text="Add Movie Listings to Cities", font=("Arial", 36, "bold"),
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        tk.Label(self.listing_frame, text="City:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.listing_city_entry = tk.Entry(self.listing_frame, font=("Arial", 14), width=40)
        self.listing_city_entry.pack(pady=5)
    
        tk.Label(self.listing_frame, text="Select Movie:", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.listing_movie_combo = ttk.Combobox(self.listing_frame, font=("Arial", 14), width=50)
        self.listing_movie_combo.pack(pady=5)
        cursor.execute("SELECT Movie_ID, Movie_Name FROM movies")
        movies = cursor.fetchall()
        self.listing_movie_map = {f"{name} (ID:{mid})": mid for mid, name in movies}
        self.listing_movie_combo['values'] = list(self.listing_movie_map.keys())
    
        tk.Label(self.listing_frame, text="Showtime (e.g. 19:00):", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
        self.listing_showtime_entry = tk.Entry(self.listing_frame, font=("Arial", 14), width=30)
        self.listing_showtime_entry.pack(pady=5)
    
        tk.Button(self.listing_frame, text="Add Listing", font=("Arial", 16), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.save_listing).pack(pady=15)
    
        tk.Button(self.listing_frame, text="Back", font=("Arial", 14), bg=ACCENT_COLOR, fg=BUTTON_FG,
                  command=self.back_to_manager).pack(pady=10)
    
    def save_listing(self):
        city = self.listing_city_entry.get().strip()
        showtime = self.listing_showtime_entry.get().strip()
        movie_id = self.listing_movie_map.get(self.listing_movie_combo.get())
    
        if not (city and showtime and movie_id):
            messagebox.showerror("Input Error", "Please fill all fields.")
            return
    
        cursor.execute("""
            SELECT COUNT(*) FROM movie_showings WHERE movie_id = %s AND show_time = %s AND city = %s
        """, (movie_id, showtime, city))
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning("Duplicate", "This listing already exists.")
            return
    
        cursor.execute("INSERT INTO movie_showings (movie_id, show_time, city) VALUES (%s, %s, %s)",
                       (movie_id, showtime, city))
        conn.commit()
        messagebox.showinfo("Success", "Listing added to city.")
    
    def view_analytics(self):
        messagebox.showinfo("Analytics", "Analytics functionality is not implemented.")
    
    # ---------------------- Add New Cinema (Manager) ----------------------
    def add_cinema(self):
        self.manager_frame.pack_forget()
        self.add_cinema_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.add_cinema_frame.pack(fill='both', expand=True)
    
        title = tk.Label(self.add_cinema_frame, text="Add New Cinema", font=("Arial", 36, "bold"),
                         fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)
    
        city_label = tk.Label(self.add_cinema_frame, text="City:", font=("Arial", 18), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        city_label.pack(pady=5)
        self.city_entry = tk.Entry(self.add_cinema_frame, font=("Arial", 16), width=30)
        self.city_entry.pack(pady=5)
    
        screens_label = tk.Label(self.add_cinema_frame, text="Number of Screens:", font=("Arial", 18), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        screens_label.pack(pady=5)
        self.screens_entry = tk.Entry(self.add_cinema_frame, font=("Arial", 16), width=30)
        self.screens_entry.pack(pady=5)

        uh_label = tk.Label(self.add_cinema_frame, text="Upper Hall Capacity:", font=("Arial", 18), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        uh_label.pack(pady=5)
        self.uh_entry = tk.Entry(self.add_cinema_frame, font=("Arial", 16), width=30)
        self.uh_entry.pack(pady=5)

# LH Capacity
        lh_label = tk.Label(self.add_cinema_frame, text="Lower Hall Capacity:", font=("Arial", 18), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        lh_label.pack(pady=5)
        self.lh_entry = tk.Entry(self.add_cinema_frame, font=("Arial", 16), width=30)
        self.lh_entry.pack(pady=5)

# VIP Capacity
        vip_label = tk.Label(self.add_cinema_frame, text="VIP Capacity:", font=("Arial", 18), fg=TEXT_COLOR, bg=DARK_BLUE_BG)
        vip_label.pack(pady=5)
        self.vip_entry = tk.Entry(self.add_cinema_frame, font=("Arial", 16), width=30)
        self.vip_entry.pack(pady=5)
    
        add_btn = tk.Button(self.add_cinema_frame, text="Add Cinema", font=("Arial", 18, "bold"),
                            bg=ACCENT_COLOR, fg=BUTTON_FG, command=self.save_cinema)
        add_btn.pack(pady=20)
    
        back_btn = tk.Button(self.add_cinema_frame, text="Back", font=("Arial", 16, "bold"),
                             bg=ACCENT_COLOR, fg=BUTTON_FG, command=self.back_to_manager)
        back_btn.pack()
    
    def save_cinema(self):
        city = self.city_entry.get().strip()
        screens = self.screens_entry.get().strip()
        uh = self.uh_entry.get().strip()
        lh = self.lh_entry.get().strip()
        vip = self.vip_entry.get().strip()

        if not city or not screens.isdigit() or not uh.isdigit() or not lh.isdigit() or not vip.isdigit():
            messagebox.showerror("Input Error", "Please enter valid numeric values for all fields.")
            return

        uh_capacity = int(uh)
        lh_capacity = int(lh)
        vip_capacity = int(vip)
        seating_capacity = uh_capacity + lh_capacity + vip_capacity

        try:
            cursor.execute("INSERT INTO cinemas (City, Number_Of_Screens) VALUES (%s, %s)", (city, int(screens)))

            for i in range(1, int(screens) + 1):
                cursor.execute("""
                INSERT INTO screen (City, Screen_Number, Seating_Capacity, UH_Capacity, LH_Capacity, VIP_Capacity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (city, i, seating_capacity, uh_capacity, lh_capacity, vip_capacity))

            conn.commit()
            messagebox.showinfo("Success", f"Cinema in '{city}' with {screens} screen(s) added.")
            self.add_cinema_frame.pack_forget()
            self.manager_view()

        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate", "A cinema already exists in this city.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    
    def generate_reports(self):
        report_win = tk.Toplevel(self.root)
        report_win.title("Reports")
        report_win.geometry("1000x700")

        notebook = ttk.Notebook(report_win)
        notebook.pack(fill="both", expand=True)

        # ---------- TAB 1: Bookings by Movie ----------
        tab1 = tk.Frame(notebook, bg="white")
        notebook.add(tab1, text="Bookings by Movie")

        tree1 = ttk.Treeview(tab1, columns=("MovieName", "TotalBookings"), show="headings")
        tree1.heading("MovieName", text="Movie Name")
        tree1.heading("TotalBookings", text="Total Bookings")
        tree1.column("MovieName", width=300, anchor="w")
        tree1.column("TotalBookings", width=150, anchor="center")
        tree1.pack(fill="both", expand=True)

        if self.user_role == "Manager":
            cursor.execute("SELECT movie_name, COUNT(*) FROM Booking GROUP BY movie_name")
        else:
            query = """
                SELECT b.movie_name, COUNT(*)
                FROM Booking b
                JOIN movie_showings ms ON b.showing_id = ms.showing_id
                WHERE ms.city = %s
                GROUP BY b.movie_name
            """
            cursor.execute(query, (self.user_city,))

        for row in cursor.fetchall():
            tree1.insert("", "end", values=(row[0], row[1]))

        # ---------- TAB 2: Revenue by City ----------
        tab2 = tk.Frame(notebook, bg="white")
        notebook.add(tab2, text="Revenue by City")

        tree2 = ttk.Treeview(tab2, columns=("CityName", "TotalRevenue"), show="headings")
        tree2.heading("CityName", text="City")
        tree2.heading("TotalRevenue", text="Total Revenue (£)")
        tree2.column("CityName", width=300, anchor="w")
        tree2.column("TotalRevenue", width=200, anchor="center")
        tree2.pack(fill="both", expand=True)

        if self.user_role == "Manager":
            query = """
                SELECT ms.city, SUM(b.number_of_tickets * p.price) AS total_revenue
                FROM Booking b
                JOIN movie_showings ms ON b.showing_id = ms.showing_id
                JOIN price p ON p.city = ms.city 
                    AND p.time_id = ms.time_id 
                    AND p.category_id = (
                        SELECT Category_ID FROM category WHERE Category_Name = b.ticket_category LIMIT 1
                    )
                GROUP BY ms.city
            """
            cursor.execute(query)
        else:
            query = """
                SELECT ms.city, SUM(b.number_of_tickets * p.price) AS total_revenue
                FROM Booking b
                JOIN movie_showings ms ON b.showing_id = ms.showing_id
                JOIN price p ON p.city = ms.city 
                    AND p.time_id = ms.time_id 
                    AND p.category_id = (
                        SELECT Category_ID FROM category WHERE Category_Name = b.ticket_category LIMIT 1
                    )
                WHERE ms.city = %s
                GROUP BY ms.city
            """
            cursor.execute(query, (self.user_city,))

        for row in cursor.fetchall():
            tree2.insert("", "end", values=(row[0], f"£{row[1]:,.2f}"))


    
    def destroy_admin_frames(self):
        frame_names = ['admin_frame', 'movie_frame', 'assign_frame', 'showtime_frame']
        for name in frame_names:
            if hasattr(self, name):
                getattr(self, name).destroy()

    def back_to_admin(self):
        self.destroy_admin_frames()
        self.admin_view()

        
    def destroy_manager_frames(self):
        frame_names = [
        'manager_frame', 
        'add_cinema_frame', 
        'listing_frame', 
        'assign_frame', 
        'showtime_frame', 
        'movie_frame',
        'add_user_frame'
    ]
        for name in frame_names:
            if hasattr(self, name):
                frame = getattr(self, name)
                frame.destroy()
                self.manager_view()


    def back_to_manager(self):
        self.destroy_manager_frames()
        self.manager_view()


    def add_user(self):
        self.manager_frame.pack_forget()
        self.add_user_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.add_user_frame.pack(fill='both', expand=True)

        tk.Label(self.add_user_frame, text="Add New User (Staff/Admin)", font=("Arial", 30, "bold"),
             fg=ACCENT_COLOR, bg=DARK_BLUE_BG).pack(pady=30)

        labels = ["First Name", "Last Name", "Username", "Password", "City", "Role (Admin/Staff)"]
        self.user_entries = {}
        for label in labels:
            tk.Label(self.add_user_frame, text=label + ":", font=("Arial", 16), fg=TEXT_COLOR, bg=DARK_BLUE_BG).pack()
            entry = tk.Entry(self.add_user_frame, font=("Arial", 16), width=40, show="*" if label == "Password" else "")
            entry.pack(pady=5)
            self.user_entries[label] = entry

        submit_btn = tk.Button(self.add_user_frame, text="Add User", font=("Arial", 18, "bold"),
                           fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.save_user)
        submit_btn.pack(pady=20)

        back_btn = tk.Button(self.add_user_frame, text="Back", font=("Arial", 14),
                         fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.back_to_manager)
        
        back_btn.pack()

    def save_user(self):
        fname = self.user_entries["First Name"].get().strip()
        lname = self.user_entries["Last Name"].get().strip()
        username = self.user_entries["Username"].get().strip()
        password = self.user_entries["Password"].get().strip()
        city = self.user_entries["City"].get().strip()
        role = self.user_entries["Role (Admin/Staff)"].get().strip().lower()

        if not all([fname, lname, username, password, city, role]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        if role not in ['admin', 'staff']:
            messagebox.showerror("Role Error", "Role must be either 'Admin' or 'Staff'.")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        try:
            if role == 'admin':
                cursor.execute("INSERT INTO admin (username, password, city) VALUES (%s, %s, %s)",
                            (username, hashed_pw, city))
            elif role == 'staff':
                cursor.execute("INSERT INTO staff (first_name, last_name, city, username, password) VALUES (%s, %s, %s, %s, %s)",
                            (fname, lname, city, username, hashed_pw))

            conn.commit()
            messagebox.showinfo("Success", f"New {role.capitalize()} user added!")
            self.add_user_frame.pack_forget()
            self.manager_view()

        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate Username", "That username already exists.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {e}")



    def show_category_breakdown(self, showing_id, screen_id):
        try:
            booking_date_str = self.booking_date.strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT c.category_name, COUNT(s.seat_id)
                FROM seat s
                JOIN category c ON s.category_id = c.category_id
                WHERE s.screen_id = %s
                AND s.seat_id NOT IN (
                    SELECT seatID FROM booked_seats
                    WHERE showings_id = %s AND `date` = %s
                )
                GROUP BY c.category_name
            """, (screen_id, showing_id, booking_date_str))
            rows = cursor.fetchall()

            popup = tk.Toplevel(self.root)
            popup.title("Available Seats by Category")
            popup.geometry("300x200")
            popup.configure(bg="#1e1e1e")

            tk.Label(popup, text="Seats Available", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)
            for cat, count in rows:
                tk.Label(popup, text=f"{cat}: {count}", font=("Arial", 14), bg="#1e1e1e", fg="white").pack(pady=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch seat breakdown:\n{e}")


    def view_and_cancel_bookings(self):
        self.staff_booking_frame.pack_forget()
        self.cancel_frame = tk.Frame(self.root, bg=DARK_BLUE_BG)
        self.cancel_frame.pack(fill='both', expand=True)

        title = tk.Label(self.cancel_frame, text="Cancel Booking", font=("Arial", 36, "bold"),
                        fg=ACCENT_COLOR, bg=DARK_BLUE_BG)
        title.pack(pady=30)

        self.booking_listbox = tk.Listbox(self.cancel_frame, font=("Arial", 14), width=90, height=12)
        self.booking_listbox.pack(pady=20)

        cancel_btn = tk.Button(self.cancel_frame, text="Cancel Selected Booking", font=("Arial", 16, "bold"),
                            fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.cancel_selected_booking)
        cancel_btn.pack(pady=10)

        back_btn = tk.Button(self.cancel_frame, text="Back", font=("Arial", 16, "bold"),
                     fg=BUTTON_FG, bg=ACCENT_COLOR, command=self.back_to_staff_from_cancel)

        back_btn.pack(pady=10)

        self.load_all_bookings_for_cancellation()

    def load_all_bookings_for_cancellation(self):
        self.booking_listbox.delete(0, 'end')
        today_str = date.today().strftime('%Y-%m-%d')

        query = """
            SELECT b.booking_id, b.movie_name, b.show_time, b.booking_date, b.first_name, b.last_name
            FROM Booking b
            JOIN movie_showings ms ON b.showing_id = ms.showing_id
            WHERE ms.city = %s AND b.booking_date >= %s
            ORDER BY b.booking_date ASC
        """ 
        cursor.execute(query, (self.user_city, today_str))
        results = cursor.fetchall()

        self.booking_data_map = {}
        if not results:
            self.booking_listbox.insert('end', "No upcoming bookings in your city.")
            return

        for row in results:
            text = f"Booking ID: {row[0]} | {row[1]} | {row[2]} | {row[3]} | Guest: {row[4]} {row[5]}"
            self.booking_listbox.insert('end', text)
            self.booking_data_map[text] = row

    def cancel_selected_booking(self):
        selection = self.booking_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Select a booking to cancel.")
            return

        selected_text = self.booking_listbox.get(selection[0])
        if selected_text == "No upcoming bookings in your city.":
            return

        booking_id, _, _, b_date, _, _ = self.booking_data_map[selected_text]
        today = date.today()

        if b_date <= today:
            messagebox.showwarning("Policy", "Bookings cannot be cancelled on the day of the show.")
            return

        confirm = messagebox.askyesno("Confirm", "Cancel this booking with 50% charge?")
        if not confirm:
            return

        try:
            cursor.execute("DELETE FROM booked_seats WHERE showings_id = (SELECT showing_id FROM Booking WHERE booking_id = %s)", (booking_id,))
            cursor.execute("DELETE FROM Booking WHERE booking_id = %s", (booking_id,))
            conn.commit()
            messagebox.showinfo("Success", "Booking cancelled successfully.")
            self.load_all_bookings_for_cancellation()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel booking:\n{e}")


        

    def back_to_staff_from_cancel(self):
        self.cancel_frame.destroy()
        self.staff_booking_page()

    def access_admin_view(self):
        if hasattr(self, 'manager_frame'):
            self.manager_frame.destroy()  
        self.admin_view()  
        
if __name__ == "__main__":
    root = tk.Tk()
    app = HorizonCinemasApp(root)
    root.mainloop()

