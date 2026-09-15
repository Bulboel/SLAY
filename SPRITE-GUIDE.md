# Format des sprites de SLAY

Chaque nouvel asset passe par `tools/prepare-sprites.ps1` avant publication.

## Personnages et Slays sur la carte

- Une bande horizontale de quatre poses : face immobile, face en marche, profil, dos.
- Sortie normalisée : `384 × 96 px`, soit quatre cellules de `96 × 96 px`.
- Sujet centré dans chaque cellule et pieds alignés en bas.
- Fond réellement transparent : aucun damier dessiné dans l’image.

## Slays en combat

- Quatre fichiers séparés : `normal`, `attack`, `hit`, `down`.
- Sortie normalisée : `384 × 384 px` par attitude.
- Le sujet doit tenir entièrement dans la zone et conserver la même échelle visuelle.

## Contrôle obligatoire

Le script refuse un fichier si ses dimensions sont incorrectes, si le sujet a disparu pendant le détourage ou si aucune transparence n’est détectée. Le jeu ne doit jamais référencer la planche source brute : uniquement les fichiers normalisés et validés.

