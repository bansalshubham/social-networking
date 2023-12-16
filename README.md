# SOCIAL NETWORKING

[![Build Status](https://travis-ci.org/your-username/your-project.svg?branch=master)](https://travis-ci.org/your-username/your-project)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Django Apllication build on REST.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bansalshubham/social-networking.git
   ```

2. Navigate to the project directory:

   ```bash
   cd social-networking
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On Unix or MacOS:

     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run Test cases.

   ```bash
   python manage.py test backend_api.tests
   ```

7. Runserver

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

8. Access project at [http://0.0.0.0:8000](http://0.0.0.0:8000)

## Running with Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/bansalshubham/social-networking.git
   ```

2. Navigate to the project directory:

   ```bash
   cd social-networking
   ```

3. Build the Docker image:

   ```bash
   docker-compose build
   ```

4. Run the Docker container:

   ```bash
   docker-compose up
   ```

5. Access your project at [http://0.0.0.0:8000](http://0.0.0.0:8000)
