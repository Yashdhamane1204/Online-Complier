from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import os
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

# Get absolute paths for executables
NODE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nodejs', 'node.exe'))
PYTHON_PATH = sys.executable
JAVA_PATH = shutil.which('java')
JAVAC_PATH = shutil.which('javac')
MINGW_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mingw', 'bin'))
GPP_PATH = os.path.join(MINGW_PATH, 'g++.exe')

def check_compiler(name):
    """Check if a compiler/runtime is available"""
    if name == 'node':
        return os.path.exists(NODE_PATH)
    elif name == 'python':
        return PYTHON_PATH is not None
    elif name == 'java':
        return JAVA_PATH is not None and JAVAC_PATH is not None
    elif name == 'g++':
        # Add MinGW to PATH temporarily for compiler check
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = MINGW_PATH + os.pathsep + old_path
        exists = os.path.exists(GPP_PATH)
        os.environ['PATH'] = old_path
        return exists
    return shutil.which(name) is not None

# Check available compilers/runtimes
AVAILABLE_LANGUAGES = {
    'python': check_compiler('python'),
    'javascript': check_compiler('node'),
    'java': check_compiler('java'),
    'cpp': check_compiler('g++')
}

# Language configurations
LANGUAGE_CONFIGS = {
    'python': {
        'file_extension': '.py',
        'compile_cmd': None,
        'run_cmd': [PYTHON_PATH, '{file}'],
        'timeout': 10,
        'template': 'print("Hello, World!")\n\n# Try some calculations\nprint("5 + 10 =", 5 + 10)\n\n# Create a list\nnumbers = [1, 2, 3, 4, 5]\nprint("List:", numbers)\nprint("Sum of list:", sum(numbers))'
    },
    'javascript': {
        'file_extension': '.js',
        'compile_cmd': None,
        'run_cmd': [NODE_PATH, '{file}'],
        'timeout': 10,
        'template': '''// Node.js examples
console.log("Hello from Node.js!");

// System Information
console.log("\\nSystem Information:");
console.log("Node.js version:", process.version);
console.log("Platform:", process.platform);
console.log("Architecture:", process.arch);
console.log("Current working directory:", process.cwd());

// Environment Information
console.log("\\nEnvironment Information:");
console.log("NODE_ENV:", process.env.NODE_ENV || "development");
console.log("PATH:", process.env.PATH);

// Advanced Array Operations
console.log("\\nAdvanced Array Operations:");
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
console.log("Original array:", numbers);

// Filter even numbers
const evenNumbers = numbers.filter(n => n % 2 === 0);
console.log("Even numbers:", evenNumbers);

// Map to square numbers
const squaredNumbers = numbers.map(n => n * n);
console.log("Squared numbers:", squaredNumbers);

// Reduce to find sum
const sum = numbers.reduce((acc, curr) => acc + curr, 0);
console.log("Sum of numbers:", sum);

// Find maximum number
const max = Math.max(...numbers);
console.log("Maximum number:", max);

// Advanced String Operations
console.log("\\nAdvanced String Operations:");
const text = "Node.js is a powerful runtime environment!";
console.log("Original text:", text);

// Split into words and count
const words = text.split(" ");
console.log("Number of words:", words.length);
console.log("Words:", words);

// Replace text
const replacedText = text.replace("powerful", "amazing");
console.log("Replaced text:", replacedText);

// Advanced Object Operations
console.log("\\nAdvanced Object Operations:");
const person = {
    name: "John",
    age: 30,
    skills: ["JavaScript", "Node.js", "Python"],
    address: {
        city: "New York",
        country: "USA"
    }
};

// Object destructuring
const { name, age, skills, address: { city } } = person;
console.log("Destructured values:", { name, age, skills, city });

// Object methods
console.log("Object keys:", Object.keys(person));
console.log("Object values:", Object.values(person));
console.log("Object entries:", Object.entries(person));

// Advanced Function Examples
console.log("\\nAdvanced Function Examples:");

// Arrow function with multiple parameters
const multiply = (a, b) => a * b;
console.log("Multiply 5 and 3:", multiply(5, 3));

// Function with default parameters
function greet(name = "Guest", greeting = "Hello") {
    return `${greeting}, ${name}!`;
}
console.log("Greet with defaults:", greet());
console.log("Greet with parameters:", greet("John", "Hi"));

// Date and Time Operations
console.log("\\nDate and Time Operations:");
const now = new Date();
console.log("Current date and time:", now);
console.log("Formatted date:", now.toLocaleDateString());
console.log("Formatted time:", now.toLocaleTimeString());
console.log("Timestamp:", now.getTime());

// Math Operations
console.log("\\nMath Operations:");
console.log("Random number:", Math.random());
console.log("PI:", Math.PI);
console.log("Square root of 16:", Math.sqrt(16));
console.log("Power of 2^3:", Math.pow(2, 3));
console.log("Round 3.7:", Math.round(3.7));
console.log("Ceil 3.2:", Math.ceil(3.2));
console.log("Floor 3.7:", Math.floor(3.7));

// Error Handling
console.log("\\nError Handling Example:");
try {
    // Simulate an error
    throw new Error("This is a test error");
} catch (error) {
    console.log("Caught error:", error.message);
} finally {
    console.log("This always executes");
}'''
    },
    'java': {
        'file_extension': '.java',
        'compile_cmd': [JAVAC_PATH, '{file}'] if JAVAC_PATH else None,
        'run_cmd': [JAVA_PATH, '{classname}'] if JAVA_PATH else None,
        'timeout': 15,
        'template': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n        \n        // Array operations\n        int[] numbers = {1, 2, 3, 4, 5};\n        System.out.print("Numbers: ");\n        for (int n : numbers) {\n            System.out.print(n + " ");\n        }\n        System.out.println();\n    }\n}'
    },
    'cpp': {
        'file_extension': '.cpp',
        'compile_cmd': [GPP_PATH, '{file}', '-o', '{output}'],
        'run_cmd': ['{output}'],
        'timeout': 10,
        'template': '''#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    
    // Working with vectors (dynamic arrays)
    vector<int> numbers = {1, 2, 3, 4, 5};
    cout << "\\nVector operations:" << endl;
    cout << "Numbers: ";
    for(int num : numbers) {
        cout << num << " ";
    }
    cout << endl;
    
    // String operations
    string text = "C++ is powerful!";
    cout << "\\nString operations:" << endl;
    cout << "Original text: " << text << endl;
    cout << "Length: " << text.length() << endl;
    cout << "Substring: " << text.substr(0, 3) << endl;
    
    // Basic calculations
    int sum = 0;
    for(int num : numbers) {
        sum += num;
    }
    cout << "\\nSum of numbers: " << sum << endl;
    cout << "Average: " << static_cast<double>(sum) / numbers.size() << endl;
    
    return 0;
}'''
    }
}

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/get-languages', methods=['GET'])
def get_languages():
    """Get list of available languages and their templates"""
    return jsonify({
        'languages': {
            lang: {
                'available': available,
                'template': LANGUAGE_CONFIGS[lang]['template'] if available else None
            }
            for lang, available in AVAILABLE_LANGUAGES.items()
        }
    })

def get_java_class_name(code):
    """Extract public class name from Java code"""
    import re
    match = re.search(r'public\s+class\s+(\w+)', code)
    return match.group(1) if match else 'Main'

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        code = request.json.get('code', '')
        language = request.json.get('language', 'python').lower()
        
        if language not in LANGUAGE_CONFIGS:
            return jsonify({
                'output': '',
                'error': f'Unsupported language: {language}',
                'status': 'error'
            })

        if not AVAILABLE_LANGUAGES[language]:
            return jsonify({
                'output': '',
                'error': f'The compiler/runtime for {language} is not installed or not properly configured.',
                'status': 'error'
            })

        config = LANGUAGE_CONFIGS[language]
        
        # Create a temporary directory for the code execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up file paths
            file_path = os.path.join(temp_dir, f'source{config["file_extension"]}')
            output_path = os.path.join(temp_dir, 'output.exe' if os.name == 'nt' else 'output')
            
            # Handle Java class name
            class_name = 'Main'
            if language == 'java':
                class_name = get_java_class_name(code)
                file_path = os.path.join(temp_dir, f'{class_name}.java')
            
            # Write the code to a temporary file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            output = ''
            error = ''
            
            # Add MinGW to PATH for C++ compilation
            if language == 'cpp':
                os.environ['PATH'] = MINGW_PATH + os.pathsep + os.environ.get('PATH', '')
            
            # Compile if necessary
            if config['compile_cmd']:
                try:
                    compile_cmd = [
                        cmd.format(
                            file=file_path,
                            output=output_path,
                            classname=class_name
                        ) for cmd in config['compile_cmd']
                    ]
                    
                    compile_result = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        cwd=temp_dir
                    )
                    
                    if compile_result.returncode != 0:
                        return jsonify({
                            'output': '',
                            'error': f'Compilation error:\n{compile_result.stderr}',
                            'status': 'error'
                        })
                except Exception as e:
                    return jsonify({
                        'output': '',
                        'error': f'Compilation error: {str(e)}',
                        'status': 'error'
                    })
            
            # Run the code
            try:
                run_cmd = [
                    cmd.format(
                        file=file_path,
                        output=output_path,
                        classname=class_name
                    ) for cmd in config['run_cmd']
                ]
                
                result = subprocess.run(
                    run_cmd,
                    capture_output=True,
                    text=True,
                    timeout=config['timeout'],
                    cwd=temp_dir
                )
                
                output = result.stdout
                error = result.stderr
                
            except subprocess.TimeoutExpired:
                return jsonify({
                    'output': '',
                    'error': f'Execution timed out ({config["timeout"]} seconds limit)',
                    'status': 'error'
                })
            except Exception as e:
                return jsonify({
                    'output': '',
                    'error': f'Execution error: {str(e)}',
                    'status': 'error'
                })
            
            return jsonify({
                'output': output,
                'error': error,
                'status': 'success' if not error else 'error'
            })
                
    except Exception as e:
        return jsonify({
            'output': '',
            'error': str(e),
            'status': 'error'
        })

if __name__ == '__main__':
    app.run(debug=True) 