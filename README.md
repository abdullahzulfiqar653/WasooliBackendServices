# BoilerPlateDjango

**clone project using HTTPS or SSH**

**_HTTPS:_**

```
git clone https://github.com/abdullahzulfiqar653/SimpleBoilerplateDjango.git
```

**_SSH:_**

```
git clone git@github.com:abdullahzulfiqar653/SimpleBoilerplateDjango.git
```

**Make and activate environment for the project using commands given**

**1: making environment and installing dependencies**
**_Install python 3.11.7 on local machine https://www.python.org/_**

**i: installing poetry:**

**_windows:_**

```
pip install poetry
```

**_macOS/Linux:_**

```
pip3 install poetry
```

**ii: installing package:\_**
open the terminal in SimpleBoilerplateDjango and run to make virtualenv and install packages in that
**_macOS/Linux/Windows:_**

```
poetry install
```

**ii: activating environment:\_**
after installation complete and execute the following command
**_macOS/Linux/Windows:_**

```
poetry shell
```

**3: Setup .env to load environment variables**

add .env file in the main source directory at the same level as manage.py and .env.example and set all variables using the help of .env.example

**5: Run the Application and API in the terminal or in vs code terminal**
Make sure to activate the virtual environment and you are in SimpleBoilerplateDjango directory
_​use command to run Django-server:_

```
python manage.py runserver
```
