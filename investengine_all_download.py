#!/usr/bin/env python3

from urllib.request import urlretrieve

ALL = 'investengine_all.html'


def main():
    urlretrieve('https://investengine.com/etfs/all/', ALL)


if __name__ == "__main__":
    main()
