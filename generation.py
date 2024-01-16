"""
Generation module
"""

from ...util import TemplateFormatter
import logging


class Generation:
    """
    Base class for generative models. This class has common logic for building prompts and cleaning model results.
    """

    def __init__(self, path=None, template=None, **kwargs):
        """
        Creates a new Generation instance.

        Args:
            path: model path
            template: prompt template
            kwargs: additional keyword arguments
        """

        self.path = path
        self.template = template
        self.kwargs = kwargs

    def __call__(self, text, maxlength, **kwargs):
        """
        Generates text using input text

        Args:
            text: text|list
            maxlength: maximum sequence length
            kwargs: additional generation keyword arguments

        Returns:
            generated text
        """

        if self.method != "ollama":
            # List of texts
            texts = text if isinstance(text, list) else [text]
            # Apply template, if necessary
            if self.template:
                formatter = TemplateFormatter()
                texts = [formatter.format(self.template, text=x) for x in texts]
               # print(f"self.template output is: {texts}")
            # Run pipeline
            results = self.execute(texts, maxlength, **kwargs)
            #print(f"results of run pipeline on execute: {results}")
            # Extract and clean the generated text
            if 'response' in results:
                generated_text = results['response']  
                #cleaned_text = self.clean(text, generated_text)
                cleaned_text = [self.clean(texts[x], generated_text) for x, generated_text in enumerate(results)]

                return cleaned_text
            else:
                # Handle the case where 'response' is not in the result_data
                logging.error("'response' key not found in the result_data.")
                return ""

        else:
            texts = text if isinstance(text, list) else [text]
            #print("\n\n\n This is the def call from generation.py.  It's my generation.  And here's the texts \n" ,texts)
             # Apply template, if necessary
            if self.template:
                formatter = TemplateFormatter()
                texts = [formatter.format(self.template, text=x) for x in texts]
               # print(f"self.template output is: {texts}")
            response = self.execute(texts, maxlength, **kwargs)
        if len(response) > 1:
            #print("Metadata:", result_dict['metadata'])
            print(response)
            result_dict = {'response': response[0][0], **response[1]}
            # Assuming you want to print the metadata, uncomment the following line
            return result_dict
        else:
            cleaned_text = response[0]
            return cleaned_text
    

    def execute(self, texts, maxlength, **kwargs):
        """
        Runs a list of prompts through a generative model.

        Args:
            texts: list of prompts to run
            maxlength: maximum sequence length
            kwargs: additional generation keyword arguments
        """

        raise NotImplementedError

    def clean(self, prompt, result):
        """
        Applies a series of rules to clean generated text.

        Args:
            prompt: original input prompt
            result: result text

        Returns:
            clean text
        """
        #print(f"Inputs to the function 'clean': prompt = {prompt}, result = {result}")
        # Replace input prompt
        text = result.replace(prompt, "")

        # Apply text cleaning rules
        return text.replace("$=", "<=").strip()
