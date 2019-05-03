#!/bin/bash

cd frontend
if [ $? = 0 ]; then
    npm update
    npm install
    npm build
    cd ..
    tar -xzf frontend.tar.gz frontend/dist
fi


