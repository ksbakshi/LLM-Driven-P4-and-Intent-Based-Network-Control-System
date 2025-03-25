import os #The os module in Python provides a way to interact with the operating system.
import openai #The OpenAI API library for generating P4 code
from datetime import datetime
import subprocess
import time
import re
import glob

def cleanup_files():
    """Clean up all P4 and error-related files before starting."""
    # Files to remove
    patterns = [
        "*.p4",      # All P4 files
        "*.p4i",     # P4 intermediate files
        "*.json",    # JSON configuration files
        "validation_status.txt",
        "error_summary.txt",
        "p4_validation_errors.txt",
        "temp_errors.txt"
    ]
    
    print("\nCleaning up previous files...")
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except OSError as e:
                print(f"Error removing {file}: {e}")
    print("Cleanup complete.\n")

def get_user_intent():
    #Get the networking intent from the user
    print("\nPlease provide your network intent here, please try to be as specific as possible (e.g., 'Create a P4 program for basic packet forwarding'):")
    return input("> ").strip() #Getting the user's intent

# Making a function that uses the user's intent to create a detailed prompt for the LLM
def create_detailed_prompt(intent, error_feedback=None):
    base_prompt = f"""Generate P4-16 code that implements the following network intent: {intent}

IMPORTANT: Start your response with the P4 code directly. Do not include any text, explanations, or markdown formatting before the code.

The code must be compatible with the v1model.p4 architecture and follow P4_16 syntax. Include:

1. Required includes:
   #include <core.p4>
   #include <v1model.p4>

2. Header and metadata definitions:
   - Define headers using 'header' keyword, not 'header_type'
   - Define a metadata struct
   - Define a headers struct containing all headers

3. Define the following components with UNIQUE names (avoid using standard names like Parser, Ingress, etc.):
   - Parser: (packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata)
   - VerifyChecksum: (inout headers hdr, inout metadata meta)
   - Ingress: (inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata)
   - Egress: (inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata)
   - ComputeChecksum: (inout headers hdr, inout metadata meta)
   - Deparser: (packet_out packet, in headers hdr)

4. End with V1Switch instantiation using your unique component names:
   V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;

The code should be complete, properly structured, and ready to compile with p4c."""

    if error_feedback:
        base_prompt += f"\n\nHere is the complete history of validation errors from previous attempts. Please analyze these errors carefully and ensure the new code addresses ALL of these issues:\n{error_feedback}\n\nGenerate a corrected version that addresses all these issues and does not repeat any of the previous errors. Remember to start with the code directly, no text before it."

    return base_prompt

def generate_p4_code(prompt):
    #Generate P4 code using OpenAI API
    try:
        # Seting the API key
        #I went to https://platform.openai.com/api-keys and got my API key
        #Used the export OPENAI_API_KEY='your-api-key' command to set the API key
        #then refered to this- https://platform.openai.com/docs/quickstart?api-mode=chat
        #to set the API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Create the completion
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a P4 programming expert. Your task is to generate P4 code.
                IMPORTANT RULES:
                1. Start your response with the P4 code directly
                2. Do not include any text, explanations, or markdown formatting before the code
                3. Do not include any text after the code
                4. The code must be complete and valid P4-16 code
                5. Follow the P4-16 specification for:
                   - Header definitions and parsers
                   - Control blocks (ingress/egress)
                   - Match-action tables
                   - Actions and action blocks
                   - Error handling
                   - Metadata structures
                6. Ensure all code follows P4-16 standards and best practices"""},
                {"role": "user", "content": prompt}
            ],
            #Used this link to know about the temperature and max tokens: https://platform.openai.com/docs/api-reference/debugging-requests
            temperature=0.7, #This is the temperature of the model, it controls the randomness of the model
            max_tokens=4000 #To get a better response, I set the max tokens to 4000
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error generating P4 code: {e}")
        return None

def clean_p4_code(raw_code):
    """Clean up the generated P4 code by removing markdown formatting and extra content."""
    # Find the P4 code block
    p4_block = re.search(r'```(?:P4|p4)?\n(.*?)```', raw_code, re.DOTALL)
    if p4_block:
        code = p4_block.group(1).strip()
    else:
        # If no code block found, try to find the first #include
        code = raw_code.strip()
        if '#include' in code:
            code = code[code.find('#include'):]
    
    # Remove any text before the first #include
    if '#include' in code:
        code = code[code.find('#include'):]
    
    # Remove any "p4" or "P4" line at the start of the file
    code = re.sub(r'^[pP]4\s*\n', '', code)
    
    # Remove any leading/trailing whitespace
    code = code.strip()
    
    return code

def validate_p4_code(p4_code, filename, attempt):
    # Clean up the code before saving
    cleaned_code = clean_p4_code(p4_code)
    
    # Save the code to a file
    with open(filename, 'w') as f:
        f.write(cleaned_code)
    
    # Run the validation script with attempt number
    subprocess.run(['./validate_p4.sh', str(attempt)], shell=True)
    
    # Check validation status
    try:
        with open('validation_status.txt', 'r') as f:
            status = f.read().strip()
        
        if status == "SUCCESS":
            return True, None
        
        # If validation failed, read the error summary
        with open('error_summary.txt', 'r') as f:
            error_feedback = f.read()
        return False, error_feedback
    
    except FileNotFoundError:
        return False, "Validation process failed to create status file"

def read_error_summary():
    """Read the error summary file and return its contents."""
    try:
        with open("error_summary.txt", "r") as f:
            content = f.read()
            # Only return the last 3 attempts to keep the context size manageable
            attempts = content.split("=== Attempt")
            if len(attempts) > 4:  # Keep header + last 3 attempts
                return "=== P4 Code Validation Error History ===\n" + "=== Attempt".join(attempts[-3:])
            return content
    except FileNotFoundError:
        return "No error history available."

def main():
    # Clean up existing files
    cleanup_files()
    
    # Check for OpenAI API key
    if 'OPENAI_API_KEY' not in os.environ:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it using: export OPENAI_API_KEY='your-api-key'")
        return

    # Get user intent
    intent = get_user_intent()
    
    # Maximum number of validation attempts
    max_attempts = 10
    attempt = 1
    error_feedback = None
    generated_p4_code = None
    
    while attempt <= max_attempts:
        print(f"\nAttempt {attempt} of {max_attempts}")
        
        if attempt == 1:
            # First attempt: use original intent
            prompt = create_detailed_prompt(intent)
            print("\nGenerating P4 code according to your intent...")
        else:
            # Subsequent attempts: use generated code with error history
            error_feedback = read_error_summary()
            prompt = f"""Previous P4 code generated:
{generated_p4_code}

Error history:
{error_feedback}

Please fix the P4 code based on the error history above. Generate a complete, valid P4_16 program that addresses all the errors."""

        # Generate P4 code
        p4_code = generate_p4_code(prompt)
        if p4_code is None:
            print("\n❌ Failed to generate P4 code. Please try again with a different intent.")
            return
            
        generated_p4_code = p4_code  # Store for subsequent attempts
        
        # Save the generated code
        with open("test.p4", "w") as f:
            f.write(p4_code)
        
        print("\nValidating generated P4 code...")
        # Run validation script with current attempt number
        subprocess.run(["./validate_p4.sh", str(attempt)])  # Removed check=True
        
        # Check validation status
        with open("validation_status.txt", "r") as f:
            status = f.read().strip()
        
        if status == "SUCCESS":
            print("\n✅ Successfully generated valid P4 code!")
            break
        else:
            print(f"\nValidation failed on attempt {attempt}. Errors found:")
            with open("error_summary.txt", "r") as f:
                print(f.read())
            
            if attempt < max_attempts:
                print("\nRetrying with error feedback...")
            
        attempt += 1
    
    if attempt > max_attempts:
        print("\n❌ Failed to generate valid P4 code after", max_attempts, "attempts.")
        print("Please refine your intent or check the error feedback for more details.")

if __name__ == "__main__":
    main() 
