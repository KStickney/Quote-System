# Business Quote System
This is a fully functioning customizable quoting system. It is currently being used by a small business in North Carolina.

# Making Windows Executable
In order to work properly on a Windows computer, an .exe file has to be made. The .exe can be made with the ```pyinstaller``` module, which can be installed with pip:
~~~
pip install pyinstaller
~~~
To create the executable, navigate to the directory in the terminal. Then run the following command:
~~~
pyinstaller Quote_System.py
~~~
The other source code (data/ fonts/ images/ pdf/ styles/ stylesheets/ web_scraping/ CustomClasses.py database.py) should then be copied into the ```dist``` file made by pyinstaller in the directory.