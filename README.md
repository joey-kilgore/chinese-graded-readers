# Autogenerate Graded Readers

FOR Text-To-Speech you will need an Azure account setup and put your API key and region in `constants.py`

For an Azure account go [HERE](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account?icid=ai-services&azure-portal=true)  
Create a Speech service [HERE](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource)  
From there you should be able to grab the API key and region to put in `constants.py`


Usage：
```
virtualenv venv
pip3 install -r requirements.txt
python3 story_to_tex.py input_file.txt
```

This will generate a few things
1. LaTeX file for creating the PDF document
2. A text file with just the chinese (for personal TTS use)
3. A text file with chinese-english-chinese (for personal TTS use)
4. Audio file of just chinese audio
5. Audio file of the chinese-english-chinese

## Text input format
Test input files are in the following form

```
中文
chinese

(刘备)
Liu Bei

[朋友][friend]
friend

\p一二三
one two three
```

where we have lines in order of chinese, english, blank.
Then there are some additional formatting:
- parenthesis for bolding (names)
- square brackets for vocab [中文][chinese]
- \p for starting new paragraphs
