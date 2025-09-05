Print-Opcodes


Linux Commands Tried: 

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

Git Commands Tried: 

git config -global user.name "VimaleshTK"
git config -global user.email "vimaleshtk1@gmail.com"
git clone https://github.com/riscv/riscv-opcodes
git add .
git commit -m "upload"
git push 



