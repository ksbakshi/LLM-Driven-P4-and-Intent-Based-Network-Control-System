import os #The os module in Python provides a way to interact with the operating system.
import openai #The OpenAI API library for generating P4 code
from datetime import datetime

def get_user_intent():
    #Get the networking intent from the user
    print("\nPlease provide you networkk intent here, please try to be as specific as possible (e.g., 'Create a P4 program for basic packet forwarding'):")
    return input("> ") #Getting the user's intent

# Making a function that uses the user's intent to create a detailed prompt for the LLM
def create_detailed_prompt(intent):
    return f"""Generate P4-16 code that implements the following network intent: {intent}

The code must be compatible with the v1model.p4 architecture and include all required components:

1. Include the v1model.p4 header at the top:
   #include <v1model.p4>

2. Define the following components with unique names (avoid using standard names like Ingress, Egress):
   - Headers (e.g., MyHeaders)
   - Parser (e.g., MyParser)
   - VerifyChecksum control block
   - Ingress control block
   - Egress control block
   - ComputeChecksum control block
   - Deparser (e.g., MyDeparser)

3. The main V1Switch instantiation must include all 6 components:
   V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;

4. Include standard metadata and packet_in/packet_out parameters

5. Implement the specific functionality requested in the intent

The code should be complete and ready to compile with the P4 behavioral model (BMv2).

Reference P4-16 specification: https://p4.org/p4-spec/docs/P4-16-v1.2.4.html"""

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
                {"role": "system", "content": """You are a P4 programming expert. Generate clean, well-commented P4 code.
                Follow the P4-16 specification (https://p4.org/p4-spec/docs/P4-16-working-spec.html) for:
                - Header definitions and parsers
                - Control blocks (ingress/egress)
                - Match-action tables
                - Actions and action blocks
                - Error handling
                - Metadata structures
                Ensure all code follows P4-16 standards and best practices."""},
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

def save_p4_code(generated_code, user_intent):
    #Saving the generated P4 code to a text file as its easier to read and edit
    # Create a filename based on the timestamp of the intent was generated
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"p4_intent_program_{timestamp}.txt"
    
    try:
        #using the writing permission to write the code to the text file
        with open(filename, 'w') as f:
            f.write(generated_code)
        print(f"\nP4 code has been saved to: {filename}")   
        return filename
    except Exception as e:
        print(f"Error saving P4 code: {e}")
        return None

def main():
    # Check for OpenAI API key
    if 'OPENAI_API_KEY' not in os.environ:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it using: export OPENAI_API_KEY='your-api-key'")
        return

    # Get user intent
    user_intent = get_user_intent()
    
    # Create detailed prompt
    prompt = create_detailed_prompt(user_intent)
    
    # Generate P4 code
    print("\nGenerating P4 code according to your intent...")
    p4_code = generate_p4_code(prompt)
    
    #Checking if the code was generated successfully
    #If the code was generated successfully, it will save the code to a text file
    #If the code was not generated successfully, it will print a message saying that the code was not generated 
    if p4_code:
        # Save the code
        filename = save_p4_code(p4_code, user_intent)
        if filename:
            print("\nProcess completed successfully!")
        else:
            print("\nFailed to save the P4 code.")
    else:
        print("\nFailed to generate P4 code.")

if __name__ == "__main__":
    main() 
