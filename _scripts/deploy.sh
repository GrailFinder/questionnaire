#!/bin/bash
set -x
if [ $TRAVIS_BRANCH == 'master' ] ; then
    # Initialize a new git repo in _site, and push it to our server.
    git init
        
    git remote add deploy "deploy@159.65.124.54:/var/www/ankete"
    git config user.name "Travis CI"
    git config user.email "GrailFinder+travisCI@gmail.com"
    ls -la
    git add .
    git commit -m "Deploy"
    git fetch --unshallow upstream
    git push --force deploy master
else
    echo "Not deploying, since this branch isn't master."
fi