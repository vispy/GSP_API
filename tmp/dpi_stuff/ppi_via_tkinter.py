import tkinter as tk

root = tk.Tk()

# import customtkinter as tk
# root = tk.CTk()

dpi = root.winfo_fpixels("1i")
print("DPI:", dpi)

root.mainloop()
