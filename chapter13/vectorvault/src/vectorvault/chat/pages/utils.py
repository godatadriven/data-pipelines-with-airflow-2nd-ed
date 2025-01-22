from langchain.prompts import PromptTemplate


prompt_template = """


ONLY PROVIDE RECIPES INCLUDED IN THE CONTEXT

However, If the context doesn't contain the answer, reply saying that you don't know how to do that recipe.

You can be nice and respond to greetings if the user does not is specifically ask for a recipe.

If you know the recipe, provide the whole recipe. If they ask you for a recipe that is not in the context provide them three options of recipes that you from the context

return a json object with the following format:

    "answer": (str) "The answer to the question",
    "provided_recipe": (bool) "True if provided a recipe, False otherwise",

Do not provide ```json``` in the response. I'm assuming the response is a json object.

Try to always answer in a recipe format. First, give the ingredients in bullets, then the steps numbered. Unless you are giving them options.
Or don't know how to do that.

Question:
{input}

Message history:
{chat_history}

Context:
{context}

"""


PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "input" ,"chat_history"]
)
