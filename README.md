# Readme Reviver

Welcome to Readme Reviver!

Readme files are crucial for software projects, but keeping them updated is tough. That's where Readme Reviver comes in. It's a tool that automatically detects outdated parts of your readme by analyzing GitHub commits.

The goal? To make readme maintenance easier, ensuring documentation stays relevant and informative as project evolves.

## Installation

### Clone this Repository

- Using Git
Open your terminal and run the following command:

        git clone https://github.com/teJab-2610/ReadMeRevive.git

- Using Download ZIP
    - Go to the GitHub page of the repository.
    - Click on the green Code button.
    - In the dropdown menu, select Download ZIP.

Now navigate to this folder and open a terminal .

### Dependencies
The backend runs using **Flask**, you need a few key packages like Gensim, Pandas, PyDriller.

Before you set up the backend, you might need to install dependencies just as shown below;

    python -m pip install -r requirements.txt   

This step is very important to make the project work! please make sure you get correct keys and set up everything correctly.

#### Frontend/Keys.js
    # Use your own Github API key 
    const token = ""
    export default token; 

#### Server/Keys.py
    #Use your Gemini API Key here
    GEMINI_API_KEY = ""

In order to use this extension, you need to start the backend server which runs on your localhost,

**Run this command :**

    cd Server
    python backend.py

### Setting up the frontend:

- Open the extension list in your browser settings: [chrome://extensions](chrome://extensions)/[brave://extensions](brave://extensions)/[edge://extensions](edge://extensions)
- Enable **Developer mode**
- Click on **Load unpacked** and select the folder named **"Frontend"** containing the extension files.
- The extension should now appear in the list of installed extensions.


## Usage :
- **Start the Backend Server**: Execute the command provided above to initiate the backend server.
- **Enable the Extension**: If not already enabled, access your browser settings and enable the extension.
- **Navigate to Repository**: Proceed to the repository requiring documentation suggestions.
- **Access Documentation Suggestions**:
  - Click on the "Revive" button located next to the "Readme" button.
  - Ensure that the backend server is running.
  - Processing may take some time; please be patient.
  - Once processing is complete, the suggested readme content will be displayed.

- **Review and Implement Suggestions**:
  - At the end of each line, you'll see red dots.
  - Hover over them to view the suggestions.
  - Copy the suggested lines to your README file.
    
### This is how you enhance your poorly documented Repository by reviving their dead README files...
