"""
Ollama module
"""
from .generation import Generation
import logging
import requests
import json

#OLLAMA = True

class Ollama(Generation):
    """
    Ollama generative model.
    """

    @staticmethod
    def ismodel(path):
        """
        Checks if path is an Ollama model.

        Args:
            path: input path

        Returns:
            True if this is an Ollama model, False otherwise
        """
        import requests
        import json
        # pylint: disable=W0702
        if isinstance(path, str):
            try:
                # Send a GET request to the Ollama API
                response = requests.get("http://localhost:11434/api/tags")
                # Parse the JSON response
                models = json.loads(response.text)["models"]
                # Check if the 'path' is present in the "name" key-pair value
                for model in models:
                    if path in model["name"].split(":")[0]:
                        return True
            except Exception as e:
                print(f"An error occurred while trying to verify the Ollama model: {e}")
                return False
        return False

    def __init__(self, path, template=None, **kwargs):
        #print(f"Values at class init: path = {path}, template = {template}, kwargs = {kwargs}")
        super().__init__(path, template, **kwargs)
        
        # Dynamically set attributes with a prefix based on kwargs
        #for key, value in kwargs.items():   #If there's a clash or overwriting values then will need to set this, as it adds 'init_' to the prefix.  I'm taking it out initially so that I can put all the self. values into kwargs with the same name.

        print("kwargs from Ollama.py - __init__")
        for key, value in kwargs.items():
            print(key, value)
            setattr(self, f"{key}", value)
        print("self.stream value: ", self.stream)
        
        print("\n")

        # Register prompt template
        self.register(path)

#The commented out below is the original from the LLMLite file that I have repurposed for this use in Ollama
    '''def execute(self, texts, maxlength, **kwargs):
        results = []
        for text in texts:
            result = api.completion(model=self.path, messages=[{"content": text, "role": "user"}], max_tokens=maxlength, **{**kwargs, **self.kwargs})
            results.append(result["choices"][0]["message"]["content"])

        return results'''
        
        
    def execute(self, texts, maxlength, **kwargs):
    #def execute(self, model_name, gen_type="generate", **kwargs):
        #print(f"Before execute, gen_type = {gen_type}")  # Debug print
        #print(f"Inputs to the function: texts = {texts}, maxlength = {maxlength}, kwargs = {kwargs}")
       
        """
        Send a request to the Ollama API to either generate text or conduct a chat session.

        Parameters:
        model_name (str): The name of the model to use for generation or chat (required).
        gen_type (str): The type of generation to perform ('generate' or 'chat'). Default is 'generate'.

        **kwargs: Arbitrary keyword arguments, which can include:
            - prompt (str): The prompt to generate a response for (required for 'generate').
            - messages (list of dict): The messages of the chat, used to keep a chat memory (required for 'chat').
                Each message object can have the following fields:
                    - role (str): The role of the message, either 'system', 'user', or 'assistant'.
                    - content (str): The content of the message.
                    - images (list of str): A list of base64-encoded images to include in the message (optional, for multimodal models).
...(about 4 lines omitted)...

        Returns:
        dict: The response from the API, parsed as a JSON object.

        Raises:
        requests.exceptions.RequestException: If the API request fails.
        """
        

        print(f"Inputs to the execute function: texts = {texts}, maxlength = {maxlength}, kwargs = {kwargs}")
        
        # Define a function to handle API calls safely - not having lots of open sessions!yyyy
        def safe_api_call(api_url, payload):
            try:
                # Use a context manager to ensure the session is closed after use
                with requests.Session() as session:
                    # Set a reasonable timeout for the request
                    response = session.post(api_url, json=payload, timeout=10)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    return response.json()  # Return the parsed JSON response
            except requests.RequestException as e:
                # Handle any request-related errors here
                print(f"An error occurred: {e}")
                return None

        
        metadata = False
        if hasattr(self, 'metadata'):
            metadata = self.kwargs.pop('metadata', True)
        
        # Base API URL
        base_api_url = "http://localhost:11434/api/"
        
        stream = self.stream if hasattr(self, 'stream') else False
        gen_type = self.gen_type if hasattr(self, 'gen_type') else "generate"
        if gen_type not in ["chat", "generate"]:
            print(f"current gen_type =  {gen_type}" )
            raise ValueError("Invalid generation type specified. Use 'generate' or 'chat'.")
        else:
            api_url = base_api_url + gen_type 
            print(api_url)

        # makes a variable value out of any self.keys so that any kwarg passed into the LLM creation is passed into the LLM at time of calling it & construct the payload using the variables created from self.keywords
        if not hasattr(self, 'model') or not self.model:
            raise ValueError("model_name must be provided")
        #for debug
        #print(f"\nOllama.py\nModel: {self.model}")
        
        # Initialize payload with kwargs, excluding 'method' and 'gen_type'
        payload = {key: value for key, value in self.kwargs.items() if key not in ['method', 'gen_type']}
        
        if gen_type == "generate":
            # Initialize prompt as None
            prompt = None
            
            # Check if 'prompt' is directly provided in the texts
            if isinstance(texts, str):
                prompt = texts
            elif isinstance(texts, dict) and 'prompt' in texts:
                prompt = texts['prompt']
            elif isinstance(texts, list) and len(texts) == 1 and isinstance(texts[0], str):
                prompt = texts[0]
            elif isinstance(texts, list) and len(texts) == 1 and isinstance(texts[0], dict) and 'prompt' in texts[0]:
                prompt = texts[0]['prompt']
            else:
                raise ValueError("Invalid format for 'texts'. Must be a string, a dictionary with a 'prompt' key, or a single-item list containing a string.")
            
            # Update the payload with the prompt
            payload["prompt"] = prompt
            
        elif gen_type == "chat":
            # Initialize messages as None
            messages = None
            
            # Check if 'messages' is directly provided in the texts
            if isinstance(texts, dict) and 'messages' in texts:
                messages = texts['messages']
            # If not, and texts is a list of messages, extract all user messages
            elif isinstance(texts, list) and any(isinstance(text, dict) and text.get('role') == 'user' for text in texts):
                messages = [message for message in texts if message.get('role') == 'user']
            # If messages is still None, normalize texts to a single string if it's a single-item list
            if messages is None:      
                if isinstance(texts, list) and len(texts) == 1:
                    messages = [texts[0]]
                else:
                    messages = texts
            
            # Update the payload with the messages
            payload["messages"] = messages
        
        # Update the payload with any additional kwargs
        payload.update(kwargs)
        print(payload)
           

        
        print(f"JL - Complete API call: {api_url}, Payload: {payload}")
        
        # Send the POST request to the Ollama API
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            #print(f"Raw API response: {response.text}")
          #  logging.debug(f"JL - Raw API response: {response.text}")

            response_data = response.json()  # Parse the response data as JSON
            if gen_type == "generate":
                if 'response' in response_data:
                    # Extract the 'response' value
                    generated_text = response_data.pop('response')
                    # If the response contains a single string, wrap it in a list
                    generated_texts = [generated_text] if isinstance(generated_text, str) else generated_text
                else:
                    logging.error("The key 'response' was not found in the API response.")
                    return [], {}
            elif gen_type == "chat":
                print(response_data)
                if 'messages' in response_data:
                    generated_texts = [message['content'] for message in response_data['messages'] if message['role'] == 'assistant']
                elif 'message' in response_data and response_data['message']['role'] == 'assistant':
                    generated_texts = [response_data['message']['content']]
                else:
                    logging.error("No assistant messages found in the API response.")
                    return [], {}

            if metadata:
                return generated_texts, response_data
            else:
                return generated_texts

        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama API request failed: {e}")
            return {"error": str(e)}  # Return an error object
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {e}")
            return {"error": str(e)}  # Return an error object indicating JSON parsing issue




    def register(self, path):
        """
        Registers a custom prompt template for path.

        Args:
            path: model path
        """
        pass
        #api.register_prompt_template(model=path, roles={"user": {"pre_message": "", "post_message": ""}})
