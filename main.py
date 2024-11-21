if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QSplashScreen
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap
    from logic import *

    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash_pixmap = QPixmap("splash.bmp")  # Replace with your splash image
    splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.setMask(splash_pixmap.mask())
    splash.show()

    # Simulate loading operations (optional)
    app.processEvents()  # Allows the splash screen to be responsive

    # Initialize and show the main window
    window = MainWindowExtended()
    splash.finish(window)  # Close the splash screen when the main window is ready
    window.show()

    sys.exit(app.exec())
