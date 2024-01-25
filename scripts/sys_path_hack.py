
if __name__ == "__main__" and __package__ is None:
    from sys import path
    import os
    from os.path import dirname as dir

    parentdir = dir(path[0])
    # path.append(parentdir)
    
    path.insert(0, parentdir)
    os.chdir(parentdir)
    __package__ = "scripts"