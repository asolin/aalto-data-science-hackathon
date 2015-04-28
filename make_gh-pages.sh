#!/bin/bash

GIT="git --work-tree=."

git checkout gh-pages         && \
rm -rf TEMP                   && \
mkdir TEMP                    && \
cd TEMP                       && \
$GIT checkout gh-pages -- .   && \
$GIT checkout master -- site  && \
\cp -r site/* ./              && \
rm -rf site                   && \
$GIT add .                    && \
$GIT commit -a                && \
$GIT push                     && \
cd ..                         && \
rm -rf TEMP                   && \
git reset --hard              && \
git checkout master

