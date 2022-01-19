# How to contribute to Haystack-Ada

:tada: First off, thanks for taking the time to contribute! :tada:

### Did you find a bug?
* Ensure the bug was not already reported by searching on GitHub under [issues](https://github.com/BurritoZz/Haystack-Ada/issues)
* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/BurritoZz/Haystack-Ada/issues/new). Be sure to include a title and clear description, as much relevant information as possible, and a code sample, test case or set of instructions demonstrating the expected behaviour that is not occurring.

### Setting up your environment
There are several software requirements to be able to effectively develop Haystack-Ada.
First of all, Haystack-Ada is written using python 3.7.6, so for the best compatibility, it's recommended to install this specific version of python.
Then there are a few dependencies:

#### libadalang
libadalang is already included in most installations of GNATStudio, but outside of GNATStudio you won't be able to import that package into your programming environment.
This makes testing Haystack-Ada impossible without a system-wide installation of libadalang. Therefore, it's highly recommended to install libadalang by either compiling it from source or installing it using a binary provided by AdaCore.

#### pylint and black
We use pylint and black to style and lint our code. To ensure that your code passes the linting and codestyle checks, make sure to install pylint and black to style your code.

#### pytest
Pytest is the module we use to test our code. To be able to execute the unit tests incleded in our codebase, it is recommended to install pytest.

#### GPS.py and gs_utils.py
Finally, GPS.py and gs_utils.py are two modules that are imported by haystack_plugin.py. These are internal modules provided by GNATStudio which can not be imported outside of GNATStudio. Because of this, you will likely encounter some errors because python is unable to locate these modules.
To solve this, you can source these files yourself:

GPS.py can be found in <prefix>/share/gnatstudio/support/ui/GNATSTudio_doc/\_\_init\_\_.py. Simply move the \_\_init\_\_.py file to your repository and rename it to GPS.py
gs_utils.py can be found in <prefix>/share/gnatstudio/support/core/gs_utils/\_\_init\_\_.py. Once again, move \_\_init\_\_.py to your repository and rename it to gs_utils.py
In both these cases <prefix> refers to the GNATStudio install directory.
 
### Submitting changes
* Before doing anything, if you're submitting a code change, make sure to run black on your repository to make sure your code conforms to our code styling.
* Please send a [Github Pull Request to Haystack-Ada](https://github.com/BurritoZz/Haystack-Ada/pull/new/main) with a clear list of what you've done (read more about [pull requests](help.github.com/pull-requests/)).
* When you send a pull request containing code changes, we will love you forever if you include a pytest test case demonstrating the change in behaviour.

### Coding conventions
* We format our code to satisfy pylint and black.
  * To satisfy black, you can run black on your local repository to format the code automatically.
  * For pylint, you'll need to format the code manually.
