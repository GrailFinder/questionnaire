#!/bin/bash
set -x
if [ $TRAVIS_BRANCH == 'master' ] ; then
    # Initialize a new git repo in _site, and push it to our server.
    git init
        
    git remote add deploy "grail@159.65.124.54:/var/www/ankete"
    git config user.name "Travis CI"
    git config user.email "GrailFinder+travisCI@gmail.com"
    
    git add .
    git commit -m "Deploy"
    git push --force deploy master
else
    echo "Not deploying, since this branch isn't master."
fi