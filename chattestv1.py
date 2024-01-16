from txtai.pipeline import LLM
import requests
import gradio as gr
import time
import inspect
import re
from icecream import ic

def my_inputs():
    return [llm_model_box, system_prompt_box, chatbot, user_input_box, llm_class_options, llm_model_kwargs]
     
def my_outputs():
   return [total_duration_box, eval_count_box, chatbot, user_input_box]
   #return [total_duration_box, eval_count_box]

def my_input_str(func):
    source_lines = inspect.getsource(func).splitlines()
    for line in source_lines:
        if 'return' in line:
            return_line = line
            break
    variable_names = re.findall(r'\b\w+\b', return_line)
    variable_names = [name for name in variable_names if name not in ['return', '[', ']', ',']]
    return variable_names

def process_user_input(user_input_box, chatbot):
    if not isinstance(chatbot, list):
        chatbot = []
    chatbot.append((user_input_box, None))  # Append user input as a tuple
    return "", chatbot 

def undo_last_action(history):
    if history and len(history) > 1:
        history.pop()
    return history

def get_llm_models():
    import subprocess
    process = subprocess.Popen(['ollama', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    lines = stdout.decode('utf-8').strip().split('\n')
    model_names = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            model_name = parts[0].split(':')[0]
            model_names.append(model_name)
    return model_names

def create_interface():
    llm_models = get_llm_models()
    other_llm_class_kwargs = gr.Textbox(label="add LLM Class kwargs as a string", render=False)
    with gr.Row():
        total_duration_box = gr.Number(label="Total Duration (s)", interactive=False)
        eval_count_box = gr.Number(label="Eval Count", interactive=False)
    with gr.Row():
        llm_model_box = gr.Dropdown(llm_models, interactive=True, label="Select Model from List", value="mistral")
        system_prompt_box = gr.Textbox(label="System Prompt", value="you are a very sarcastic AI")
    chatbot = gr.Chatbot()
    with gr.Row():
        clear_button = gr.Button("Clear")
        undo_button = gr.Button("Undo")
    with gr.Row():
        user_input_box = gr.Textbox(scale=8)
        submit_button = gr.Button("Submit")
    with gr.Accordion(label="Additional Options", open=False):
        with gr.Row():
            llm_class_options = gr.CheckboxGroup(choices=['stream', 'metadata', 'chat', 'memory'], value=['metadata', 'memory', 'chat'], label='LLM Class Options', interactive=True)
            llm_model_kwargs = gr.Textbox(label="String: Add keywords for values to extract from the response, comma separated")
    return (total_duration_box, eval_count_box, llm_model_box, system_prompt_box, chatbot, clear_button, undo_button, user_input_box, submit_button, llm_class_options, llm_model_kwargs)

def submit_logic(*args):
   # user_input = args[3]
   # chatbot_component = args[4]
   # chat_history = chatbot_component.get_history()
   
    #chat_history = process_user_input(ordered_args2)
    outputs = my_outputs()
    input_names = my_input_str(my_inputs)
    #ic(input_names)
    args_dict = dict(zip(input_names, args))
    #ic(args_dict)
    
    params = inspect.signature(process_user_input).parameters
    ordered_args2 = [args_dict[param] for param in params if param in args_dict]
    #ic(ordered_args2)
    process_user_input(*ordered_args2)
    
    params = inspect.signature(generate_bot_response).parameters
    ordered_args1 = [args_dict[param] for param in params if param in args_dict]
    #ic (ordered_args1)
    outputs = generate_bot_response(*ordered_args1) + ("",)

    #return chatbot, total_duration_box, eval_count_box  # Return updated chat history and other info
    #ic(outputs)
    return outputs

    
    
def generate_bot_response(llm_model_box, llm_class_options, system_prompt_box, chatbot):


    def process_history(messages_history, last_user_message):
        outbound_message = ""
        chat_list = []
        if 'memory' in llm_class_options:
            for user, bot in messages_history:
                if 'chat' in llm_class_options:
                    # Add history as list of dicts
                    if len (messages_history)>1:
                        chat_list.extend([
                            {"role": "user", "content": user},
                            {"role": "assistant", "content": bot}
                        ])
                else:
                    if len (messages_history)>1:
                    # Add history as a single string
                        outbound_message += f"User: {user} Assistant: {bot} "

        # Process the latest user message based on chat flag
        if 'chat' in llm_class_options:
            # Add the latest user message as a dict
            chat_list.append({"role": "user", "content": last_user_message})
            return chat_list
        else:
            # Add the latest user message to the string
            outbound_message += f"User: {last_user_message}"
            return  outbound_message
    

    messages_history = chatbot
    last_user_message = messages_history[-1][0]
    user_message_and_history = process_history(messages_history, last_user_message)
    #ic(user_message_and_history)

    if 'chat' in llm_class_options:
        api_payload = { "messages":[{"role": "system", "content": system_prompt_box}] + user_message_and_history
        }
            
    else:
        api_payload = {
            "prompt": f"system message: {system_prompt_box}, User Message:  {user_message_and_history}"
        }
        
        
    llm_class_options = {option: True for option in llm_class_options}
    llm = LLM(model=llm_model_box, method='ollama', **llm_class_options)
    try:
        response = llm(api_payload)
        bot_message = response.get('response', "Sorry, I couldn't process that.")
        total_duration = round(response.get('eval_duration', 0) / 1e9, 1)        
        eval_count = response.get('eval_count', 0)
        if chatbot and chatbot[-1][1] is None:
            chatbot[-1] = (chatbot[-1][0], bot_message)  # Update the last tuple with the bot's response
        else:
            chatbot.append((None, bot_message)) 
    except Exception as e:
        print(f"An error occurred: {e}")
        bot_message = "Sorry, an error occurred while processing your request."
        total_duration = 0
        eval_count = 0
        if messages_history and messages_history[-1][1] is None:
            messages_history[-1] = (messages_history[-1][0], bot_message)
        else:
            messages_history.append((last_user_message, bot_message))
    return total_duration, eval_count, messages_history

with gr.Blocks() as my_app:
    (total_duration_box, eval_count_box, llm_model_box, system_prompt_box, chatbot, clear_button, undo_button, user_input_box, submit_button, llm_class_options, llm_model_kwargs) = create_interface()
    inputs = my_inputs(); outputs = my_outputs()
    submit_button.click(
        fn=submit_logic,
        inputs=inputs,
        outputs=outputs
    )
    clear_button.click(
        lambda: ([], "", ""),
        inputs=[],
        outputs=[chatbot, total_duration_box, eval_count_box]
    )
    undo_button.click(
        undo_last_action,
        inputs=[chatbot],
        outputs=[chatbot]
    )
my_app.launch()
