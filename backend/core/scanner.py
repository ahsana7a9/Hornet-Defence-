import os

suspicious_extensions = [
".exe",
".bat",
".vbs",
".ps1",
".scr"
]

def scan_system():

    suspicious_files = []

    for root, dirs, files in os.walk("C:/"):

        for file in files:

            for ext in suspicious_extensions:

                if file.lower().endswith(ext):
                    suspicious_files.append(os.path.join(root,file))

    return suspicious_files[:50]
