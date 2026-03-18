# MapMyCode
An AI-powered system that analyzes codebases and automatically generates architecture diagrams and documentation using LLM-driven code understanding.

# Motivation
We have all been in a situation where after writing and testing the
codebase, we are eventually tasked to create architecture diagrams or documentation for the code. It is a good practice to have proper documentation and architecture diagrams but creating them can be a hassle especially when we are starting from scratch.

That led us to create Mapmycode. The idea is simple, once you have created and tested the code, run mapmycode on the code directory.

The objective is to have a ready to use code documentation and architecture diagram which can be modified easily by the user if required instead of writing everything from scratch.

# Usage

First install the package from pypi using the pip command
```
pip install mapmycode
```
Internally the library uses Groq api as the LLM endpoint. Please go to groq website and create a token for yourself.

Then in terminal run the below command
```
Windows Powershell: $env:GROQ_API_KEY = 'your_api_key_here'
Windows CMD: set GROQ_API_KEY=your_api_key_here
Linux/macOS: export GROQ_API_KEY=your_api_key_here
```
Once your api key has been successfully set, navigate to your code directory and run the below command
```
mapmycode .
```
This runs the package on your codebase and creates three files inside a folder called **"mapmycode_output"**. The three files are

1. Code documentation
2. Codebase architecture diagram
3. Json comprising of the descriptions of each file.

**Note : The package currently only deals with python files. We plan to add support for other languages soon.**
