import os
import requests
import zipfile
import shutil
import time
import subprocess
from tqdm import tqdm

def download_file(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, allow_redirects=True)
    final_url = response.url
    
    response = requests.get(final_url, stream=True, headers=headers)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True
    ) as progress_bar:
        for data in response.iter_content(chunk_size=8192):
            size = file.write(data)
            progress_bar.update(size)

def copy_directory(src, dst):
    """Copy a directory tree with better error handling"""
    try:
        if not os.path.exists(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            
            if os.path.isdir(s):
                copy_directory(s, d)
            else:
                try:
                    shutil.copy2(s, d)
                except Exception as e:
                    print(f"Error copying {s} to {d}: {str(e)}")
                    # Try alternative copy method
                    try:
                        with open(s, 'rb') as src_file:
                            with open(d, 'wb') as dst_file:
                                dst_file.write(src_file.read())
                    except Exception as e2:
                        print(f"Alternative copy also failed: {str(e2)}")
                        raise
    except Exception as e:
        print(f"Error in copy_directory: {str(e)}")
        raise

def main():
    print("Starting MinGW installation...")
    
    # Clean up any existing installation
    print("Cleaning up previous installation if any...")
    if os.path.exists('mingw'):
        try:
            shutil.rmtree('mingw', ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not remove existing mingw directory: {str(e)}")
    
    if os.path.exists('mingw_temp'):
        try:
            shutil.rmtree('mingw_temp', ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not remove existing mingw_temp directory: {str(e)}")
    
    # Wait a bit to ensure cleanup is complete
    time.sleep(2)
    
    # Create fresh directories
    try:
        os.makedirs('mingw', exist_ok=True)
        os.makedirs('mingw_temp', exist_ok=True)
    except Exception as e:
        print(f"Error creating directories: {str(e)}")
        return

    # Download MinGW
    mingw_url = "https://github.com/niXman/mingw-builds-binaries/releases/download/13.2.0-rt_v11-rev0/x86_64-13.2.0-release-posix-seh-msvcrt-rt_v11-rev0.7z"
    zip_path = "mingw.7z"
    
    print("\nDownloading MinGW (this may take a few minutes)...")
    try:
        download_file(mingw_url, zip_path)
    except Exception as e:
        print(f"Error downloading MinGW: {str(e)}")
        return
    
    print("\nExtracting MinGW...")
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
    if not os.path.exists(seven_zip_path):
        print(f"Error: 7-Zip not found at {seven_zip_path}")
        return
    
    try:
        extract_result = subprocess.run(
            [seven_zip_path, 'x', '-y', zip_path, '-omingw_temp'],
            capture_output=True,
            text=True
        )
        
        if extract_result.returncode != 0:
            print(f"Error extracting MinGW: {extract_result.stderr}")
            return
    except Exception as e:
        print(f"Error running 7-Zip: {str(e)}")
        return
    
    print("\nSetting up MinGW...")
    try:
        # Use our custom copy function instead of xcopy
        mingw64_path = os.path.join('mingw_temp', 'mingw64')
        if not os.path.exists(mingw64_path):
            print(f"Error: mingw64 directory not found at {mingw64_path}")
            return
            
        print(f"Copying files from {mingw64_path} to mingw...")
        copy_directory(mingw64_path, 'mingw')
        print("File copying completed successfully")
    except Exception as e:
        print(f"Error copying MinGW files: {str(e)}")
        return
    
    # Ensure all necessary header files are present
    print("\nVerifying header files...")
    required_headers = [
        'wchar.h',
        'stdio.h',
        'stdlib.h',
        'string.h',
        'iostream',
        'vector',
        'string'
    ]
    
    missing_headers = []
    for header in required_headers:
        header_path = os.path.join('mingw', 'include', header)
        if not os.path.exists(header_path):
            missing_headers.append(header)
            print(f"Warning: {header} not found in include directory")
    
    if missing_headers:
        print("\nMissing header files:")
        for header in missing_headers:
            print(f"- {header}")
    
    # Clean up
    print("\nCleaning up temporary files...")
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists('mingw_temp'):
            shutil.rmtree('mingw_temp', ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not clean up temporary files: {str(e)}")
    
    # Verify installation
    print("\nVerifying installation...")
    gcc_path = os.path.join(os.getcwd(), 'mingw', 'bin', 'gcc.exe')
    if not os.path.exists(gcc_path):
        print(f"Error: GCC not found at {gcc_path}")
        return
    
    print("\nTesting GCC installation...")
    
    # Create a test C file
    test_c_path = 'test.c'
    try:
        with open(test_c_path, 'w') as f:
            f.write('#include <stdio.h>\\nint main() { printf("Hello from GCC!\\n"); return 0; }')
    except Exception as e:
        print(f"Error creating test file: {str(e)}")
        return
    
    try:
        # Add MinGW bin directory to PATH temporarily
        mingw_bin = os.path.abspath(os.path.join('mingw', 'bin'))
        os.environ['PATH'] = mingw_bin + os.pathsep + os.environ['PATH']
        
        print(f"Using GCC from: {mingw_bin}")
        
        # Test compilation
        print("\nCompiling test program...")
        compile_cmd = [os.path.join(mingw_bin, "gcc.exe"), test_c_path, '-o', 'test.exe']
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode == 0:
            print("Compilation successful!")
            print("Running test program...")
            run_result = subprocess.run(
                ['test.exe'],
                capture_output=True,
                text=True
            )
            
            if run_result.returncode == 0:
                print("\nGCC is working correctly!")
                print(f"\nMinGW has been installed successfully in: {os.path.abspath('mingw')}")
                print("\nTo use GCC/G++ from any terminal, add this path to your system's PATH environment variable:")
                print(f"{mingw_bin}")
            else:
                print(f"\nError: Failed to run the test program: {run_result.stderr}")
        else:
            print(f"\nError: Failed to compile the test program: {compile_result.stderr}")
    except Exception as e:
        print(f"\nError testing GCC: {str(e)}")
    finally:
        # Clean up test files
        try:
            if os.path.exists(test_c_path):
                os.remove(test_c_path)
            if os.path.exists('test.exe'):
                os.remove('test.exe')
        except Exception as e:
            print(f"Warning: Could not clean up test files: {str(e)}")

if __name__ == "__main__":
    main() 