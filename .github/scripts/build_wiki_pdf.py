#!/usr/bin/env python3
"""
build_wiki_pdf.py

Usage:
    python build_wiki_pdf.py <wiki_folder> <output_pdf> <language>

Example:
    python build_wiki_pdf.py ./v2.wiki en-manuals.pdf english
    python build_wiki_pdf.py ./v2.wiki uk-manuals.pdf ukrainian

This script performs the following steps:
  1) Reads <wiki_folder>/_Sidebar.md.
  2) Extracts the "# Public Manuals" section (until the next heading) and
     filters links by the specified language (e.g. "english" or "ukrainian").
  3) For each referenced .md file, it parses the first heading to build a Table of Contents (TOC).
  4) Merges the files into a combined markdown file that begins with a TOC.
     For each file, if the first non-empty line is not already an H1 header,
     it inserts a proper H1 header.
  5) Uses Pandoc to convert the combined markdown to HTML (optionally linking a custom CSS file).
  6) Injects a page header style into the HTML so that each printed page displays:
         "Proprietary and Confidential - TELETACTICA Sp. z o.o."
  7) Uses WeasyPrint to convert the HTML into the final PDF.

Environment Variables:
    MARKDOWN_CSS (optional): Path to a CSS file for styling. If not set, the script will look for
                             "weasyprint-markdown.css" in the current working directory.
"""

import os
import re
import subprocess
import logging
import sys
import argparse
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_first_heading(md_path: str) -> Tuple[str, str]:
    """
    Extracts the first ATX heading from a markdown file.

    Args:
        md_path: Path to the markdown file.

    Returns:
        A tuple (heading_text, anchor) where heading_text is the text of the first heading
        (or the file's basename if no heading is found) and anchor is a sanitized (lowercase, hyphenated)
        version used for internal linking.
    """
    file_basename = os.path.basename(md_path)
    fallback_text = os.path.splitext(file_basename)[0]
    heading_text: str = ""
    heading_regex = re.compile(r"^(#{1,6})\s+(.*)")

    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            match = heading_regex.match(line.strip())
            if match:
                heading_text = match.group(2).strip()
                break

    if not heading_text:
        heading_text = fallback_text

    anchor = re.sub(r"[^a-zA-Z0-9]+", "-", heading_text.lower()).strip("-")
    if not anchor:
        anchor = fallback_text.lower().replace(".", "-")
    return heading_text, anchor


def inject_page_header(html_path: str) -> None:
    """
    Injects a <style> block into the HTML file to define a page header that appears on every page.
    The header text is "Proprietary and Confidential - TELETACTICA Sp. z o.o."

    Args:
        html_path: Path to the HTML file to modify.
    """
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        logging.error(f"Error reading {html_path}: {e}")
        return

    style_block = (
        "<style>\n"
        "@page {\n"
        "  @top-center {\n"
        "    content: \"Proprietary and Confidential - TELETACTICA Sp. z o.o.\";\n"
        "    font-size: 10pt;\n"
        "    color: #555;\n"
        "    margin-top: 10px;\n"
        "  }\n"
        "}\n"
        "</style>\n"
    )

    if "<head>" in html_content:
        html_content = html_content.replace("<head>", "<head>" + style_block, 1)
    else:
        html_content = style_block + html_content

    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        logging.error(f"Error writing {html_path}: {e}")


def parse_sidebar(wiki_folder: str, language: str) -> List[str]:
    """
    Parses the _Sidebar.md file in the wiki folder to extract markdown file references
    from the "# Public Manuals" section that match the specified language.

    Args:
        wiki_folder: Path to the wiki folder.
        language: Target language string (e.g., "english" or "ukrainian").

    Returns:
        A list of markdown file names (with extension) that are referenced in the Public Manuals section.
    """
    sidebar_path = os.path.join(wiki_folder, "_Sidebar.md")
    if not os.path.exists(sidebar_path):
        raise FileNotFoundError(f"Could not find _Sidebar.md at '{sidebar_path}'")

    with open(sidebar_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    heading_pattern = re.compile(r"^(#{1,6})\s+.*")
    link_pattern = re.compile(r"\[(.*?)\]\((.*?)\)")
    in_public_manuals = False
    md_links = []  # List of tuples: (link_text, link_target)

    for line in lines:
        line_stripped = line.strip()
        heading_match = heading_pattern.match(line_stripped)
        if heading_match:
            heading_text = line_stripped.lstrip("#").strip().lower()
            if heading_text == "public manuals":
                in_public_manuals = True
                continue
            elif in_public_manuals:
                # End of Public Manuals section
                break

        if not in_public_manuals:
            continue

        for (ltxt, ltarget) in link_pattern.findall(line):
            if language in ltxt.lower():
                md_links.append((ltxt, ltarget))

    md_files: List[str] = []
    for (_, link_target) in md_links:
        link_target = link_target.strip()
        if not link_target.lower().endswith(".md"):
            link_target += ".md"
        full_path = os.path.join(wiki_folder, link_target)
        if os.path.exists(full_path):
            md_files.append(link_target)
        else:
            logging.warning(f"Link target '{link_target}' not found in wiki folder.")
    return md_files


def build_file_info(wiki_folder: str, md_files: List[str]) -> List[Tuple[str, str, str]]:
    """
    For each markdown file, extract its first heading and build a tuple (filename, heading_text, anchor).

    Args:
        wiki_folder: Path to the wiki folder.
        md_files: List of markdown file names (with extension).

    Returns:
        A list of tuples for each file.
    """
    file_info: List[Tuple[str, str, str]] = []
    for mdfile in md_files:
        full_md_path = os.path.join(wiki_folder, mdfile)
        htext, hanchor = extract_first_heading(full_md_path)
        file_info.append((mdfile, htext, hanchor))
    return file_info


def merge_markdown_files(wiki_folder: str, file_info: List[Tuple[str, str, str]], language: str) -> str:
    """
    Merges the markdown files specified in file_info into a single combined markdown file.
    It creates a Table of Contents with a language-specific header ("Table of Contents" or "Зміст")
    and, for each file, writes an anchor plus a proper H1 header if the file content doesn't already start with one.

    Args:
        wiki_folder: Path to the wiki folder.
        file_info: List of tuples (filename, heading_text, anchor).
        language: The language (used for TOC header).

    Returns:
        The path to the merged markdown file.
    """
    combined_md_path = os.path.join(wiki_folder, "combined.md")
    toc_heading = "Зміст" if language == "ukrainian" else "Table of Contents"
    toc_lines = [f"# {toc_heading}\n"]
    for (_, htext, hanchor) in file_info:
        toc_lines.append(f"- [{htext}](#{hanchor})\n")
    toc_section = "".join(toc_lines) + "\n"

    with open(combined_md_path, "w", encoding="utf-8") as outf:
        outf.write(toc_section)
        for (mdfile, htext, hanchor) in file_info:
            full_md_path = os.path.join(wiki_folder, mdfile)
            with open(full_md_path, "r", encoding="utf-8") as inf:
                content = inf.read()

            outf.write("\n<div style=\"page-break-after: always;\"></div>\n")
            outf.write(f"\n\n<!-- Start of {mdfile} -->\n\n")
            outf.write(f"<a name=\"{hanchor}\"></a>\n\n")
            # Check if the first non-empty line is an H1 header.
            first_line = ""
            for line in content.splitlines():
                if line.strip():
                    first_line = line.strip()
                    break
            if not first_line.startswith("#"):
                outf.write(f"# {htext}\n\n")
            outf.write(content)
            outf.write(f"\n\n<!-- End of {mdfile} -->\n\n")
    return combined_md_path


def convert_markdown_to_html(combined_md_path: str, css_file: str) -> str:
    """
    Uses Pandoc to convert a markdown file to HTML, linking a custom CSS file if provided.

    Args:
        combined_md_path: Path to the merged markdown file.
        css_file: Path to the CSS file (if exists).

    Returns:
        The path to the generated HTML file.
    """
    combined_html_path = os.path.join(os.path.dirname(combined_md_path), "combined.html")
    css_argument = []
    if css_file and os.path.exists(css_file):
        css_argument = ["--css", css_file]
    cmd_pandoc = ["pandoc", "--standalone"] + css_argument + ["-o", combined_html_path, combined_md_path]
    logging.info("Running pandoc to generate combined.html...")
    result = subprocess.run(cmd_pandoc)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed with exit code {result.returncode}")
    return combined_html_path


def convert_html_to_pdf(html_path: str, output_pdf: str) -> None:
    """
    Uses WeasyPrint to convert an HTML file to a PDF.
    Also injects a page header into the HTML before conversion.

    Args:
        html_path: Path to the HTML file.
        output_pdf: Path where the final PDF should be saved.
    """
    inject_page_header(html_path)
    cmd_weasy = ["weasyprint", "-p", html_path, output_pdf]
    logging.info(f"Running weasyprint to generate {output_pdf}...")
    result = subprocess.run(cmd_weasy)
    if result.returncode != 0:
        raise RuntimeError(f"WeasyPrint failed with exit code {result.returncode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a PDF from a wiki folder of markdown files.")
    parser.add_argument("wiki_folder", help="Path to the wiki folder.")
    parser.add_argument("output_pdf", help="Name of the output PDF file.")
    parser.add_argument("language", help="Language to filter (e.g., 'english' or 'ukrainian').")
    args = parser.parse_args()

    wiki_folder: str = args.wiki_folder
    output_pdf: str = args.output_pdf
    language: str = args.language.lower()

    # Determine CSS file via environment variable or default.
    css_file: str = os.environ.get("MARKDOWN_CSS") or os.path.join(os.getcwd(), "weasyprint-markdown.css")
    if os.path.exists(css_file):
        logging.info(f"Using CSS file: {css_file}")
    else:
        logging.info("No custom CSS file found; proceeding without extra CSS.")
        css_file = ""

    sidebar_path: str = os.path.join(wiki_folder, "_Sidebar.md")
    if not os.path.exists(sidebar_path):
        logging.error(f"Could not find _Sidebar.md at '{sidebar_path}'")
        sys.exit(1)

    # Parse _Sidebar.md and filter links from the "# Public Manuals" section by language.
    try:
        md_files: List[str] = parse_sidebar(wiki_folder, language)
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)

    if not md_files:
        logging.error(f"No matching .md files found for language '{language}' in # Public Manuals.")
        sys.exit(1)

    # Gather heading info for TOC.
    file_info = build_file_info(wiki_folder, md_files)
    logging.info(f"Merging {len(file_info)} files for '{language}'...")

    combined_md_path = merge_markdown_files(wiki_folder, file_info, language)
    logging.info(f"Created merged file: {combined_md_path}")

    # Convert merged markdown to HTML.
    combined_html_path = convert_markdown_to_html(combined_md_path, css_file)
    logging.info(f"Generated HTML file: {combined_html_path}")

    # Convert HTML to PDF.
    output_pdf_path = os.path.join(wiki_folder, output_pdf)
    convert_html_to_pdf(combined_html_path, output_pdf_path)
    logging.info(f"Success! Generated {output_pdf_path}")


if __name__ == "__main__":
    main()
