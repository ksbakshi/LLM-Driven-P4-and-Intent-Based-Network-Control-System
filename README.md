# LLM-Driven P4 Code Generation System

This system uses Large Language Models (LLMs) to generate P4 code based on high-level network intents. It provides an automated way to convert network requirements into valid P4 programs.

## Summary

This project implements an intelligent system that bridges the gap between high-level network intents and low-level P4 programming. Key features include:

- **Intent-Based Programming**: Convert natural language network requirements into P4 code
- **Automated Validation**: Built-in P4 code validation using p4c compiler
- **Error Handling**: Comprehensive error tracking and history maintenance
- **Interactive Interface**: Simple command-line interface for code generation
- **Flexible Architecture**: Easy to extend and modify for different network requirements

The system is designed to simplify P4 programming by allowing network engineers to focus on their intent rather than implementation details, while ensuring the generated code meets P4 specifications and best practices.

## Prerequisites

- Python 3.x
- OpenAI API key
- Git
- p4c compiler (P4 compiler)

## Setup Instructions

### 1. Install p4c Compiler

First, install the P4 compiler (p4c) on your system:

```bash
# Clone the p4c repository
git clone --recursive https://github.com/p4lang/p4c.git
cd p4c

# Build and install p4c
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_GC=OFF
make -j1
sudo make install
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/LLM-Driven-P4-and-Intent-Based-Network-Control-System.git
cd LLM-Driven-P4-and-Intent-Based-Network-Control-System
```

### 3. Set Up Python Environment

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
python3 -m pip install -r requirements.txt
```

### 4. Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

## Usage

1. Before running the system, you can clean up any unnecessary files:
```bash
rm -f test.p4 test.p4i validation_status.txt p4_validation_errors.txt temp_errors.txt
```
Note: This will not delete error_summary.txt which maintains the history of validation errors.

2. Run the main script:
```bash
python3 network_intent_to_p4.py
```

3. When prompted, enter your network intent. Be as specific as possible, for example:
   - "Create a P4 program for basic packet forwarding"
   - "Implement a P4 program for P2P setup"
   - "Generate P4 code for a simple router with ACL"

4. The system will:
   - Generate P4 code based on your intent
   - Validate the code using p4c
   - Save the generated code to `test.p4`
   - Save validation results to `validation_status.txt`
   - Maintain error history in `error_summary.txt`

## Output Files

- `test.p4`: The generated P4 code
- `test.p4i`: Intermediate representation of the P4 code
- `validation_status.txt`: Contains the validation results
- `error_summary.txt`: Contains detailed error information and history
- `p4_validation_errors.txt`: Temporary file for current validation errors

## Troubleshooting

### Common Issues

1. **p4c Not Found**
   - Ensure p4c is properly installed and in your system PATH
   - Verify installation by running `p4c --version`

2. **OpenAI API Key Issues**
   - Make sure the API key is set correctly
   - Verify the key is valid and has sufficient credits

3. **Validation Errors**
   - Check `error_summary.txt` for detailed error messages and history
   - The system will attempt to fix common issues automatically

### Cleanup

Everytime the user runs the python script all the unwanted files will be deleted to avoid any kinds of conflicts.

## Contact

For questions or issues, please open an issue in the GitHub repository or email me at kunwardeepsingh00@gmail.com.

