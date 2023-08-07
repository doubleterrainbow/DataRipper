import os
import difflib


if __name__ == '__main__':
    old_folder = "D:\\Documents\\Sun Haven Assets\\output\\full_1.2"
    updated_folder = "D:\\Documents\\Sun Haven Assets\\output\\1.2.2"
    diff_folder = "D:\\Documents\\Sun Haven Assets\\output\\diffs"
    
    if not os.path.exists(diff_folder):
        os.mkdir(diff_folder)
    
    for file_name in os.listdir(old_folder):
        print(f"Checking {file_name} for changes...")
        
        if file_name.startswith("fileTypes"):
            print("Skipping file types file.")
            continue
        
        matching_updated_file = os.path.join(updated_folder, file_name)
        if not os.path.exists(matching_updated_file):
            print(f"{file_name} not in updated folder, writing to diffs...")
            with open(f"{diff_folder}/{file_name}", 'w', encoding='utf-8') as diff_file:
                with open(os.path.join(old_folder, file_name), 'r', encoding='utf-8') as old_file:
                    diff_file.writelines(old_file.readlines())
        else:
            with open(os.path.join(old_folder, file_name), 'r', encoding='utf-8') as old_file:
                with open(matching_updated_file, 'r', encoding='utf-8') as updated_file:
                    diff = difflib.HtmlDiff().make_file(
                        fromlines=old_file.readlines(),
                        tolines=updated_file.readlines(),
                        context=True,
                        numlines=8
                    )
                    
                    with open(os.path.join(diff_folder, file_name.split('.')[0] + ".html"), 'w') as diff_file:
                        diff_file.writelines(diff)
        
    for diff_file_name in os.listdir(diff_folder):
        files_to_delete = []
        
        diff_path = os.path.join(diff_folder, diff_file_name)
        
        diff_file = open(diff_path)
        if 'No Differences Found' in diff_file.read():
            files_to_delete.append(diff_path)
        diff_file.close()
            
        for file in files_to_delete:
            print(f"No difference in {diff_file_name}.")
            os.remove(diff_path)