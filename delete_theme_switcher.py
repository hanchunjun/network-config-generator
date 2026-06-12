import os
if os.path.exists("src/ui/theme_switcher_page.py"):
    os.remove("src/ui/theme_switcher_page.py")
    print("Deleted theme_switcher_page.py")
else:
    print("File not found")
