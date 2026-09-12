import os
import subprocess
import shutil
import glob

print("==================================================")
print("   COMPILING SATURN FOR iOS (MACOS RUNNER)       ")
print("==================================================")

# 1. Define paths (adjust 'xcode_src' to where your files are located in the repo)
src_dir = "./xcode_src"
staging_dir = "./Saturn_Build_Staging"
payload_dir = os.path.join(staging_dir, "Payload")
app_dest = os.path.join(payload_dir, "MyApplication.app")
binary_name = "MyApplication"
output_ipa = "SaturnCompletePackage.ipa"

if os.path.exists(staging_dir):
    shutil.rmtree(staging_dir)

os.makedirs(app_dest, exist_ok=True)

print("[+] Searching for C, C++, and Header files...")

# Gather all .cpp and .c source files recursively
c_files = glob.glob(os.path.join(src_dir, "**", "*.c"), recursive=True)
cpp_files = glob.glob(os.path.join(src_dir, "**", "*.cpp"), recursive=True)
source_files = c_files + cpp_files

print(f"[+] Found {len(source_files)} source files to compile.")

if len(source_files) == 0:
    print("[!] Error: No .cpp or .c files found in the source directory!")
    exit(1)

# 2. Get the iOS SDK Path from Xcode
try:
    sdk_path = subprocess.check_output(
        ["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]
    ).decode("utf-8").strip()
    print(f"[✔] iOS SDK located at: {sdk_path}")
except Exception as e:
    print(f"[!] Error finding iOS SDK: {e}")
    exit(1)

# 3. Compile source files into a real ARM64 Mach-O iOS binary using Clang
output_binary_path = os.path.join(app_dest, binary_name)

# Base compiler command for iOS
compile_cmd = [
    "clang++",
    "-arch", "arm64",
    "-isysroot", sdk_path,
    "-miphoneos-version-min=14.0",
    # Link essential iOS frameworks so UI and functions work properly
    "-framework", "UIKit",
    "-framework", "Foundation",
    "-framework", "CoreGraphics",
    "-framework", "OpenGLES", # Included if Saturn uses basic graphics rendering
] + source_files + ["-o", output_binary_path]

print("[+] Compiling and linking source files (this may take a moment)...")
result = subprocess.run(compile_cmd, capture_output=True, text=True)

if result.returncode != 0:
    print("[!] Compilation failed!")
    print(result.stderr)
    exit(1)
else:
    print("[✔] Successfully compiled real ARM64 iOS executable!")

# 4. Generate a valid Info.plist configuration file
plist_path = os.path.join(app_dest, "Info.plist")
plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://apple.com">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>MyApplication</string>
    <key>CFBundleIdentifier</key>
    <string>com.zezo.saturnmobile</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Saturn</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>MinimumOSVersion</key>
    <string>14.0</string>
    <key>UIDeviceFamily</key>
    <array>
        <integer>1</integer>
        <integer>2</integer>
    </array>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>arm64</string>
    </array>
</dict>
</plist>"""

with open(plist_path, "w", encoding="utf-8") as f:
    f.write(plist_content)

# 5. Compress into the final .ipa distribution package
import zipfile
print("[+] Packaging into .ipa container...")
with zipfile.ZipFile(output_ipa, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(payload_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, start=staging_dir)
            arcname = arcname.replace("\\", "/")
            zipf.write(file_path, arcname)

print("==================================================")
print(f"[✔] SUCCESS: REAL iOS IPA GENERATED!")
print(f"OUTPUT: {output_ipa}")
print("==================================================")
