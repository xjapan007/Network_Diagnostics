import speedtest
import subprocess
import platform
import datetime
import time
import locale

# (La fonction _decode_bytes ne change pas)
def _decode_bytes(byte_string):
    if not byte_string:
        return ""
    encodings_to_try = [
        'utf-8', 'cp850', 'cp1252', locale.getpreferredencoding()
    ]
    unique_encodings = []
    for enc in encodings_to_try:
        if enc and enc not in unique_encodings:
            unique_encodings.append(enc)
    for encoding in unique_encodings:
        try:
            return byte_string.decode(encoding)
        except UnicodeDecodeError:
            continue 
    return byte_string.decode('cp1252', errors='replace')

# (La fonction run_ping_test ne change pas)
def run_ping_test(host="google.com", count=4):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    commande = ['ping', param, str(count), host]
    try:
        result = subprocess.run(commande, capture_output=True, check=True)
        output_str = _decode_bytes(result.stdout)
        return {"success": True, "output": output_str.strip(), "timestamp": datetime.datetime.now().isoformat()}
    except subprocess.CalledProcessError as e:
        output_str = _decode_bytes(e.stdout)
        error_str = _decode_bytes(e.stderr)
        return {"success": False, "output": output_str.strip() + "\n" + error_str.strip(), "error": f"Commande ping échouée : {e}", "timestamp": datetime.datetime.now().isoformat()}
    except Exception as e:
        return {"success": False, "output": "", "error": f"Erreur inattendue lors du ping : {e}", "timestamp": datetime.datetime.now().isoformat()}


# --- SUPPRIMÉ ---
# La fonction get_server_list() a été supprimée car elle est bloquée (403 Forbidden)


# --- MODIFIÉ : run_speed_test utilise TOUJOURS le meilleur serveur ---
def run_speed_test(log_callback=None):
    """
    Lance un speedtest en utilisant le meilleur serveur automatiquement.
    """
    
    def do_log(message):
        if log_callback:
            log_callback(message)

    try:
        st = speedtest.Speedtest()
        
        # Comportement automatique
        do_log("Recherche du meilleur serveur... (cela peut prendre 10-20s)")
        st.get_best_server() 
        
        do_log(f"Serveur utilisé : {st.results.server['host']} ({st.results.server['country']})")
        
        do_log("Test de téléchargement (Download) en cours...")
        st.download()
        
        do_log("Test d'envoi (Upload) en cours...")
        st.upload()
        
        results = st.results
        
        return {
            "success": True,
            "download": results.download / 1_000_000,
            "upload": results.upload / 1_000_000,
            "ping": results.ping,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except speedtest.ConfigRetrievalError as e:
        do_log(f"Erreur : Impossible de se connecter à Speedtest.net. {e}")
        return {"success": False, "error": "Impossible de se connecter à Speedtest.net.", "timestamp": datetime.datetime.now().isoformat()}
    except Exception as e:
        do_log(f"Une erreur est survenue : {e}")
        return {"success": False, "error": f"Une erreur est survenue lors du speedtest : {e}", "timestamp": datetime.datetime.now().isoformat()}