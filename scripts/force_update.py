#!/usr/bin/env python
import sys
import bukgen

def force_update(*plugins):
    p = bukgen.bukkit.Parser()
    for plugin in plugins:
        p.plugin(plugin)

if __name__ == '__main__':
    force_update(*sys.argv[1:])