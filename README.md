# Ankete [![Build Status](https://travis-ci.org/GrailFinder/questionnaire.svg?branch=dev)](https://travis-ci.org/GrailFinder/questionnaire)

Service where users can create inquiries and track answers on them.
One does not need to became user in order to pass a questionnaire.

## Project structure

### Questmaker: service that contains api for creation inquiries, questions, answers and showing them to user
- api structure
- postgres
- does it need user registration?

### ResultKeeper: service that keeps result (answers). Can recieve and return answers through rpc (nameko).
- mongo db
- logic where data gets scaled cleaned in proper form
- some analysis (maybe will be moved in analyser service)


### Swagger: documentation (for questmaker)
- http://159.65.124.54:8080/

### Services registration and communication:
- [nameko](https://nameko.readthedocs.io/en/stable/) rpc calls between services
- rabbitmq


No front yet implemented... Feel free to give any help with it.