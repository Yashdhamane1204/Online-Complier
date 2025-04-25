import requests
import json
import time

def test_language(language, code):
    print(f"\nTesting {language}...")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/execute',
            json={'code': code, 'language': language}
        )
        result = response.json()
        if result['status'] == 'success':
            print(f"✅ {language} test passed!")
            print("Output:", result['output'])
        else:
            print(f"❌ {language} test failed!")
            print("Error:", result['error'])
    except Exception as e:
        print(f"❌ {language} test failed with exception:", str(e))

# Test cases for each language
test_cases = {
    'python': 'print("Hello from Python!")',
    'javascript': '''// Basic output
console.log("Hello from JavaScript!");

// System Information
console.log("\\nSystem Information:");
console.log("Node.js version:", process.version);
console.log("Platform:", process.platform);
console.log("Architecture:", process.arch);
console.log("Current working directory:", process.cwd());

// Array Operations
console.log("\\nArray Operations:");
const numbers = [1, 2, 3, 4, 5];
console.log("Original array:", numbers);
console.log("Doubled numbers:", numbers.map(n => n * 2));
console.log("Even numbers:", numbers.filter(n => n % 2 === 0));
console.log("Sum:", numbers.reduce((a, b) => a + b, 0));

// String Operations
console.log("\\nString Operations:");
const text = "Node.js is amazing!";
console.log("Original text:", text);
console.log("Uppercase:", text.toUpperCase());
console.log("Words count:", text.split(" ").length);

// Object Operations
console.log("\\nObject Operations:");
const person = {
    name: "John",
    age: 30,
    skills: ["JavaScript", "Node.js"]
};
console.log("Person object:", person);
console.log("Object keys:", Object.keys(person));

// Date Operations
console.log("\\nDate Operations:");
const now = new Date();
console.log("Current time:", now.toLocaleString());

// Math Operations
console.log("\\nMath Operations:");
console.log("Random number:", Math.random());
console.log("PI:", Math.PI);
console.log("Square root of 16:", Math.sqrt(16));

// Error Handling
console.log("\\nError Handling:");
try {
    console.log("Inside try block");
    // Simulate successful operation
    console.log("Operation successful!");
} catch (error) {
    console.log("Error caught:", error.message);
} finally {
    console.log("Finally block executed");
}''',
    'java': '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}''',
    'cpp': '''#include <iostream>

int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}'''
}

# Run tests
print("Starting language tests...")
for language, code in test_cases.items():
    test_language(language, code)
    time.sleep(1)  # Wait a bit between tests to avoid overwhelming the server

print("\nAll tests completed!") 