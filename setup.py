from setuptools import setup, find_packages

# Read the contents of your README.md file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Configuration for your package
setup(
    name="gemini2-powershell-command-gen",  # Name of your project
    version="0.1.0",  # Version of your project
    author="Elias Andrade",  # Your name
    author_email="oeliasandrade@gmail.com",  # Your email
    description="A web application to generate PowerShell commands using Google Gemini 2.",  # A brief description
    long_description=long_description,  # Long description from README.md
    long_description_content_type="text/markdown", # Specifies the format of the long description
    url="https://github.com/chaos4455/gemini2-powershell-command-gen",  # URL of your repository
    packages=find_packages(), # Automatically find all packages within the project
    classifiers=[ # Metadata for your project
        "Programming Language :: Python :: 3", # Specifies the programming language and version
        "License :: OSI Approved :: MIT License", # License used
        "Operating System :: OS Independent", # Specifies that the code is OS-independent
    ],
    python_requires='>=3.7',  # Minimum Python version required
    install_requires=[  # Dependencies required to install the package
      "streamlit",
      "google-generativeai",
      "python-dotenv"
    ],
)
