from TTS.api import TTS

tts = TTS(model_name="tts_models/pt/cv/vits", progress_bar=False, gpu=False)

texto = "Senha C quarenta e dois, por favor dirigir-se ao consultório sete."
tts.tts_to_file(text=texto, file_path="teste_coqui.wav")

print("Gerado: teste_coqui.wav")
