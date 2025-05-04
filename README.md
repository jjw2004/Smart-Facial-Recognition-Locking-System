# Smart Facial Recognition Locking System  
#### Student Name: John Joey Wright  Student ID: 20105823

## Project Description
This project implements a smart access system using facial recognition, built around a Raspberry Pi. When a user presses a button, the system checks the ambient light level using a Grove Light Sensor. The current light condition and system status are displayed on a 16x2 LCD screen.

If light conditions are acceptable, a picture is taken using a connected camera (either a Raspberry Pi Camera Module or USB webcam). The image is uploaded to a local web server (running in a container on the student's laptop) which performs facial recognition. If the face is verified as a known user, the system plays a happy beep and unlocks the door via a relay. If the face is not recognized, a sad beep is played and access is denied.

## Tools, Technologies, and Equipment

### Hardware:
- Raspberry Pi (running Python-based controller script)
- USB Webcam or Raspberry Pi Camera Module (for capturing photos)
- Grove Light Sensor (for detecting ambient light levels)
- Grove 16x2 LCD Display (for displaying status and light messages)
- Grove Button (for user input)
- Grove Relay Module (for activating door lock)
- Grove Buzzer (for feedback sounds)
- Grove Base Hat (for sensor and module connectivity)

### Software:
- Python 3 (used for all hardware interfacing and logic)
- Flask Web Server (running in Docker container on a local laptop)
- OpenCV (for USB webcam image capture)
- GitHub (for version control and collaboration)
- Markdown & editing software (for documentation and video explanation)
