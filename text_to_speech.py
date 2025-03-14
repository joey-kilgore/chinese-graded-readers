import os
import azure.cognitiveservices.speech as speechsdk
import tempfile
import constants


def text_to_speech(inputText, outputFileName='default.mp3'):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=constants.SPEECH_KEY, region=constants.SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The neural multilingual voice can speak different languages based on the input text.
    speech_config.speech_synthesis_voice_name='zh-CN-XiaochenMultilingualNeural'

    temp_file_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file_path)

    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(inputText).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(inputText))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    with open(outputFileName, 'wb') as audio_file:
        audio_file.write(speech_synthesis_result.audio_data)

    print(f"Audio saved to {outputFileName}")