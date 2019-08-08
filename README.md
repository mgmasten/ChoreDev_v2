# ChoreDev

## Development Environment

1. Download Python 3.6.5
2. Download latest stable release of Node.js
3. Clone the repository using `git clone https://github.com/jonnylin13/ChoreDev/`
4. Run a `pipenv install` and an `npm install` in the server and client folders respectively
5. If you can build the Angular project or run `pipenv run python server/api.py` then you're good

## Build Process

* Python just needs to be tested (no build)

`pipenv run python server/test.py`
`pipenv run python server/api.py`

* Angular project needs to be tested then built
`ng test`
`ng build --prod`