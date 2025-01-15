# Import the Streamlit library for creating web applications.
import streamlit as st
# Import the Google Generative AI library for interacting with Gemini models.
import google.generativeai as genai
# Import the JSON library for working with JSON data.
import json
# Import the regular expression library for pattern matching.
import re
# Import the datetime library for working with dates and times.
import datetime

# --- Begin: Configuration and Setup ---

# Accessing the API key from Streamlit's secrets management.
# This is a secure way to store and access sensitive information like API keys.
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Configuring the Streamlit page layout.
# 'page_title' sets the title that appears in the browser tab.
# 'page_icon' sets the icon that appears in the browser tab.
# 'layout' set to 'wide' to use the full width of the screen
st.set_page_config(page_title="🤖 Gemini2 PowerShell Command Gen", page_icon="🤖", layout="wide")

# --- End: Configuration and Setup ---

# --- Begin: Function Definitions ---

# Defining a function to send a message to the AI model and retrieve its response.
def send_message_to_model(message, model_name, temperature, max_tokens):
    """
    This function sends a message to a specified AI model (Google Gemini) 
    and returns the model's text response.

    Parameters:
        message (str): The message (prompt) to be sent to the AI model.
        model_name (str): The name of the Gemini model to be used (e.g., "gemini-2.0-flash-exp").
        temperature (float): A value between 0 and 1 controlling the randomness of the model's output.
        max_tokens (int): The maximum number of tokens (words/parts of words) the model is allowed to generate.

    Returns:
        str: The text response from the AI model, or None if an error occurs.

    Detailed Breakdown:
        1. Error Handling: A try-except block is used to catch any exceptions that might occur during the interaction with the AI model.
        2. Model Configuration: The generation configurations (temperature, top_p, top_k, mime type, max tokens) are defined.
           - temperature: Controls the randomness of the output. Lower values make the output more deterministic.
           - top_p & top_k: These parameters control the diversity of the output.
           - response_mime_type: Specifies that the expected response is plain text.
           - max_output_tokens: Limits the size of the response.
        3. Model Initialization: A GenerativeModel object is created with the specified model name and generation configurations.
        4. Chat Initialization: A new chat session is started with an empty history.
        5. Sending Message: The message is sent to the model and the response is stored.
        6. Response Handling: The text part of the model's response is returned.
        7. Error Handling: If an error occurs during any step, an error message is displayed in the Streamlit app, and None is returned.
    """
    try:
        # Configuration for the AI model's generation behavior.
        GENERATION_CONFIG = {
            "temperature": temperature, # Controls the randomness of the model's output.
            "top_p": 0.8, # Controls the nucleus sampling, a method to control diversity of the generated text.
            "top_k": 40, #  Controls the number of tokens from which the model can choose the next one.
            "response_mime_type": "text/plain", # Specifies that we expect a plain text output.
            "max_output_tokens": max_tokens, # Limits the maximum size of the response from the AI model.
        }
        # Initializes the Gemini AI model with the specified model name and generation configurations
        MODEL = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
        )
        
        # Starts a new chat session with the model (history is empty).
        # Sends the user's message to the model and retrieves the response.
        response = MODEL.start_chat(history=[]).send_message(message)
        # Returns the text of the model's response.
        return response.text
    # Handles exceptions during communication with the AI model.
    except Exception as e:
        # Displays an error message in the Streamlit app if an exception occurs.
        st.error(f"❌ Error communicating with the AI: {e}")
        # Returns None to indicate that the message sending failed.
        return None

def generate_powershell_command(prompt_base, detail_level, script_type, security_level, model_name, temperature, max_tokens, prompt_detail, encoding, add_header, add_error_handling, log_level):
    """
    This function generates a PowerShell command by sending a detailed prompt to the AI model based on user-defined settings.

    Parameters:
        prompt_base (str): The base description of the desired PowerShell command.
        detail_level (str): The level of detail in the generated command (e.g., "More detailed", "Default", "More concise").
        script_type (str): The type of the PowerShell script ("More automatic", "More interactive").
        security_level (str): The security level of the generated command ("High", "Medium", "Low").
        model_name (str): The name of the Gemini model to use.
        temperature (float): The temperature for the AI model.
        max_tokens (int): The maximum number of tokens in the model's response.
        prompt_detail (str): The level of detail in the prompt sent to the AI model ("More descriptive", "Default", "Concise").
        encoding (str): The text encoding for the generated script.
        add_header (bool): Indicates whether to add a header to the generated script.
        add_error_handling (bool): Indicates whether to add error handling to the script.
        log_level (str): The level of logging in the generated script ("Detailed", "Default", "Minimum").

    Returns:
        str: The generated PowerShell command in a string format, or None if an error occurs.

    Detailed Breakdown:
        1. Prompt Construction: Constructs a detailed prompt string that includes:
           - Instructions to act as a PowerShell expert.
           - The base command description provided by the user.
           - The detail level, script type, security level, and prompt detail selected by the user.
           - Detailed guidelines on the response format (Markdown, code blocks, etc).
           - Specific instructions regarding how the command should handle files and output.
           - Emphasis on using advanced PowerShell practices and ensuring security.
           - Considerations about the default operating system and PowerShell version.
           - Logging level and error handling settings.
           - Importance of generating the most complete, detailed, and efficient code possible.
           - Instruction to use contextual information and incremental reasoning.
        2. Sending the Prompt: Sends the constructed prompt to the AI model using the 'send_message_to_model' function.
        3. Response Handling: Returns the response received from the AI model.
    """
    #  Constructing the prompt for the AI model using f-strings for easy variable insertion.
    prompt = f"""
    You are a Powershell expert. Your task is to generate a single Powershell command based on the following description:

    **Goal:** Create the most complete, detailed, and efficient Powershell command possible, considering all variables and scenarios.

    **Command Description:** {prompt_base}

    **Detail Level:** {detail_level}
    **Script Type:** {script_type}
    **Security Level:** {security_level}
    **Prompt Detail Level**:{prompt_detail}

    **Response Format:**
    - Respond in Markdown format, including a Powershell code block with its original formatting, without line breaks.
    - The Powershell code block must be delimited by ```powershell and ```.
    - Do not include comments, explanations, or any other text outside the code block.
    - The Powershell code must maintain its full vertical formatting, respecting indentation and line breaks.
    - The code must be realistic, using real-world examples, data, and situations.
    - Explore different approaches, techniques, and advanced practices.
    - If generating a command with a chain of commands, do not use semicolons at the end or beginning.
    - If necessary, use the pipe "|" to chain commands.
    - Do not use any special formatting in the result, only the code.
    - If the description asks to create a file, the command should create the file directly in the file system and not use a screen output for this.
    - If the description asks to read a file, the command should read the file directly from the file system and not use a screen input for this.
    - Use advanced PowerShell resources, such as pipelines, variables, functions, and script blocks, when necessary.
     - The default operating system is Windows Server 2016, and the default Powershell version is 7, unless the user specifies otherwise.
     - Make sure that the generated command is secure and follows the best Powershell practices.

    **Log Level**:{log_level}
    **Error Handling**:{add_error_handling}

     **Important:**
    - Generate only one command at a time.
    - Create the longest, most complete, and detailed code possible.
    - Consider all the details of the request, expanding the response and improving the command.
     - Use contextual information (such as PowerShell version and operating system) to generate the command.
     - If possible, use incremental reasoning to add improvements, expansions, and considerations to your code.
     - Use the history of the conversations so that the response is incremental.

    """
    # Calls the send_message_to_model function to get the AI model's response, then returns that response
    response = send_message_to_model(prompt, model_name, temperature, max_tokens)
    return response

def parse_and_save_ps1(ai_code, short_title, encoding, add_header):
    """
    Parses the markdown content from the AI response, extracts the PowerShell code,
    and saves it as a .ps1 file.

    Parameters:
        ai_code (str): The AI model's response, expected to contain PowerShell code within Markdown code blocks.
        short_title (str): A short title for the command, used to generate the filename.
        encoding (str): The text encoding for the file (e.g., "utf-8", "ansi").
        add_header (bool): Indicates whether to add a header to the file.

    Returns:
        tuple: A tuple containing the filename of the saved .ps1 file and the PowerShell code.

    Detailed Breakdown:
        1. Code Extraction:
           - Uses regular expressions to search for the PowerShell code block (delimited by ```powershell and ```) within the AI's response.
           - If a match is found, the code is extracted from the matched group and any leading/trailing white spaces are removed using strip().
           - If no code block is found, the entire response is considered as the PowerShell code.
        2. Filename Generation:
           - Constructs the filename based on the 'short_title' using an f-string and adds a '.ps1' extension.
        3. Header Addition (Conditional):
           - If 'add_header' is True, it generates a header comment block including the current date and the author's name
           - Prepends the header to the PowerShell code
        4. File Saving:
           - Opens a file with the generated filename in write mode ('w') with the specified encoding.
           - Writes the extracted (or modified) PowerShell code to the file.
        5. Return Values:
           - Returns the filename and the extracted PowerShell code.
    """
    # Uses a regular expression to find the PowerShell code block
    match = re.search(r'```powershell\s*(.*?)\s*```', ai_code, re.DOTALL | re.IGNORECASE)
    if match:
        # Extracts the code from the matched group and removes any leading/trailing spaces.
        ps1_code = match.group(1).strip()
    else:
        # If no code block is found, considers the entire response as the PowerShell code.
        ps1_code = ai_code.strip()

    # Constructs the filename using the short title.
    file_name = f"command_{short_title}.ps1"

    # Checks if the header should be added based on the add_header parameter.
    if add_header:
        # Gets the current date and time.
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Defines the header text.
        header = f"""
#===============================================================================
# Script Generated by Google Gemini 2 PowerShell Command Gen
# Date: {current_date}
# Author: Elias Andrade AKA Chaos4455
#===============================================================================
    """
        # Adds the header to the beginning of the code.
        ps1_code = header + ps1_code

    # Opens the file for writing, encoding it with the selected encoding.
    with open(file_name, "w", encoding=encoding) as f:
        # Writes the generated PowerShell code to the file.
        f.write(ps1_code)
    # Returns the filename and the generated PowerShell code
    return file_name, ps1_code

# --- End: Function Definitions ---

# --- Begin: Main Application Logic ---
def main():
    """
    Main function of the Streamlit application.

    Detailed Breakdown:
    1.  Title and Introduction: Sets the title of the app and adds an introductory markdown text
        using the Streamlit's title and markdown features.
        This includes a link to my GitHub page.
    2.  Layout Setup: Sets up a two-column layout to organize the page using st.columns. 
        This layout separates settings to the left and the main content area to the right.
    3.  Sidebar Configuration (Column 1):
        a.  Settings Header: Creates a header for the settings section.
        b.  AI Settings Expander: Creates a collapsible section for AI model configurations.
            i.   Model Selection: Allows user to choose the Gemini AI model via st.selectbox.
            ii.  Temperature Slider: Provides a slider for adjusting the temperature parameter of the AI, controlling creativity.
            iii. Max Tokens Input: Provides a numerical input for controlling the maximum length of the generated text by the AI.
        c.  Prompt Settings Expander: Creates a collapsible section for setting up the prompt.
            i.   Predefined Prompts Selection: Allows selection of pre-defined prompts.
            ii.  Prompt Detail: Allows selection of different level of prompt details.
        d.  PowerShell Settings Expander: Creates a collapsible section for PowerShell script configurations.
            i.   PowerShell Version Selection: Allows the user to select the target PowerShell version
            ii.  Operating System Selection: Allows the user to select the target operating system
            iii. Encoding Selection: Allows the user to select the encoding type for the generated file (.ps1).
            iv.  Header Addition Checkbox: A checkbox to include a header in the generated script, providing additional information.
            v.   Error Handling Checkbox: Option to include standard error handling practices in the generated code.
            vi.  Logging Level Selection: Allows the user to select the level of logging that will be used in the script.
            vii. Detail Level Selection: Allows the user to select the level of detail for the generated code.
            viii. Script Type Selection: Allows the user to select if the script should be more interactive or more automatic.
            ix.  Security Level Radio: Allow the user to select the security level of the generated script.
    4.  Main Content Area (Column 2):
        a.  Command Prompt Input: Creates a text input field where the user can describe their desired PowerShell command.
        b.  Preset Prompts: If the user selects a predefined prompt, the code updates the main prompt with the predefined prompt.
        c.  Generate Command Button: Creates a button that triggers the command generation process, 
           and if the user did not inform the command description, an error message is displayed.
        d.  Command Generation:
            i.   Starts a spinner animation to indicate that the AI is processing.
            ii.  Calls the generate_powershell_command function with all the user configurations to get the generated code from the AI.
            iii. If there is a code, displays the generated PowerShell code using st.code for syntax highlighting.
            iv.  Generates a short title based on the prompt description
            v.   Saves the generated PowerShell code as a .ps1 file using the parse_and_save_ps1 function,
            vi.  Provides a download button to allow the user to download the generated .ps1 file.
            vii.  If the AI model did not generate a command, an error message is displayed.
    5. Execution Guard: Ensures that main() is only called when the script is run directly.
    """
    # Sets the title of the Streamlit app.
    st.title("🤖 Gemini2 PowerShell Command Gen by [Elias Andrade](https://github.com/chaos4455)")
    # Adds an introductory markdown message.
    st.markdown("Create PowerShell commands easily and quickly! 🚀")
    # Adds a separator line using Markdown
    st.markdown("---")

    # --- Begin: Layout Setup ---
    # Sets up a two-column layout for the app.
    col1, col2 = st.columns([1, 3])
    # --- End: Layout Setup ---
    
    # --- Begin: Sidebar Configuration (Column 1) ---
    # Places all configuration widgets within the first column.
    with col1:
        # Adds a header for the settings section.
        st.header("⚙️ Settings")
        
        # --- Begin: AI Settings Expander ---
        with st.expander("✨ AI Settings"):
            # Dropdown to choose the AI model.
            model_name = st.selectbox("🤖 AI Model", ["gemini-2.0-flash-exp", "gemini-1.5-flash"], index=0, help="Choose the AI model.")
            # Slider to adjust the temperature.
            temperature = st.slider("🌡️ Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1, help="Adjust the AI's creativity.")
            # Number input for maximum tokens.
            max_tokens = st.number_input("📏 Max Tokens", min_value=128, max_value=8192, value=8192, step=128, help="Adjust the maximum size of the response.")
        # --- End: AI Settings Expander ---
            
        # --- Begin: Prompt Settings Expander ---
        with st.expander("📝 Prompt Settings"):
            # Dropdown for selecting predefined prompts.
            prompt_presets = st.selectbox("🎯 Predefined Prompts", ["None", "List files", "Manage processes", "Manage services"], index=0, help="Choose a predefined prompt.")
            # Dropdown for selecting the prompt detail.
            prompt_detail = st.selectbox("🧐 Prompt Detail", ["More descriptive", "Default", "Concise"], index=1, help="Defines the level of detail of the prompt")
        # --- End: Prompt Settings Expander ---

        # --- Begin: PowerShell Settings Expander ---
        with st.expander("🛠️ PowerShell Settings"):
            # Dropdown to select the PowerShell version.
            powershell_version = st.selectbox("🎛️ PowerShell Version", ["7", "5.1"], index=0, help="Choose the PowerShell version.")
            # Dropdown to select the operating system.
            operating_system = st.selectbox(
                "💻 Operating System",
                [
                    "Windows Server 2022", "Windows Server 2019", "Windows Server 2016",
                    "Windows Server 2012 R2", "Windows Server 2012", "Windows Server 2008 R2",
                    "Windows Server 2008", "Windows 11", "Windows 10", "Windows 8.1", "Windows 8", "Windows 7", "Other"
                ],
                index=2, help="Choose the target operating system."
            )
            # Dropdown to select the encoding of the .ps1 file.
            encoding = st.selectbox("🔤 Encoding", ["utf-8", "ansi"], index=0, help="Choose the encoding of the .ps1 file.")
            # Checkbox to add a header to the .ps1 file.
            add_header = st.checkbox("📜 Add Header", value=True, help="Add a header with information in the .ps1 file.")
            # Checkbox to add error handling to the script
            add_error_handling = st.checkbox("🛡️ Error Handling", value=True, help="Add standard error handling to the script.")
            # Dropdown to select the level of logging.
            log_level = st.selectbox("🗂️ Logging Level", ["Detailed", "Default", "Minimum"], index=1, help="Defines the detail level of logs.")
            
            # Dropdown to select the detail level of the command.
            detail_level = st.selectbox("Detail Level", ["More detailed", "Default", "More concise"], index=1)
            # Dropdown to select the script type.
            script_type = st.selectbox("Script Type", ["More automatic", "More interactive"], index=0)
            # Radio buttons to select the security level.
            security_level = st.radio("Security Level", ["High", "Medium", "Low"], index=1)
        # --- End: PowerShell Settings Expander ---
    # --- End: Sidebar Configuration (Column 1) ---

    # --- Begin: Main Content Area (Column 2) ---
    # Places the main UI elements in the second column.
    with col2:
        # Text input for the user to describe the PowerShell command.
        prompt_base = st.text_input("Describe the PowerShell Command:", placeholder="Ex: List all running processes", key="prompt_base")

        # Checks if a preset is selected
        if prompt_presets != "None":
            # If there is a previous prompt, concats it with the preset, otherwise, it replaces the default prompt.
            if prompt_base:
               prompt_base = f"{prompt_presets} , {prompt_base}"
            else:
               prompt_base = prompt_presets;
        # Button to trigger the generation of the PowerShell command.
        if st.button("✨ Generate PowerShell Command"):
            # Validates that the command description is filled
            if not prompt_base:
                # Displays an error message if the command description is empty
                st.error("⚠️ Please enter a command description.")
                # Exits the execution to prevent an invalid request to the AI.
                return

            # Uses a spinner to indicate that the command is being generated.
            with st.spinner("⏳ Generating command..."):
                # Calls the generate_powershell_command to generate the command
                ai_code = generate_powershell_command(
                   prompt_base, 
                   detail_level, 
                   script_type, 
                   security_level,
                   model_name,
                   temperature,
                   max_tokens,
                   prompt_detail,
                   encoding,
                   add_header,
                   add_error_handling,
                   log_level
                   )

                # Checks if the AI code is valid
                if ai_code:
                    # Displays the generated command with syntax highlighting.
                    st.markdown("### ✅ Generated Command:")
                    st.code(ai_code, language="powershell")

                    # Creates a short title based on the command description
                    short_title = prompt_base[:30].strip().replace(" ", "_").lower()
                    # Parses the code and saves the PS1 file.
                    file_name_ps1, ps1_code = parse_and_save_ps1(ai_code, short_title, encoding, add_header)

                    # Download button for the generated PS1 file.
                    st.download_button(
                        label="⬇️ Download Command (.ps1)",
                        data=ps1_code,
                        file_name=file_name_ps1,
                        mime="application/powershell",
                    )
                else:
                    # Displays an error if the command generation fails.
                    st.error("❌ Error generating the command. Check the connection with the AI and try again.")
    # --- End: Main Content Area (Column 2) ---
    
# --- End: Main Application Logic ---

# --- Begin: Execution Guard ---
# Checks if the script is the main one being executed and then calls the main function.
if __name__ == "__main__":
    main()
# --- End: Execution Guard ---
