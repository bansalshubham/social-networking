# SOCIAL NETWORKING

[![Build Status](https://travis-ci.org/your-username/your-project.svg?branch=master)](https://travis-ci.org/your-username/your-project)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Django Apllication build on REST.

## Table of Contents

- [Installation](#installation)
- [Running with Docker](#running-with-docker)
- [Limitations](#limitations)
- [Postman collection](#postman-collection)

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

## Limitations

1. Currently DRF Throtlling is used for API rate limiting. This rate limit per server basis.Hence it required changes to work on application level.
2. Add more logging
3. Need to use pagination in all GET API

## Postman collection

    social-networking.postman_collection.json
