import sys
import re

LATEX_HEADER = r"""\documentclass[16pt]{ctexart} % Increase font size
\usepackage{xpinyin}
\usepackage{setspace} % Package to control spacing
\usepackage{reledmac} % three column footnotes
\arrangementX[A]{threecol}
\let\footnote\footnoteA
\renewcommand{\baselinestretch}{2} % Adjust line spacing globally

% Manually adjust the font size to ensure it takes effect
\makeatletter
\renewcommand{\normalsize}{\@setfontsize{\normalsize}{16pt}{16pt}} % Define base font size
\makeatother

\newcommand{\underword}[2]{\underline{#1}\footnote{#2}}

\begin{document}

\section*{Generated Graded Reader}

"""

LATEX_FOOTER = r"""

\end{document}
"""

def parse_script(file_path):
    """Parses the input script file into structured data."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n\n")  # Split on blank lines

    parsed_sentences = []
    for block in lines:
        parts = block.split("\n")
        if len(parts) < 2:
            continue  # Skip malformed entries
        chinese, english = parts[0], parts[1]
        parsed_sentences.append((chinese.strip(), english.strip()))

    return parsed_sentences

def format_latex(sentences):
    """Formats sentences into LaTeX with xpinyin, bold names, and footnotes."""
    def process_formatting(text):
        """Apply both bold and underword formatting to a single line."""
        para_break = "\n\n" if r"\p" in text else ""

        # Handle bold names (parentheses)
        text = re.sub(r"\((.*?)\)", r"\\textbf{\1}", text)

        # Handle footnotes {curly braces}
        text = re.sub(r"\[(.*?)\]\[(.*?)\]", r"\\underword{\1}{\2}", text)

        # add paragraph breaks \p
        text = re.sub(r"\\p", "", text)

        return text, para_break

    formatted_lines = []
    for chinese, _ in sentences:
        chinese, para_break = process_formatting(chinese)
        formatted_lines.append(f"{para_break}\\xpinyin*{{{chinese}}}")
    
    formatted_txt = ""
    for l in formatted_lines:
        formatted_txt += l + "\n"
    return LATEX_HEADER + "\n" + formatted_txt + "\n" + LATEX_FOOTER

def generate_text_files(sentences, base_name):
    """Generates two text files for TTS:
    - One with only the Chinese text.
    - One with Chinese, English, and repeated Chinese.
    """
    chinese_lines = []
    chinese_eng_repeat_lines = []

    for chinese, english in sentences:
        # Process bold formatting (remove parentheses)
        chinese_clean = re.sub(r"[()]", "", chinese)
        # Process footnote formatting (remove curly braces)
        chinese_clean = re.sub(r"\[(.*?)\]\[(.*?)\]", r"\1", chinese_clean)
        chinese_clean = re.sub(r"\\p", "", chinese_clean)

        chinese_lines.append(chinese_clean)
        chinese_eng_repeat_lines.extend([chinese_clean, english, chinese_clean])

    with open(f"{base_name}_chinese.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(chinese_lines))

    with open(f"{base_name}_chinese_english_repeat.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(chinese_eng_repeat_lines))

def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_to_latex.py <input_script.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    base_name = input_file.rsplit(".", 1)[0]  # Remove file extension

    sentences = parse_script(input_file)
    latex_output = format_latex(sentences)

    with open(f"{base_name}.tex", "w", encoding="utf-8") as f:
        f.write(latex_output)

    generate_text_files(sentences, base_name)

    print(f"Generated: {base_name}.tex, {base_name}_chinese.txt, {base_name}_chinese_english_repeat.txt")

if __name__ == "__main__":
    main()
