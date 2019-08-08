#!/usr/bin/python3

import requests
import os
import argparse
from subprocess import run, PIPE, STDOUT

parser = argparse.ArgumentParser()
parser.add_argument("version", type=str)
parser.add_argument("-p", "--patch", type=str, action='append', nargs='*', help="Extra patch to apply. Can be used multiple times")
parser.add_argument("-n", "--nobuild", action='store_true', help="Don't build")
args = parser.parse_args()

patch_folder = "patches-{}".format(args.version)
linux_dir = os.getcwd() + '/linux'
env = os.environ.copy()

if not os.path.exists(patch_folder):
  os.mkdir(patch_folder)

def get_sources(ver):
  r = requests.get("https://kernel.ubuntu.com/~kernel-ppa/mainline/v{}/SOURCES".format(ver))

  if r.status_code != 200:
    print("Kernel version not found")
    raise NameError

  sources = r.text.strip().split('\n')
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
  run("git -C {0} checkout v{1}".format(linux_dir, ver), shell=True, check=True)

def patch(version, patch):
  for r, d, f in os.walk(patch_folder):
    for file in sorted(f):
      print(file)
      with open(os.path.join(r, file), 'r') as data:
        run("git apply ../{}".format(os.path.join(r, file)), cwd=linux_dir, shell=True, check=True)

  for p in patch:
    p = p[0]
    print(p)
    run("git apply ../{}".format(p), cwd=linux_dir, shell=True, check=True)

def config():
  run("cp /boot/config-`uname -r` .config", cwd=linux_dir, shell=True)
  run("nice make olddefconfig", cwd=linux_dir, shell=True, env=env, check=True)
  run("scripts/config --disable DEBUG_INFO", cwd=linux_dir, shell=True, env=env, check=True)

def build():
  run("nice make -j `nproc` deb-pkg LOCALVERSION=-mainline", cwd=linux_dir, shell=True, env=env, check=True)

get_sources(args.version)
checkout_branch(args.version)
patch(args.version, args.patch)
config()

if not args.nobuild:
  build()
