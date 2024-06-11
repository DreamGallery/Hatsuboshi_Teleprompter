import re

# change these two path to you actual path
origin_adv_file = "adv/txt/..."
new_adv_file = "adv/txt/..."

with open(origin_adv_file, "r", encoding="utf8") as fp1, open(new_adv_file, "w", encoding="utf8") as fp2:
    group_end = 0
    for index, line in enumerate(fp1):
        if "branch groupLength" in line:
            fp2.write("\nChoice group: \n")
            group_length = int(re.findall(r"\d+", line)[0])
            group_end = index + group_length
            continue
        if index != 0 and index == group_end:
            group_end = 0
            if "message" in line or "narration" in line:
                fp2.write(f"{line}\n")
                continue
        if "message" in line or "narration" in line:
            fp2.write(line)
