#!/usr/bin/python3

import argparse
import os

parser = argparse.ArgumentParser(prog="user creation")
parser.add_argument('login')
parser.add_argument('password')
args = parser.parse_args()

with open("data/passwords.txt", "a") as out:
	out.write(f"{args.login}:{args.password}\n")

dir = f"data/users/{args.login}"
os.makedirs(dir)
with open(f"{dir}/account.ini", "w") as out:
	out.write("""
[user]
email =
projects =
""")

