#!/usr/bin/env python
import os
import click
import shutil
import subprocess
import glob
from typing import Optional

from generate_csv import generate_csv as gen_csv, batch_generation as batch_csv
from generate_ass import generate_ass as gen_ass
from src.read_ini import config

TXT_PATH = config.get("File Path", "TXT_PATH")
ASS_PATH = config.get("File Path", "ASS_PATH")
CSV_PATH = config.get("File Path", "CSV_PATH")


def ensure_directories():
    os.makedirs(TXT_PATH, exist_ok=True)
    os.makedirs(ASS_PATH, exist_ok=True)
    os.makedirs(CSV_PATH, exist_ok=True)


@click.group()
def cli():
    """Convert game txt files to subtitles or CSV with AI translation."""
    ensure_directories()


@cli.command("csv")
@click.argument("filename", required=False)
@click.option("--all", "-a", is_flag=True, help="Process all txt files")
@click.option("--concurrent", "-c", is_flag=True, help="Use concurrent processing")
@click.option(
    "--workers", "-w", default=5, help="Number of concurrent workers, default is 5"
)
def process_csv(filename: Optional[str], all: bool, concurrent: bool, workers: int):
    """Convert txt files to CSV format"""
    if all:
        click.echo("Processing all TXT files and converting to CSV format...")
        if concurrent:
            click.echo(f"Using {workers} concurrent threads")
            batch_csv(max_workers=workers)
        else:
            for filepath, dirnames, filenames in os.walk(TXT_PATH):
                for file in filenames:
                    if not file.endswith(".txt") or not file.startswith("adv_"):
                        continue
                    gen_csv(file)
    elif filename:
        if not os.path.exists(f"{TXT_PATH}/{filename}"):
            click.echo(f"Error: File {filename} does not exist!")
            return
        gen_csv(filename)
    else:
        click.echo(
            "Please specify a filename or use the --all option to process all files."
        )


@cli.command("ass")
@click.argument("filename", required=False)
@click.option("--all", "-a", is_flag=True, help="Process all txt files")
def process_ass(filename: Optional[str], all: bool):
    """Convert txt files to ASS format"""
    if all:
        click.echo("Processing all TXT files and converting to ASS format...")
        for filepath, dirnames, filenames in os.walk(TXT_PATH):
            for file in filenames:
                if not file.endswith(".txt") or not file.startswith("adv_"):
                    continue
                gen_ass(file)
    elif filename:
        if not os.path.exists(f"{TXT_PATH}/{filename}"):
            click.echo(f"Error: File {filename} does not exist!")
            return
        gen_ass(filename)
    else:
        click.echo(
            "Please specify a filename or use the --all option to process all files."
        )


@cli.command("clone")
@click.argument(
    "repo_url", default="https://github.com/DreamGallery/Campus-adv-txts.git"
)
@click.option("--branch", "-b", default="main", help="Specify the branch to clone")
@click.option(
    "--path",
    "-p",
    default="",
    help="Specify the path to copy the text files in the repository",
)
def clone_repo(repo_url: str, branch: str, path: str):
    """Clone text files from a remote repository to the adv/txt"""
    temp_dir = "temp_clone"

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    try:
        click.echo(f"Cloning repository {repo_url} branch {branch}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir],
            check=True,
        )

        source_path = os.path.join(temp_dir, path) if path else temp_dir

        copied_count = 0
        for txt_file in glob.glob(f"{source_path}/**/*.txt", recursive=True):
            filename = os.path.basename(txt_file)
            if filename.startswith("adv_"):
                target_path = os.path.join(TXT_PATH, filename)
                shutil.copy2(txt_file, target_path)
                copied_count += 1

        click.echo(f"Completed! {copied_count} files copied to {TXT_PATH}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error cloning repository: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@cli.command("convert-all")
@click.option("--concurrent", "-c", is_flag=True, help="Use concurrent processing")
@click.option(
    "--workers", "-w", default=5, help="Number of concurrent workers, default is 5"
)
def convert_all(concurrent: bool, workers: int):
    """Convert all TXT files to CSV and ASS format at the same time"""
    click.echo("Start converting all files to CSV format...")
    if concurrent:
        click.echo(f"Using {workers} concurrent threads")
        batch_csv(max_workers=workers)
    else:
        for filepath, dirnames, filenames in os.walk(TXT_PATH):
            for file in filenames:
                if not file.endswith(".txt") or not file.startswith("adv_"):
                    continue
                click.echo(f"CSV processing: {file}")
                gen_csv(file)

    click.echo("Start converting all files to ASS format...")
    for filepath, dirnames, filenames in os.walk(TXT_PATH):
        for file in filenames:
            if not file.endswith(".txt") or not file.startswith("adv_"):
                continue
            click.echo(f"ASS processing: {file}")
            gen_ass(file)

    click.echo("All files processed")


@cli.command("count")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["txt", "csv", "ass", "all"]),
    default="all",
    help="Count the number of files",
)
def list_files(format: str):
    """Count the number of files"""
    if format in ["txt", "all"]:
        files = os.listdir(TXT_PATH)
        files = [f for f in files if f.endswith(".txt") and f.startswith("adv_")]
        click.echo(f"There are {len(files)} TXT files")

    if format in ["csv", "all"]:
        files = os.listdir(CSV_PATH)
        files = [f for f in files if f.endswith(".csv")]
        click.echo(f"There are {len(files)} CSV files")

    if format in ["ass", "all"]:
        files = os.listdir(ASS_PATH)
        files = [f for f in files if f.endswith(".ass")]
        click.echo(f"There are {len(files)} ASS files")


if __name__ == "__main__":
    cli()
