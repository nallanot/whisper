import subprocess
import sys
import tempfile
import threading
from pathlib import Path
import streamlit as st
from summary import summarize

st.set_page_config(page_title="Résumés de rencontres", page_icon="📝", layout="centered")

@st.cache_resource
def processing_lock():
    return threading.Lock()

st.title("Résumés de rencontres")
st.caption("Transcription et compte rendu sur votre serveur • Traitement local")
st.write("Déposez un enregistrement pour obtenir une transcription horodatée, les décisions et les suivis.")
st.info("Relisez le résultat avant utilisation. Les noms, chiffres et passages peu audibles peuvent être mal transcrits.")
uploaded = st.file_uploader("Enregistrement audio (200 Mo maximum)", type=["m4a", "mp3", "wav", "ogg", "flac", "aac", "mp4"])
language = st.selectbox("Langue de l'enregistrement", ["Français", "Détection automatique", "Anglais"])
lang = {"Français": "fr", "Détection automatique": "auto", "Anglais": "en"}[language]

with st.expander("Reprendre une transcription déjà enregistrée"):
    saved_text = st.file_uploader("Transcription UTF-8 (.txt, 5 Mo maximum)", type=["txt"])
    if st.button("Charger la transcription", disabled=saved_text is None):
        if saved_text.size > 5 * 1024 * 1024:
            st.error("Le fichier texte dépasse 5 Mo.")
        else:
            try:
                restored = saved_text.getvalue().decode("utf-8-sig")
                if not restored.strip():
                    raise ValueError("La transcription est vide.")
                st.session_state.transcript = restored
                st.session_state.pop("summary", None)
                st.success("Transcription chargée. Cliquez sur Générer le résumé ci-dessous.")
            except (UnicodeDecodeError, ValueError) as error:
                st.error(f"Fichier texte invalide : {error}")

if st.button("Transcrire et résumer", type="primary", disabled=uploaded is None):
    lock = processing_lock()
    if not lock.acquire(blocking=False):
        st.warning("Un traitement est déjà en cours. Réessayez après sa fin.")
    else:
        st.session_state.pop("transcript", None)
        st.session_state.pop("summary", None)
        try:
            with st.status("Transcription en cours…", expanded=True) as status:
                with tempfile.TemporaryDirectory() as directory:
                    source = Path(directory) / ("audio" + Path(uploaded.name).suffix.lower())
                    target = Path(directory) / "transcription.txt"
                    source.write_bytes(uploaded.getbuffer())
                    # Le sous-processus libère toute la mémoire Whisper avant Ollama.
                    process = subprocess.run([sys.executable, "/app/transcribe.py", str(source), str(target), lang],
                                             capture_output=True, timeout=21600)
                    if process.returncode:
                        raise RuntimeError("Transcription impossible : vérifiez le format audio, l'installation du modèle et la mémoire disponible.")
                    transcript = target.read_text(encoding="utf-8")
                if not transcript.strip():
                    raise RuntimeError("Aucune parole détectée dans ce fichier.")
                st.session_state.transcript = transcript
                st.session_state.summary = summarize(transcript, lambda message: status.update(label=message))
                status.update(label="Compte rendu prêt", state="complete", expanded=False)
        except Exception as error:
            st.error(str(error))
            st.caption("Si la transcription a réussi, elle reste téléchargeable ci-dessous.")
        finally:
            lock.release()

if "transcript" in st.session_state and st.button("Générer le résumé à partir de la transcription"):
    lock = processing_lock()
    if not lock.acquire(blocking=False):
        st.warning("Un traitement est déjà en cours. Réessayez après sa fin.")
    else:
        try:
            with st.status("Génération du résumé…", expanded=True) as status:
                result = summarize(st.session_state.transcript,
                                   lambda message: status.update(label=message))
                st.session_state.summary = result
                status.update(label="Compte rendu prêt", state="complete", expanded=False)
        except Exception as error:
            st.error(str(error))
        finally:
            lock.release()

if "summary" in st.session_state:
    st.markdown(st.session_state.summary)
    st.download_button("Télécharger le compte rendu (.md)", st.session_state.summary, "compte-rendu.md", "text/markdown")
if "transcript" in st.session_state:
    with st.expander("Transcription horodatée"):
        st.text(st.session_state.transcript)
    st.download_button("Télécharger la transcription (.txt)", st.session_state.transcript, "transcription.txt", "text/plain")
    if st.button("Effacer les résultats de cette session"):
        st.session_state.pop("summary", None)
        st.session_state.pop("transcript", None)
        st.rerun()
st.caption("Les résultats restent dans la session : téléchargez-les avant de fermer la page. Aucun historique permanent n'est créé. Pas d'identification automatique des intervenants.")

