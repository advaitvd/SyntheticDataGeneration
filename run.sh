#!/bin/bash

#lang=Kannada
#lang=Malayalam
#lang=Telugu
#lang=Tamil
#lang=Gujarati
#lang=Hindi
#lang=Marathi
#lang=Bengali
lang=Marathi

python chatGPT.py Data/Input/$lang/ $lang;

for domain in $(ls Data/Input/$lang/);
do 
	./prepare.sh Data/Input/$lang/$domain Data/Output/$lang/$domain;
done
