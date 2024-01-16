"""
LLM module
"""

from .factory import GenerationFactory

from ..base import Pipeline
from spinner import spin, unspin


class LLM(Pipeline):
    """
    Pipeline for running large language models (LLMs). This class supports the following LLM backends:

      - Local LLMs with Hugging Face Transformers
      - Local LLMs with llama.cpp
      - Remote API LLMs with LiteLLM
      - Local LLMs with Ollama
      - Custom generation implementations
    """

    def __init__(self, path=None, method=None, **kwargs):
        """
        Creates a new LLM.

        Args:
            For Ollama: include model= , method='ollama', metadata=bool, stream=False
            path: model path
            method: llm model framework, infers from path if not provided.
            kwargs: model keyword arguments
            
        """
        # Set 'stream' variable as False, maxlength as 512, but both will be overwritten by the user instructions
        #stream = False
       # maxlength = int(4000)
        # Include 'stream' in kwargs
        #kwargs['stream'] = stream
        #kwargs['maxlength'] = maxlength
        self.stream = False
        self.maxlength = int(4000)
        # Include 'stream' and 'maxlength' in kwargs if not already provided by the user
        kwargs.setdefault('stream', self.stream)
        kwargs.setdefault('maxlength', self.maxlength)


        # Generation instance
        def print_initialization_parameters(path, method, kwargs):
            print("Initializing LLM with the following parameters (from llm.py, __init__):")
            print(f"Path: {path}")
            print(f"Method: {method}")
            print(f"Additional arguments: {kwargs}\n")

        print_input = False

        # Default LLM if not provided
        if method == 'ollama':
            path = None
        else:
            path = path if path else "google/flan-t5-base"

        if print_input:
            print_initialization_parameters(path, method, kwargs)

        self.generator = GenerationFactory.create(path, method, **kwargs)
    def __call__(self, text, **kwargs): #removed maxlength=512
        """
        Generates text using input text

        Args:
            text: text|list
            maxlength: maximum sequence length
            kwargs: additional generation keyword arguments

        Returns:
            generated text
        """
        
        
        def print_call_parameters(text, maxlength, kwargs):
            print("Calling LLM with the following parameters (from llm.py, __call__):")
            print(f"Text: {text}")
            print(f"Maxlength: {maxlength}")
            print(f"Additional arguments: {kwargs}\n")

        print_input = False

        if print_input:
            print_call_parameters(text, self.maxlength, kwargs) #added self. to maxlength
        
        # Run LLM generation
        #spin(f"Making LLM call with {text}, {maxlength}, {combined_kwargs}")
        llm_call = self.generator(text, self.maxlength, **kwargs) #added self. to maxlength
       # unspin()
        #print(llm_call)
        return  llm_call
