<!-- https://www.markdownguide.org/basic-syntax/ Markdown syntax sheet -->

# 4JCanvasDocs

*This extensive e-text outlines the current code and process for 4J School District's LMS and other coding processes as they relate to Canvas LMS, Google API, and other services. This document assumes the reader has a basic understanding of code principles and Python basics as well as some familiarity with REST API or the like.*  

## Author ##
Written by: Nicholas Hadley, M.Ed. Digital Learning Platform Manager for 4J Schools in Eugene, Oregon.

**Useful Websites**  
- [Canvas API Docs](https://canvas.instructure.com/doc/api/all_resources.html)  
- [CanvasReadTheDocs](https://canvasapi.readthedocs.io/en/stable/)  
- [UFC Canvas Repo](https://github.com/ucfopen/canvasapi/tree/master)  
- [UFC Canvas Community](ucfopen.slack.com)  

## Getting Started
### Installation
The system in place currently relies on Visual Studio Code on a Mac device. In a Terminal window enter `pip3 --version` to ensure pip is installed. If pip3 is not installed run `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py` and then execute `python3 get-pip.py`. 

If *python3* is not installed, go to python.org to download the latest repository and install it to PATH on your machine per their instructions. 

#### Verify Installation 
Ensure that installation is complete and everything is up to date by opening a new Terminal window and running `python3 --version` and `pip3 --version` as before. Now you are ready to install VSCode from their [site](https://code.visualstudio.com/download).  
**Note** that's always a good idea to restart your machine to ensure all elements install and refresh properly. Occasionally you will need to run `pip3 install --upgrade pip` to keep things updated. 
Once all repositories are installed, open VS Code and try running some python script, ie `print(Hello World)`. Once Python is successfully installed and tested, open a terminal window and run `pip3 install canvasapi`. To update the package on your machine as needed, run `pip3 install --upgrade canvasapi`, periodically.

### Canvas Setup ###
You will need to be a Canvas Admin with *root* access. If you are unsure if you have the correct level of access navigate to your Canvas settings by clicking the *Admin* shield to the left, clicking on Eugene SD 4J, and going to settings in the bottom left. At the top of the page that loads, click on Admins. You should see your name listed with "Account Admin" underneath your name and email. **If** you do not have any of this, you need to speak with your Canvas CSM or other Account Admins to be added.  

Once your access has been verified, you will need to generate an [API Token](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89). It is entirely up to you if you want to set this token to expire or not. I recommend generating two tokens and using one for the beta instance and one for the live instance. This allows you to track better where changes are happening, in my opinion. Be sure to keep the token hidden and safe as it would allow anyone to use Canvas as though they were you, and furthermore make unlimited API calls. 

You will see in the [Scripts](Scripts.md) that there is a variable for the APILive and APIBeta, this follows this method so that we don't accidentally make changes to our life instance. You will simply verify the Key prior to running the script. 


## Contents ##
>
> - [Definitions ](Definitions.md)
> - [Scripts and Processes](Scripts.md)
> - 

