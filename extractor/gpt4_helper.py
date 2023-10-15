import openai

# Initialize API key
openai.api_key = "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"

def query_gpt4(prompt, model="gpt-4"):
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant that provides brief and to-the-point answers. This is a CLI-based application."
    }

    user_message = {
        "role": "user",
        "content": prompt
    }

    result = openai.ChatCompletion.create(
        model=model,
        messages=[system_message, user_message]
    )
    
    generated_text = result['choices'][0]['message']['content']
    return generated_text.strip()  # Added strip() to remove extra whitespace, if any

def handle_api_query():
    while True:
        print("Type of Query:")
        print("1. Add new contact feature")
        print("2. Debug an issue")
        print("3. Optimize existing code")
        print("4. Prompt for user input")
        print("5. Quit")
        user_choice = input("Choose an option: ")

        if user_choice == '5':
            break

        if user_choice == "4":
            user_prompt = input("Enter your prompt: ")
            response = query_gpt4(user_prompt)  # Assuming the second argument can be None if no fields are specified.
            print("Generated code/response:", response)
            continue


        if user_choice == '1':
            user_prompt = "How can I implement a feature to add a new contact to a list?"
        elif user_choice == '2':
            user_prompt = "I'm getting a KeyError when trying to access a dictionary element. How to debug?"
        elif user_choice == '3':
            user_prompt = "How can I make my contact gathering function more efficient?"
        
        response = query_gpt4(user_prompt)
        suggestions = [s.strip().split('. ')[-1] for s in response.split('\n') if s.strip()]
        
        print("Generated code/response:")
        for idx, suggestion in enumerate(suggestions, 1):
            print(f"{idx}. {suggestion}")
        
        print("Select one of the following suggestions for more details or type 'back' to go back:")
        sub_choice = input()

        if sub_choice.lower() == 'back':
            continue

        try:
            selected_suggestion = int(sub_choice) - 1
            detailed_response = query_gpt4(suggestions[selected_suggestion])
            print(f"More details on: {suggestions[selected_suggestion]}")
            print(f"Generated code/response: {detailed_response}\n")
        except (ValueError, IndexError):
            print("Invalid selection.")
