import os
import subprocess
import shutil
import glob
import zipfile

print("==================================================")
print("   COMPILING SATURN FOR iOS (MACOS RUNNER)       ")
print("==================================================")

# 1. Recursively search the entire workspace for C and C++ source files
print("[+] Searching entire workspace for .cpp and .c files...")

c_files = glob.glob("./**/*.c", recursive=True)
cpp_files = glob.glob("./**/*.cpp", recursive=True)

# Filter out build staging and git metadata directories
source_files = [
    f for f in (c_files + cpp_files) 
    if "Saturn_Build_Staging" not in f and ".git" not in f
]

print(f"[+] Found {len(source_files)} source files.")

if len(source_files) == 0:
    print("[!] Error: No .cpp or .c files found anywhere in the repository!")
    exit(1)

# Find all header directories so the compiler can locate .h files anywhere
h_files = glob.glob("./**/*.h", recursive=True)

include_dirs = list(set(os.path.dirname(hf) for hf in h_files if "Saturn_Build_Staging" not in hf and ".git" not in f))

include_flags = []
for d in include_dirs:
    include_flags.extend(["-I", d])

print(f"[+] Found header files across {len(include_dirs)} directories.")

# 2. Automatically patch header files for compatibility
print("[+] Patching header files for modern compiler compatibility...")
for hf in h_files:
    if "Saturn_Build_Staging" not in hf and ".git" not in f:
        try:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            modified = False

            # Fix 1: Replace NULL default parameter assignments with nullptr
            if "= NULL" in content:
                content = content.replace("= NULL", "= nullptr")
                modified = True

            # Fix 2: If this is the custom libc string.h file, ensure memset is declared
            if os.path.basename(hf) == "string.h" and "memset" not in content:
                content += "\n#ifdef __cplusplus\nextern \"C\" {\n#endif\nvoid *memset(void *b, int c, size_t len);\n#ifdef __cplusplus\n}\n#endif\n"
                modified = True
                print(f"[✔] Added memset declaration to custom string.h: {hf}")

            if modified:
                with open(hf, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[✔] Patched: {hf}")

        except Exception as e:
            print(f"[!] Warning: Could not patch {hf}: {e}")

# 3. Get the iOS SDK Path from Xcode
try:
    sdk_path = subprocess.check_output(
        ["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]
    ).decode("utf-8").strip()
    print(f"[✔] iOS SDK located at: {sdk_path}")
except Exception as e:
    print(f"[!] Error finding iOS SDK: {e}")
    exit(1)

# Setup output staging directories
staging_dir = "./Saturn_Build_Staging"
payload_dir = os.path.join(staging_dir, "Payload")
app_dest = os.path.join(payload_dir, "MyApplication.app")
binary_name = "MyApplication"
output_ipa = "SaturnCompletePackage.ipa"

if os.path.exists(staging_dir):
    shutil.rmtree(staging_dir)

os.makedirs(app_dest, exist_ok=True)

# 4. Compile source files into a real ARM64 Mach-O iOS binary using Clang++
output_binary_path = os.path.join(app_dest, binary_name)

compile_cmd = [
    "clang++",
    "-arch", "arm64",
    "-isysroot", sdk_path,
    "-miphoneos-version-min=14.0",
    "-std=c++17",
    # Link essential iOS frameworks for UI, buttons, and graphics
    "-framework", "UIKit",
    "-framework", "Foundation",
    "-framework", "CoreGraphics",
    "-framework", "OpenGLES",
] + include_flags + source_files + ["-o", output_binary_path]

print("[+] Compiling and linking source files (this may take a moment)...")
result = subprocess.run(compile_cmd, capture_output=True, text=True)

if result.returncode != 0:
    print("[!] Compilation failed!")
    print(result.stderr)
    exit(1)
else:
    print("[✔] Successfully compiled real ARM64 iOS executable!")

# 5. Generate a valid Info.plist configuration file
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

# 6. Compress into the final .ipa distribution package
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
