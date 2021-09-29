import glob

import fire


def main():
    all_guesses = glob.glob("guess*")
    hits = 0
    for filename in all_guesses:
        num = filename[-3:]
        info_filename = f"info{num}"

        with open(filename, "r") as f:
            guess = f.read().strip()

        with open(info_filename, "r") as f:
            f.readline()
            target = f.readline().split(":")[1].strip()

        if guess == target:
            hits += 1

    return hits / len(all_guesses)


fire.Fire(main)