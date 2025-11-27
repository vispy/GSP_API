# import tkinter as tk
import customtkinter as tk

root = tk.CTk()
dpi = root.winfo_fpixels("1i")
print("DPI:", dpi)

root.mainloop()
