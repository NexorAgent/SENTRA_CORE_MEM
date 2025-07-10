import base64
import json
import os
import zlib

# Fonction pour encoder une chaîne de caractères en format zmem
# et mettre à jour l'index de mémoire


def encode_zmem(
    content: str,
    ctx_tag: str,
    zlib_txt_out: str,
    zlib_bin_out: str,
    zmem_src_out: str,
    zmem_bin_out: str,
    update_dict_path: str,
):
    """
    Simule la compression d'une entrée de mémoire (content) et met à jour l'index.
    - Écrit le contenu brut dans zmem_src_out
    - Écrit une version compressée simple (via zlib + base64) dans zmem_bin_out
    - Met à jour l'index JSON spécifié par update_dict_path
    """
    # Créer les dossiers parents pour toutes les sorties
    for path in [zmem_src_out, zmem_bin_out, zlib_txt_out, zlib_bin_out]:
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                print(f"❌ Erreur création du dossier {parent_dir}: {e}")

    # Écrire le contenu texte dans zmem_src_out
    try:
        with open(zmem_src_out, "w", encoding="utf-8") as f_src:
            f_src.write(content)
    except Exception as e:
        print(f"❌ Erreur écriture zmem_src_out: {e}")

    # Compression via zlib + base64
    try:
        compressed = zlib.compress(content.encode("utf-8"))
        b64 = base64.b64encode(compressed).decode("utf-8")
        # Écriture de la version base64 compressée dans zmem_bin_out
        with open(zmem_bin_out, "w", encoding="utf-8") as f_bin:
            f_bin.write(b64)
    except Exception as e:
        print(f"❌ Erreur compression zmem: {e}")

    # Écrire également le texte compressé en clair dans zlib_txt_out (optionnel)
    try:
        with open(zlib_txt_out, "w", encoding="utf-8") as f_ztxt:
            f_ztxt.write(b64)
    except Exception as e:
        print(f"❌ Erreur écriture zlib_txt_out: {e}")

    # Mettre à jour l'index de mémoire (update_dict_path)
    index = {}
    if os.path.exists(update_dict_path):
        try:
            with open(update_dict_path, "r", encoding="utf-8") as f_idx:
                index = json.load(f_idx)
        except json.JSONDecodeError:
            index = {}
        except Exception as e:
            print(f"❌ Erreur lecture index mémoire: {e}")

    # Utiliser ctx_tag comme clé, et stocker le chemin du fichier .zmem (ici zmem_bin_out)
    index[ctx_tag] = zmem_bin_out
    try:
        with open(update_dict_path, "w", encoding="utf-8") as f_idx:
            json.dump(index, f_idx, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Erreur écriture index mémoire: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Encoder un fichier texte en mémoire compressée (.zmem)"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Chemin vers le fichier texte à compresser"
    )
    parser.add_argument(
        "-n", "--name", required=True, help="Nom à donner à la mémoire (fichier .zmem)"
    )
    args = parser.parse_args()

    input_path = args.input
    name = args.name

    # Lire le fichier d'entrée
    try:
        with open(input_path, "r", encoding="utf-8") as f_in:
            content = f_in.read()
    except Exception as e:
        print(f"❌ Erreur lecture fichier d'entrée: {e}")
        exit(1)

    # Générer les noms de fichiers de sortie
    zmem_src_out = os.path.join("memory_zia", f"{name}.src")
    zmem_bin_out = os.path.join("memory_zia", f"{name}.zmem")
    zlib_txt_out = os.path.join("memory_zia", f"{name}.l64.t")
    zlib_bin_out = os.path.join("memory_zia", f"{name}.l64.b")
    update_dict_path = "memory_index.json"

    # Appeler la fonction encode_zmem
    encode_zmem(
        content=content,
        ctx_tag=name,
        zlib_txt_out=zlib_txt_out,
        zlib_bin_out=zlib_bin_out,
        zmem_src_out=zmem_src_out,
        zmem_bin_out=zmem_bin_out,
        update_dict_path=update_dict_path,
    )
    print(f"[OK] Mémoire '{name}' sauvegardée.")
