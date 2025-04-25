import os
import requests
import zipfile
import shutil
import subprocess
from tqdm import tqdm

def download_file(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True, headers=headers)
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

def main():
    print("Starting GCC installation...")
    
    # Clean up any existing installation
    if os.path.exists('mingw'):
        try:
            shutil.rmtree('mingw', ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not remove existing mingw directory: {str(e)}")
    
    # Create mingw directory
    try:
        os.makedirs('mingw', exist_ok=True)
    except Exception as e:
        print(f"Error creating mingw directory: {str(e)}")
        return
    
    # Download pre-built GCC
    gcc_url = "https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0-16.0.6-11.0.0-ucrt-r1/winlibs-x86_64-posix-seh-gcc-13.2.0-mingw-w64ucrt-11.0.0-r1.zip"
    zip_path = "gcc.zip"
    
    try:
        download_file(gcc_url, zip_path)
        
        print("\nExtracting GCC...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('mingw')
        
        print("\nCleaning up...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Move files from mingw64 to mingw
        print("\nSetting up GCC...")
        mingw64_path = os.path.join('mingw', 'mingw64')
        if os.path.exists(mingw64_path):
            for item in os.listdir(mingw64_path):
                src = os.path.join(mingw64_path, item)
                dst = os.path.join('mingw', item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)
            shutil.rmtree(mingw64_path)
        
        # Test the installation
        print("\nTesting GCC installation...")
        mingw_bin = os.path.abspath(os.path.join('mingw', 'bin'))
        os.environ['PATH'] = mingw_bin + os.pathsep + os.environ['PATH']
        
        # Create a test C file
        test_c_path = 'test.c'
        with open(test_c_path, 'w') as f:
            f.write('''#include <stdio.h>

int main() {
    printf("Hello from GCC!\\n");
    return 0;
}''')
        
        # Try to compile and run
        compile_cmd = [os.path.join(mingw_bin, 'gcc.exe'), test_c_path, '-o', 'test.exe']
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode == 0:
            run_result = subprocess.run(
                ['test.exe'],
                capture_output=True,
                text=True
            )
            
            if run_result.returncode == 0:
                print("\nGCC is working correctly!")
                print(f"\nGCC has been installed successfully in: {os.path.abspath('mingw')}")
                print("\nTo use GCC/G++ from any terminal, add this path to your system's PATH environment variable:")
                print(f"{mingw_bin}")
            else:
                print(f"\nError: Failed to run the test program: {run_result.stderr}")
        else:
            print(f"\nError: Failed to compile the test program: {compile_result.stderr}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
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