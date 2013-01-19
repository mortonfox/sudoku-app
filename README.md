# sudoku-app

Sudoku Solver for Google App Engine.

## Introduction

This is a simple example web app that has been updated for HRD and Python 2.7. It takes a Sudoku puzzle as input in a text box and outputs the solution.

If Javascript is enabled in the browser, it uses AJAX to call the solver and retrieve the solution.

If Javascript is not enabled, it regenerates the page using a Django template with the solution added inline.

## Installation

1. Clone this repository.
1. In the Google App Engine admin console, create an application.
1. Edit app.yaml to set the application name to the name you chose in the previous step.
1. Run ```appcfg.py update ./``` to upload the source code.

## Demo

See http://sudoku-app.appspot.com/ for a live demo.
