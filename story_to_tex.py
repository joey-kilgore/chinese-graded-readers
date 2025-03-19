import sys
import re
import argparse
from text_to_speech import text_to_speech
from gen_anki import generate_anki_flashcards

LATEX_HEADER = r"""\documentclass[16pt]{ctexart} % Increase font size
\usepackage{xpinyin}
\usepackage{setspace} % Package to control spacing
\usepackage{reledmac} % three column footnotes
\usepackage[a6paper]{geometry}
\arrangementX[A]{threecol}
\let\footnote\footnoteA
\renewcommand{\baselinestretch}{2} % Adjust line spacing globally

% Manually adjust the font size to ensure it takes effect
\makeatletter
\renewcommand{\normalsize}{\@setfontsize{\normalsize}{16pt}{16pt}} % Define base font size
\makeatother

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
    """Formats sentences into LaTeX with numbered footnotes per page."""
    vocab_dict = {}
    footnote_texts = []
    footnote_counter = 1

    def process_formatting(text):
        nonlocal footnote_counter
        para_break = "\n\n" if "\\p" in text else ""
        text = re.sub(r"\\p", "", text)  # Remove paragraph markers
        text = re.sub(r"\((.*?)\)", r"\\textbf{\1}", text)  # Bold formatting
        text = re.sub(r"==(.*?)==",r"\\section{\1}", text)
        
        def replace_vocab(match):
            nonlocal footnote_counter
            vocab, meaning = match.groups()
            if vocab not in vocab_dict:
                # First occurrence: Define the footnote with a label
                vocab_dict[vocab] = f"{footnote_counter}"
                footnote_counter += 1
                return f"\\underline{{{vocab}}}\\footnote{{\\label{{{vocab_dict[vocab]}}} {meaning}}}"
            else:
                # Subsequent occurrences: Reference the existing footnote
                return f"\\underline{{{vocab}}}\\footnotemark[{vocab_dict[vocab]}]"
        
        return re.sub(r"\[(.*?)\]\[(.*?)\]", replace_vocab, text), para_break

    processed_sentences = [process_formatting(ch) for ch, _ in sentences]
    formatted_lines = [pb + "\\xpinyin*{" + ch + "}" for ch, pb in processed_sentences]
    footnotes_section = "\n".join(footnote_texts) + "\n"

    return LATEX_HEADER + "\n".join(formatted_lines) + "\n" + footnotes_section + LATEX_FOOTER

def generate_text_and_audio_files(sentences, base_name):
    """Generates two text files for TTS:
    - One with only the Chinese text.
    - One with Chinese, English, and repeated Chinese.
    """
    chinese_lines = []
    chinese_chapters = []
    chinese_eng_repeat_lines = []
    chinese_eng_chapters = []

    for chinese, english in sentences:
        # move to next chapter when we find chapter markers
        if "==" in chinese and chinese_lines != []:
            chinese_chapters.append(chinese_lines)
            chinese_lines = []
            chinese_eng_chapters.append(chinese_eng_repeat_lines)
            chinese_eng_repeat_lines = []

        # Process bold formatting (remove parentheses)
        chinese_clean = re.sub(r"[()]", "", chinese)
        # Process footnote formatting (remove curly braces)
        chinese_clean = re.sub(r"\[(.*?)\]\[(.*?)\]", r"\1", chinese_clean)
        chinese_clean = re.sub(r"\\p", "", chinese_clean)
        chinese_clean = re.sub(r"==(.*?)==", r"\1", chinese_clean)

        chinese_lines.append(chinese_clean)
        chinese_eng_repeat_lines.extend([chinese_clean, english, chinese_clean])

    chinese_chapters.append(chinese_lines)
    chinese_eng_chapters.append(chinese_eng_repeat_lines)

    for chapter in range(len(chinese_chapters)):
        chinese_lines = chinese_chapters[chapter]
        chinese_eng_repeat_lines = chinese_eng_chapters[chapter]

        with open(f"{base_name}_chinese_{chapter}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(chinese_lines))

        full_chinese_txt = ""
        for c in chinese_lines:
            full_chinese_txt += f"{c}\n"
        text_to_speech(full_chinese_txt, f"{base_name}_chinese_{chapter}.mp3")

        with open(f"{base_name}_chinese_english_repeat_{chapter}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(chinese_eng_repeat_lines))

        full_chinese_txt = ""
        for c in chinese_eng_repeat_lines:
            full_chinese_txt += f"{c}\n"
        text_to_speech(full_chinese_txt, f"{base_name}_chinese_english_repeat_{chapter}.mp3")

def main():
    parser = argparse.ArgumentParser(description="Convert a formatted text file to LaTeX, TTS files, and Anki CSV.")
    parser.add_argument("input_file", help="Path to the input script file")
    parser.add_argument("--generate-audio", action="store_true", help="Generate audio files (optional, costs money)")
    args = parser.parse_args()

    base_name = args.input_file.rsplit(".", 1)[0]
    sentences = parse_script(args.input_file)
    latex_output = format_latex(sentences)

    with open(f"{base_name}.tex", "w", encoding="utf-8") as f:
        f.write(latex_output)

    print(f"Generated: {base_name}.tex, {base_name}_chinese.txt, {base_name}_chinese_english_repeat.txt")

    generate_anki_flashcards(sentences, base_name)

    if args.generate_audio:
        generate_text_and_audio_files(sentences, base_name)

if __name__ == "__main__":
    main()
