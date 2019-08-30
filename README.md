# ubuntu-mainline-build

### Dependencies
You need the kernel development packages
```
sudo apt install git build-essential kernel-package fakeroot libncurses5-dev libssl-dev bison flex
```

### Using

```
git submodule update --init # This takes a while
./build.py [version] -p patches/*.patch -p <some_other_patch>...
```
