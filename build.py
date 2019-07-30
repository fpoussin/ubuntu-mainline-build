#!/usr/bin/python3

import requests
import os
import argparse
from subprocess import run, PIPE, STDOUT

parser = argparse.ArgumentParser()
parser.add_argument("version", type=str)
parser.add_argument("-p", "--patch", type=str, help="Extra patches to apply")
parser.add_argument("-g", "--gcc", type=str, help="GCC version")
parser.add_argument("-n", "--nobuild", action='store_true', help="Don't build")
args = parser.parse_args()

patch_folder = "patches-{}".format(args.version)
linux_dir = os.getcwd() + '/linux'
env = os.environ.copy()

gcc = ''
if args.gcc:
  env["CC"] = gcc

print('Using', gcc)

if not os.path.exists(patch_folder):
  os.mkdir(patch_folder)

def get_sources(ver):
  sources = requests.get("https://kernel.ubuntu.com/~kernel-ppa/mainline/v{}/SOURCES".format(ver)).text.strip().split('\n')
  git = sources[0].split(' ')[0]
  patches = sources[1:]

  print('git repo:', git)
  print('patches:', patches)

  if not os.path.exists(linux_dir):
    run("git clone {0} {1}".format(git, linux_dir))

  for i in patches:
    patch_path = "{0}/{1}".format(patch_folder, i)
    if i == "" or os.path.exists(patch_path):
      continue
    url = "https://kernel.ubuntu.com/~kernel-ppa/mainline/v{0}/{1}".format(ver, i)
    patch = requests.get(url).text
    open(patch_path, 'w').write(patch)

def checkout_branch(ver):
  run("git -C {0} clean -fxd".format(linux_dir), shell=True)
  run("git -C {0} reset --hard".format(linux_dir, ver), shell=True)
  run("git -C {0} fetch --all --tags".format(linux_dir, ver), shell=True)
  run("git -C {0} checkout v{1}".format(linux_dir, ver), shell=True)

def patch(version, patch):
  for r, d, f in os.walk(patch_folder):
    for file in sorted(f):
      print(file)
      with open(os.path.join(r, file), 'r') as data:
        run("git apply ../{}".format(os.path.join(r, file)), cwd=linux_dir, shell=True)

  if patch:
    print(patch)
    run("git apply ../{}".format(patch), cwd=linux_dir, shell=True)

def config():
  run("cp /boot/config-`uname -r` .config", cwd=linux_dir, shell=True)
  run("nice make olddefconfig", cwd=linux_dir, shell=True, env=env)
  run("scripts/config --disable DEBUG_INFO", cwd=linux_dir, shell=True, env=env)

def build():
  run("nice make -j `nproc` deb-pkg LOCALVERSION=-mainline", cwd=linux_dir, shell=True, env=env)

get_sources(args.version)
checkout_branch(args.version)
patch(args.version, args.patch)
config()

if not args.nobuild:
  build()
