#!/bin/bash
set -x # Show the output of the following commands (useful for debugging)
    

# Import the SSH deployment key
openssl aes-256-cbc -K $encrypted_1f39af138ba1_key -iv $encrypted_1f39af138ba1_iv -in id_rsa.enc -out id_rsa -d
rm id_rsa.enc # Don't need it anymore
chmod 600 id_rsa
mv id_rsa ~/.ssh/id_rsa
ssh-add ~/.ssh/id_rsa
