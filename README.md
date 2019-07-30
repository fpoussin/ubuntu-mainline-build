# ubuntu-mainline-build

### Dependencies
You need the kernel development packages
```
sudo apt install git build-essential kernel-package fakeroot libncurses5-dev libssl-dev bison flex
```

### Using

```
git submodule update --init
./build.py [version] -p <patch1> -p <patch2> -p <patchN>...
```
