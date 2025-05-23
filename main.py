from src.gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import logging
import sys

def setup_logging():
    """
    Configures the logging for the application.
    Logs are written to both a file and the console.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler("gcs.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """
    The main entry point of the application.
    Initializes the QApplication and sets up the main window.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting NovoGround Ground Control System")

    app = QApplication(sys.argv)
    app.setApplicationName("NovoGround GCS")
    app.setOrganizationName("NovoGround")
    app.setOrganizationDomain("novoground.com")

    # Specify the path to the rocket model file if available
    rocket_model_path = "assets/rocket_model.obj"  # Update this path as needed

    main_window = MainWindow(rocket_model_path=rocket_model_path)
    main_window.show()

    try:
        # Use the standard Qt event loop
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception("An unhandled exception occurred: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()