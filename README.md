# Attendance Scanner System (RFID + Camera for Student Profiles)

A **Python Flask** web application designed for recording student attendance using **RFID** technology and **camera snapping** for student profiles. The system uses a **USB RFID reader** to scan student IDs, and an **OpenCV2 camera** to capture student profile photos. Attendance is logged in an **SQLite3** database, and the UI is designed to be **mobile-friendly** using **W3.CSS**.

---

## Features

### RFID-Based Attendance
- **RFID scanning:** Uses a **USB RFID Reader** (keyboard-emulating input)
- **Real-time attendance tracking:** Automatically logs attendance with **date and time**
- **Prevent duplicate entries:** Ensures no multiple attendance records for the same session

### Camera for Student Profiles (OpenCV2)
- **Capture student photos:** Takes a snapshot using the webcam for each student during registration
- **Associate profile photos:** Photos are stored alongside student records for future reference

### Student Management
- **Add, edit, and delete students:** Manage student records including their RFID and profile pictures
- **View attendance history:** Check historical attendance logs for each student

### Attendance Logs
- **View logs:** Display timestamped attendance records in real-time
- **Filter logs:** Filter attendance logs by **date** or **student**
- **Export logs:** Optional export of attendance records to **CSV**

### Admin Dashboard
- **Responsive design:** Mobile-friendly interface using **W3.CSS**
- **User-friendly:** Simple UI for admins to view attendance and manage student profiles

---

## Tech Stack

- **Backend:** Python Flask  
- **Database:** SQLite3  
- **Frontend:** HTML + W3.CSS  
- **RFID Input:** USB RFID Reader (keyboard emulation)  
- **Camera:** OpenCV2 (for profile snapshots)

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/rfid-attendance-system.git
cd rfid-attendance-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

### 4. Use the System
- **Register a new student** by scanning their **RFID** and capturing their **profile photo** using the webcam.
- **Log attendance** by scanning the student’s RFID card.
- View and manage attendance logs in the **Admin Dashboard**.

---

## How It Works

1. **Student Registration:**
   - The admin registers students by scanning their **RFID card**.
   - A **profile photo** is captured using the webcam and associated with the student's record.
   
2. **Attendance Tracking:**
   - When a student scans their **RFID card**, their attendance is logged in the system.
   - The admin can view attendance logs and manage student records.

3. **Student Profile Photos:**
   - Profile photos are stored and associated with each student’s data.
   - The system supports photo capture using a webcam and stores images for reference.

---

## Notes

- The **camera** is only used for **snapping student profile photos** during registration.
- Ensure the **webcam** is accessible and not used by other applications.
- The **RFID reader** acts like a keyboard, and no special driver is needed.

---

## License

This project is licensed under the MIT License.

---

Feel free to explore this project and add more features you like