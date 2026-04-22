"""
SmartAlert Main Controller
Allows user to run Fire Detection or Fall Detection
Supports custom video input for testing
"""

import sys
import os
from fire_detection.fire_detection import start_fire_detection
from fall_detection.fall_detection import start_fall_detection
from utils import print_system_info


def show_menu():

    print("\n" + "="*60)
    print("SMART ALERT SYSTEM")
    print("="*60)
    print("1 -> Fire Detection (Default video)")
    print("2 -> Fall Detection (Default video)")
    print("3 -> Fall Detection (Custom video)")
    print("4 -> Fire Detection (Custom video)")
    print("5 -> Exit")
    print("="*60)


def get_video_path(detection_type):
    """Get video path from user with validation"""
    print(f"\n--- {detection_type.upper()} DETECTION ---")
    print("Enter the full path to your video file")
    print("Example: C:/Users/YourName/Videos/fall_clip.mp4")
    print("(or drag and drop the file here)")
    print()

    video_path = input("Video path: ").strip()

    # Remove quotes if present (from drag and drop)
    video_path = video_path.strip('"').strip("'")

    if not video_path:
        print("No path entered.")
        return None

    if not os.path.exists(video_path):
        print(f"File not found: {video_path}")
        print("Please check the path and try again.")
        return None

    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm']
    _, ext = os.path.splitext(video_path.lower())

    if ext not in valid_extensions:
        print(f"Warning: Unexpected file type '{ext}'")
        print(f"Supported formats: {', '.join(valid_extensions)}")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return None

    return video_path


def main():

    print_system_info()

    while True:

        show_menu()

        choice = input("Enter option: ").strip()

        if choice == "1":
            print("\nStarting Fire Detection (default video)...")
            video_path = "fire_detection/fire_test.mp4"
            start_fire_detection(video_path)

        elif choice == "2":
            print("\nStarting Fall Detection (default video)...")
            video_path = "fall_detection/wheelchair_fall.mp4"
            start_fall_detection(video_path)

        elif choice == "3":
            video_path = get_video_path("fall")
            if video_path:
                print("\nStarting Fall Detection...")
                start_fall_detection(video_path)

        elif choice == "4":
            video_path = get_video_path("fire")
            if video_path:
                print("\nStarting Fire Detection...")
                start_fire_detection(video_path)

        elif choice == "5":
            print("\nExiting SmartAlert System")
            sys.exit()

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()

