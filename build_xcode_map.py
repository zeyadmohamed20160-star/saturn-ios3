import os
import glob
import uuid

def generate_pbx_id():
    # Xcode requires unique 24-character hexadecimal IDs for file targets
    return uuid.uuid4().hex[:24].upper()

print("=== Starting Deep Structural C/C++ Xcode Mapping ===")

# Locate files across your exact tree paths
extensions = ['*.cpp', '*.c', '*.h', '*.hpp']
file_paths = []
for folder in ['src', 'actors', 'levels', 'data', 'dynos']:
    if os.path.exists(folder):
        for ext in extensions:
            found = glob.glob(f"{folder}/**/{ext}", recursive=True)
            file_paths.extend([f.replace('\\', '/') for f in found])

print(f"Collected {len(file_paths)} active code items. Creating structural project map...")

# Initialize standard file reference strings and compilation build phase groups
file_refs = ""
build_files = ""
compile_phase = ""

for path in file_paths:
    filename = os.path.basename(path)
    file_id = generate_pbx_id()
    ref_id = generate_pbx_id()
    
    # 1. Map out individual file paths relative to repository root
    file_refs += f'\t\t{file_id} /* {filename} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.cpp.cpp; name = "{filename}"; path = "{path}"; sourceTree = "<group>"; }};\n'
    
    # 2. Assign implementation compilation switches for executable components (.c and .cpp)
    if path.endswith('.cpp') or path.endswith('.c'):
        build_files += f'\t\t{ref_id} /* {filename} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_id} /* {filename} */; }};\n'
        compile_phase += f'\t\t\t\t{ref_id} /* {filename} in Sources */,\n'

# Assemble the complete properties blueprint text
pbxproj_content = f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{}};
	objectVersion = 56;
	objects = {{
/* Begin PBXBuildFile section */
{build_files}/* End PBXBuildFile section */

/* Begin PBXFileReference section */
{file_refs}\t\t92CBCB3D /* SaturnIOS3.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = SaturnIOS3.app; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXGroup section */
		45A18653 /* Root Group */ = {{
			isa = PBXGroup;
			children = (
				B45522BA /* SaturnIOS3 Code */,
			);
			sourceTree = "<group>";
		}};
		B45522BA /* SaturnIOS3 Code */ = {{
			isa = PBXGroup;
			children = (
"""

for path in file_paths:
    # Tie all individual file identifiers back into the parent workspace array
    pbxproj_content += f'\t\t\t\t{generate_pbx_id()} /* {os.path.basename(path)} */,\n'

pbxproj_content += f"""			);
			name = SaturnIOS3;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXSourcesBuildPhase section */
		0F113AB7 /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
{compile_phase}			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin PBXNativeTarget section */
		3E417E5D /* SaturnIOS3 Target */ = {{
			isa = PBXNativeTarget;
			buildPhases = (
				0F113AB7 /* Sources */,
			);
			name = SaturnIOS3;
			productName = SaturnIOS3;
			productReference = 92CBCB3D /* SaturnIOS3.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		919CA22D /* Project object */ = {{
			isa = PBXProject;
			mainGroup = 45A18653 /* Root Group */;
			targets = (
				3E417E5D /* SaturnIOS3 Target */,
			);
		}};
/* End PBXProject section */
	}};
	rootObject = 919CA22D /* Project object */;
}}
"""

# Recreate the target bundle directory container structure cleanly
os.makedirs("SaturnIOS3.xcodeproj", exist_ok=True)
with open("SaturnIOS3.xcodeproj/project.pbxproj", "w", encoding="utf-8") as f:
    f.write(pbxproj_content)

print("=== Structural project.pbxproj Generation Successful! ===")
