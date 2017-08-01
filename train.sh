#!/bin/bash

set -e

echo "=> Training: Pride and Prejudice"
curl -XPUT -d@samples/pride-prejudice.txt "http://localhost:8000/train/pride-and-prejudice" >/dev/null


echo "=> Training: Alice's Adventures in Wonderland"
curl -XPUT -d@samples/alice-in-wonderland.txt "http://localhost:8000/train/alice-in-wonderland" >/dev/null


echo "=> Training: Adventures of Huckleberry Finn"
curl -XPUT -d@samples/huckleberry-finn.txt "http://localhost:8000/train/huckleberry-finn" >/dev/null


echo "=> Training: The Adventures of Tom Sawyer"
curl -XPUT -d@samples/tom-sawyer.txt "http://localhost:8000/train/tom-sawyer" >/dev/null
