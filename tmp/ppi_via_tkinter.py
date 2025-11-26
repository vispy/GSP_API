import tkinter as tk

root = tk.Tk()
dpi = root.winfo_fpixels("1i")
print("DPI:", dpi)

root.mainloop()
