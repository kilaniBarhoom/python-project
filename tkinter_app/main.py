"""
Smart Records System - Tkinter Desktop Application
Main entry point

Run with: python main.py
"""
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path for models import
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Load environment variables from parent directory's .env file
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

from gui.app_controller import AppController
from gui.theme import Theme


def main():
    """Main entry point for the application"""
    print("=" * 50)
    print("Smart Records System - Desktop Application")
    print("=" * 50)
    print("Starting application...")
    print()

    try:
        # Create and configure application
        app = AppController()

        # Configure ttk styles
        Theme.configure_ttk_styles()

        print("✓ Application started successfully")
        print("✓ Window initialized")
        print()
        print("Application running... (Close window to exit)")
        print()

        # Start main loop
        app.mainloop()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✕ Error starting application: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
