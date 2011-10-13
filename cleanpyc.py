import os
import shutil

def walk_all_file(dir_path, all_file_path):
    for f in os.listdir(dir_path):
        if os.path.isfile(f):
            all_file_path.append(f)
        else:
            try:
                walk_all_file(f, all_file_path)
            except:
                pass

if __name__ == '__main__':
    all_file_list = []
    #walk_all_file('.', all_file_list)
    topdown = True
    for root, dirs, files in os.walk('', topdown):
        for name in files:
            all_file_list.append(os.path.join(root, name))

    for f in all_file_list:
        if f[-4:] == '.pyc':
            print f
            os.remove(f)
            
if 0:
    for f in all_file_list:
        if os.path.splitext(os.path.basename(f))[1] == '.jpg':
            if os.path.exists(f[:-4]):
                print f
                if os.path.getsize(f[:-4]) >= os.path.getsize(f):
                    os.remove(f)
                else:
                    shutil.move(f, f[:-4])
            else:
                shutil.move(f, f[:-4])
