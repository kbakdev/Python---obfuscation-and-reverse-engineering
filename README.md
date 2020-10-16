# Python---obfuscation-and-reverse-engineering

python3
## The code is executed in two steps:
1. Rewriting the code and recording jump positions, as well as creating a map of the original addresses of the instructions to the addresses valid after the changes.
2. Correction of parameters of the noted jump instructions using the created map.
