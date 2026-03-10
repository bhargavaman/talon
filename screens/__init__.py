# So, I have a confession to make, I was working on Talon and
# kept coming across a "failed to import module 'screens'". I
# ran out of ideas so I made this __init__.py file and it for
# some reason worked.
# 
# I have a feeling this issue has since been resolved, and
# this file is likely not necessary anymore, but frankly I am
# too afraid to find out.
#
# Developers with more confidence than me can try



from importlib import import_module



__all__ = ["load"]



def load(name: str):
    return import_module(f"screens.{name}")
