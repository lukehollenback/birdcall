# Birdcall

![Status: Stable & Ongoing](https://img.shields.io/badge/status-Stable%20&%20Ongoing-green.svg)

A collection of Python scripts for serverless Twitter bots. Leverages
[Tweepy](https://www.tweepy.org/) and other techniques.

## Setup

This project uses Python Virtual Environments for development and deployment. This makes it
possible to install packages using `pip` specifically for this project without affecting the rest
of the host system.

1. Ensure that `pip` (a.k.a. `python3-pip`) and `venv` (a.k.a. `python3-venv`) are installed using
   your system's package manager.
2. Instantate a new virtual environment using `python -m venv env` from within your clone of this
   project. This will create a new virtual environment inside of a new `env/` directory. You can
   activate this environment by using `source ./env/bin/activate`, which will cause all usages of
   `python` and `pip` to redirect to the versions installed in the environment.
3. Install the project's dependencies using `pip -r requirements.txt`. Make sure that your virtual
   environment is activated when you do this.
