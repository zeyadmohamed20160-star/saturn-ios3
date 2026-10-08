import os
import glob

def find_and_report_files():
    print("=== Scanning Repository for Source and Header Files ===")
    
    # Extensions to hunt for
    extensions = ['*.cpp', '*.c', '*.h', '*.hpp']
    found_files = []
    
    for ext in extensions:
        # Recursively search directories ignoring build artifacts
        files = glob.glob(f"**/{ext}", recursive=True)
        for f in files:
            if "build_xcode" not in f and ".xcodeproj" not in f:
                print(f"Found and verified: {f}")
                found_files.append(f)
                
    print(f"=== Total source files tracked for build: {len(found_files)} ===")
    return found_files

if __name__ == "__main__":
    find_and_report_files()
