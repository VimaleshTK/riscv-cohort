# Print-Opcodes

## Objective
The goal of this assignment is to:    

 • Parse the YAML files in opcodes/.  
 • Extract and list all defined instruction names (mnemonics).  
 • Print them sorted alphabetically.  
 • Save the list to all_opcodes.txt.  

## Steps Followed
### 1. Clone the RISC-V Opcodes Repository
```
git clone https://github.com/riscv/riscv-opcodes.git
cd riscv-opcodes`
```
### 2. Setup Python Environment
```
pip3 install pyyaml
```
### 3. Located YAML Files
The YAML instruction definition files are in the opcodes/ folder.

### 4. Wrote the Script print_opcodes.py
This Python script:

- Opens all YAML files in the opcodes/ directory.  
- Extracts all instruction names (mnemonics).  
- Sorts them alphabetically.  
- Saves the results into all_opcodes.txt  

Run:   

```
python3 print_opcodes.py
```

### 5. Output
The sorted list of mnemonics is saved into the file:  
all_opcodes.txt


## Linux Commands Tried: 

```
mkdir riscv-opcodes-assignment
 
cd riscv-opcodes-assignment
 
git clone https://github.com/riscv/riscv-opcodes
 
python3 -m pip install --user pyyaml

python3 print_opcodes.py

grep "^\$" all_opcodes.txt

grep "^\." all_opcodes.txt

wc -l all_opcodes.txt

head all_opcodes.txt

tail all_opcodes.txt

cp "print_opcodes.py" ../../print-opcodes

cp "all_opcodes.txt" ../../print-opcodes

cd ../../print-opcodes
```

## Git Commands Tried: 

```
git config -global user.name "VimaleshTK"

git config -global user.email "vimaleshtk1@gmail.com"

git clone https://github.com/riscv/riscv-opcodes

git add .

git commit -m "upload"

git push
```



