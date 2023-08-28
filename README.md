# magnet_cfu for 17 lab.
Project for controlling the magnet power supply

# Tools

![](https://img.shields.io/badge/PyQt5-blue?style=for-the-circle)
![](https://img.shields.io/badge/pyqt5--tools-blueviolet?style=for-the-circle) 
![](https://img.shields.io/badge/zhinst.toolkit-yellow?style=for-the-circle)
![](https://img.shields.io/badge/pyqtgraph-orange?style=for-the-circle)

# PyQt5
The GPL version of PyQt5 can be installed from PyPI:

    pip install PyQt5

``pip`` will also build and install the bindings from the sdist package but
Qt's ``qmake`` tool must be on ``PATH``.

The ``sip-install`` tool will also install the bindings from the sdist package
but will allow you to configure many aspects of the installation.

# pyqt5-tools
    yourenv/Scripts/pip.exe install pyqt5-tools~=5.15
You will generally install pyqt5-tools using ``pip install``. In most cases you should be using [virtualenv](https://virtualenv.pypa.io/en/stable/) or [venv](https://docs.python.org/3/library/venv.html) to create isolated environments to install your dependencies in. The above command assumes an env in the directory ``yourenv``. The ``~=5.15`` specifies a [release compatible with](https://www.python.org/dev/peps/pep-0440/#compatible-release) 5.15 which will be the latest version of pyqt5-tools built for [PyQt5](https://pypi.org/project/PyQt5/) 5.15. If you are using a different PyQt5 version, specify it instead of 5.15. PyPI keeps a list of [all available versions](https://pypi.org/project/pyqt5-tools/#history).

# zhinst.toolkit
Install the package with pip:

    pip install zhinst-toolkit
For a full documentation see [here](https://docs.zhinst.com/zhinst-toolkit/en/latest).

# pyqtgraph
From PyPI
Last released version:

    pip install pyqtgraph
Latest development version:

    pip install git+https://github.com/pyqtgraph/pyqtgraph@master
From conda
Last released version:

    conda install -c conda-forge pyqtgraph
To install system-wide from source distribution:

    python setup.py install
Many linux package repositories have release versions.
To use with a specific project, simply copy the PyQtGraph subdirectory anywhere that is importable from your project.

**Documentation**
The official documentation lives at [pyqtgraph.readthedocs.io](https://pyqtgraph.readthedocs.io/)

The easiest way to learn PyQtGraph is to browse through the examples; run `python -m pyqtgraph.examples` to launch the examples application.
