# phasterWeb

**ReadMe- Phaster**

Open up the “Terminal” application, and copy and paste these commands. Do so line by line, hitting enter after every line ends.
You will see output text and lots of progress bars in the terminal window; that’s good, it means installation is working!

**Whenever it asks for your password, your typing will be hidden. This is for security's sake. You are, in fact, typing.**

- Run the following commands:
    - ###### /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    - ###### brew install curl
    - ###### curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    - ###### python get-pip.py

If you’re having trouble, see: https://pip.pypa.io/en/stable/installing/


- Next (still in the terminal), enter these commands:
    - ###### cd
    - ###### sh -c "$(curl -fsSL ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
- When prompted, enter “y”

- Next, you need to create your bash file.
- Type these commands into the terminal.
    - ###### cd
    - ###### vi .bash_profile

- A new file will be created. To write in this file, type “i” and then paste these lines. THIS IS NOT HE ACTUAL API KEY. EMAIL ALICE (alicecastillo@wustl.edu) OR ALEX FOR THE API KEY, AND REPLACE THIS FAKE API KEY WITH THE ONE PROVIDED TO YOU:
    - ###### # NCBI API Key for Entrez
    - ###### export NCBI_API_KEY=12345678910abcdefg123
- Once you have pasted those lines, hit the "ESC" key (top left).
- Then type ":wq", then hit enter. This means "save and quit".

Now when you run the program, you will be using the API key provided to the Bradley lab! This lets the NCBI database know that you are a registered user, and increases the amount of calls (requests for data) you are allowed to make.


**New to Terminal’s Command Line Interface (CLI)? No problem!**

- Open “Finder” and navigate to your downloaded phaster-project folder.  If you just began this process, it will most likely be in your Downloads , Desktop, or user folder (whatever your Mac username is, with a house icon next to it). 
- Click on the phasterWeb folder. There should be another phasterWeb folder inside of it; right-click on THIS phasterWeb folder, and select the option “New Terminal Tab at Folder”
- This will take you to a terminal window. Once you are there, type this command:
    - ###### ls -l
    - If you see several different files and folders, including “requirements.txt” and “manage.py” you are in the correct folder!
    - ###### Pip install -r requirements.txt
    Once installation is finished, run this command to start your local app:
    - ###### python manage.py runserver
- If your app builds successfully, you will see a notice directing you to http://127.0.0.1:8000/
    - Open your go-to browser and navigate to this address. 
- When you are done using phaster, hit “CTRL+C” to power down the web app
- Enjoy phaster!
