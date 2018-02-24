# Ankete (croatian for questionnarie) [![Build Status](https://travis-ci.org/GrailFinder/questionnaire.svg?branch=dev)](https://travis-ci.org/GrailFinder/questionnaire)

Service where users can create inquiries and track answers on them.
One does not need to became user in order to pass a questionnaire.

## Project structure (hooray for microservices)

### Questmaker: service that contains api for creation inquiries, questions, answers and showing them to user
- api structure
- sql db (postgres coz its the best)
- does it need user registration?

### ResultKeeper: service that keeps result (answers). Can recieve and return answers through rpc (nameko).
- mongo db
- logic where data gets scaled cleaned in proper form
- some analysis (maybe will be moved in analyser service)

### Front: service about graphics and visuals
- charts.js?
- react.js?

### Swagger: documentation (for questmaker)
- http://104.236.251.23:8080/

### Services registration and communication:
- nameko (https://nameko.readthedocs.io/en/stable/)
- rabbitmq
